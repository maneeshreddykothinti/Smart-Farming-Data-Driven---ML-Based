"""
ML service for Smart Farming app.
Loads the trained crop-recommendation model and the FAO-56 irrigation model,
plus crop calendar / season data.
"""

import os
import sys
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

CR_MODEL_DIR = os.path.join(PROJECT_ROOT, 'CR_ML', 'Models')
IR_MODEL_DIR = os.path.join(PROJECT_ROOT, 'IR_ML', 'Models')
CROP_SEASON_CSV = os.path.join(PROJECT_ROOT, 'crop_season', 'crop_season.csv')
CALENDAR_CSV = os.path.join(PROJECT_ROOT, 'upag_crop_calendar', 'upag_crop_calendar_processed.csv')
PROCESSED_CSV = os.path.join(PROJECT_ROOT, 'crop_recommendation_processed', 'crop_recommendation_processed.csv')

# Feature order expected by the crop recommendation model
FEATURE_COLUMNS = [
    'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
    'soil_moisture', 'soil_type', 'sunlight_exposure', 'wind_speed',
    'co2_concentration', 'organic_matter', 'irrigation_frequency',
    'crop_density', 'pest_pressure', 'fertilizer_usage', 'growth_stage',
    'urban_area_proximity', 'water_source_type', 'frost_risk',
    'water_usage_efficiency'
]

# Mappings used by the frontend forms
SOIL_TYPE_OPTIONS = [
    {'code': 1, 'name': 'Sandy soil', 'irrigation_name': 'sand'},
    {'code': 2, 'name': 'Loamy soil', 'irrigation_name': 'loam'},
    {'code': 3, 'name': 'Clayey soil', 'irrigation_name': 'clay'},
]

IRRIGATION_FREQUENCY_OPTIONS = [
    {'code': 1, 'name': 'Rainfed only'},
    {'code': 2, 'name': 'Monthly'},
    {'code': 3, 'name': 'Every 2 weeks'},
    {'code': 4, 'name': 'Weekly'},
    {'code': 5, 'name': 'Every 2-3 days'},
    {'code': 6, 'name': 'Daily'},
]

WATER_SOURCE_OPTIONS = [
    {'code': 1, 'name': 'Borewell'},
    {'code': 2, 'name': 'Canal'},
    {'code': 3, 'name': 'Open well / Pond'},
]

GROWTH_STAGE_OPTIONS = [
    {'code': 1, 'name': 'Initial (germination / early growth)'},
    {'code': 2, 'name': 'Mid (vegetative / flowering)'},
    {'code': 3, 'name': 'Late (maturity / ripening)'},
]

SEASON_OPTIONS = ['Kharif', 'Rabi', 'Zaid']

# Agronomic reference data for the 22 crops the model can predict.
# duration_days: total crop duration; stages: days per growth stage
# (initial / mid / late as fractions); water_mm: seasonal water requirement.
CROP_INFO = {
    'rice':        {'duration_days': 150, 'water_mm': 1200, 'stages': [30, 70, 50], 'season': 'Kharif'},
    'wheat':       {'duration_days': 110, 'water_mm': 450,  'stages': [20, 55, 35], 'season': 'Rabi'},
    'maize':       {'duration_days': 110, 'water_mm': 600,  'stages': [20, 60, 30], 'season': 'Kharif'},
    'cotton':      {'duration_days': 180, 'water_mm': 700,  'stages': [30, 110, 40], 'season': 'Kharif'},
    'chickpea':    {'duration_days': 100, 'water_mm': 300,  'stages': [20, 55, 25], 'season': 'Rabi'},
    'lentil':      {'duration_days': 110, 'water_mm': 350,  'stages': [20, 60, 30], 'season': 'Rabi'},
    'mungbean':    {'duration_days': 65,  'water_mm': 350,  'stages': [15, 35, 15], 'season': 'Kharif'},
    'blackgram':   {'duration_days': 90,  'water_mm': 400,  'stages': [20, 50, 20], 'season': 'Kharif'},
    'pigeonpeas':  {'duration_days': 150, 'water_mm': 500,  'stages': [30, 80, 40], 'season': 'Kharif'},
    'mothbeans':   {'duration_days': 75,  'water_mm': 250,  'stages': [15, 45, 15], 'season': 'Kharif'},
    'kidneybeans': {'duration_days': 90,  'water_mm': 400,  'stages': [20, 50, 20], 'season': 'Kharif'},
    'jute':        {'duration_days': 120, 'water_mm': 500,  'stages': [20, 70, 30], 'season': 'Kharif'},
    'sugarcane':   {'duration_days': 365, 'water_mm': 1800, 'stages': [60, 240, 65], 'season': 'Kharif'},
    'banana':      {'duration_days': 365, 'water_mm': 1500, 'stages': [60, 240, 65], 'season': 'Kharif'},
    'mango':       {'duration_days': 365, 'water_mm': 1200, 'stages': [60, 240, 65], 'season': 'Perennial'},
    'orange':      {'duration_days': 365, 'water_mm': 900,  'stages': [60, 240, 65], 'season': 'Perennial'},
    'apple':       {'duration_days': 240, 'water_mm': 800,  'stages': [40, 160, 40], 'season': 'Perennial'},
    'pomegranate': {'duration_days': 240, 'water_mm': 600,  'stages': [40, 160, 40], 'season': 'Perennial'},
    'grapes':      {'duration_days': 180, 'water_mm': 500,  'stages': [30, 110, 40], 'season': 'Perennial'},
    'papaya':      {'duration_days': 300, 'water_mm': 900,  'stages': [50, 200, 50], 'season': 'Perennial'},
    'coconut':     {'duration_days': 365, 'water_mm': 1200, 'stages': [60, 240, 65], 'season': 'Perennial'},
    'coffee':      {'duration_days': 365, 'water_mm': 1000, 'stages': [60, 240, 65], 'season': 'Perennial'},
    'muskmelon':   {'duration_days': 100, 'water_mm': 450,  'stages': [15, 70, 15], 'season': 'Kharif'},
    'watermelon':  {'duration_days': 90,  'water_mm': 400,  'stages': [15, 60, 15], 'season': 'Kharif'},
}

# Map predicted crop names -> irrigation model crop keys
IR_CROP_MAP = {
    'kidneybeans': 'chickpea',
    'mothbeans': 'mungbean',
    'blackgram': 'lentil',
}


class MLService:
    def __init__(self):
        self._model = None
        self._encoder = None
        self._defaults = None
        self._dataset_df = None
        self._crop_season = None
        self._irrigation_model = None
        self._load()

    # ---------------- loading ----------------
    def _load(self):
        sys.path.insert(0, IR_MODEL_DIR)
        try:
            from IR_model_irrigation import IrrigationModel
            self._irrigation_model = IrrigationModel()
        except Exception as e:
            print(f'[ML] Irrigation model failed to load: {e}')

        try:
            self._model = joblib.load(os.path.join(CR_MODEL_DIR, 'random_forest_model.pkl'))
            self._encoder = joblib.load(os.path.join(CR_MODEL_DIR, 'label_encoder_rf.pkl'))
            self._defaults = joblib.load(os.path.join(CR_MODEL_DIR, 'default_values_rf.pkl'))
        except Exception as e:
            print(f'[ML] Crop model failed to load: {e}')

        try:
            self._dataset_df = pd.read_csv(PROCESSED_CSV)
        except Exception:
            self._dataset_df = None

        try:
            self._crop_season = pd.read_csv(CROP_SEASON_CSV)
        except Exception:
            self._crop_season = None

    # ---------------- helpers ----------------
    def feature_defaults(self):
        """Median defaults for every model feature, for form prefill."""
        if self._defaults:
            return {k: (round(float(v), 3) if isinstance(v, (int, float)) else v)
                    for k, v in self._defaults.items()}
        return {}

    def crops(self):
        """All crops the model can predict."""
        if self._encoder is not None:
            return sorted([str(c) for c in self._encoder.classes_])
        return sorted(CROP_INFO.keys())

    # ---------------- crop recommendation ----------------
    def predict_crops(self, features, top_n=3):
        """Return top-N crop suggestions with confidence scores."""
        if self._model is None or self._encoder is None:
            return {'error': 'Model not loaded'}

        vals = []
        for col in FEATURE_COLUMNS:
            v = features.get(col)
            if v is None or v == '':
                v = self._defaults.get(col, 0)
            vals.append(float(v))

        import numpy as np
        X = pd.DataFrame([vals], columns=FEATURE_COLUMNS)
        proba = self._model.predict_proba(X)[0]
        classes = self._encoder.classes_

        ranked = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)[:top_n]
        return {
            'suggestions': [
                {'crop': str(c), 'confidence': round(float(p) * 100, 1)}
                for c, p in ranked
            ]
        }

    # ---------------- irrigation ----------------
    def irrigation_recommendation(self, params):
        """Run the FAO-56 irrigation model."""
        if self._irrigation_model is None:
            return {'error': 'Irrigation model not loaded'}

        crop = (params.get('crop_type') or 'rice').lower().strip()
        crop = IR_CROP_MAP.get(crop, crop)
        soil = params.get('soil_type', 'loam')
        if isinstance(soil, int):
            soil = next((o['irrigation_name'] for o in SOIL_TYPE_OPTIONS if o['code'] == soil), 'loam')
        stage = params.get('growth_stage', 'mid')
        if isinstance(stage, int):
            stage = {1: 'initial', 2: 'mid', 3: 'late'}.get(stage, 'mid')

        clean = {
            'soil_moisture': float(params.get('soil_moisture', 50)),
            'recent_rainfall_mm': float(params.get('recent_rainfall_mm', 0)),
            'rainfall_days_ago': float(params.get('rainfall_days_ago', 7)),
            'temperature': float(params.get('temperature', 25)),
            'humidity': float(params.get('humidity', 60)),
            'wind_speed': float(params.get('wind_speed', 2)),
            'soil_type': soil,
            'crop_type': crop,
            'growth_stage': stage,
            'acres': float(params.get('acres', 1)),
        }
        return self._irrigation_model.predict(clean)

    # ---------------- crop info / calendar ----------------
    def crop_info(self, crop):
        """Growth report data for a crop: duration, stages, water, calendar."""
        crop = (crop or '').lower().strip()
        info = CROP_INFO.get(crop, {'duration_days': 120, 'water_mm': 500,
                                    'stages': [20, 70, 30], 'season': 'Kharif'})

        stage_names = ['Initial / Germination', 'Mid / Vegetative', 'Late / Maturity']
        stages = []
        acc = 0
        for name, days in zip(stage_names, info['stages']):
            stages.append({
                'name': name,
                'days': days,
                'start_day': acc,
                'end_day': acc + days,
            })
            acc += days

        calendar = self._calendar_for(crop)
        return {
            'crop': crop,
            'duration_days': info['duration_days'],
            'total_water_mm': info['water_mm'],
            'season': info['season'],
            'stages': stages,
            'calendar': calendar,
        }

    def _calendar_for(self, crop):
        """Sowing/harvest windows from crop_season.csv (prefers 'All India')."""
        result = {'sowing': None, 'harvest': None, 'season': None, 'source': None}
        if self._crop_season is None:
            return result
        df = self._crop_season
        mask = df['label'].str.lower() == crop
        sub = df[mask]
        if sub.empty:
            sub = df[df['crop'].str.lower() == crop]
        if sub.empty:
            return result
        all_india = sub[sub['state'].str.lower() == 'all india']
        row = (all_india.iloc[0] if not all_india.empty else sub.iloc[0])
        st_m, en_m = row.get('harvesting_st_month'), row.get('harvesting_end_month')
        st_s = '' if pd.isna(st_m) else str(st_m)
        en_s = '' if pd.isna(en_m) else str(en_m)
        if st_s and en_s:
            harvest_months = f"{st_s} - {en_s}"
        else:
            harvest_months = st_s or en_s or None
        return {
            'sowing': None if pd.isna(row.get('sowing_time_period')) else str(row.get('sowing_time_period')),
            'harvest': None if pd.isna(row.get('harvesting_time')) else str(row.get('harvesting_time')),
            'harvest_months': harvest_months,
            'season': None if pd.isna(row.get('season')) else str(row.get('season')),
            'state': str(row.get('state')),
        }

    # ---------------- growth schedule ----------------
    def growth_schedule(self, crop, start_date, acres=1, soil_code=2,
                        temperature=28, humidity=60, wind_speed=2):
        """
        Build a per-stage growth + irrigation schedule for a crop.
        Returns stages with date ranges, water need and irrigation interval.
        """
        from datetime import date, timedelta
        crop_key = IR_CROP_MAP.get((crop or '').lower(), (crop or '').lower())
        info = self.crop_info(crop)

        # reference evapotranspiration for interval estimates
        if self._irrigation_model:
            eto = self._irrigation_model.calculate_reference_evapotranspiration(
                temperature, humidity, wind_speed)
        else:
            eto = 4.5

        soil_name = next((o['irrigation_name'] for o in SOIL_TYPE_OPTIONS
                          if o['code'] == soil_code), 'loam')

        # soil water buffer available before irrigation is needed (mm)
        try:
            from crop_coefficients import get_soil_water_capacity, get_crop_info
            cap = get_soil_water_capacity(soil_name)
            ci = get_crop_info(crop_key) or get_crop_info('rice')
            buffer_mm = cap * ci['root_depth'] * ci['depletion_fraction']
        except Exception:
            buffer_mm = 40.0

        stage_labels = ['initial', 'mid', 'late']
        stages = []
        for s, label in zip(info['stages'], stage_labels):
            kc = 1.0
            if self._irrigation_model:
                try:
                    kc = self._irrigation_model.calculate_crop_evapotranspiration(
                        eto, crop_key, label)
                except Exception:
                    pass
            etc = kc  # already includes Kc*ETo via method above
            interval = max(1, int(round(buffer_mm / max(etc, 0.5))))
            stages.append({
                'name': s['name'],
                'days': s['days'],
                'start_day': s['start_day'],
                'end_day': s['end_day'],
                'start_date': (date.fromisoformat(start_date) +
                               timedelta(days=s['start_day'])).isoformat(),
                'end_date': (date.fromisoformat(start_date) +
                             timedelta(days=s['end_day'] - 1)).isoformat(),
                'daily_water_mm': round(etc, 2),
                'irrigation_interval_days': interval,
                'stage_water_mm': round(etc * s['days'], 1),
            })

        return {
            'crop': crop_key,
            'start_date': start_date,
            'total_days': info['duration_days'],
            'expected_harvest': (date.fromisoformat(start_date) +
                                 timedelta(days=info['duration_days'])).isoformat(),
            'total_water_mm': info['total_water_mm'],
            'total_water_liters': round(info['total_water_mm'] * acres * 4046.86),
            'stages': stages,
        }

    def session_progress(self, session, schedule):
        """Progress info for an active farming session."""
        from datetime import date
        try:
            start = date.fromisoformat(session['start_date'])
        except Exception:
            start = date.today()
        elapsed = max(0, (date.today() - start).days)
        total = schedule['total_days']
        pct = min(100, round(elapsed / total * 100, 1)) if total else 0

        current = None
        for s in schedule['stages']:
            if elapsed <= s['end_day'] or s == schedule['stages'][-1]:
                current = s
                break

        days_left = max(0, total - elapsed)
        return {
            'elapsed_days': elapsed,
            'total_days': total,
            'progress_pct': pct,
            'current_stage': current['name'] if current else None,
            'days_to_next_stage': max(0, (current['end_day'] - elapsed)) if current else 0,
            'days_remaining': days_left,
            'expected_harvest': schedule['expected_harvest'],
        }

    # ---------------- season suggestion ----------------
    def season_for_crop(self, crop):
        cal = self._calendar_for((crop or '').lower())
        return cal.get('season') or CROP_INFO.get((crop or '').lower(), {}).get('season', 'Kharif')


ml = MLService()
