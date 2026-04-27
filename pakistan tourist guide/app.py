"""
Pakistan Tourist Guide - Web Application
Built with Starlette (ASGI) + Jinja2 + SQLite
Run: uvicorn app:app --host 0.0.0.0 --port 5000
"""

import sqlite3
import json
import os
import math
from pathlib import Path

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'pakistan_tourism.db'
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))

DAILY_COSTS = {
    'luxury':     {'accommodation': 25000, 'food': 8000, 'transport': 12000, 'activities': 5000, 'misc': 3000},
    'standard':   {'accommodation': 7000,  'food': 2500, 'transport': 3000,  'activities': 1500, 'misc': 800},
    'budget':     {'accommodation': 2200,  'food': 1200, 'transport': 800,   'activities': 400,  'misc': 200},
    'backpacker': {'accommodation': 600,   'food': 700,  'transport': 350,   'activities': 150,  'misc': 100},
}

BUDGET_LABELS = {
    'luxury':     'Luxury (PKR 53,000+/day)',
    'standard':   'Standard (PKR 14,800/day)',
    'budget':     'Budget (PKR 4,800/day)',
    'backpacker': 'Backpacker (PKR 1,900/day)',
}

ACCOMMODATION_TIPS = {
    'luxury':     'Stay at premium hotels with full amenities, room service, and concierge.',
    'standard':   'Comfortable mid-range hotels with private bathroom and breakfast.',
    'budget':     'Clean guesthouses or budget hotels with basic amenities.',
    'backpacker': 'Hostels, community guesthouses, or camping.',
}

DAY_THEMES = [
    'Arrival & City Highlights',
    'Cultural Immersion',
    'Nature & Scenery',
    'Adventure & Exploration',
    'Local Life & Cuisine',
    'Hidden Gems & Off-the-Beaten-Path',
    'Relaxation & Reflection',
    'Markets & Shopping',
    'Spiritual & Heritage Sites',
    'Farewell & Departure',
]

TRANSPORT_TIPS = {
    'luxury':     'Hire a private air-conditioned car with driver for the day (PKR 6,000–15,000).',
    'standard':   'Use a mix of hired Suzuki pickups, local taxis, and occasional rickshaws.',
    'budget':     'Local buses, shared jeeps, and rickshaws for maximum savings.',
    'backpacker': 'Wagons, local buses, and hitch-hiking with locals—the authentic way.',
}


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db():
    if not DB_PATH.exists():
        import init_db
        init_db.init_db()


# ── ROUTE HANDLERS ────────────────────────────────────────────────

async def homepage(request: Request):
    ensure_db()
    return templates.TemplateResponse(request, 'index.html')


async def api_terrains(request: Request):
    ensure_db()
    db = get_db()
    try:
        rows = db.execute('SELECT * FROM terrain_types ORDER BY id').fetchall()
        terrains = []
        for r in rows:
            t = dict(r)
            count = db.execute('SELECT COUNT(*) FROM cities WHERE terrain_type_id=?',
                               (r['id'],)).fetchone()[0]
            t['city_count'] = count
            terrains.append(t)
        return JSONResponse(terrains)
    finally:
        db.close()


async def api_cities(request: Request):
    ensure_db()
    terrain_id = request.query_params.get('terrain_id')
    db = get_db()
    try:
        if terrain_id:
            rows = db.execute(
                'SELECT c.*, t.name as terrain_name, t.icon as terrain_icon '
                'FROM cities c JOIN terrain_types t ON c.terrain_type_id=t.id '
                'WHERE c.terrain_type_id=? ORDER BY c.name',
                (int(terrain_id),)
            ).fetchall()
        else:
            rows = db.execute(
                'SELECT c.*, t.name as terrain_name, t.icon as terrain_icon '
                'FROM cities c JOIN terrain_types t ON c.terrain_type_id=t.id ORDER BY c.name'
            ).fetchall()
        cities = []
        for r in rows:
            c = dict(r)
            c['gallery_images'] = json.loads(c['gallery_images']) if c['gallery_images'] else []
            c['highlights'] = json.loads(c['highlights']) if c['highlights'] else []
            cities.append(c)
        return JSONResponse(cities)
    finally:
        db.close()


async def api_city_detail(request: Request):
    ensure_db()
    city_id = int(request.path_params['city_id'])
    db = get_db()
    try:
        row = db.execute(
            'SELECT c.*, t.name as terrain_name, t.icon as terrain_icon, t.color as terrain_color '
            'FROM cities c JOIN terrain_types t ON c.terrain_type_id=t.id WHERE c.id=?',
            (city_id,)
        ).fetchone()
        if not row:
            return JSONResponse({'error': 'City not found'}, status_code=404)
        city = dict(row)
        city['gallery_images'] = json.loads(city['gallery_images']) if city['gallery_images'] else []
        city['highlights'] = json.loads(city['highlights']) if city['highlights'] else []

        attractions = db.execute(
            'SELECT * FROM attractions WHERE city_id=? ORDER BY priority ASC, duration_hours DESC',
            (city_id,)
        ).fetchall()
        city['attractions'] = []
        for a in attractions:
            att = dict(a)
            att['budget_levels'] = json.loads(att['budget_levels']) if att['budget_levels'] else ['all']
            city['attractions'].append(att)
        return JSONResponse(city)
    finally:
        db.close()


async def api_route(request: Request):
    ensure_db()
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({'error': 'Invalid JSON body'}, status_code=400)

    city_id = data.get('city_id')
    budget = str(data.get('budget', 'standard')).lower()
    days = int(data.get('days', 5))

    if budget not in DAILY_COSTS:
        return JSONResponse({'error': 'Invalid budget type'}, status_code=400)
    if not city_id:
        return JSONResponse({'error': 'city_id required'}, status_code=400)

    db = get_db()
    try:
        city_row = db.execute(
            'SELECT c.*, t.name as terrain_name, t.icon as terrain_icon, t.color as terrain_color '
            'FROM cities c JOIN terrain_types t ON c.terrain_type_id=t.id WHERE c.id=?',
            (int(city_id),)
        ).fetchone()
        if not city_row:
            return JSONResponse({'error': 'City not found'}, status_code=404)

        city = dict(city_row)
        city['gallery_images'] = json.loads(city['gallery_images']) if city['gallery_images'] else []
        city['highlights'] = json.loads(city['highlights']) if city['highlights'] else []

        all_attractions = db.execute(
            'SELECT * FROM attractions WHERE city_id=? ORDER BY priority ASC, duration_hours DESC',
            (int(city_id),)
        ).fetchall()

        def budget_ok(att_row):
            levels = json.loads(att_row['budget_levels']) if att_row['budget_levels'] else ['all']
            if 'all' in levels:
                return True
            if budget in levels:
                return True
            if budget == 'luxury':
                return True
            return False

        eligible = [dict(a) for a in all_attractions if budget_ok(a)]
        for e in eligible:
            if isinstance(e['budget_levels'], str):
                e['budget_levels'] = json.loads(e['budget_levels'])

        daily_cost = DAILY_COSTS[budget]
        per_day_cost = sum(daily_cost.values())

        day_plans = []
        used_ids = set()

        for day_num in range(1, days + 1):
            theme_idx = (day_num - 1) % len(DAY_THEMES)
            if day_num == days and days > 1:
                theme = 'Farewell & Departure'
            elif day_num == 1:
                theme = 'Arrival & City Highlights'
            else:
                theme = DAY_THEMES[theme_idx]

            day_atts = []
            hours_used = 0.0
            max_hours = 7.0

            remaining = [a for a in eligible if a['id'] not in used_ids]
            if not remaining:
                used_ids.clear()
                remaining = list(eligible)

            remaining.sort(key=lambda x: (x['priority'], -x['duration_hours']))

            for att in remaining:
                if hours_used + att['duration_hours'] <= max_hours and len(day_atts) < 4:
                    day_atts.append(att)
                    hours_used += att['duration_hours']
                    used_ids.add(att['id'])

            # If still empty (very few attractions), force add the top ones
            if not day_atts and eligible:
                used_ids.clear()
                sorted_all = sorted(eligible, key=lambda x: (x['priority'], -x['duration_hours']))
                for att in sorted_all[:3]:
                    day_atts.append(att)
                    used_ids.add(att['id'])

            acc_key = f'accommodation_{budget}'
            accommodation = city.get(acc_key) or 'Local guesthouse'

            food_suggestion_base = city.get('local_food') or 'Local Pakistani cuisine'
            if day_num == 1:
                food_note = f'Welcome dinner: Try the local specialty — {food_suggestion_base}'
            elif day_num == days:
                food_note = f'Farewell meal: Savour {food_suggestion_base} one last time before departure'
            else:
                food_note = f'Try {food_suggestion_base} at a local restaurant for an authentic experience'

            day_notes = [
                f'Start your day in {city["name"]} with a hearty Pakistani breakfast before heading out.',
                f'A wonderful day of exploration in {city["name"]} — pace yourself and enjoy the journey.',
                f'Today\'s highlights in {city["name"]} will create lasting memories.',
                f'Immerse yourself in the culture and scenery of {city["name"]}.',
                f'Another spectacular day exploring the wonders of {city["name"]}.',
            ]
            day_note = day_notes[(day_num - 1) % len(day_notes)]
            day_entry_cost = sum(a.get('entry_fee_pkr', 0) for a in day_atts)

            day_plans.append({
                'day': day_num,
                'theme': theme,
                'note': day_note,
                'attractions': day_atts,
                'accommodation': accommodation,
                'food_suggestion': food_note,
                'transport_tip': TRANSPORT_TIPS[budget],
                'entry_fees': day_entry_cost,
                'day_cost': per_day_cost + day_entry_cost,
            })

        total_accommodation = daily_cost['accommodation'] * days
        total_food = daily_cost['food'] * days
        total_transport = daily_cost['transport'] * days
        total_activities = daily_cost['activities'] * days
        total_misc = daily_cost['misc'] * days
        total_entry = sum(d['entry_fees'] for d in day_plans)
        grand_total = sum(daily_cost.values()) * days + total_entry

        hotels_rows = db.execute(
            'SELECT * FROM hotels WHERE city_id=? ORDER BY stars DESC',
            (int(city_id),)
        ).fetchall()
        hotels_data = []
        for h in hotels_rows:
            hd = dict(h)
            hd['amenities'] = json.loads(hd['amenities']) if hd['amenities'] else []
            hotels_data.append(hd)

        route = {
            'city': city,
            'budget': budget,
            'budget_label': BUDGET_LABELS[budget],
            'days': days,
            'day_plans': day_plans,
            'hotels': hotels_data,
            'cost_breakdown': {
                'accommodation': total_accommodation,
                'food': total_food,
                'transport': total_transport,
                'activities': total_activities,
                'misc': total_misc,
                'entry_fees': total_entry,
                'grand_total': grand_total,
                'per_day_avg': math.ceil(grand_total / days),
            },
            'travel_tips': [
                f'Best time to visit {city["name"]}: {city.get("best_season", "Check seasonal conditions")}',
                city.get('climate_info') or 'Pack appropriately for the climate.',
                f'Local speciality not to miss: {city.get("local_food") or "Ask locals for recommendations"}',
                ACCOMMODATION_TIPS[budget],
                'Always carry cash — many remote areas have no ATMs.',
                'Respect local customs and dress modestly, especially at religious sites.',
                'Register with local police if visiting remote areas — it\'s required and for your safety.',
            ],
        }
        return JSONResponse(route)
    finally:
        db.close()


# ── APP ───────────────────────────────────────────────────────────

routes = [
    Route('/', homepage),
    Route('/api/terrains', api_terrains),
    Route('/api/cities', api_cities),
    Route('/api/cities/{city_id:int}', api_city_detail),
    Route('/api/route', api_route, methods=['POST']),
    Mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static'),
]

app = Starlette(routes=routes)


if __name__ == '__main__':
    import uvicorn
    ensure_db()
    uvicorn.run('app:app', host='0.0.0.0', port=5000, reload=True)
