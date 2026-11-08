/* Smart Farming - frontend logic */

const state = {
  meta: null,
  farmer: null,
  view: 'dashboard',
  lastWeather: null,
};

const $ = (sel) => document.querySelector(sel);
const view = () => $('#view');

/* ---------------- helpers ---------------- */
async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

function toast(msg, type = '') {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  $('#toasts').appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function num(v, d = 1) {
  const n = parseFloat(v);
  return isNaN(n) ? '—' : n.toFixed(d);
}

function field(name, label, { type = 'number', value = '', step, min, max, options, hint, required, placeholder } = {}) {
  let input;
  if (options) {
    input = `<select name="${name}" ${required ? 'required' : ''}>` +
      options.map(o => `<option value="${o.value}" ${String(o.value) === String(value) ? 'selected' : ''}>${esc(o.label)}</option>`).join('') +
      `</select>`;
  } else {
    const stepAttr = step !== undefined ? `step="${step}"` : 'step="any"';
    const phAttr = placeholder ? `placeholder="${esc(placeholder)}"` : '';
    input = `<input name="${name}" type="${type}" value="${esc(value)}" ${type === 'number' ? stepAttr : ''} ${min !== undefined ? `min="${min}"` : ''} ${max !== undefined ? `max="${max}"` : ''} ${required ? 'required' : ''} ${phAttr}>`;
  }
  return `<div class="field"><label>${esc(label)}</label>${input}${hint ? `<span class="hint">${esc(hint)}</span>` : ''}</div>`;
}

function formValues(container) {
  const out = {};
  container.querySelectorAll('input,select,textarea').forEach(el => {
    if (!el.name) return;
    const v = el.value;
    out[el.name] = v === '' ? null : (isNaN(Number(v)) ? v : Number(v));
  });
  return out;
}

function seasonTag(season) {
  const s = (season || '').toLowerCase();
  const cls = s === 'rabi' ? 'rabi' : s === 'zaid' ? 'zaid' : '';
  return `<span class="tag ${cls}">${esc(season || 'Kharif')}</span>`;
}

/* ---------------- farmer / onboarding ---------------- */
function profileFields(f = {}, { forOnboard = false } = {}) {
  const soilOpts = state.meta.soil_types.map(o => ({ value: o.code, label: o.name }));
  const freqOpts = [{ value: '', label: '— select —' }, ...state.meta.irrigation_frequencies.map(o => ({ value: o.code, label: o.name }))];
  const waterOpts = [{ value: '', label: '— select —' }, ...state.meta.water_sources.map(o => ({ value: o.code, label: o.name }))];

  const d = state.meta.feature_defaults;

  return `
    <div class="section-title">Personal details</div>
    <div class="form-grid">
      ${field('name', 'Full name', { type: 'text', value: f.name || '', required: true })}
      ${field('state', 'State', { type: 'text', value: f.state || '', required: true })}
      ${field('village', 'Village / Taluk', { type: 'text', value: f.village || '' })}
      ${field('total_land_acres', 'Total land (acres)', { value: f.total_land_acres ?? '', step: 'any', min: '0', required: true, placeholder: 'e.g. 2.5' })}
      ${field('lat', 'Latitude (for weather)', { value: f.lat ?? '', step: 'any', placeholder: 'e.g. 13.1' })}
      ${field('lon', 'Longitude (for weather)', { value: f.lon ?? '', step: 'any', placeholder: 'e.g. 77.6' })}
    </div>
    <div class="section-title">Soil & nutrition (permanent values)</div>
    <div class="form-grid">
      ${field('N', 'Nitrogen N (kg/ha)', { value: f.N ?? '', step: 'any', min: '0', placeholder: `avg ${num(d.N,0)}` })}
      ${field('P', 'Phosphorus P (kg/ha)', { value: f.P ?? '', step: 'any', min: '0', placeholder: `avg ${num(d.P,0)}` })}
      ${field('K', 'Potassium K (kg/ha)', { value: f.K ?? '', step: 'any', min: '0', placeholder: `avg ${num(d.K,0)}` })}
      ${field('ph', 'Soil pH', { value: f.ph ?? '', step: 'any', min: '0', max: '14', placeholder: `avg ${num(d.ph,1)}` })}
      ${field('organic_matter', 'Organic matter (%)', { value: f.organic_matter ?? '', step: 'any', min: '0', placeholder: `avg ${num(d.organic_matter,1)}` })}
      ${field('soil_moisture', 'Current soil moisture (%)', { value: f.soil_moisture ?? '', step: 'any', min: '0', max: '100', placeholder: `avg ${num(d.soil_moisture,0)}` })}
      ${field('soil_type_code', 'Soil type', { value: f.soil_type_code ?? 2, options: soilOpts })}
      ${field('water_source_type', 'Water source', { value: f.water_source_type ?? '', options: waterOpts })}
      ${field('irrigation_frequency', 'Usual irrigation frequency', { value: f.irrigation_frequency ?? '', options: freqOpts })}
    </div>
    ${forOnboard ? '' : `
    <div class="section-title">Environmental reference values</div>
    <div class="form-grid">
      ${field('temperature', 'Avg temperature (°C)', { value: f.temperature ?? '', step: 'any', placeholder: `avg ${num(d.temperature,1)}` })}
      ${field('humidity', 'Avg humidity (%)', { value: f.humidity ?? '', step: 'any', min: '0', max: '100', placeholder: `avg ${num(d.humidity,0)}` })}
      ${field('rainfall', 'Annual rainfall (mm)', { value: f.rainfall ?? '', step: 'any', min: '0', placeholder: `avg ${num(d.rainfall,0)}` })}
      ${field('wind_speed', 'Avg wind speed (m/s)', { value: f.wind_speed ?? '', step: 'any', min: '0', placeholder: `avg ${num(d.wind_speed,1)}` })}
      ${field('lat', 'Latitude (for weather)', { value: f.lat ?? '', step: 'any', placeholder: 'e.g. 13.1' })}
      ${field('lon', 'Longitude (for weather)', { value: f.lon ?? '', step: 'any', placeholder: 'e.g. 77.6' })}
    </div>`}
  `;
}

async function openOnboarding() {
  $('#onboard-form').innerHTML = profileFields({}, { forOnboard: true });
  $('#onboard-modal').classList.remove('hidden');
  const close = () => {
    $('#onboard-modal').classList.add('hidden');
    if (state.farmer) navigate('dashboard');
  };
  $('#onboard-close').onclick = close;
  $('#onboard-cancel').onclick = close;
  $('#onboard-modal').onclick = (e) => { if (e.target === $('#onboard-modal')) close(); };
  document.addEventListener('keydown', function esc(e) {
    if (e.key === 'Escape' && !$('#onboard-modal').classList.contains('hidden')) {
      close();
      document.removeEventListener('keydown', esc);
    }
  });
  $('#onboard-submit').onclick = async () => {
    const form = $('#onboard-form');
    const vals = formValues(form);
    if (!vals.name || !vals.state || !vals.total_land_acres) {
      toast('Name, state and land are required', 'error'); return;
    }
    vals.soil_type = state.meta.soil_types.find(o => o.code === Number(vals.soil_type_code))?.irrigation_name || 'loam';
    try {
      state.farmer = await api('/api/farmers', { method: 'POST', body: vals });
      localStorage.setItem('sf_farmer_id', state.farmer.id);
      $('#onboard-modal').classList.add('hidden');
      toast('Profile created!', 'success');
      renderSidebar();
      navigate('dashboard');
      // auto-fetch weather if lat/lon provided
      if (vals.lat && vals.lon) {
        try {
          const w = await api(`/api/weather?lat=${vals.lat}&lon=${vals.lon}`);
          if (!w.error) {
            state.lastWeather = w;
            localStorage.setItem('sf_weather', JSON.stringify(w));
            renderWeatherChip();
            toast('Weather auto-fetched from your location', 'success');
          }
        } catch {}
      }
    } catch (e) { toast(e.message, 'error'); }
  };
}

async function loadFarmer() {
  const id = localStorage.getItem('sf_farmer_id');
  if (!id) return openOnboarding();
  try {
    state.farmer = await api(`/api/farmers/${id}`);
  } catch {
    localStorage.removeItem('sf_farmer_id');
    return openOnboarding();
  }
  renderSidebar();
  navigate(state.view);
}

function renderSidebar() {
  const chip = $('#farmer-chip');
  if (state.farmer) {
    chip.innerHTML = `👨‍🌾 ${esc(state.farmer.name)}<br><span class="muted" style="opacity:.75">${num(state.farmer.total_land_acres, 2)} acres · ${esc(state.farmer.state || '')}</span>`;
  } else {
    chip.textContent = 'No farmer selected';
  }
}

/* ---------------- navigation ---------------- */
const TITLES = {
  dashboard: 'Dashboard', profile: 'My Profile', crops: 'My Crops',
  predict: 'Crop Prediction', report: 'Crop Report',
  irrigation: 'Irrigation Recommendation', weather: 'Weather',
};

function navigate(v) {
  state.view = v;
  document.querySelectorAll('.nav-item').forEach(b =>
    b.classList.toggle('active', b.dataset.view === v));
  $('#view-title').textContent = TITLES[v];
  ({ dashboard: renderDashboard, profile: renderProfile, crops: renderCrops,
     predict: renderPredict, report: renderReport, irrigation: renderIrrigation,
     weather: renderWeather })[v]();
}

/* ---------------- dashboard ---------------- */
async function renderDashboard() {
  if (!state.farmer) return view().innerHTML = emptyState('Select a farmer to begin');
  let report;
  try { report = await api(`/api/farmers/${state.farmer.id}/report`); }
  catch (e) { return view().innerHTML = `<div class="card">${esc(e.message)}</div>`; }

  const f = report.farmer;
  const land = report.land;
  const active = report.active_reports;
  const plots = f.plots || [];

  // resolve crop seasons for tags
  const seasonMap = {};
  await Promise.all([...new Set(active.map(r => r.session.crop))]
    .map(async c => { seasonMap[c] = await mlSeason(c); }));

  // land allocation bar
  const palette = ['#66bb6a', '#42a5f5', '#ffa726', '#ab47bc', '#26c6da', '#ef5350', '#8d6e63', '#78909c'];
  const segs = plots.map((p, i) =>
    `<div class="alloc-seg" style="width:${(p.acres / (land.total_acres || 1)) * 100}%;background:${palette[i % palette.length]}" title="${esc(p.crop)}: ${p.acres} ac"></div>`).join('');
  const legend = plots.map((p, i) =>
    `<span><span class="dot" style="background:${palette[i % palette.length]}"></span>${esc(p.crop)} — ${p.acres} ac</span>`).join('');

  let html = `
    <div class="grid grid-4 mb">
      <div class="card stat-card"><div class="num">${num(land.total_acres, 2)}</div><div class="lbl">Total Land (acres)</div></div>
      <div class="card stat-card"><div class="num">${num(land.allocated_acres, 2)}</div><div class="lbl">Allocated</div></div>
      <div class="card stat-card"><div class="num">${active.length}</div><div class="lbl">Active Crops</div></div>
      <div class="card stat-card"><div class="num">${plots.length}</div><div class="lbl">Crop Plots</div></div>
    </div>

    <div class="card mb">
      <h3>Land Allocation</h3>
      <div class="sub">${num(land.remaining_acres, 2)} acres unallocated</div>
      <div class="alloc-bar">${segs || '<div style="width:100%;background:#eee"></div>'}</div>
      <div class="alloc-legend">${legend || '<span class="muted">No crops added yet — visit Crop Prediction to add some.</span>'}</div>
    </div>`;

  if (active.length) {
    html += `<h3 class="section-title">Active Farming Sessions</h3><div class="grid grid-2">`;
    for (const r of active) {
      const s = r.session, p = r.progress, sch = r.schedule;
      const cur = sch.stages.find(st => st.name === p.current_stage) || sch.stages[0];
      html += `
      <div class="card">
        <div class="row" style="justify-content:space-between">
          <h3 style="text-transform:capitalize">${esc(s.crop)}</h3>
          ${seasonTag(seasonMap[s.crop])}
        </div>
        <div class="sub">${s.acres} acres · started ${esc(s.start_date)}</div>
        <div class="progress-wrap mb"><div style="width:${p.progress_pct}%"></div></div>
        <div class="progress-label"><span>Day ${p.elapsed_days} of ${p.total_days}</span><span>${p.progress_pct}%</span></div>
        <div class="mt">
          <div class="tl-water">🌱 Current stage: <b>${esc(p.current_stage || '—')}</b> (${p.days_to_next_stage}d left)</div>
          <div class="tl-water">💧 Irrigate every ~<b>${cur.irrigation_interval_days} days</b> this stage · ~${cur.daily_water_mm} mm/day</div>
          <div class="tl-water">🗓 Expected harvest: <b>${esc(p.expected_harvest)}</b></div>
        </div>
        <div class="row mt">
          <button class="btn btn-secondary btn-sm" onclick="quickIrrigate('${s.id}')">💧 Check Irrigation</button>
          <button class="btn btn-danger btn-sm" onclick="endSession('${s.id}')">End Season</button>
        </div>
      </div>`;
    }
    html += `</div>`;
  } else {
    html += `<div class="card empty-state"><div class="big">🌾</div>
      <p>No active farming sessions. Add crops in <b>My Crops</b>, then press <b>Start Farming</b> to track progress & irrigation.</p></div>`;
  }
  view().innerHTML = html;
}

// crop season lookup cached client-side
const seasonCache = {};
async function mlSeason(crop) {
  if (!seasonCache[crop]) {
    try { const i = await api(`/api/crop-info/${crop}`); seasonCache[crop] = i.season; }
    catch { seasonCache[crop] = 'Kharif'; }
  }
  return seasonCache[crop];
}

window.quickIrrigate = (sid) => navigateToIrrigationFor(sid);
window.endSession = async (sid) => {
  if (!confirm('Mark this farming session as completed?')) return;
  await api(`/api/farmers/${state.farmer.id}/sessions/${sid}/end`, { method: 'POST' });
  toast('Session ended', 'success');
  renderDashboard();
};

async function navigateToIrrigationFor(sid) {
  const f = state.farmer;
  const sess = (f.sessions || []).find(s => s.id === sid);
  if (!sess) return;
  navigate('irrigation');
  setTimeout(() => {
    const cropSel = document.querySelector('#irr-form [name=crop_type]');
    const stageSel = document.querySelector('#irr-form [name=growth_stage]');
    const acresInp = document.querySelector('#irr-form [name=acres]');
    if (cropSel) cropSel.value = sess.crop;
    if (acresInp) acresInp.value = sess.acres;
    if (stageSel) {
      // guess stage from progress
      const days = Math.max(0, (Date.now() - new Date(sess.start_date)) / 86400000);
      stageSel.value = days < 40 ? 'initial' : days < 110 ? 'mid' : 'late';
    }
    toast(`Form pre-filled for ${sess.crop}`, 'success');
  }, 50);
}

/* ---------------- profile ---------------- */
function renderProfile() {
  if (!state.farmer) return view().innerHTML = emptyState('No farmer selected');
  view().innerHTML = `
    <div class="card">
      <h3>Edit Profile</h3>
      <div class="sub">Update your permanent farm values anytime. Changes apply to predictions and irrigation.</div>
      <form id="profile-form">${profileFields(state.farmer)}</form>
      <div class="modal-actions" style="justify-content:flex-start">
        <button class="btn btn-primary" id="profile-save">Save Changes</button>
      </div>
    </div>`;
  $('#profile-save').onclick = async () => {
    const vals = formValues($('#profile-form'));
    vals.soil_type = state.meta.soil_types.find(o => o.code === Number(vals.soil_type_code))?.irrigation_name || 'loam';
    try {
      state.farmer = await api(`/api/farmers/${state.farmer.id}`, { method: 'PUT', body: vals });
      renderSidebar();
      toast('Profile updated', 'success');
      // auto-fetch weather if lat/lon provided
      if (vals.lat && vals.lon) {
        try {
          const w = await api(`/api/weather?lat=${vals.lat}&lon=${vals.lon}`);
          if (!w.error) {
            state.lastWeather = w;
            localStorage.setItem('sf_weather', JSON.stringify(w));
            renderWeatherChip();
            toast('Weather auto-fetched from your location', 'success');
          }
        } catch {}
      }
    } catch (e) { toast(e.message, 'error'); }
  };
}

/* ---------------- crops ---------------- */
async function renderCrops() {
  if (!state.farmer) return view().innerHTML = emptyState('No farmer selected');
  const f = state.farmer;
  const land = f.total_land_acres || 1;
  const allocated = (f.plots || []).reduce((a, p) => a + p.acres, 0);
  const over = allocated > land;

  let html = `
    <div class="card mb">
      <h3>Add a Crop Plot</h3>
      <div class="sub">Split your ${num(land, 2)} acres across 2–3 crops, e.g. 1.5 + 0.5 + 0.5.</div>
      <form id="plot-form" class="row" style="align-items:flex-end">
        <div class="field" style="flex:2"><label>Crop</label>
          <select name="crop" required>${state.meta.crops.map(c => `<option value="${c}">${c}</option>`).join('')}</select></div>
        <div class="field" style="flex:1"><label>Area (acres)</label>
          <input name="acres" type="number" step="0.01" min="0.01" required></div>
        <div class="field" style="flex:2"><label>Notes (optional)</label>
          <input name="notes" type="text" placeholder="e.g. near canal"></div>
        <button class="btn btn-primary" type="submit">+ Add Plot</button>
      </form>
      ${over ? `<div class="banner warn mt"><span class="b-icon">⚠️</span><div><b>Over-allocated:</b> plots total ${num(allocated, 2)} ac but you have ${num(land, 2)} ac. Adjust areas.</div></div>` : ''}
    </div>

    <div class="card">
      <h3>Your Crop Plots</h3>
      <div class="sub">${num(allocated, 2)} / ${num(land, 2)} acres allocated</div>`;

  if (!f.plots || !f.plots.length) {
    html += `<div class="empty-state"><div class="big">🧑‍🌾</div><p>No crops yet. Add your first plot above or get suggestions from <b>Crop Prediction</b>.</p></div>`;
  } else {
    html += `<table><tr><th>Crop</th><th>Area</th><th>Added</th><th>Active Session</th><th></th></tr>`;
    for (const p of f.plots) {
      const active = (f.sessions || []).some(s => s.plot_id === p.id && s.status === 'active');
      html += `<tr>
        <td style="text-transform:capitalize;font-weight:600">${esc(p.crop)}</td>
        <td>${p.acres} ac</td>
        <td>${esc(p.added_at)}</td>
        <td>${active ? '<span class="tag">Farming</span>' : '<span class="muted">—</span>'}</td>
        <td class="row" style="justify-content:flex-end">
          <button class="btn btn-secondary btn-sm" onclick="plotReport('${p.id}')">Report</button>
          ${active ? '' : `<button class="btn btn-accent btn-sm" onclick="startFarming('${p.id}')">▶ Start Farming</button>`}
          <button class="btn btn-danger btn-sm" onclick="delPlot('${p.id}')">✕</button>
        </td></tr>`;
    }
    html += `</table>`;
  }
  html += `</div>`;
  view().innerHTML = html;

  $('#plot-form').onsubmit = async (e) => {
    e.preventDefault();
    const vals = formValues(e.target);
    try {
      await api(`/api/farmers/${state.farmer.id}/plots`, { method: 'POST', body: vals });
      state.farmer = await api(`/api/farmers/${state.farmer.id}`);
      toast('Plot added', 'success');
      renderCrops();
    } catch (err) { toast(err.message, 'error'); }
  };
}

window.delPlot = async (pid) => {
  if (!confirm('Remove this plot?')) return;
  await api(`/api/farmers/${state.farmer.id}/plots/${pid}`, { method: 'DELETE' });
  state.farmer = await api(`/api/farmers/${state.farmer.id}`);
  renderCrops();
};

window.startFarming = async (pid) => {
  try {
    await api(`/api/farmers/${state.farmer.id}/sessions`, { method: 'POST', body: { plot_id: pid } });
    state.farmer = await api(`/api/farmers/${state.farmer.id}`);
    toast('Farming started! Track progress on the Dashboard.', 'success');
    renderCrops();
  } catch (e) { toast(e.message, 'error'); }
};

window.plotReport = (pid) => {
  const p = state.farmer.plots.find(x => x.id === pid);
  if (p) { sessionStorage.setItem('sf_report_crop', p.crop); navigate('report'); }
};

/* ---------------- prediction ---------------- */
function predictionForm() {
  const f = state.farmer || {};
  const d = state.meta.feature_defaults;
  const w = state.lastWeather || {};

  return `
  <div class="card mb">
    <h3>Farm conditions</h3>
    <div class="sub">Use averages from your profile as reference — or enter your current values.</div>
    <form id="pred-form">
      <div class="section-title">Soil & nutrition</div>
      <div class="form-grid">
        ${field('N', 'Nitrogen N', { placeholder: `avg ${num(d.N,0)}` })}
        ${field('P', 'Phosphorus P', { placeholder: `avg ${num(d.P,0)}` })}
        ${field('K', 'Potassium K', { placeholder: `avg ${num(d.K,0)}` })}
        ${field('ph', 'Soil pH', { placeholder: `avg ${num(d.ph,1)}`, min: '0', max: '14' })}
        ${field('organic_matter', 'Organic matter %', { placeholder: `avg ${num(d.organic_matter,1)}` })}
        ${field('soil_moisture', 'Soil moisture %', { placeholder: `avg ${num(d.soil_moisture,0)}`, min: '0', max: '100' })}
        ${field('soil_type', 'Soil type', { value: f.soil_type_code ?? d.soil_type, options: state.meta.soil_types.map(o => ({ value: o.code, label: o.name })) })}
        ${field('water_source_type', 'Water source', { value: f.water_source_type ?? d.water_source_type, options: [{ value: '', label: '— select —' }, ...state.meta.water_sources.map(o => ({ value: o.code, label: o.name }))] })}
        ${field('irrigation_frequency', 'Usual irrigation frequency', { value: f.irrigation_frequency ?? d.irrigation_frequency, options: [{ value: '', label: '— select —' }, ...state.meta.irrigation_frequencies.map(o => ({ value: o.code, label: o.name }))] })}
      </div>
      <div class="section-title">Current weather</div>
      <div class="form-grid">
        ${field('temperature', 'Temperature (°C)', { placeholder: w.temperature != null ? `${num(w.temperature,1)} (live)` : `avg ${num(d.temperature,1)}` })}
        ${field('humidity', 'Humidity (%)', { placeholder: w.humidity != null ? `${num(w.humidity,0)}% (live)` : `avg ${num(d.humidity,0)}`, min: '0', max: '100' })}
        ${field('rainfall', 'Rainfall (mm)', { placeholder: `avg ${num(d.rainfall,0)}`, min: '0' })}
        ${field('wind_speed', 'Wind speed (m/s)', { placeholder: w.wind_speed != null ? `${num(w.wind_speed,1)} (live)` : `avg ${num(d.wind_speed,1)}`, min: '0' })}
      </div>
      <details class="mt"><summary class="muted" style="cursor:pointer">Advanced parameters (defaults prefilled)</summary>
        <div class="form-grid mt">
          ${['sunlight_exposure','co2_concentration','crop_density','pest_pressure','fertilizer_usage','urban_area_proximity','frost_risk','water_usage_efficiency']
            .map(k => field(k, k.replace(/_/g,' '), { placeholder: `avg ${num(d[k],1)}` })).join('')}
        </div>
      </details>
      <div class="mt"><button class="btn btn-primary" type="submit">🔮 Get Crop Suggestions</button></div>
    </form>
  </div>
  <div id="pred-results"></div>`;
}

async function renderPredict() {
  if (!state.farmer) return view().innerHTML = emptyState('Create a profile first to get personalized suggestions');
  view().innerHTML = predictionForm();
  $('#pred-form').onsubmit = async (e) => {
    e.preventDefault();
    const vals = formValues(e.target);
    const body = {};
    // merge: feature defaults <- profile env values <- form values
    Object.assign(body, state.meta.feature_defaults);
    for (const k of ['temperature','humidity','rainfall','wind_speed']) {
      if (state.farmer[k] != null) body[k] = state.farmer[k];
    }
    Object.assign(body, vals);
    body.growth_stage = 1; // prediction is for starting a new crop -> initial stage
    const box = $('#pred-results');
    box.innerHTML = '<div class="card"><p class="muted">Analyzing…</p></div>';
    try {
      const res = await api('/api/predict', { method: 'POST', body });
      if (res.error) throw new Error(res.error);
      renderPredictions(res.suggestions);
    } catch (err) {
      box.innerHTML = `<div class="card"><p style="color:var(--danger)">${esc(err.message)}</p></div>`;
    }
  };
}

function renderPredictions(sugs) {
  const box = $('#pred-results');
  box.innerHTML = `<h3 class="section-title">Top suggestions for your field</h3>
    <div class="grid grid-3">` + sugs.map((s, i) => `
      <div class="pred-card ${i === 0 ? 'best' : ''}">
        ${i === 0 ? '<span class="badge-best">BEST MATCH</span>' : ''}
        <div class="crop-name">${esc(s.crop)}</div>
        <div class="conf">${s.confidence}% confidence</div>
        <div class="conf-bar"><div style="width:${s.confidence}%"></div></div>
        <div class="row mt" style="justify-content:center">
          <button class="btn btn-secondary btn-sm" onclick="predInfo('${s.crop}')">📋 Report</button>
          <button class="btn btn-primary btn-sm" onclick="predAdd('${s.crop}')">+ Add to Crops</button>
        </div>
      </div>`).join('') + `</div>`;
}

window.predInfo = async (crop) => {
  const info = await api(`/api/crop-info/${crop}`);
  showCropModal(info);
};

function askAcres(crop, defAcres) {
  return new Promise(resolve => {
    let modal = $('#acres-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'acres-modal';
      modal.className = 'modal-backdrop hidden';
      document.body.appendChild(modal);
    }
    modal.innerHTML = `<div class="modal" style="max-width:400px">
      <div class="row" style="justify-content:space-between">
        <h3 style="text-transform:capitalize">Add ${esc(crop)}</h3>
        <button class="btn btn-ghost btn-sm acres-close" style="font-size:18px;min-width:32px;height:32px;padding:0;display:flex;align-items:center;justify-content:center">×</button>
      </div>
      <div class="sub">How much area should this crop cover?</div>
      <form id="acres-form" class="form-grid mt">
        <div class="field"><label>Area (acres)</label>
          <input name="acres" type="number" step="any" min="0.01" value="${defAcres.toFixed(2)}" required></div>
      </form>
      <div class="modal-actions">
        <button type="button" class="btn btn-secondary acres-cancel">Cancel</button>
        <button type="button" class="btn btn-primary acres-ok">Add Plot</button>
      </div>
    </div>`;
    modal.classList.remove('hidden');
    const close = (val) => { modal.classList.add('hidden'); resolve(val); };
    modal.querySelector('.acres-close').onclick = () => close(null);
    modal.querySelector('.acres-cancel').onclick = () => close(null);
    modal.onclick = (e) => { if (e.target === modal) close(null); };
    modal.querySelector('.acres-ok').onclick = () => {
      const v = parseFloat(document.querySelector('#acres-form [name=acres]').value);
      close(isNaN(v) || v <= 0 ? null : v);
    };
    document.querySelector('#acres-form [name=acres]').focus();
    document.querySelector('#acres-form [name=acres]').select();
  });
}

window.predAdd = async (crop) => {
  const plots = state.farmer?.plots || [];
  const remaining = Math.max(0, (state.farmer?.total_land_acres || 0) - plots.reduce((a, p) => a + p.acres, 0));
  const defAcres = remaining > 0 ? Math.min(remaining, remaining / Math.max(1, 3 - plots.length)) : 0.5;
  const acres = await askAcres(crop, defAcres || 1);
  if (!acres) return;
  try {
    await api(`/api/farmers/${state.farmer.id}/plots`, { method: 'POST', body: { crop, acres } });
    state.farmer = await api(`/api/farmers/${state.farmer.id}`);
    toast(`${crop} added to your crops`, 'success');
  } catch (e) { toast(e.message, 'error'); }
};

/* ---------------- crop report ---------------- */
async function renderReport() {
  const preselect = sessionStorage.getItem('sf_report_crop');
  sessionStorage.removeItem('sf_report_crop');

  const crops = [...new Set([...(state.farmer?.plots || []).map(p => p.crop), ...state.meta.crops])];
  view().innerHTML = `
    <div class="card mb">
      <h3>Crop Growth Report</h3>
      <div class="sub">Duration, stage-wise water needs, irrigation intervals and sowing/harvest windows.</div>
      <div class="row">
        <div class="field" style="flex:1"><label>Select crop</label>
          <select id="report-crop">${crops.map(c => `<option value="${c}" ${c === preselect ? 'selected' : ''}>${c}</option>`).join('')}</select></div>
      </div>
    </div>
    <div id="report-body"></div>`;

  const load = async (crop) => {
    const body = $('#report-body');
    body.innerHTML = '<div class="card"><p class="muted">Loading…</p></div>';
    const info = await api(`/api/crop-info/${crop}`);
    const session = (state.farmer?.sessions || []).find(s => s.crop === crop && s.status === 'active');
    let sched = null, prog = null;
    if (session) {
      // reuse dashboard schedule endpoint per session is complex; compute via report? use growth_schedule indirectly
      const rep = await api(`/api/farmers/${state.farmer.id}/report`);
      const r = rep.active_reports.find(x => x.session.id === session.id);
      sched = r?.schedule; prog = r?.progress;
    }
    body.innerHTML = reportHTML(info, session, sched, prog);
  };

  $('#report-crop').onchange = (e) => load(e.target.value);
  if (preselect) load(preselect);
  else load(crops[0]);
}

function reportHTML(info, session, sched, prog) {
  const cal = info.calendar || {};
  let html = `
  <div class="grid grid-2">
    <div class="card">
      <h3 style="text-transform:capitalize">${esc(info.crop)}</h3>
      <div class="sub">${seasonTag(info.season)} ${cal.state ? '· ' + esc(cal.state) : ''}</div>
      <table>
        <tr><td class="muted">Total duration</td><td><b>${info.duration_days} days</b></td></tr>
        <tr><td class="muted">Seasonal water need</td><td><b>~${info.total_water_mm} mm</b>${sched ? ` (${num(sched.total_water_liters, 0)} L for ${sched && session ? session.acres : 1} ac)` : ''}</td></tr>
        <tr><td class="muted">Sowing window</td><td>${esc(cal.sowing || '—')}</td></tr>
        <tr><td class="muted">Harvest window</td><td>${esc(cal.harvest || cal.harvest_months || '—')}</td></tr>
      </table>
    </div>
    <div class="card">
      <h3>Growth Stages</h3>
      <div class="sub">Stage-wise duration, water use and irrigation interval${sched ? ' (live estimates)' : ''}</div>
      <div class="timeline">`;

  info.stages.forEach((s, i) => {
    const live = sched?.stages?.[i];
    const isCurrent = prog && prog.current_stage === s.name;
    const isDone = prog && prog.elapsed_days > s.end_day;
    html += `<div class="tl-item ${isDone ? 'done' : ''} ${isCurrent ? 'current' : ''}">
      <div class="tl-title">${esc(s.name)}</div>
      <div class="tl-meta">Day ${s.start_day}–${s.end_day} · ${s.days} days${live ? ` · ${live.start_date} → ${live.end_date}` : ''}</div>
      <div class="tl-water">💧 ${live ? `~${live.daily_water_mm} mm/day · irrigate every ~${live.irrigation_interval_days} days · ${live.stage_water_mm} mm total` : `part of ~${info.total_water_mm} mm seasonal need`}</div>
    </div>`;
  });
  html += `</div></div></div>`;

  if (session && prog) {
    html += `<div class="card mt">
      <h3>Live Progress — ${esc(session.crop)}</h3>
      <div class="progress-wrap mb"><div style="width:${prog.progress_pct}%"></div></div>
      <div class="progress-label"><span>Day ${prog.elapsed_days}/${prog.total_days} · ${esc(prog.current_stage || '')}</span><span>${prog.days_remaining} days left</span></div>
      <div class="mt muted" style="font-size:13px">Started ${esc(session.start_date)} · Expected harvest ${esc(prog.expected_harvest)}</div>
    </div>`;
  } else {
    const plot = state.farmer?.plots?.find(p => p.crop === info.crop);
    if (plot) {
      const hasActive = (state.farmer.sessions || []).some(s => s.plot_id === plot.id && s.status === 'active');
      if (!hasActive) {
        html += `<div class="card mt"><div class="row" style="justify-content:space-between">
          <div><b>Ready to grow ${esc(info.crop)}</b> on ${plot.acres} acres?</div>
          <button class="btn btn-accent" onclick="startFarming('${plot.id}'); setTimeout(()=>renderReport(),300)">▶ Start Farming</button>
        </div></div>`;
      }
    }
  }
  return html;
}

/* crop info modal */
function showCropModal(info) {
  let modal = $('#crop-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'crop-modal';
    modal.className = 'modal-backdrop hidden';
    document.body.appendChild(modal);
    modal.onclick = (e) => { if (e.target === modal) modal.classList.add('hidden'); };
  }
  modal.innerHTML = `<div class="modal modal-lg">
    <div class="row" style="justify-content:space-between">
      <h3 style="text-transform:capitalize">${esc(info.crop)} — Growth Report</h3>
      <button class="btn btn-ghost btn-sm crop-modal-close" style="font-size:18px;min-width:32px;height:32px;padding:0;display:flex;align-items:center;justify-content:center">×</button>
    </div>
    <div class="sub">${info.duration_days} days · ~${info.total_water_mm} mm water · ${seasonTag(info.season)}</div>
    <div class="timeline mt">` + info.stages.map(s => `
      <div class="tl-item"><div class="tl-title">${esc(s.name)}</div>
      <div class="tl-meta">Day ${s.start_day}–${s.end_day} (${s.days} days)</div></div>`).join('') + `</div>
    <div class="mt muted" style="font-size:13px">
      Sowing: ${esc(info.calendar?.sowing || '—')} · Harvest: ${esc(info.calendar?.harvest || info.calendar?.harvest_months || '—')}
    </div>
    <div class="modal-actions"><button class="btn btn-secondary crop-modal-close">Close</button></div>
  </div>`;
  modal.classList.remove('hidden');
  modal.querySelectorAll('.crop-modal-close').forEach(b => b.onclick = () => modal.classList.add('hidden'));
}

/* ---------------- irrigation ---------------- */
function renderIrrigation() {
  const f = state.farmer || {};
  const d = state.meta.feature_defaults;
  const w = state.lastWeather || {};
  const soilIrrName = state.meta.soil_types.find(o => o.code === Number(f.soil_type_code))?.irrigation_name || 'loam';
  const soilOptions = [
    ...state.meta.soil_types.map(o => ({ value: o.irrigation_name, label: o.name })),
    { value: 'sandy_loam', label: 'Sandy loam' },
    { value: 'silt_loam', label: 'Silt loam' },
    { value: 'clay_loam', label: 'Clay loam' },
    { value: 'sandy_clay_loam', label: 'Sandy clay loam' },
    { value: 'silty_clay', label: 'Silty clay' },
  ];
  const stageOptions = [
    { value: 'initial', label: 'Initial (germination / early growth)' },
    { value: 'mid', label: 'Mid (vegetative / flowering)' },
    { value: 'late', label: 'Late (maturity / ripening)' },
  ];

  view().innerHTML = `
  <div class="grid grid-2">
    <div class="card">
      <h3>Irrigation Recommendation</h3>
      <div class="sub">FAO-56 based — tells you <b>if</b> irrigation is needed and <b>how much</b>.</div>
      <form id="irr-form" class="form-grid">
        <div class="field"><label>Crop</label>
          <input name="crop_type" list="irr-crops" placeholder="e.g. rice">
          <datalist id="irr-crops">${['rice','wheat','maize','cotton','sugarcane','potato','tomato','chickpea','lentil','mungbean','blackgram','pigeonpeas','jute','banana','mango','orange','apple','pomegranate','grapes','papaya','coconut','coffee','muskmelon','watermelon','kidneybeans','mothbeans'].map(c=>`<option value="${c}">`).join('')}</datalist>
        </div>
        ${field('acres', 'Area (acres)', { placeholder: 'e.g. 1.5', min: '0.01' })}
        ${field('soil_moisture', 'Soil moisture now (%)', { placeholder: `avg ${num(d.soil_moisture,0)}`, min: '0', max: '100' })}
        ${field('recent_rainfall_mm', 'Rainfall last event (mm)', { placeholder: '0 if none', min: '0' })}
        ${field('rainfall_days_ago', 'Days since rainfall', { placeholder: 'e.g. 7', min: '0', max: '30' })}
        ${field('temperature', 'Temperature (°C)', { placeholder: w.temperature != null ? `${num(w.temperature,1)} (live)` : `avg ${num(d.temperature,1)}` })}
        ${field('humidity', 'Humidity (%)', { placeholder: w.humidity != null ? `${num(w.humidity,0)}% (live)` : `avg ${num(d.humidity,0)}`, min: '0', max: '100' })}
        ${field('wind_speed', 'Wind speed (m/s)', { placeholder: w.wind_speed != null ? `${num(w.wind_speed,1)} (live)` : `avg ${num(d.wind_speed,1)}`, min: '0' })}
        ${field('soil_type', 'Soil type', { value: soilIrrName, options: soilOptions })}
        ${field('growth_stage', 'Growth stage', { value: 'mid', options: stageOptions })}
        <div class="field" style="justify-content:flex-end"><button class="btn btn-primary btn-block" type="submit">Check Irrigation</button></div>
      </form>
    </div>
    <div>
      <div id="irr-result"></div>
      <div class="card mt">
        <h3>All Active Crops</h3>
        <div class="sub">One-tap irrigation check for each running session.</div>
        <div id="irr-active-list"></div>
      </div>
    </div>
  </div>`;

  $('#irr-form').onsubmit = async (e) => {
    e.preventDefault();
    const vals = formValues(e.target);
    const box = $('#irr-result');
    box.innerHTML = '<div class="card"><p class="muted">Calculating…</p></div>';
    try {
      const res = await api('/api/irrigation', { method: 'POST', body: vals });
      if (res.error) throw new Error(res.error);
      box.innerHTML = irrResultHTML(res, vals.crop_type);
    } catch (err) {
      box.innerHTML = `<div class="card"><p style="color:var(--danger)">${esc(err.message)}</p></div>`;
    }
  };

  renderActiveIrrigationList();
}

function irrResultHTML(res, crop) {
  const d = res.details || {};
  if (!res.irrigation_required) {
    return `<div class="banner ok"><span class="b-icon">✅</span><div>
      <h4>No irrigation needed for ${esc(crop)}</h4>
      <div>Soil moisture is sufficient${d.effective_rainfall ? ` and effective rainfall (${d.effective_rainfall} mm) covers demand` : ''}.
      Daily crop water use ≈ ${d.crop_evapotranspiration} mm. Check again in a few days.</div></div></div>
      <div class="card"><h3>Calculation details</h3><table>
        <tr><td class="muted">Reference ET (ETo)</td><td>${d.reference_evapotranspiration} mm/day</td></tr>
        <tr><td class="muted">Crop ET (ETc)</td><td>${d.crop_evapotranspiration} mm/day</td></tr>
        <tr><td class="muted">Effective rainfall</td><td>${d.effective_rainfall} mm</td></tr>
        <tr><td class="muted">Soil water deficit</td><td>${d.soil_water_deficit} mm</td></tr>
        <tr><td class="muted">Confidence</td><td>${Math.round((res.confidence || 0) * 100)}%</td></tr>
      </table></div>`;
  }
  return `<div class="banner warn"><span class="b-icon">💧</span><div>
    <h4>Irrigation required for ${esc(crop)}</h4>
    <div>Apply <b>${res.water_amount_mm} mm</b> now.</div></div></div>
    <div class="grid grid-3">
      <div class="card stat-card"><div class="num">${num(res.water_amount_liters_per_sqm, 0)}</div><div class="lbl">Litres / m²</div></div>
      <div class="card stat-card"><div class="num">${num(res.total_water_liters / 1000, 1)}</div><div class="lbl">m³ total</div></div>
      <div class="card stat-card"><div class="num">${num(res.total_water_liters, 0)}</div><div class="lbl">Litres total</div></div>
    </div>
    <div class="card mt"><h3>Calculation details</h3><table>
      <tr><td class="muted">Reference ET (ETo)</td><td>${d.reference_evapotranspiration} mm/day</td></tr>
      <tr><td class="muted">Crop ET (ETc)</td><td>${d.crop_evapotranspiration} mm/day</td></tr>
      <tr><td class="muted">Effective rainfall</td><td>${d.effective_rainfall} mm</td></tr>
      <tr><td class="muted">Soil water deficit</td><td>${d.soil_water_deficit} mm</td></tr>
      <tr><td class="muted">Confidence</td><td>${Math.round((res.confidence || 0) * 100)}%</td></tr>
    </table></div>`;
}

async function renderActiveIrrigationList() {
  const box = $('#irr-active-list');
  const sessions = (state.farmer?.sessions || []).filter(s => s.status === 'active');
  if (!sessions.length) {
    box.innerHTML = '<p class="muted" style="font-size:13px">No active sessions. Start farming on a plot first.</p>';
    return;
  }
  const f = state.farmer;
  box.innerHTML = sessions.map(s => `
    <div class="row" style="justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border)">
      <div><b style="text-transform:capitalize">${esc(s.crop)}</b> <span class="muted">· ${s.acres} ac</span></div>
      <button class="btn btn-secondary btn-sm" onclick="checkSessionIrrigation('${s.id}')">Check</button>
    </div>`).join('');
}

window.checkSessionIrrigation = async (sid) => {
  const s = state.farmer.sessions.find(x => x.id === sid);
  const f = state.farmer;
  const w = state.lastWeather || {};
  // estimate stage from elapsed days
  const days = Math.max(0, (Date.now() - new Date(s.start_date)) / 86400000);
  const stage = days < 40 ? 'initial' : days < 110 ? 'mid' : 'late';
  const body = {
    crop_type: s.crop, acres: s.acres,
    soil_moisture: f.soil_moisture ?? 50,
    recent_rainfall_mm: w.rain_1h_mm ?? 0, rainfall_days_ago: 1,
    temperature: w.temperature ?? f.temperature ?? 28,
    humidity: w.humidity ?? f.humidity ?? 60,
    wind_speed: w.wind_speed ?? f.wind_speed ?? 2,
    soil_type: state.meta.soil_types.find(o => o.code === Number(f.soil_type_code))?.irrigation_name || 'loam',
    growth_stage: stage,
  };
  const res = await api('/api/irrigation', { method: 'POST', body });
  toast(res.irrigation_required
    ? `💧 ${s.crop}: irrigate ${res.water_amount_mm} mm (${num(res.total_water_liters/1000,1)} m³)`
    : `✅ ${s.crop}: no irrigation needed`, res.irrigation_required ? 'success' : '');
};

/* ---------------- weather ---------------- */
async function renderWeather() {
  const w = state.lastWeather;
  const cfg = await api('/api/weather/config').catch(() => ({ provider: 'openmeteo', api_key: '' }));

  view().innerHTML = `
  <div class="card" style="position:relative">
    <h3>Weather Station</h3>
    <div class="sub">Powered by Open-Meteo (free, no key). Optional: switch to OpenWeatherMap.</div>
    <div class="mt">
      ${w ? `<button class="btn btn-secondary btn-sm" id="wx-change-loc">Change Location</button>` : ''}
      <div id="wx-form-wrap" class="${w ? 'hidden' : ''} mt">
        <form id="wx-form" class="form-grid">
          ${field('lat', 'Latitude', { value: state.farmer?.lat ?? '', step: 'any', placeholder: 'e.g. 13.1' })}
          ${field('lon', 'Longitude', { value: state.farmer?.lon ?? '', step: 'any', placeholder: 'e.g. 77.6' })}
          <div class="field"><label>Provider</label>
            <select name="provider">
              <option value="openmeteo" ${cfg.provider === 'openmeteo' ? 'selected' : ''}>Open-Meteo (free, no key)</option>
              <option value="openweathermap" ${cfg.provider === 'openweathermap' ? 'selected' : ''}>OpenWeatherMap (requires API key)</option>
            </select>
          </div>
          ${cfg.provider === 'openweathermap' ? field('api_key', 'OpenWeatherMap API key', { type: 'text', value: cfg.api_key || '', placeholder: 'Paste your key here' }) : ''}
          <div class="field" style="justify-content:flex-end"><button class="btn btn-primary" type="submit">Fetch Weather</button></div>
        </form>
        <div id="wx-status" class="mt muted" style="font-size:13px"></div>
      </div>
    </div>
    <div id="wx-result" class="mt">${w ? wxCard(w) : ''}</div>
  </div>`;

  $('#wx-form').onsubmit = async (e) => {
    e.preventDefault();
    const vals = formValues(e.target);
    if (!vals.lat || !vals.lon) {
      $('#wx-status').innerHTML = '<span style="color:var(--danger)">Enter latitude & longitude.</span>';
      return;
    }
    await api('/api/weather/config', { method: 'POST', body: { provider: vals.provider, api_key: vals.api_key || '' } });
    $('#wx-status').textContent = 'Fetching…';
    try {
      const res = await api(`/api/weather?lat=${vals.lat}&lon=${vals.lon}`);
      if (res.error) {
        $('#wx-status').innerHTML = `<span style="color:var(--danger)">${esc(res.message || res.error)}</span>`;
        return;
      }
      state.lastWeather = res;
      localStorage.setItem('sf_weather', JSON.stringify(res));
      $('#wx-status').textContent = '';
      renderWeather();
      renderWeatherChip();
      toast('Weather updated — prediction & irrigation forms will use it', 'success');
    } catch (err) {
      $('#wx-status').innerHTML = `<span style="color:var(--danger)">${esc(err.message)}</span>`;
    }
  };

  if (w) {
    $('#wx-change-loc').onclick = () => {
      $('#wx-form-wrap').classList.remove('hidden');
      $('#wx-change-loc').classList.add('hidden');
      $('#wx-result').innerHTML = '';
    };
  }
}

function wxCard(w) {
  const forecast = w.forecast || {};
  const nextRain = forecast.next_rain;
  const daily = forecast.daily || [];

  let forecastHTML = '';
  if (nextRain) {
    forecastHTML = `<div class="banner info"><span class="b-icon">🌧️</span><div>
      <h4>Rain expected</h4>
      <div>On <b>${esc(nextRain.date)}</b>: ~${num(nextRain.mm, 1)} mm (${nextRain.probability}% chance, ${nextRain.hours}h of rain)</div></div></div>`;
  } else {
    forecastHTML = `<div class="banner ok"><span class="b-icon">☀️</span><div><h4>No rain in next 5 days</h4></div></div>`;
  }

  const rows = daily.slice(0, 5).map(([date, mm, prob]) => `
    <tr><td>${esc(date.slice(5))}</td><td>${num(mm, 1)} mm</td><td>${prob}%</td></tr>`).join('');

  return `<div class="grid grid-2" style="gap:20px">
    <div style="background:#f9f9f9;border-radius:12px;padding:16px">
      <h4 style="margin-bottom:12px">Current Conditions ${w.location ? '· ' + esc(w.location) : ''}</h4>
      <div class="sub" style="margin-bottom:12px">Powered by ${w.provider === 'openmeteo' ? 'Open-Meteo' : 'OpenWeatherMap'}</div>
      <div class="grid grid-4 mb">
        <div class="stat-card" style="padding:12px 8px"><div class="num" style="font-size:22px">${num(w.temperature, 1)}°C</div><div class="lbl">Temp</div></div>
        <div class="stat-card" style="padding:12px 8px"><div class="num" style="font-size:22px">${num(w.humidity, 0)}%</div><div class="lbl">Humidity</div></div>
        <div class="stat-card" style="padding:12px 8px"><div class="num" style="font-size:22px">${num(w.wind_speed, 1)}</div><div class="lbl">Wind m/s</div></div>
        <div class="stat-card" style="padding:12px 8px"><div class="num" style="font-size:22px">${num(w.rain_1h_mm, 1)}</div><div class="lbl">Rain 1h</div></div>
      </div>
      <p class="muted" style="text-align:center;text-transform:capitalize;font-size:13px;margin-bottom:12px">${esc(w.description || '')}</p>
    </div>
    <div class="column" style="display:flex;flex-direction:column;gap:16px">
      ${forecastHTML}
      <div style="background:#f9f9f9;border-radius:12px;padding:16px">
        <h4 style="margin-bottom:10px">5-Day Forecast</h4>
        <table style="font-size:12px">
          <tr><th>Date</th><th>Precip (mm)</th><th>Probability</th></tr>
          ${rows}
        </table>
      </div>
    </div>
  </div>`;
}

function renderWeatherChip() {
  const el = $('#weather-chip');
  if (state.lastWeather && state.lastWeather.temperature != null) {
    el.innerHTML = `⛅ ${num(state.lastWeather.temperature, 0)}°C · ${num(state.lastWeather.humidity, 0)}% humidity`;
  } else {
    el.textContent = '';
  }
}

function emptyState(msg) {
  return `<div class="card empty-state"><div class="big">🌱</div><p>${msg}</p></div>`;
}

/* ---------------- init ---------------- */
document.addEventListener('DOMContentLoaded', async () => {
  document.querySelectorAll('.nav-item').forEach(b =>
    b.addEventListener('click', () => navigate(b.dataset.view)));
  $('#switch-farmer').onclick = () => {
    localStorage.removeItem('sf_farmer_id');
    state.farmer = null;
    openOnboarding();
  };
  $('#delete-farmer').onclick = async () => {
    if (!confirm('Delete ALL farmer data? This cannot be undone.')) return;
    try {
      await api('/api/reset', { method: 'POST' });
      localStorage.removeItem('sf_farmer_id');
      localStorage.removeItem('sf_weather');
      state.farmer = null;
      state.lastWeather = null;
      renderSidebar();
      renderWeatherChip();
      toast('All data deleted', 'success');
      openOnboarding();
    } catch (e) {
      toast(e.message, 'error');
    }
  };
  try {
    state.meta = await api('/api/meta');
    const w = localStorage.getItem('sf_weather');
    if (w) state.lastWeather = JSON.parse(w);
    await loadFarmer();
    renderWeatherChip();
  } catch (e) {
    view().innerHTML = `<div class="card"><p style="color:var(--danger)">Failed to load: ${esc(e.message)}</p></div>`;
  }
});
