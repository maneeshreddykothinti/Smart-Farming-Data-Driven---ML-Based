"""
Smart Farming - Flask backend.
Serves the web UI and REST API for farmer profiles, crop management,
prediction, growth reports, irrigation recommendations and weather.
"""

import os
from flask import Flask, jsonify, request, send_from_directory

from ml_service import ml, SOIL_TYPE_OPTIONS, IRRIGATION_FREQUENCY_OPTIONS, \
    WATER_SOURCE_OPTIONS, GROWTH_STAGE_OPTIONS, SEASON_OPTIONS
from store import store
import weather as weather_mod

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')


# ---------------- pages ----------------
@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')


# ---------------- meta ----------------
@app.route('/api/meta')
def meta():
    return jsonify({
        'crops': ml.crops(),
        'feature_defaults': ml.feature_defaults(),
        'soil_types': SOIL_TYPE_OPTIONS,
        'irrigation_frequencies': IRRIGATION_FREQUENCY_OPTIONS,
        'water_sources': WATER_SOURCE_OPTIONS,
        'growth_stages': GROWTH_STAGE_OPTIONS,
        'seasons': SEASON_OPTIONS,
    })


# ---------------- farmers ----------------
@app.route('/api/farmers', methods=['GET', 'POST'])
def farmers():
    if request.method == 'GET':
        return jsonify(store.list_farmers())
    profile = request.get_json(force=True) or {}
    name = (profile.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name is required'}), 400
    return jsonify(store.create_farmer(profile)), 201


@app.route('/api/farmers/<farmer_id>', methods=['GET', 'PUT', 'DELETE'])
def farmer(farmer_id):
    if request.method == 'GET':
        f = store.get_farmer(farmer_id)
        return jsonify(f) if f else (jsonify({'error': 'not found'}), 404)
    if request.method == 'DELETE':
        ok = store.delete_farmer(farmer_id)
        return jsonify({'deleted': ok})
    profile = request.get_json(force=True) or {}
    f = store.update_farmer(farmer_id, profile)
    return jsonify(f) if f else (jsonify({'error': 'not found'}), 404)


# ---------------- plots ----------------
@app.route('/api/farmers/<farmer_id>/plots', methods=['POST'])
def add_plot(farmer_id):
    data = request.get_json(force=True) or {}
    crop = (data.get('crop') or '').strip()
    acres = data.get('acres')
    if not crop or not acres:
        return jsonify({'error': 'crop and acres are required'}), 400
    plot = store.add_plot(farmer_id, crop, acres, data.get('notes', ''))
    return jsonify(plot) if plot else (jsonify({'error': 'farmer not found'}), 404)


@app.route('/api/farmers/<farmer_id>/plots/<plot_id>', methods=['DELETE'])
def remove_plot(farmer_id, plot_id):
    ok = store.remove_plot(farmer_id, plot_id)
    return jsonify({'deleted': ok})


# ---------------- farming sessions ----------------
@app.route('/api/farmers/<farmer_id>/sessions', methods=['POST'])
def start_session(farmer_id):
    data = request.get_json(force=True) or {}
    res = store.start_session(farmer_id, data.get('plot_id'), data.get('start_date'))
    if res is None:
        return jsonify({'error': 'farmer or plot not found'}), 404
    if isinstance(res, dict) and res.get('error'):
        return jsonify(res), 409
    return jsonify(res), 201


@app.route('/api/farmers/<farmer_id>/sessions/<session_id>/end', methods=['POST'])
def end_session(farmer_id, session_id):
    ok = store.end_session(farmer_id, session_id)
    return jsonify({'ended': ok})


@app.route('/api/farmers/<farmer_id>/sessions/<session_id>/irrigate', methods=['POST'])
def log_irrigation(farmer_id, session_id):
    data = request.get_json(force=True) or {}
    entry = store.log_irrigation(
        farmer_id, session_id,
        data.get('amount_mm', 0), data.get('amount_liters', 0),
        data.get('note', ''))
    return jsonify(entry) if entry else (jsonify({'error': 'not found'}), 404)


@app.route('/api/farmers/<farmer_id>/report', methods=['GET'])
def farmer_report(farmer_id):
    """Full dashboard report: plots, active sessions with progress & schedule."""
    f = store.get_farmer(farmer_id)
    if not f:
        return jsonify({'error': 'not found'}), 404

    soil_code = f.get('soil_type_code', 2)
    reports = []
    for s in f.get('sessions', []):
        if s.get('status') != 'active':
            continue
        schedule = ml.growth_schedule(
            s['crop'], s['start_date'], s.get('acres', 1), soil_code)
        progress = ml.session_progress(s, schedule)
        reports.append({
            'session': s,
            'schedule': schedule,
            'progress': progress,
        })

    total_acres = f.get('total_land_acres', 0) or 0
    allocated = sum(p.get('acres', 0) for p in f.get('plots', []))
    return jsonify({
        'farmer': f,
        'active_reports': reports,
        'land': {
            'total_acres': total_acres,
            'allocated_acres': round(allocated, 2),
            'remaining_acres': round(total_acres - allocated, 2),
        },
    })


# ---------------- prediction ----------------
@app.route('/api/predict', methods=['POST'])
def predict():
    features = request.get_json(force=True) or {}
    return jsonify(ml.predict_crops(features))


# ---------------- irrigation ----------------
@app.route('/api/irrigation', methods=['POST'])
def irrigation():
    params = request.get_json(force=True) or {}
    return jsonify(ml.irrigation_recommendation(params))


# ---------------- crop info ----------------
@app.route('/api/crop-info/<crop>')
def crop_info(crop):
    return jsonify(ml.crop_info(crop))


# ---------------- weather ----------------
@app.route('/api/weather', methods=['GET'])
def weather_current():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if lat is None or lon is None:
        return jsonify({'error': 'lat and lon are required'}), 400
    return jsonify(weather_mod.fetch_weather(float(lat), float(lon)))


@app.route('/api/weather/config', methods=['GET', 'POST'])
def weather_config():
    if request.method == 'GET':
        return jsonify(weather_mod.get_config())
    data = request.get_json(force=True) or {}
    weather_mod.set_config(data.get('provider', 'openmeteo'), data.get('api_key', ''))
    return jsonify({'saved': True})


# ---------------- data reset ----------------
@app.route('/api/reset', methods=['POST'])
def reset_all_data():
    """Delete all farmer data and reset the app."""
    try:
        store.reset_all()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
