/* ── STATE ────────────────────────────────────────────────────── */
const state = {
  step: 0,
  terrains: [],
  cities: [],
  selectedTerrain: null,
  selectedCity: null,
  budget: 'standard',
  days: 5,
  route: null,
};

/* ── TERRAIN CLASS MAP ─────────────────────────────────────────── */
const terrainClasses = {
  'Mountains':        'terrain-mountains',
  'Rivers':           'terrain-rivers',
  'Deserts':          'terrain-deserts',
  'Beaches':          'terrain-beaches',
  'Historical Sites': 'terrain-historical',
  'Lakes':            'terrain-lakes',
  'Valleys':          'terrain-valleys',
  'Wildlife & Forests': 'terrain-wildlife',
};

const categoryIcons = {
  nature:    '🌿',
  culture:   '🏛️',
  adventure: '🧗',
  food:      '🍽️',
  shopping:  '🛍️',
  spiritual: '🕌',
};

/* ── UTILITIES ─────────────────────────────────────────────────── */
function formatPKR(amount) {
  return 'PKR ' + Number(amount).toLocaleString('en-PK');
}

async function api(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: 'Network error' }));
    throw new Error(err.error || 'API error');
  }
  return res.json();
}

function el(selector) { return document.querySelector(selector); }
function els(selector) { return document.querySelectorAll(selector); }

function showLoading(message = 'Loading…') {
  el('#appMain').innerHTML = `
    <div class="loading-wrap">
      <div class="spinner"></div>
      <p class="loading-text">${message}</p>
    </div>`;
}

/* ── PROGRESS BAR ─────────────────────────────────────────────── */
function updateProgress(step) {
  const pb = el('#progressBar');
  pb.classList.remove('hidden');
  els('.progress-step').forEach(s => {
    const n = parseInt(s.dataset.step);
    s.classList.remove('active', 'done');
    if (n === step) s.classList.add('active');
    else if (n < step) s.classList.add('done');
  });
  // Progress lines
  for (let i = 1; i <= 3; i++) {
    const line = el(`#line-${i}-${i+1}`);
    if (line) {
      if (i < step) line.classList.add('done');
      else line.classList.remove('done');
    }
  }
}

function hideProgress() {
  el('#progressBar').classList.add('hidden');
}

/* ── STEP DISPLAY ─────────────────────────────────────────────── */
function showStep(n) {
  state.step = n;
  el('#hero').classList.add('hidden');
  el('#btnRestart').classList.remove('hidden');
  updateProgress(n);
}

function showHero() {
  el('#hero').classList.remove('hidden');
  el('#progressBar').classList.add('hidden');
  el('#btnRestart').classList.add('hidden');
  el('#appMain').innerHTML = '';
  state.step = 0;
}

/* ── STEP 1: TERRAINS ─────────────────────────────────────────── */
function renderTerrains(terrains) {
  showStep(1);
  el('#appMain').innerHTML = `
    <div class="section-header">
      <h2>Choose Your Adventure Terrain</h2>
      <p>What kind of landscape calls to your soul?</p>
    </div>
    <div class="terrain-grid" id="terrainGrid"></div>`;

  const grid = el('#terrainGrid');
  terrains.forEach(t => {
    const cls = terrainClasses[t.name] || 'terrain-mountains';
    const card = document.createElement('div');
    card.className = `terrain-card ${cls}`;
    card.innerHTML = `
      <div class="terrain-icon">${t.icon}</div>
      <div class="terrain-name">${t.name}</div>
      <div class="terrain-desc">${t.description}</div>
      <div class="terrain-count">${t.city_count} destinations</div>`;
    card.addEventListener('click', () => selectTerrain(t));
    grid.appendChild(card);
  });
}

async function selectTerrain(terrain) {
  state.selectedTerrain = terrain;
  showLoading(`Finding cities for ${terrain.name}…`);
  try {
    const cities = await api(`/api/cities?terrain_id=${terrain.id}`);
    state.cities = cities;
    renderCities(cities, terrain);
  } catch(e) {
    el('#appMain').innerHTML = `<p style="color:red;padding:2rem">Error: ${e.message}</p>`;
  }
}

/* ── STEP 2: CITIES ───────────────────────────────────────────── */
function renderCities(cities, terrain) {
  showStep(2);
  el('#appMain').innerHTML = `
    <button class="back-btn" id="backToTerrains">&#8592; Back to Terrains</button>
    <div class="section-header">
      <h2>${terrain.icon} ${terrain.name} Destinations</h2>
      <p>Select a city to explore</p>
    </div>
    <div class="cities-grid" id="citiesGrid"></div>`;

  el('#backToTerrains').addEventListener('click', () => renderTerrains(state.terrains));

  const grid = el('#citiesGrid');
  cities.forEach(city => {
    const highlights = (city.highlights || []).slice(0, 2);
    const card = document.createElement('div');
    card.className = 'city-card';
    card.innerHTML = `
      <div class="city-card-img">
        <img src="${city.image_url}" alt="${city.name}" loading="lazy">
        <div class="city-card-overlay">
          <div class="city-season-badge">Best: ${city.best_season || 'Year round'}</div>
        </div>
      </div>
      <div class="city-card-body">
        <div class="city-card-name">${city.name}</div>
        <div class="city-card-province">📍 ${city.province}</div>
        <div class="city-card-desc">${city.description}</div>
        ${highlights.length ? `<div class="city-highlights">${highlights.map(h => `<span class="highlight-chip">${h}</span>`).join('')}</div>` : ''}
      </div>`;
    card.addEventListener('click', () => selectCity(city));
    grid.appendChild(card);
  });
}

async function selectCity(city) {
  state.selectedCity = city;
  showLoading(`Loading ${city.name} details…`);
  try {
    const detail = await api(`/api/cities/${city.id}`);
    state.selectedCity = detail;
    renderBudgetStep(detail);
  } catch(e) {
    el('#appMain').innerHTML = `<p style="color:red;padding:2rem">Error: ${e.message}</p>`;
  }
}

/* ── STEP 3: BUDGET & DAYS ────────────────────────────────────── */
const budgets = [
  {
    key: 'luxury', emoji: '✨', name: 'Luxury',
    range: 'PKR 50,000+/day',
    features: ['5-star hotels', 'Private car', 'Fine dining', 'All activities'],
  },
  {
    key: 'standard', emoji: '🏨', name: 'Standard',
    range: 'PKR 15,000–50,000/day',
    features: ['3-4 star hotels', 'Hired taxi', 'Good restaurants', 'Most activities'],
  },
  {
    key: 'budget', emoji: '🏠', name: 'Budget',
    range: 'PKR 5,000–15,000/day',
    features: ['Guesthouses', 'Shared transport', 'Local food', 'Free attractions'],
  },
  {
    key: 'backpacker', emoji: '🎒', name: 'Backpacker',
    range: 'PKR 1,500–5,000/day',
    features: ['Hostels/camping', 'Local buses', 'Street food', 'Free sights'],
  },
];

function renderBudgetStep(city) {
  showStep(3);
  el('#appMain').innerHTML = `
    <button class="back-btn" id="backToCities">&#8592; Back to Cities</button>
    <div class="section-header">
      <h2>Plan Your Trip to ${city.name}</h2>
      <p>Choose your budget style and trip duration</p>
    </div>

    <div class="city-preview">
      <div class="city-preview-img">
        <img src="${city.image_url}" alt="${city.name}" loading="lazy">
      </div>
      <div class="city-preview-info">
        <div class="city-preview-name">${city.name}</div>
        <div class="city-preview-province">📍 ${city.province} &nbsp;·&nbsp; ${city.terrain_icon} ${city.terrain_name}</div>
        <div class="city-preview-desc">${city.description}</div>
        ${city.local_food ? `<div style="margin-top:0.6rem;font-size:0.82rem;color:var(--text-muted)">🍽️ Local specialty: <strong>${city.local_food}</strong></div>` : ''}
      </div>
    </div>

    <div class="section-header" style="margin-top:1.5rem;margin-bottom:1.2rem">
      <h2 style="font-size:1.5rem">Select Budget</h2>
    </div>

    <div class="budget-grid" id="budgetGrid"></div>

    <div class="days-section">
      <div class="days-header">
        <div class="days-title">How many days?</div>
        <div class="days-counter" id="daysCounter">${state.days}</div>
      </div>
      <input type="range" class="days-slider" id="daysSlider"
        min="1" max="14" value="${state.days}" step="1">
      <div class="days-marks">
        <span>1 day</span><span>3</span><span>5</span><span>7</span><span>10</span><span>14 days</span>
      </div>
    </div>

    <button class="generate-btn" id="generateBtn">Generate My Route &#8594;</button>`;

  el('#backToCities').addEventListener('click', () => renderCities(state.cities, state.selectedTerrain));

  // Budget cards
  const grid = el('#budgetGrid');
  budgets.forEach(b => {
    const card = document.createElement('div');
    card.className = `budget-card${state.budget === b.key ? ' selected' : ''}`;
    card.dataset.key = b.key;
    card.innerHTML = `
      <div class="budget-emoji">${b.emoji}</div>
      <div class="budget-name">${b.name}</div>
      <div class="budget-range">${b.range}</div>
      <ul class="budget-features">
        ${b.features.map(f => `<li>${f}</li>`).join('')}
      </ul>`;
    card.addEventListener('click', () => {
      state.budget = b.key;
      els('.budget-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });
    grid.appendChild(card);
  });

  // Slider
  const slider = el('#daysSlider');
  const counter = el('#daysCounter');
  updateSliderStyle(slider);

  slider.addEventListener('input', () => {
    state.days = parseInt(slider.value);
    counter.textContent = state.days;
    updateSliderStyle(slider);
  });

  el('#generateBtn').addEventListener('click', generateRoute);
}

function updateSliderStyle(slider) {
  const min = slider.min || 1;
  const max = slider.max || 14;
  const val = slider.value;
  const pct = ((val - min) / (max - min)) * 100;
  slider.style.setProperty('--val', pct + '%');
}

/* ── STEP 4: ROUTE ────────────────────────────────────────────── */
async function generateRoute() {
  showLoading('Crafting your perfect Pakistan itinerary…');
  showStep(4);
  try {
    const route = await api('/api/route', {
      method: 'POST',
      body: JSON.stringify({
        city_id: state.selectedCity.id,
        budget: state.budget,
        days: state.days,
      }),
    });
    state.route = route;
    renderRoute(route);
  } catch(e) {
    el('#appMain').innerHTML = `
      <button class="back-btn" id="backToBudget">&#8592; Back</button>
      <p style="color:red;padding:2rem">Error generating route: ${e.message}</p>`;
    el('#backToBudget').addEventListener('click', () => renderBudgetStep(state.selectedCity));
  }
}

function renderRoute(route) {
  const city = route.city;
  const cost = route.cost_breakdown;

  el('#appMain').innerHTML = `
    <button class="back-btn" id="backToBudget2">&#8592; Change Budget / Days</button>

    <div class="route-section">

      <!-- City Hero -->
      <div class="route-hero">
        <img src="${city.image_url}" alt="${city.name}">
        <div class="route-hero-overlay">
          <div class="route-hero-text">
            <h2>${city.name}, ${city.province}</h2>
            <p>${city.description}</p>
            <div class="route-meta">
              <span class="route-meta-badge">${city.terrain_icon} ${city.terrain_name}</span>
              <span class="route-meta-badge">${route.days}-Day Trip</span>
              <span class="route-meta-badge accent">${route.budget_label}</span>
              ${city.best_season ? `<span class="route-meta-badge">📅 Best: ${city.best_season}</span>` : ''}
            </div>
          </div>
        </div>
      </div>

      <!-- Gallery -->
      <div class="gallery-section">
        <div class="gallery-title">📷 Photo Gallery</div>
        <div class="gallery-grid" id="galleryGrid"></div>
      </div>

      <!-- Cost Summary -->
      <div class="cost-card">
        <div class="cost-card-header">
          <div>
            <div class="cost-card-title">Total Estimated Cost</div>
            <div class="cost-total">${formatPKR(cost.grand_total)}</div>
            <div class="cost-per-day">≈ ${formatPKR(cost.per_day_avg)} per day average</div>
          </div>
          <div style="text-align:right">
            <div class="cost-card-title">Trip Summary</div>
            <div style="font-size:1rem;font-weight:600;color:var(--accent-light)">${route.days} Days · ${route.day_plans.length} Days Planned</div>
            ${city.best_season ? `<div class="season-badge" style="margin-top:8px">Best Season: ${city.best_season}</div>` : ''}
          </div>
        </div>
        <div class="cost-breakdown-grid">
          <div class="cost-item">
            <div class="cost-item-label">🏨 Accommodation</div>
            <div class="cost-item-amount">${formatPKR(cost.accommodation)}</div>
          </div>
          <div class="cost-item">
            <div class="cost-item-label">🍽️ Food & Dining</div>
            <div class="cost-item-amount">${formatPKR(cost.food)}</div>
          </div>
          <div class="cost-item">
            <div class="cost-item-label">🚗 Transport</div>
            <div class="cost-item-amount">${formatPKR(cost.transport)}</div>
          </div>
          <div class="cost-item">
            <div class="cost-item-label">🎭 Activities</div>
            <div class="cost-item-amount">${formatPKR(cost.activities)}</div>
          </div>
          <div class="cost-item">
            <div class="cost-item-label">🎟️ Entry Fees</div>
            <div class="cost-item-amount">${formatPKR(cost.entry_fees)}</div>
          </div>
          <div class="cost-item">
            <div class="cost-item-label">💼 Miscellaneous</div>
            <div class="cost-item-amount">${formatPKR(cost.misc)}</div>
          </div>
        </div>
      </div>

      <!-- Day-by-Day Timeline -->
      <div class="section-header">
        <h2>Your Day-by-Day Itinerary</h2>
        <p>A carefully crafted route for your ${route.days}-day adventure</p>
      </div>

      <div id="hotelsSection"></div>

      <div class="timeline" id="timeline"></div>

      <!-- Travel Tips -->
      <div class="tips-card">
        <div class="tips-title">💡 Travel Tips for ${city.name}</div>
        <ul class="tips-list" id="tipsList"></ul>
      </div>

    </div>`;

  // Gallery
  renderGallery(city.gallery_images, city);

  // Timeline
  renderTimeline(route);

  // Hotels
  renderHotelsSection(route.hotels, route.budget);

  // Tips
  const tipsList = el('#tipsList');
  (route.travel_tips || []).forEach(tip => {
    const li = document.createElement('li');
    li.textContent = tip;
    tipsList.appendChild(li);
  });

  el('#backToBudget2').addEventListener('click', () => renderBudgetStep(state.selectedCity));
}

function renderGallery(images, city) {
  const grid = el('#galleryGrid');
  if (!grid) return;
  const allImages = images && images.length ? images : [city.image_url];
  allImages.slice(0, 4).forEach((url, i) => {
    const item = document.createElement('div');
    item.className = 'gallery-item';
    item.innerHTML = `<img src="${url}" alt="${city.name} photo ${i+1}" loading="lazy">`;
    grid.appendChild(item);
  });
}

function renderTimeline(route) {
  const timeline = el('#timeline');
  if (!timeline) return;

  route.day_plans.forEach((day, idx) => {
    const dayColors = ['#1a6b3c','#2d8a5e','#0d4526','#1e7a50','#2d6a4f'];
    const borderColor = dayColors[idx % dayColors.length];

    const card = document.createElement('div');
    card.className = 'day-card';
    card.style.animationDelay = `${idx * 0.1}s`;

    const attractionsHtml = (day.attractions || []).map(att => {
      const catIcon = categoryIcons[att.category] || '📍';
      const feeChip = att.entry_fee_pkr > 0
        ? `<span class="chip chip-fee">PKR ${att.entry_fee_pkr} entry</span>`
        : `<span class="chip chip-fee">Free entry</span>`;
      return `
        <div class="attraction-item">
          <div class="attraction-img">
            <img src="${att.image_url}" alt="${att.name}" loading="lazy">
          </div>
          <div class="attraction-info">
            <div class="attraction-name">${catIcon} ${att.name}</div>
            <div class="attraction-desc">${att.description}</div>
            <div class="attraction-chips">
              <span class="chip chip-category">${att.category}</span>
              <span class="chip chip-time">${att.time_of_day}</span>
              <span class="chip chip-duration">⏱ ${att.duration_hours}h</span>
              ${feeChip}
            </div>
            ${att.tip ? `<div class="attraction-tip">💡 ${att.tip}</div>` : ''}
          </div>
        </div>`;
    }).join('');

    card.innerHTML = `
      <div class="day-number" style="background:linear-gradient(135deg,${borderColor},${borderColor}cc)">
        <span class="day-number-big">${day.day}</span>
        <span>Day</span>
      </div>
      <div class="day-body" style="border-left-color:${borderColor}">
        <div class="day-theme">${day.theme}</div>
        <div class="day-note">${day.note}</div>
        <div class="attractions-list">${attractionsHtml}</div>
        <div class="day-footer">
          <div class="day-info-item">
            <div class="day-info-label">🏨 Stay Tonight</div>
            <div class="day-info-value">${day.accommodation}</div>
          </div>
          <div class="day-info-item">
            <div class="day-info-label">🍽️ Food Suggestion</div>
            <div class="day-info-value">${day.food_suggestion}</div>
          </div>
          <div class="day-info-item">
            <div class="day-info-label">🚗 Transport</div>
            <div class="day-info-value">${day.transport_tip}</div>
          </div>
          <div class="day-info-item">
            <div class="day-info-label">💰 Estimated Day Cost</div>
            <div class="day-info-value" style="color:var(--primary);font-weight:700">${formatPKR(day.day_cost)}</div>
          </div>
        </div>
      </div>`;

    timeline.appendChild(card);
  });
}

/* ── INIT ─────────────────────────────────────────────────────── */
async function init() {
  showLoading('Loading Pakistan Tourist Guide…');
  try {
    const terrains = await api('/api/terrains');
    state.terrains = terrains;
    // Show hero instead of terrains immediately
    el('#appMain').innerHTML = '';
    el('#hero').classList.remove('hidden');
  } catch(e) {
    el('#appMain').innerHTML = `<p style="color:red;padding:2rem">Failed to load: ${e.message}</p>`;
  }
}

function renderHotelsSection(hotels, selectedBudget) {
  const section = el('#hotelsSection');
  if (!section || !hotels || hotels.length === 0) return;

  const budgetOrder = ['luxury', 'standard', 'budget', 'backpacker'];
  const budgetLabels = {
    luxury: { label: '✨ Luxury', cls: 'luxury' },
    standard: { label: '🏨 Standard', cls: 'standard' },
    budget: { label: '🏠 Budget', cls: 'budget' },
    backpacker: { label: '🎒 Backpacker', cls: 'backpacker' },
  };

  const byBudget = {};
  hotels.forEach(h => {
    if (!byBudget[h.budget_level]) byBudget[h.budget_level] = [];
    byBudget[h.budget_level].push(h);
  });

  const sorted = budgetOrder.filter(b => byBudget[b]);

  const cardsHtml = sorted.map(level => {
    const h = byBudget[level][0];
    const isRec = level === selectedBudget;
    const bl = budgetLabels[level] || { label: level, cls: 'standard' };
    const stars = '⭐'.repeat(h.stars || 3);
    const amenitiesHtml = (h.amenities || []).slice(0, 5).map(a =>
      `<span class="hotel-amenity">${a}</span>`
    ).join('');

    return `
      <div class="hotel-card${isRec ? ' recommended' : ''}">
        <div class="hotel-card-header">
          <span class="hotel-badge ${bl.cls}">${bl.label}</span>
          ${isRec ? '<span class="recommended-badge">✓ Your Pick</span>' : ''}
        </div>
        <div class="hotel-name">${h.name}</div>
        <div class="hotel-stars-row">
          <span class="hotel-stars">${stars}</span>
          <span class="hotel-price">${formatPKR(h.price_per_night_pkr)}/night</span>
        </div>
        ${h.address ? `<div class="hotel-address">📍 ${h.address}</div>` : ''}
        <div class="hotel-amenities">${amenitiesHtml}</div>
        <div class="hotel-desc">${h.description}</div>
        ${h.booking_tip ? `<div class="hotel-tip">💡 ${h.booking_tip}</div>` : ''}
      </div>`;
  }).join('');

  const cityName = (state.selectedCity && state.selectedCity.name) || 'your destination';
  section.innerHTML = `
    <div class="hotels-section">
      <div class="section-header">
        <h2>🏨 Where to Stay in ${cityName}</h2>
        <p>Hand-picked options for every budget — your selected tier is highlighted</p>
      </div>
      <div class="hotels-grid">${cardsHtml}</div>
    </div>`;
}

/* ── EVENT LISTENERS ──────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  init();

  el('#btnStart').addEventListener('click', () => {
    el('#hero').classList.add('hidden');
    renderTerrains(state.terrains);
  });

  el('#btnRestart').addEventListener('click', () => {
    state.selectedTerrain = null;
    state.selectedCity = null;
    state.budget = 'standard';
    state.days = 5;
    state.route = null;
    showHero();
  });
});
