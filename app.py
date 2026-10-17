import calendar, hashlib, json, math, uuid
from datetime import date, datetime, timedelta
from pathlib import Path
import streamlit as st

st.set_page_config(page_title='DailyBloom', page_icon='✿', layout='wide')
ROOT = Path(__file__).parent
USERS = ROOT / 'users.json'
MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']


# ---------- Datos ----------
def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def user_file():
    return ROOT / f'habits_{st.session_state.user_id}.json'


def get_data():
    return read_json(user_file(), {'habits': [
        {'id': 'h1', 'name': 'Meditar 10 minutos', 'category': 'Mind'},
        {'id': 'h2', 'name': 'Beber agua', 'category': 'Body'},
        {'id': 'h3', 'name': 'Caminar 10.000 pasos', 'category': 'Body'},
        {'id': 'h4', 'name': 'Comer de forma equilibrada', 'category': 'Body'},
        {'id': 'h5', 'name': 'Dormir entre 7 y 8 horas', 'category': 'Energy'},
        {'id': 'h6', 'name': 'Desconectar de las pantallas', 'category': 'Energy'},
        {'id': 'h7', 'name': 'Leer 20 minutos', 'category': 'Mind'}], 'completed': {}, 'metrics': {}})


def save_data():
    write_json(user_file(), st.session_state.data)


def done(day):
    return set(st.session_state.data['completed'].get(day, []))


def progress(day):
    hs = st.session_state.data['habits']
    n = sum(h['id'] in done(day) for h in hs)
    return n, len(hs), round(100 * n / len(hs)) if hs else 0


def cat_progress(day, cat):
    hs = [h for h in st.session_state.data['habits'] if h['category'] == cat]
    return round(100 * sum(h['id'] in done(day) for h in hs) / len(hs)) if hs else 0


def metric(day, key, default=0):
    return st.session_state.data['metrics'].get(day, {}).get(key, default)


def set_metric(day, key, value):
    st.session_state.data['metrics'].setdefault(day, {})[key] = value
    save_data()


def change_month(delta):
    m = st.session_state.cal_month + delta
    y = st.session_state.cal_year
    if m < 1:
        m, y = 12, y - 1
    if m > 12:
        m, y = 1, y + 1
    st.session_state.cal_month, st.session_state.cal_year = m, y


# ---------- Flor de equilibrio ----------
def balance_svg(mind, body, energy):
    rings = ''.join(f'<circle cx="120" cy="120" r="{r}" fill="none" stroke="#e9eaf6" stroke-width="1"/>' for r in range(43, 94, 5))
    arcs = []
    for pct, color, off in [(mind, '#d99bd8', 0), (body, '#8dd5df', 120), (energy, '#9299ec', 240)]:
        circ = 2 * math.pi * 91
        arcs.append(f'<circle cx="120" cy="120" r="91" fill="none" stroke="{color}" stroke-width="2.8" stroke-linecap="round" stroke-dasharray="{circ*pct/100:.1f} {circ:.1f}" stroke-dashoffset="{-circ*off/360:.1f}" transform="rotate(-90 120 120)"/>')
    petals = ''.join(f'<ellipse cx="0" cy="-17" rx="8.5" ry="18" fill="url(#petal)" transform="rotate({a})"/>' for a in range(0, 360, 45))
    return f'''<svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block"><defs><radialGradient id="petal" cx="35%" cy="25%" r="75%"><stop stop-color="#dedcff"/><stop offset="1" stop-color="#7c85df"/></radialGradient><linearGradient id="stem"><stop stop-color="#a7dce5"/><stop offset="1" stop-color="#d5b5e9"/></linearGradient></defs>{rings}{''.join(arcs)}<g transform="translate(120 119)"><path d="M0 7 C-6 20 -6 26 -2 34" fill="none" stroke="url(#stem)" stroke-width="2.5"/><path d="M-2 27 C-18 19 -19 28 -9 31 C-5 31 -3 29 -2 27Z" fill="#a9dce2"/>{petals}<circle r="7.5" fill="#f6e7ff" stroke="#c8b4f2"/></g></svg>'''


# ---------- Estilos ----------
st.markdown('''<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root{--ink:#24274d;--muted:#7c809d;--line:#e8e9f4}
.stApp{background:radial-gradient(ellipse at 5% 0%,rgba(211,219,255,.72),transparent 30%),radial-gradient(ellipse at 95% 12%,rgba(244,220,242,.68),transparent 27%),linear-gradient(135deg,#f5f6fc,#fbfaff 52%,#f0f3fb);color:var(--ink);font-family:'DM Sans',sans-serif}
[data-testid="stSidebar"]{background:rgba(255,255,255,.94);border-right:1px solid #e9eaf5}
h1,h2,h3{font-family:'Manrope',sans-serif!important;color:#282c54!important}
h1{font-weight:800!important;letter-spacing:-1.3px;font-size:2.2rem!important}

/* Botones generales */
div.stButton>button,div.stFormSubmitButton>button{border:1px solid #e1e2f8;background:linear-gradient(115deg,#aeb6f3,#c8b8eb 55%,#efcfe7);color:#30345f;border-radius:999px;font-weight:600;min-height:2.5rem;transition:all .2s}
div.stButton>button:hover{border-color:#a5a9e8;transform:translateY(-1px)}
div[data-testid="stCheckbox"] label{color:#3c4165}

/* Sidebar: solo la página activa lleva degradado */
[data-testid="stSidebar"] div.stButton>button[kind="secondary"],
[data-testid="stSidebar"] div.stButton>button[data-testid="stBaseButton-secondary"]{background:transparent;border:none;box-shadow:none;color:#4a4e78;justify-content:flex-start}
[data-testid="stSidebar"] div.stButton>button[kind="secondary"]:hover,
[data-testid="stSidebar"] div.stButton>button[data-testid="stBaseButton-secondary"]:hover{background:#f0f0fb;transform:none}
[data-testid="stSidebar"] div.stButton>button[kind="primary"],
[data-testid="stSidebar"] div.stButton>button[data-testid="stBaseButton-primary"]{justify-content:flex-start}

/* Tarjetas HTML */
.db-card{background:rgba(255,255,255,.94);border:1px solid #eee8f4;border-radius:24px;padding:22px;box-shadow:0 8px 26px rgba(91,70,120,.045);height:100%}
.db-eyebrow{color:#817ba7;font-size:.78rem;font-weight:700;letter-spacing:.045em;text-transform:uppercase;margin-bottom:13px}
.db-muted{color:#8883a9;font-size:.92rem}
.db-quote{font-family:'Manrope',sans-serif;font-size:1.2rem;line-height:1.45;color:#34385f}
.db-brand{font-family:'Manrope',sans-serif;font-size:1.5rem;font-weight:800;color:#292d56}
.db-mark{width:38px;height:38px;border:1.7px solid #c8b8e9;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#a18bd3;font-size:22px}
.db-footer{text-align:center;color:#9690b0;font-size:.8rem;padding:1.4rem}

/* Tarjetas del dashboard (contenedores de Streamlit) */
.st-key-card_balance,.st-key-card_goals,.st-key-card_calendar{background:rgba(255,255,255,.94);border:1px solid #eee8f4;border-radius:24px;padding:22px;box-shadow:0 8px 26px rgba(91,70,120,.045);min-height:500px}
.st-key-card_goals{gap:.5rem}

/* Calendario pequeño: días redondos con número visible */
.st-key-card_calendar [data-testid="stHorizontalBlock"]{gap:.2rem}
.st-key-card_calendar [data-testid="stColumn"]{min-width:0!important}
.st-key-card_calendar div.stButton>button{height:34px;min-height:0;width:100%;padding:0;border-radius:999px;background:#eceefb;border:1px solid transparent;color:#4a4e78;font-size:.8rem;display:flex;justify-content:center;align-items:center}
.st-key-card_calendar div.stButton>button p{font-size:.8rem;margin:0;line-height:1}
.st-key-card_calendar div.stButton>button:hover{background:#d8d9f7;transform:none}
.st-key-card_calendar .cal-head{text-align:center;color:#898da9;font-size:.7rem;font-weight:600}
.st-key-card_calendar [class*="st-key-nav_"] div.stButton>button{height:36px;min-height:0;width:100%;padding:0 12px;background:linear-gradient(115deg,#aeb6f3,#c8b8eb 55%,#efcfe7)}

/* Bienestar */
.wellbeing-heading{font-family:'Manrope',sans-serif;font-size:1.8rem;font-weight:700;color:#34315f;margin:1.3rem 0 .25rem}
.wellbeing-subtitle{color:#8883a9;font-size:1rem;margin-bottom:1.1rem}
.wellbeing-label{display:flex;align-items:center;gap:10px;color:#817ba7;font-size:.95rem;font-weight:700;margin-bottom:12px}
.wellbeing-icon{font-size:1.25rem}
.wellbeing-card{background:#fff;border:1px solid #f0eaf5;border-radius:22px;padding:21px 20px 17px;box-shadow:0 6px 22px rgba(91,70,120,.035);min-height:155px}
.wellbeing-value{font-family:'Manrope',sans-serif;color:#34315f;font-size:2rem;font-weight:750;line-height:1.25;margin:7px 0}
.wellbeing-caption{font-size:.92rem;color:#8883a9}
.wellbeing-progress{height:7px;background:#f0eaf7;border-radius:999px;overflow:hidden;margin:11px 0 9px}
.wellbeing-progress-fill{height:100%;background:linear-gradient(90deg,#d783aa,#b9a5ed);border-radius:999px}
.st-key-water_buttons{margin-top:16px}
.st-key-water_buttons [data-testid="stHorizontalBlock"]{gap:24px!important}
div[data-testid="stPopover"]{margin-top:14px}

div[data-testid="stProgressBar"]>div>div{background:linear-gradient(90deg,#d783aa,#b9a5ed)}
div[data-testid="stProgressBar"]>div{background:#f0eaf7;border-radius:999px}
div[data-testid="stMetric"]{background:#ffffffdd;border:1px solid var(--line);border-radius:18px;padding:15px}
hr{border-color:#eee8f4}

.st-key-card_goals{gap:.9rem}
.st-key-card_goals .db-muted{margin-bottom:.4rem}

</style>''', unsafe_allow_html=True)

# ---------- Pantalla de bienvenida ----------
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if not st.session_state.user_id:
    users = read_json(USERS, {})
    left, right = st.columns([1.08, 1], gap='large', vertical_alignment='center')
    with left:
        st.markdown('<div style="display:flex;align-items:center;gap:12px;margin:8px 0 26px"><div class="db-mark">✿</div><div class="db-brand">DailyBloom</div></div>', unsafe_allow_html=True)
        st.markdown('# Make room to bloom.')
        st.markdown('<div style="font-size:1.05rem;line-height:1.85;color:#747995;max-width:510px">Un espacio personal para cuidar tus hábitos, encontrar tu equilibrio y celebrar cada pequeño avance. A tu ritmo, a tu manera.</div>', unsafe_allow_html=True)
        st.markdown('<div class="db-card" style="margin-top:28px"><div class="db-eyebrow">TU ESPACIO, TU RITMO</div><div style="display:flex;align-items:center;gap:16px"><div style="width:160px;flex-shrink:0">' + balance_svg(72, 63, 82) + '</div><div><div class="db-quote">“Crece a tu propio ritmo.”</div><div class="db-muted" style="margin-top:10px">Mind · Body · Energy</div></div></div></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="db-eyebrow">EMPIEZA TU CAMINO</div>', unsafe_allow_html=True)
        mode = st.radio('Acceso', ['Crear cuenta', 'Iniciar sesión'], horizontal=True, label_visibility='collapsed')
        with st.form('welcome_form'):
            name = st.text_input('Tu nombre', placeholder='¿Cómo te llamas?', max_chars=40)
            password = st.text_input('Contraseña', type='password', placeholder='Al menos 4 caracteres')
            submit = st.form_submit_button('Crear mi espacio' if mode == 'Crear cuenta' else 'Entrar a DailyBloom', use_container_width=True)
        st.markdown('<div class="db-muted" style="font-size:.76rem;margin-top:12px">Prototipo local. No uses una contraseña que utilices en otros servicios.</div>', unsafe_allow_html=True)

        if submit:
            clean = name.strip()
            key = clean.casefold()
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if not clean or not password:
                st.warning('Completa tu nombre y la contraseña.')
            elif len(password) < 4:
                st.warning('La contraseña debe tener al menos 4 caracteres.')
            elif mode == 'Crear cuenta':
                if key in users:
                    st.warning('Ya existe una cuenta con ese nombre. Inicia sesión.')
                else:
                    users[key] = {'name': clean, 'id': str(uuid.uuid4()), 'password_hash': hashed}
                    write_json(USERS, users)
                    st.session_state.user_id = users[key]['id']
                    st.session_state.user_name = clean
                    st.rerun()
            else:
                rec = users.get(key)
                if rec and rec['password_hash'] == hashed:
                    st.session_state.user_id = rec['id']
                    st.session_state.user_name = rec['name']
                    st.rerun()
                else:
                    st.error('El nombre o la contraseña no coinciden.')
    st.stop()

# ---------- Sesión iniciada ----------
users = read_json(USERS, {})
if 'user_name' not in st.session_state:
    st.session_state.user_name = next((u['name'] for u in users.values() if u['id'] == st.session_state.user_id), '')
if st.session_state.get('loaded_user') != st.session_state.user_id:
    st.session_state.data = get_data()
    st.session_state.loaded_user = st.session_state.user_id
data = st.session_state.data

today = date.today()
today_key = today.isoformat()


def greeting():
    h = datetime.now().hour
    return 'Buenos días' if h < 12 else ('Buenas tardes' if h < 19 else 'Buenas noches')


def date_label(d):
    months = [m.lower() for m in MESES]
    days = [x.lower() for x in DIAS]
    return f'{days[d.weekday()]}, {d.day} de {months[d.month-1]} de {d.year}'


if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'
if 'cal_year' not in st.session_state:
    st.session_state.cal_year = today.year
if 'cal_month' not in st.session_state:
    st.session_state.cal_month = today.month
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = today

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div style="display:flex;align-items:center;gap:10px;padding:5px 5px 22px"><div class="db-mark">✿</div><div class="db-brand">DailyBloom</div></div>', unsafe_allow_html=True)
    for label, sym in [('Dashboard', '▦'), ('Progreso', '◔'), ('Calendario', '▦'), ('Logros', '♕'), ('Consejos', '✧')]:
        if st.button(f'{sym}   {label}', key='nav_' + label, use_container_width=True, type='primary' if st.session_state.page == label else 'secondary'):
            st.session_state.page = label
            st.rerun()
    st.markdown('---')
    st.markdown(f'**{st.session_state.user_name}**  \n<span class="db-muted">Tu espacio personal</span>', unsafe_allow_html=True)
    if st.button('Cerrar sesión', use_container_width=True):
        for k in ['user_id', 'user_name', 'data', 'loaded_user']:
            st.session_state.pop(k, None)
        st.rerun()

# ---------- Cabecera ----------
hl, hr = st.columns([5, 1.5], vertical_alignment='center')
with hl:
    st.markdown(f'# {greeting()}, {st.session_state.user_name}')
    st.markdown(f'<div class="db-muted">{date_label(today).capitalize()}</div>', unsafe_allow_html=True)
with hr:
    if st.button('＋ Añadir hábito', use_container_width=True):
        st.session_state.show_add = not st.session_state.get('show_add', False)
if st.session_state.get('show_add', False):
    with st.form('add_habit', clear_on_submit=True):
        name = st.text_input('Nombre del hábito', placeholder='Ej. Leer 20 minutos')
        c1, c2 = st.columns(2)
        with c1:
            cat = st.selectbox('Área', ['Mind', 'Body', 'Energy', 'Personal'])
        with c2:
            freq = st.selectbox('Frecuencia', ['Diario', 'Días laborables', 'Semanal'])
        if st.form_submit_button('Guardar hábito'):
            if name.strip():
                data['habits'].append({'id': str(uuid.uuid4()), 'name': name.strip(), 'category': cat, 'frequency': freq})
                save_data()
                st.session_state.show_add = False
                st.rerun()
            else:
                st.warning('Escribe el nombre del hábito.')

# ---------- Páginas ----------
page = st.session_state.page

if page == 'Dashboard':
    count, total, pct = progress(today_key)
    c1, c2, c3 = st.columns([1.05, 1.1, 1.05], gap='medium')

    # Daily balance
    with c1:
        with st.container(key='card_balance'):
            st.markdown('<div class="db-eyebrow">DAILY BALANCE</div>', unsafe_allow_html=True)
            vals = [cat_progress(today_key, x) for x in ['Mind', 'Body', 'Energy']]
            st.markdown(f'<div style="max-width:260px;margin:0 auto">{balance_svg(*vals)}</div>', unsafe_allow_html=True)
            for label, val, color in zip(['Mind', 'Body', 'Energy'], vals, ['#d99bd8', '#8dd5df', '#9299ec']):
                st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:.82rem;margin-top:8px"><span><span style="color:{color}">●</span> {label}</span><strong>{val}%</strong></div>', unsafe_allow_html=True)
            st.markdown('<div class="db-muted" style="margin-top:12px">Tu equilibrio de hoy</div>', unsafe_allow_html=True)

    # Today's goals
    with c2:
        with st.container(key='card_goals'):
            st.markdown('<div class="db-eyebrow">TODAY’S GOALS</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="db-muted">{count} de {total} objetivos completados</div>', unsafe_allow_html=True)
            for h in data['habits']:
                old = h['id'] in done(today_key)
                new = st.checkbox(h['name'], value=old, key=f"habit_{h['id']}_{today_key}")
                if new != old:
                    current = done(today_key)
                    current.add(h['id']) if new else current.discard(h['id'])
                    data['completed'][today_key] = sorted(current)
                    save_data()
                    st.rerun()
            st.progress(pct / 100)
            st.markdown(f'<div class="db-muted">{pct}% de tu día completado</div>', unsafe_allow_html=True)

    # Calendario
    with c3:
        cy, cm = st.session_state.cal_year, st.session_state.cal_month
        # Estilo por día: hoy con borde, días con hábitos con relleno
        day_css = ''
        for n in range(1, calendar.monthrange(cy, cm)[1] + 1):
            iso = date(cy, cm, n).isoformat()
            p = progress(iso)[2]
            sel = f'.st-key-day_{cy}_{cm}_{n} button'
            if p >= 100:
                day_css += f'{sel}{{background:#9299ec!important;color:#fff!important}}'
            elif p > 0:
                day_css += f'{sel}{{background:#c9ccf6!important}}'
            if iso == today_key:
                day_css += f'{sel}{{border:2px solid #7c85df!important;font-weight:700}}'
        st.markdown(f'<style>{day_css}</style>', unsafe_allow_html=True)

        with st.container(key='card_calendar'):
            st.markdown('<div class="db-eyebrow">CALENDAR</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center;font-weight:700;margin:4px 0 10px">{MESES[cm-1]} {cy}</div>', unsafe_allow_html=True)
            a, b, c = st.columns([1, 1.4, 1])
            with a:
                with st.container(key='nav_prev'):
                    if st.button('‹', key='mprev', use_container_width=True):
                        change_month(-1)
                        st.rerun()
            with b:
                with st.container(key='nav_today'):
                    if st.button('Hoy', key='mtoday', use_container_width=True):
                        st.session_state.cal_month, st.session_state.cal_year = today.month, today.year
                        st.rerun()
            with c:
                with st.container(key='nav_next'):
                    if st.button('›', key='mnext', use_container_width=True):
                        change_month(1)
                        st.rerun()
            for col, wd in zip(st.columns(7, gap='small'), ['L', 'M', 'X', 'J', 'V', 'S', 'D']):
                col.markdown(f'<div class="cal-head">{wd}</div>', unsafe_allow_html=True)
            for week in calendar.Calendar(firstweekday=0).monthdayscalendar(cy, cm):
                for col, n in zip(st.columns(7, gap='small'), week):
                    with col:
                        if not n:
                            st.markdown('<div style="height:34px"></div>', unsafe_allow_html=True)
                        elif st.button(str(n), key=f'day_{cy}_{cm}_{n}', use_container_width=True):
                            st.session_state.selected_date = date(cy, cm, n)
                            st.session_state.page = 'Calendario'
                            st.rerun()
            st.markdown('<div class="db-muted" style="margin-top:8px;font-size:.8rem">Selecciona un día para ver el historial.</div>', unsafe_allow_html=True)

    # Bienestar
    st.markdown('<div class="wellbeing-heading">Tu bienestar 🌷</div><div class="wellbeing-subtitle">Pequeños pasos, grandes cambios.</div>', unsafe_allow_html=True)
    wleft, wright = st.columns(2, gap='medium')
    steps = int(metric(today_key, 'steps', 0))
    water = int(metric(today_key, 'water', 0))
    mins = int(metric(today_key, 'meditation', 0))
    sleep = float(metric(today_key, 'sleep', 0))
    with wleft:
        st.markdown(f'<div class="wellbeing-card"><div class="wellbeing-label"><span class="wellbeing-icon" style="color:#d783aa">♧</span> ACTIVIDAD</div><div class="wellbeing-value">{steps:,} pasos</div><div class="wellbeing-progress"><div class="wellbeing-progress-fill" style="width:{min(steps/10000*100,100):.1f}%"></div></div><div class="wellbeing-caption">Objetivo diario</div></div>', unsafe_allow_html=True)
        with st.popover('Registrar pasos'):
            v = st.number_input('Pasos de hoy', 0, 100000, steps, step=500)
            if st.button('Guardar pasos'):
                set_metric(today_key, 'steps', v)
                st.rerun()
        st.markdown(f'<div class="wellbeing-card" style="margin-top:14px"><div class="wellbeing-label"><span class="wellbeing-icon" style="color:#d783aa">❀</span> MEDITACIÓN</div><div class="wellbeing-value">{mins} min</div><div class="wellbeing-caption">Regálate una pausa.</div></div>', unsafe_allow_html=True)
        with st.popover('Añadir minutos'):
            v = st.number_input('Minutos', 1, 240, 10, step=5)
            if st.button('Guardar sesión'):
                set_metric(today_key, 'meditation', mins + v)
                st.rerun()
    with wright:
        st.markdown(f'<div class="wellbeing-card"><div class="wellbeing-label"><span class="wellbeing-icon" style="color:#9297e7">♧</span> HIDRATACIÓN</div><div class="wellbeing-value">{water} de 8</div><div class="wellbeing-progress"><div class="wellbeing-progress-fill" style="width:{min(water/8*100,100):.1f}%"></div></div><div class="wellbeing-caption">Vasos de agua</div></div>', unsafe_allow_html=True)
        with st.container(key='water_buttons'):
            x, y = st.columns(2, gap='large')
            with x:
                if st.button('+ Vaso', key='add_water', use_container_width=True):
                    set_metric(today_key, 'water', water + 1)
                    st.rerun()
            with y:
                if st.button('− Vaso', key='remove_water', use_container_width=True):
                    set_metric(today_key, 'water', max(0, water - 1))
                    st.rerun()
        st.markdown(f'<div class="wellbeing-card" style="margin-top:14px"><div class="wellbeing-label"><span class="wellbeing-icon" style="color:#9297e7">☾</span> DESCANSO</div><div class="wellbeing-value">{sleep:g} de 8 h</div><div class="wellbeing-progress"><div class="wellbeing-progress-fill" style="width:{min(sleep/8*100,100):.1f}%"></div></div><div class="wellbeing-caption">Tu descanso importa.</div></div>', unsafe_allow_html=True)
        with st.popover('Registrar sueño'):
            v = st.slider('Horas dormidas', 0.0, 16.0, sleep, .25)
            if st.button('Guardar descanso'):
                set_metric(today_key, 'sleep', v)
                st.rerun()
    with st.expander('Gestionar hábitos'):
        for h in list(data['habits']):
            x, y = st.columns([5, 1])
            x.write(f"**{h['name']}** · {h['category']}")
            if y.button('Eliminar', key='del_' + h['id']):
                data['habits'] = [z for z in data['habits'] if z['id'] != h['id']]
                save_data()
                st.rerun()

elif page == 'Calendario':
    st.markdown('## Tu calendario')
    a, b, c, d = st.columns([1, 1, 1.4, 1.6])
    with a:
        if st.button('← Anterior'):
            change_month(-1)
            st.rerun()
    with b:
        if st.button('Siguiente →'):
            change_month(1)
            st.rerun()
    with c:
        y = st.number_input('Año', 1900, 2200, st.session_state.cal_year)
        if y != st.session_state.cal_year:
            st.session_state.cal_year = y
            st.rerun()
    with d:
        m = st.selectbox('Mes', range(1, 13), index=st.session_state.cal_month - 1, format_func=lambda n: MESES[n - 1])
        if m != st.session_state.cal_month:
            st.session_state.cal_month = m
            st.rerun()
    st.markdown(f"### {MESES[st.session_state.cal_month-1]} {st.session_state.cal_year}")
    for col, wd in zip(st.columns(7), DIAS):
        col.markdown(f'**{wd}**')
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(st.session_state.cal_year, st.session_state.cal_month):
        cols = st.columns(7)
        for col, n in zip(cols, week):
            with col:
                if not n:
                    st.markdown('<div style="height:65px"></div>', unsafe_allow_html=True)
                else:
                    dd = date(st.session_state.cal_year, st.session_state.cal_month, n)
                    nc, nt, np_ = progress(dd.isoformat())
                    st.markdown(f'<div class="db-card" style="padding:10px;min-height:62px"><strong>{n}</strong><div class="db-muted">{nc}/{nt} hábitos</div></div>', unsafe_allow_html=True)
                    if st.button('Ver día', key=f'sel_{dd.isoformat()}'):
                        st.session_state.selected_date = dd
                        st.rerun()
    selected = st.session_state.selected_date
    nc, nt, np_ = progress(selected.isoformat())
    st.markdown(f'### {selected.strftime("%d/%m/%Y")}')
    st.progress(np_ / 100)
    st.write(f'{nc} de {nt} hábitos completados · {np_}%')
    for h in data['habits']:
        st.write(('✓' if h['id'] in done(selected.isoformat()) else '○') + '  ' + h['name'])

elif page == 'Progreso':
    import pandas as pd
    st.markdown('## Tu progreso')
    days = [today - timedelta(days=i) for i in range(13, -1, -1)]
    frame = pd.DataFrame([{'Fecha': d.strftime('%d/%m'), 'Progreso': progress(d.isoformat())[2], 'Completados': progress(d.isoformat())[0]} for d in days]).set_index('Fecha')
    a, b, c = st.columns(3)
    a.metric('Progreso de hoy', f'{progress(today_key)[2]}%')
    b.metric('Media de 14 días', f'{round(frame.Progreso.mean())}%')
    c.metric('Hábitos activos', len(data['habits']))
    st.markdown('### Evolución diaria')
    st.line_chart(frame[['Progreso']])
    st.bar_chart(frame[['Completados']])

elif page == 'Logros':
    st.markdown('## Tus logros')
    records = sum(len(set(v)) for v in data['completed'].values())
    days_active = sum(bool(v) for v in data['completed'].values())
    for title, desc, ok in [('Primera semilla', 'Completa tu primer hábito.', records >= 1),
                            ('Una semana de intención', 'Registra hábitos en siete días distintos.', days_active >= 7),
                            ('Constancia en crecimiento', 'Acumula 30 registros.', records >= 30)]:
        with st.container(border=True):
            st.markdown(f'**{title}** · {"Desbloqueado" if ok else "Por desbloquear"}')
            st.write(desc)

elif page == 'Consejos':
    st.markdown('## Pequeños recordatorios')
    st.markdown('<div class="db-muted">No necesitas hacerlo todo perfecto para avanzar.</div>', unsafe_allow_html=True)
    for title, body in [('Empieza pequeño', 'Elige una versión fácil del hábito.'),
                        ('Hazlo visible', 'Deja a la vista aquello que te ayude a recordar.'),
                        ('Deja espacio', 'Descansar también forma parte de una rutina sostenible.'),
                        ('Celebra la constancia', 'Un día difícil no borra lo que ya has construido.')]:
        with st.container(border=True):
            st.markdown(f'### {title}')
            st.write(body)

st.markdown('<div class="db-footer">DAILYBLOOM · Crece a tu propio ritmo</div>', unsafe_allow_html=True)