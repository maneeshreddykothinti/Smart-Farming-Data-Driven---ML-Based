"""
Weather integration using Open-Meteo (free, no key) with optional OpenWeatherMap override.
"""

import os
import json
import urllib.request
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'data', 'weather_config.json')


def get_config():
    """Get weather config: provider ('openmeteo' or 'openweathermap') and optional API key."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {'provider': 'openmeteo', 'api_key': ''}


def set_config(provider='openmeteo', api_key=''):
    """Save weather config."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump({'provider': provider, 'api_key': api_key}, f)


def fetch_weather(lat, lon):
    """Fetch current weather + forecast. Returns dict or {'error': ...}."""
    cfg = get_config()
    provider = cfg.get('provider', 'openmeteo')
    api_key = cfg.get('api_key', '')

    if provider == 'openweathermap' and api_key:
        return _fetch_openweathermap(lat, lon, api_key)
    else:
        return _fetch_openmeteo(lat, lon)


def _fetch_openmeteo(lat, lon):
    """Fetch from Open-Meteo (free, no key)."""
    try:
        url = (f'https://api.open-meteo.com/v1/forecast?'
               f'latitude={lat}&longitude={lon}'
               f'&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation'
               f'&daily=precipitation_sum,precipitation_probability_max,precipitation_hours'
               f'&forecast_days=5')
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        return {'error': 'fetch_failed', 'message': str(e)}

    cur = data.get('current', {})
    daily = data.get('daily', {})

    # Get today's date in the same format as the API returns (YYYY-MM-DD)
    from datetime import datetime, timezone, timedelta
    today_local = datetime.now().strftime('%Y-%m-%d')  # use local time instead of UTC
    tomorrow_local = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # Find next day with precipitation > 0 (excluding today and past dates)
    next_rain = None
    for date_str, precip, prob, hours in zip(daily.get('time', []), daily.get('precipitation_sum', []), daily.get('precipitation_probability_max', []), daily.get('precipitation_hours', [])):
        if date_str < tomorrow_local:
            continue  # skip today and past dates
        if precip > 0:
            next_rain = {'date': date_str, 'mm': precip, 'probability': prob, 'hours': hours}
            break

    # Also filter daily forecast to exclude today and past dates for display
    filtered_daily = [
        (d, p, pr) for d, p, pr in zip(daily.get('time', []), daily.get('precipitation_sum', []), daily.get('precipitation_probability_max', []))
        if d >= tomorrow_local
    ]

    return {
        'provider': 'openmeteo',
        'temperature': cur.get('temperature_2m'),
        'humidity': cur.get('relative_humidity_2m'),
        'wind_speed': cur.get('wind_speed_10m'),
        'rain_1h_mm': cur.get('precipitation', 0),
        'description': f"Rain: {cur.get('precipitation', 0)} mm/h" if cur.get('precipitation', 0) > 0 else "Clear",
        'location': f"{lat:.2f}, {lon:.2f}",
        'forecast': {
            'next_rain': next_rain,
            'daily': filtered_daily[:5],
        },
    }


def _fetch_openweathermap(lat, lon, api_key):
    """Fetch from OpenWeatherMap (requires API key)."""
    url = ('https://api.openweathermap.org/data/2.5/weather?'
           + urllib.parse.urlencode({
               'lat': lat, 'lon': lon, 'appid': api_key, 'units': 'metric'
           }))
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        return {'error': 'fetch_failed', 'message': str(e)}

    main = data.get('main', {})
    wind = data.get('wind', {})
    rain = data.get('rain', {})
    weather = (data.get('weather') or [{}])[0]
    return {
        'provider': 'openweathermap',
        'temperature': main.get('temp'),
        'humidity': main.get('humidity'),
        'wind_speed': wind.get('speed'),
        'rain_1h_mm': rain.get('1h', 0),
        'description': weather.get('description', ''),
        'location': data.get('name', ''),
        'forecast': None,  # full forecast would need another API call
    }
