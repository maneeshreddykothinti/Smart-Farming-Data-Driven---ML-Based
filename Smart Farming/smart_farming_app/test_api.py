import urllib.request, json

B = 'http://127.0.0.1:5000'

def call(path, data=None, method=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(B + path, data=body, method=method or ('POST' if body else 'GET'),
                                 headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req))

d = call('/api/meta')
print('crops:', len(d['crops']), '| defaults:', len(d['feature_defaults']))
print('defaults sample:', {k: d['feature_defaults'][k] for k in ['N','P','K','ph','soil_type']})

f = call('/api/farmers', {'name': 'Test Farmer', 'state': 'Karnataka', 'total_land_acres': 2,
                          'N': 80, 'P': 40, 'K': 40, 'ph': 6.5, 'soil_type_code': 2})
print('farmer:', f['id'], f['name'])

p = call(f"/api/farmers/{f['id']}/plots", {'crop': 'rice', 'acres': 1.5})
print('plot:', p['crop'], p['acres'])

p2 = call(f"/api/farmers/{f['id']}/plots", {'crop': 'maize', 'acres': 0.5})

s = call(f"/api/farmers/{f['id']}/sessions", {'plot_id': p['id']})
print('session:', s['id'], s['crop'], s['start_date'])

r = call(f"/api/farmers/{f['id']}/report")
rep = r['active_reports'][0]
print('progress:', rep['progress'])
print('stage:', rep['schedule']['stages'][0])
print('land:', r['land'])

pred = call('/api/predict', {'N': 90, 'P': 42, 'K': 43, 'ph': 6.5, 'rainfall': 200,
                             'temperature': 28, 'humidity': 75, 'soil_type': 2})
print('predictions:', pred)

irr = call('/api/irrigation', {'crop_type': 'rice', 'soil_moisture': 30, 'acres': 1.5,
                               'temperature': 30, 'humidity': 60})
print('irrigation:', {k: irr[k] for k in ('irrigation_required', 'water_amount_mm', 'total_water_liters')})

info = call('/api/crop-info/rice')
print('rice info:', info['duration_days'], 'days,', info['total_water_mm'], 'mm')
print('calendar:', info['calendar'])

# index page
html = urllib.request.urlopen(B + '/').read().decode()
print('index ok:', 'Smart Farming' in html, len(html), 'bytes')
