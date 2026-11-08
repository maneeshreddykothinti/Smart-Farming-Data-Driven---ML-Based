"""
Simple JSON-file storage for farmers, crop plots and farming sessions.
"""

import json
import os
import uuid
import threading
from datetime import datetime, date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'farmers.json')

_lock = threading.Lock()


def _today():
    return date.today().isoformat()


class Store:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(DB_PATH):
            self._write({'farmers': {}})

    # ---------- low level ----------
    def _read(self):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write(self, data):
        tmp = DB_PATH + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, DB_PATH)

    def _update(self, fn):
        with _lock:
            data = self._read()
            result = fn(data)
            self._write(data)
            return result

    # ---------- farmers ----------
    def create_farmer(self, profile):
        farmer_id = uuid.uuid4().hex[:12]
        farmer = {
            'id': farmer_id,
            'created_at': datetime.now().isoformat(timespec='seconds'),
            'plots': [],
            'sessions': [],
        }
        farmer.update(profile)

        def fn(data):
            data['farmers'][farmer_id] = farmer
            return farmer
        return self._update(fn)

    def get_farmer(self, farmer_id):
        data = self._read()
        f = data['farmers'].get(farmer_id)
        return self._public(f) if f else None

    def list_farmers(self):
        data = self._read()
        return [self._public(f) for f in data['farmers'].values()]

    def update_farmer(self, farmer_id, profile):
        def fn(data):
            f = data['farmers'].get(farmer_id)
            if not f:
                return None
            # never overwrite id/plots/sessions via profile
            for k in ('id', 'plots', 'sessions', 'created_at'):
                profile.pop(k, None)
            f.update(profile)
            f['updated_at'] = datetime.now().isoformat(timespec='seconds')
            return self._public(f)
        return self._update(fn)

    def delete_farmer(self, farmer_id):
        def fn(data):
            return data['farmers'].pop(farmer_id, None) is not None
        return self._update(fn)

    def _public(self, f):
        if not f:
            return None
        return json.loads(json.dumps(f))

    # ---------- plots ----------
    def add_plot(self, farmer_id, crop, acres, notes=''):
        plot_id = uuid.uuid4().hex[:10]

        def fn(data):
            f = data['farmers'].get(farmer_id)
            if not f:
                return None
            plot = {
                'id': plot_id,
                'crop': crop.lower().strip(),
                'acres': float(acres),
                'notes': notes,
                'added_at': _today(),
            }
            f['plots'].append(plot)
            return plot
        return self._update(fn)

    def remove_plot(self, farmer_id, plot_id):
        def fn(data):
            f = data['farmers'].get(farmer_id)
            if not f:
                return False
            before = len(f['plots'])
            f['plots'] = [p for p in f['plots'] if p['id'] != plot_id]
            return len(f['plots']) < before
        return self._update(fn)

    # ---------- farming sessions ----------
    def start_session(self, farmer_id, plot_id, start_date=None):
        session_id = uuid.uuid4().hex[:10]
        start = start_date or _today()

        def fn(data):
            f = data['farmers'].get(farmer_id)
            if not f:
                return None
            plot = next((p for p in f['plots'] if p['id'] == plot_id), None)
            if not plot:
                return None
            # prevent duplicate active sessions on same plot
            for s in f['sessions']:
                if s['plot_id'] == plot_id and s['status'] == 'active':
                    return {'error': 'active_session_exists', 'session': s}
            session = {
                'id': session_id,
                'plot_id': plot_id,
                'crop': plot['crop'],
                'acres': plot['acres'],
                'start_date': start,
                'status': 'active',
                'irrigation_log': [],
                'created_at': datetime.now().isoformat(timespec='seconds'),
            }
            f['sessions'].append(session)
            return session
        return self._update(fn)

    def end_session(self, farmer_id, session_id):
        def fn(data):
            f = data['farmers'].get(farmer_id)
            if not f:
                return False
            for s in f['sessions']:
                if s['id'] == session_id:
                    s['status'] = 'completed'
                    s['end_date'] = _today()
                    return True
            return False
        return self._update(fn)

    def log_irrigation(self, farmer_id, session_id, amount_mm, amount_liters, note=''):
        entry = {
            'date': _today(),
            'amount_mm': amount_mm,
            'amount_liters': amount_liters,
            'note': note,
        }

        def fn(data):
            f = data['farmers'].get(farmer_id)
            if not f:
                return None
            for s in f['sessions']:
                if s['id'] == session_id:
                    s['irrigation_log'].append(entry)
                    return entry
            return None
        return self._update(fn)

    def reset_all(self):
        """Delete all farmer data (wipe farmers.json)."""
        def fn(data):
            data['farmers'] = {}
            return True
        return self._update(fn)


store = Store()
