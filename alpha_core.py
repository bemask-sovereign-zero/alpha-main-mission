import streamlit as st
import streamlit.components.v1 as components
import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone, timedelta

# ==============================================================================
# 1. PAGE CONFIG — MOONBASE A.L.P.H.A. // MAIN MISSION COMMAND (1975 EDITION)
# ==============================================================================
st.set_page_config(
    page_title="BEMASK - MOONBASE A.L.P.H.A. // MAIN MISSION",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_italy_now():
    return datetime.now(timezone(timedelta(hours=1)))

def render_wafer_number(val_str, unit=""):
    offsets = {"0": "1px", "1": "-1px", "2": "1px", "3": "-1px", "4": "1px", "5": "-1px", "6": "1px", "7": "-1px", "8": "1px", "9": "-1px", ".": "0px", "%": "0px", ":": "0px"}
    html = "<div class='wafer-housing'>"
    for ch in str(val_str):
        y_off = offsets.get(ch, "0px")
        html += f"<span class='wafer-tube'><span class='wafer-ghost'>8</span><span class='wafer-digit' style='transform:translateY({y_off});'>{ch}</span></span>"
    if unit:
        html += f"<span class='wafer-unit'>{unit}</span>"
    html += "</div>"
    return html

@st.cache_data(ttl=1800)
def fetch_alpha_weather(lat=42.922, lon=10.758):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone=Europe%2FRome&forecast_days=5"
    )
    days_en = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            daily = data["daily"]
            forecast = []
            for i in range(5):
                dt_obj = datetime.strptime(daily["time"][i], "%Y-%m-%d")
                day_lbl = "SOL 00" if i == 0 else f"{days_en[dt_obj.weekday()]} {dt_obj.strftime('%d/%m')}"
                tmax = round(daily["temperature_2m_max"][i])
                rain_p = daily["precipitation_probability_max"][i]
                status = "NOMINAL ORBIT" if rain_p < 35 else "SOLAR STORM"
                col = "#ffb703" if rain_p < 35 else "#ff2a54"
                forecast.append({"day": day_lbl, "tmax": tmax, "rain": rain_p, "hint": status, "col": col})
            return forecast
    except Exception:
        return [
            {"day": "SOL 00", "tmax": 18, "rain": 20, "hint": "NOMINAL ORBIT", "col": "#ffb703"},
            {"day": "THU 05/11", "tmax": 19, "rain": 30, "hint": "NOMINAL ORBIT", "col": "#ffb703"},
            {"day": "FRI 06/11", "tmax": 14, "rain": 60, "hint": "SOLAR STORM", "col": "#ff2a54"},
            {"day": "SAT 07/11", "tmax": 17, "rain": 25, "hint": "NOMINAL ORBIT", "col": "#ffb703"},
            {"day": "SUN 08/11", "tmax": 17, "rain": 15, "hint": "NOMINAL ORBIT", "col": "#ffb703"}
        ]

# ==============================================================================
# 2. SPACE: 1999 SEASON 1 + CHESS TOTEM SVG ARSENAL
# ==============================================================================
TOTEM_LIBRARY = {
    "EAGLE": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><polygon points='6,34 16,28 16,38' fill='none' stroke='%23ffb703' stroke-width='2.2'/><rect x='16' y='27' width='32' height='10' fill='none' stroke='%23ffffff' stroke-width='2'/><line x1='22' y1='27' x2='28' y2='37' stroke='%23ffb703' stroke-width='1.8'/><line x1='28' y1='27' x2='34' y2='37' stroke='%23ffb703' stroke-width='1.8'/><line x1='34' y1='27' x2='40' y2='37' stroke='%23ffb703' stroke-width='1.8'/><rect x='48' y='29' width='8' height='6' fill='none' stroke='%23ff2a54' stroke-width='2'/><rect x='18' y='39' width='8' height='5' fill='none' stroke='%2300f0ff' stroke-width='2'/><rect x='38' y='39' width='8' height='5' fill='none' stroke='%2300f0ff' stroke-width='2'/></svg>",
    "ROOK": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><polyline points='16,22 16,12 23,12 23,17 29,17 29,12 35,12 35,17 41,17 41,12 48,12 48,22' fill='none' stroke='%23ff2a54' stroke-width='2.5'/><rect x='20' y='22' width='24' height='26' fill='none' stroke='%23ffffff' stroke-width='2.2'/><rect x='14' y='48' width='36' height='6' fill='none' stroke='%23ff2a54' stroke-width='2.5'/></svg>",
    "QUEEN": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><polygon points='14,46 10,20 23,32 32,14 41,32 54,20 50,46' fill='none' stroke='%23ffb703' stroke-width='2.5'/><circle cx='32' cy='10' r='2.5' fill='%23ffffff'/><rect x='14' y='49' width='36' height='5' fill='none' stroke='%23ffffff' stroke-width='2.2'/></svg>",
    "BISHOP": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><path d='M32 12 C19 22, 19 39, 24 47 L40 47 C45 39, 45 22, 32 12 Z' fill='none' stroke='%2300f0ff' stroke-width='2.5'/><line x1='26' y1='28' x2='37' y2='20' stroke='%23ffffff' stroke-width='2.5'/><circle cx='32' cy='8' r='2.2' fill='%23ffffff'/><rect x='18' y='50' width='28' height='5' fill='none' stroke='%2300f0ff' stroke-width='2.2'/></svg>",
    "KNIGHT": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><path d='M18 48 L22 30 L15 27 L21 15 L35 10 L47 19 L40 31 L46 48 Z' fill='none' stroke='%2300ff9d' stroke-width='2.5'/><circle cx='29' cy='19' r='2.2' fill='%23ffffff'/><rect x='14' y='50' width='36' height='5' fill='none' stroke='%23ffffff' stroke-width='2.2'/></svg>",
    "KING": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><line x1='32' y1='6' x2='32' y2='18' stroke='%23ffffff' stroke-width='2.8'/><line x1='26' y1='12' x2='38' y2='12' stroke='%23ffffff' stroke-width='2.8'/><polygon points='16,46 14,24 25,31 32,20 39,31 50,24 48,46' fill='none' stroke='%23a855f7' stroke-width='2.5'/><rect x='15' y='49' width='34' height='5' fill='none' stroke='%23ffffff' stroke-width='2.2'/></svg>",
    "COMMLOCK": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect x='18' y='8' width='28' height='48' rx='3' fill='none' stroke='%23ffb703' stroke-width='2.5'/><rect x='22' y='13' width='20' height='15' fill='none' stroke='%2300f0ff' stroke-width='2'/><circle cx='26' cy='36' r='2.2' fill='%23ffffff'/><circle cx='32' cy='36' r='2.2' fill='%23ffffff'/><circle cx='38' cy='36' r='2.2' fill='%23ff2a54'/><rect x='23' y='44' width='18' height='6' fill='none' stroke='%23ffffff' stroke-width='1.8'/></svg>"
}

# ==============================================================================
# 3. CSS MASTER BLUEPRINT — SPACE: 1999 SEASON 1 + CYBERPUNK CHESSBOARD
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800&family=JetBrains+Mono:wght@500;600;700&family=Michroma&family=Orbitron:wght@600;700;800;900&family=Share+Tech+Mono&display=swap');

header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], #MainMenu, footer {
    display: none !important; visibility: hidden !important; height: 0 !important;
}

.stApp {
    background-color: #030508 !important;
    background-image: 
        radial-gradient(circle at 50% 0%, rgba(255, 183, 3, 0.08) 0%, transparent 62%),
        linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px) !important;
    background-size: 100% 100%, 36px 36px, 36px 36px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

.block-container {
    padding-top: 0.7rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1080px !important;
}

div[data-testid="stVerticalBlock"] > div {
    gap: 0.25rem !important;
}

@keyframes holographicSweep {
    0% { background-position: -220% 0, 0 0; }
    100% { background-position: 220% 0, 0 0; }
}

@keyframes totemFloat {
    0%, 100% {
        filter: drop-shadow(0 0 6px rgba(255, 183, 3, 0.85)) drop-shadow(0 0 12px rgba(0, 240, 255, 0.4));
        transform: translateY(0px) scale(1);
    }
    50% {
        filter: drop-shadow(0 0 12px rgba(0, 240, 255, 0.95)) drop-shadow(0 0 20px rgba(255, 42, 84, 0.6));
        transform: translateY(-3px) scale(1.05);
    }
}

@keyframes alphaBlink {
    0%, 49% { opacity: 1; }
    50%, 100% { opacity: 0.25; }
}

/* SPACE 1999 SEASON 1 TOP DIAGNOSTIC INSERT STRIP */
.alpha-1999-strip {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #070a10;
    border: 1px solid #263248;
    border-left: 8px solid #ffb703;
    border-right: 8px solid #ff5500;
    padding: 5px 12px;
    margin-bottom: 6px;
    font-family: 'Michroma', 'Orbitron', sans-serif;
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    color: #fef08a;
    text-transform: uppercase;
}
.alpha-pill-amber {
    background: #ffb703;
    color: #000000;
    font-weight: 900;
    padding: 2px 8px;
    border-radius: 1px;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    box-shadow: 0 0 10px rgba(255, 183, 3, 0.7);
}
.alpha-pill-white {
    background: #f8fafc;
    color: #000000;
    font-weight: 900;
    padding: 2px 8px;
    border-radius: 1px;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
}
.alpha-pill-red {
    background: #ff2a54;
    color: #ffffff;
    font-weight: 900;
    padding: 2px 8px;
    border-radius: 1px;
    font-size: 0.58rem;
    letter-spacing: 0.12em;
    animation: alphaBlink 1.6s infinite;
}

/* WAFER DIGITAL TUBES */
.wafer-housing {
    display: inline-flex; align-items: center; background: #070401;
    border: 1.5px solid #522d09; border-radius: 3px; padding: 2px 5px; gap: 2px;
}
.wafer-tube {
    position: relative; width: 17px; height: 25px;
    background: radial-gradient(circle, rgba(251, 191, 36, 0.12) 0%, rgba(8, 5, 2, 0.96) 80%);
    border: 1px solid #3b2006; border-radius: 2px;
    display: inline-flex; align-items: center; justify-content: center;
}
.wafer-ghost { position: absolute; font-family: 'Share Tech Mono', monospace; font-size: 1.12rem; color: rgba(245, 158, 11, 0.03); }
.wafer-digit { position: relative; font-family: 'Share Tech Mono', monospace; font-size: 1.12rem; font-weight: 700; color: #fef08a; text-shadow: 0 0 6px #f59e0b; }
.wafer-unit { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #f59e0b; margin-left: 3px; font-weight: 700; }

/* MAIN MISSION HEADER DECK */
.apex-deck {
    background: linear-gradient(180deg, #0e131d 0%, #05080f 100%);
    border: 1.5px solid #283750;
    border-top: 3px solid #ffb703;
    border-bottom: 2px solid #00f0ff;
    border-radius: 4px;
    padding: 10px 16px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}
.apex-title {
    font-family: 'Michroma', 'Orbitron', sans-serif;
    font-size: 0.98rem;
    font-weight: 900;
    letter-spacing: 0.12em;
    color: #ffffff;
}
.apex-title span { color: #ffb703; text-shadow: 0 0 12px rgba(255, 183, 3, 0.65); }
.apex-sub { font-family: 'Share Tech Mono', monospace; font-size: 0.70rem; color: #38bdf8; letter-spacing: 0.06em; margin-top: 4px; }

/* WEATHER & LUNAR TELEMETRY STRIP */
.meteo-strip { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-bottom: 10px; }
.meteo-box {
    background: #060a12; border: 1px solid #1e293b; border-left: 3px solid #ffb703;
    border-radius: 3px; padding: 5px 8px; display: flex; justify-content: space-between; align-items: center;
}

/* TRUE 216px GEOMETRIC SQUARES WITH EMBEDDED TOTEMS */
div.stButton > button[kind="primary"] {
    background-image: 
        linear-gradient(115deg, transparent 35%, rgba(255, 255, 255, 0.08) 50%, transparent 65%),
        linear-gradient(145deg, #1b0a14 0%, #0a101d 100%) !important;
    background-size: 240% 100%, 100% 100% !important;
    animation: holographicSweep 5.5s infinite linear !important;
    border: 1px solid #1e293b !important;
    border-left: 6px solid #ff2a54 !important;
    border-top: 2px solid #ff2a54aa !important;
    border-radius: 4px !important;
    height: 216px !important;
    min-height: 216px !important;
    max-height: 216px !important;
    width: 100% !important;
    padding: 10px 6px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: center !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.75), inset 0 0 18px rgba(255, 42, 84, 0.12) !important;
    margin: 0 !important;
    position: relative !important;
}
div.stButton > button[kind="primary"]::before {
    content: "";
    display: block;
    width: 52px;
    height: 52px;
    margin-bottom: 8px;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    animation: totemFloat 4.2s ease-in-out infinite;
    flex-shrink: 0;
}
div.stButton > button[kind="primary"]:hover {
    filter: brightness(1.3) !important;
    border-color: #ffffff !important;
    transform: translateY(-2px) !important;
}
div.stButton > button[kind="primary"] div,
div.stButton > button[kind="primary"] span,
div.stButton > button[kind="primary"] p {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.96rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    letter-spacing: 0.04em !important;
    line-height: 1.38 !important;
    white-space: pre-line !important;
    overflow: visible !important;
    text-overflow: clip !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
    text-align: center !important;
    text-transform: uppercase !important;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.35) !important;
    margin: 0 !important;
    max-width: 100% !important;
}

div[class*="st-key-sq_CYAN_"] button[kind="primary"] {
    background-image: 
        linear-gradient(115deg, transparent 35%, rgba(0, 240, 255, 0.10) 50%, transparent 65%),
        linear-gradient(145deg, #061b2b 0%, #09101d 100%) !important;
    border-left: 6px solid #00f0ff !important; border-top: 2px solid #00f0ffaa !important;
}
div[class*="st-key-sq_AMBER_"] button[kind="primary"] {
    background-image: 
        linear-gradient(115deg, transparent 35%, rgba(255, 183, 3, 0.12) 50%, transparent 65%),
        linear-gradient(145deg, #241705 0%, #09101d 100%) !important;
    border-left: 6px solid #ffb703 !important; border-top: 2px solid #ffb703aa !important;
}
div[class*="st-key-sq_EMERALD_"] button[kind="primary"] {
    background-image: 
        linear-gradient(115deg, transparent 35%, rgba(0, 255, 157, 0.10) 50%, transparent 65%),
        linear-gradient(145deg, #052017 0%, #09101d 100%) !important;
    border-left: 6px solid #00ff9d !important; border-top: 2px solid #00ff9daa !important;
}
div[class*="st-key-sq_PURPLE_"] button[kind="primary"] {
    background-image: 
        linear-gradient(115deg, transparent 35%, rgba(168, 85, 247, 0.12) 50%, transparent 65%),
        linear-gradient(145deg, #190d2e 0%, #09101d 100%) !important;
    border-left: 6px solid #a855f7 !important; border-top: 2px solid #a855f7aa !important;
}

/* THE 5 INTERNAL ROWS + CLOSE BUTTON */
div.stButton > button[kind="secondary"] {
    background: #0b1523 !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e3a5f !important;
    border-left: 4px solid #ffb703 !important;
    border-radius: 3px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.74rem !important;
    padding: 0px 10px !important;
    height: 32px !important;
    min-height: 32px !important;
    max-height: 32px !important;
    margin: 0 !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
div.stButton > button[kind="secondary"]:hover {
    background: #1c2b42 !important;
    border-color: #ffb703 !important;
    color: #ffffff !important;
}

/* RIGHT TOWER */
.right-tower {
    background: linear-gradient(180deg, #0d131f 0%, #060a11 100%);
    border: 1px solid #263854; border-top: 3px solid #ffb703;
    border-radius: 4px; padding: 10px;
}
.tower-header {
    font-family: 'Michroma', 'Orbitron', monospace; font-size: 0.64rem; font-weight: 800;
    color: #ffb703; letter-spacing: 0.1em; border-bottom: 1px solid #1e293b;
    padding-bottom: 5px; margin-bottom: 8px;
}
.qr-holo-box {
    background: #040811;
    border: 1.5px solid #ffb70388;
    border-radius: 4px;
    padding: 8px 6px;
    text-align: center;
    margin-top: 4px;
}
.qr-holo-box img {
    border: 2px solid #ffb703;
    border-radius: 3px;
    padding: 3px;
    background: #060b14;
}

@media (max-width: 768px) {
    .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    .meteo-strip { grid-template-columns: repeat(2, 1fr); }
    div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: column !important; gap: 10px !important; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        width: 100% !important; min-width: 100% !important; max-width: 100% !important; flex: 1 1 100% !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 6px !important;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        flex: 1 1 calc(33.33% - 4px) !important; min-width: calc(33.33% - 4px) !important; max-width: calc(33.33% - 4px) !important;
    }
    div.stButton > button[kind="primary"] { height: 122px !important; min-height: 122px !important; max-height: 122px !important; padding: 6px 2px !important; }
    div.stButton > button[kind="primary"]::before { width: 34px !important; height: 34px !important; margin-bottom: 5px !important; }
    div.stButton > button[kind="primary"] div, div.stButton > button[kind="primary"] span, div.stButton > button[kind="primary"] p {
        font-size: 0.62rem !important; letter-spacing: 0.02em !important; line-height: 1.25 !important;
    }
}
</style>
""", unsafe_allow_html=True)

totem_css_rules = "<style>"
for t_key, t_uri in TOTEM_LIBRARY.items():
    totem_css_rules += f'div[class*="st-key-sq_"][class*="_{t_key}_"] button[kind="primary"]::before {{ background-image: url("{t_uri}") !important; }}\n'
totem_css_rules += "</style>"
st.markdown(totem_css_rules, unsafe_allow_html=True)

# ==============================================================================
# 4. SESSION STATE INITIALIZATION
# ==============================================================================
if "init_alpha_1999" not in st.session_state:
    st.session_state.init_alpha_1999 = True
    st.session_state.expanded_sq_id = None
    st.session_state.opened_sq_id = None
    st.session_state.opened_row_num = None
    st.session_state.custom_squares = []

# ==============================================================================
# 5. SPACE: 1999 SEASON 1 DIAGNOSTIC STRIP & MAIN MISSION HEADER
# ==============================================================================
now_dt = get_italy_now()
days_list = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
sys_date_str = f"{days_list[now_dt.weekday()]} {now_dt.strftime('%d/%m/%Y')}"
sys_time_str = now_dt.strftime("%H:%M")

wafer_clock = render_wafer_number(sys_time_str)
wafer_sol = render_wafer_number("1999")

# Inserto autentico Stagione 1: Tasti retroilluminati Giallo Ambra / Bianco Latte / Allarme
st.markdown(
    "<div class='alpha-1999-strip'>"
    "<div><span class='alpha-pill-amber'>MOONBASE ALPHA</span> &nbsp;MAIN MISSION // COMPUTER X5-7 // COMMANDER KOENIG</div>"
    "<div style='display:flex;gap:8px;align-items:center;'>"
    "<span class='alpha-pill-white'>EAGLE FLEET: READY</span>"
    "<span class='alpha-pill-amber'>GRAVITY SHIELDS: ON</span>"
    "<span class='alpha-pill-red'>TELEMETRY LIVE</span>"
    "</div></div>",
    unsafe_allow_html=True
)

eagle_header_svg = (
    "<svg viewBox='0 0 80 48' width='56' height='36' style='animation:totemFloat 4s ease-in-out infinite;'>"
    "<polygon points='4,26 18,18 18,32' fill='none' stroke='#ffb703' stroke-width='2.2'/>"
    "<rect x='18' y='17' width='42' height='14' fill='none' stroke='#ffffff' stroke-width='2'/>"
    "<line x1='25' y1='17' x2='33' y2='31' stroke='#ffb703' stroke-width='1.8'/>"
    "<line x1='33' y1='17' x2='41' y2='31' stroke='#ffb703' stroke-width='1.8'/>"
    "<line x1='41' y1='17' x2='49' y2='31' stroke='#ffb703' stroke-width='1.8'/>"
    "<rect x='60' y='20' width='12' height='8' fill='none' stroke='#ff2a54' stroke-width='2.2'/>"
    "<rect x='20' y='33' width='10' height='6' fill='none' stroke='#00f0ff' stroke-width='2'/>"
    "<rect x='48' y='33' width='10' height='6' fill='none' stroke='#00f0ff' stroke-width='2'/>"
    "</svg>"
)

header_html = (
    f"<div class='apex-deck'>"
    f"<div style='display:flex;align-items:center;gap:12px;'>{eagle_header_svg}"
    f"<div><div class='apex-title'>BEMASK - <span>A.L.P.H.A. MAIN MISSION</span></div>"
    f"<div class='apex-sub'>SPACE: 1999 ARCHIVE | DATE: <b style='color:#ffb703;'>{sys_date_str}</b> | CENTRAL HUB</div></div></div>"
    f"<div style='display:flex;align-items:center;gap:14px;flex-wrap:wrap;'>"
    f"<div style='display:flex;align-items:center;gap:6px;'><span style='font-family:Share Tech Mono,monospace;font-size:0.72rem;color:#ffb703;'>ALPHA TIME:</span>{wafer_clock}</div>"
    f"<div style='display:flex;align-items:center;gap:6px;'><span style='font-family:Share Tech Mono,monospace;font-size:0.72rem;color:#00f0ff;'>SECTOR:</span>{wafer_sol}</div>"
    f"</div></div>"
)
st.markdown(header_html, unsafe_allow_html=True)

forecast_5d = fetch_alpha_weather()
m_html = "<div class='meteo-strip'>"
for d in forecast_5d:
    m_html += (
        f"<div class='meteo-box' style='border-left-color:{d['col']};'>"
        f"<div><div style='font-family:Orbitron,monospace;font-size:0.65rem;font-weight:800;color:#fff;'>{d['day']} · {d['tmax']}°C</div>"
        f"<div style='font-family:JetBrains Mono,monospace;font-size:0.58rem;color:{d['col']};font-weight:700;'>{d['hint']}</div></div>"
        f"<div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#94a3b8;'>{d['rain']}%</div></div>"
    )
m_html += "</div>"
st.markdown(m_html, unsafe_allow_html=True)

# ==============================================================================
# 6. THE 6 COMMAND SQUARES OF MOONBASE A.L.P.H.A.
# ==============================================================================
base_squares = [
    {
        "id": "SQ01", "theme": "AMBER", "totem": "EAGLE",
        "title": "01\nFRONT OFFICE",
        "url": "https://boschetto.streamlit.app",
        "rows": ["1. Launch Boschetto PMS", "2. Check-In / Arrivals", "3. Room Rack Status", "4. Shift Handover", "5. Night Audit"]
    },
    {
        "id": "SQ02", "theme": "EMERALD", "totem": "QUEEN",
        "title": "02\nLAZERS F&B",
        "url": "https://bemask-sovereign-lazers.streamlit.app",
        "rows": ["1. Launch Lazers F&B", "2. Bar & Sommelier", "3. Restaurant Margin", "4. Menu Engineering", "5. Inventory Sync"]
    },
    {
        "id": "SQ03", "theme": "CYAN", "totem": "BISHOP",
        "title": "03\nHOUSEKEEPING",
        "url": "https://boschetto.streamlit.app",
        "rows": ["1. Floor Status Grid", "2. Priority Rooms", "3. Linen & Minibar", "4. Staff Assignment", "5. Inspection Log"]
    },
    {
        "id": "SQ04", "theme": "PURPLE", "totem": "COMMLOCK",
        "title": "04\nCONCIERGE",
        "url": "https://boschetto.streamlit.app",
        "rows": ["1. Guest Commlock", "2. Beach & Umb. Map", "3. E-Bike & Tours", "4. VIP Transfers", "5. Local Events"]
    },
    {
        "id": "SQ05", "theme": "CYAN", "totem": "KNIGHT",
        "title": "05\nS.K.A. TECH",
        "url": "https://sovereign-kinetic-architecture.streamlit.app",
        "rows": ["1. Launch S.K.A. Core", "2. HACCP Telemetry", "3. Energy & Boilers", "4. Maintenance Tickets", "5. Safety Shields"]
    },
    {
        "id": "SQ06", "theme": "RED", "totem": "ROOK",
        "title": "06\nSOVEREIGN APEX",
        "url": "https://sovereign-apex.streamlit.app",
        "rows": ["1. Launch Sovereign Apex", "2. 7 Tiers x 24 Bands", "3. Fast Quote Engine", "4. Waterfall Floor", "5. PMS CSV Bridge"]
    }
]

all_squares = base_squares + st.session_state.custom_squares

# ==============================================================================
# 7. CHESSBOARD + SPACE: 1999 SOUND SYNTHESIZER & QR DOCK
# ==============================================================================
if st.session_state.opened_sq_id is None:
    col_grid, col_tower = st.columns([2.85, 1.05], gap="small")

    with col_grid:
        tot_sq = len(all_squares)
        rows_count = (tot_sq + 2) // 3
        for r_i in range(rows_count):
            cols = st.columns(3, gap="small")
            for c_i in range(3):
                idx = r_i * 3 + c_i
                if idx < tot_sq:
                    sq = all_squares[idx]
                    sid = sq["id"]
                    theme = sq["theme"]
                    t_icon = sq.get("totem", "EAGLE")
                    with cols[c_i]:
                        if st.session_state.expanded_sq_id == sid:
                            for r_num, r_txt in enumerate(sq["rows"], 1):
                                if st.button(r_txt, key=f"r5_{sid}_{r_num}", type="secondary", use_container_width=True):
                                    st.session_state.opened_sq_id = sid
                                    st.session_state.opened_row_num = r_num
                                    st.rerun()
                            if st.button("✖ CLOSE", key=f"cl_{sid}", type="secondary", use_container_width=True):
                                st.session_state.expanded_sq_id = None
                                st.rerun()
                        else:
                            if st.button(sq["title"], key=f"sq_{theme}_{t_icon}_{sid}", type="primary", use_container_width=True):
                                st.session_state.expanded_sq_id = sid
                                st.rerun()

    with col_tower:
        # SINTETIZZATORE AUDIO AUTENTICO "MOONBASE ALPHA 1975" (WEB AUDIO API)
        sound_console_html = """
        <div style="background:#080c14;border:1.5px solid #ffb703;border-top:4px solid #ffb703;border-radius:4px;padding:8px;font-family:monospace;color:#fff;">
            <div style="font-size:10px;font-weight:900;color:#ffb703;letter-spacing:1.5px;margin-bottom:6px;border-bottom:1px solid #263248;padding-bottom:4px;display:flex;justify-content:space-between;">
                <span>ALPHA COMPUTER AUDIO</span>
                <span id="st-led" style="color:#00ff9d;">STANDBY</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:5px;">
                <button onclick="toggleTelemetry()" id="btn-tel" style="background:#ffb703;color:#000;border:none;padding:7px 4px;font-weight:900;font-size:10px;cursor:pointer;border-radius:2px;letter-spacing:0.5px;">
                    ▶ TELEMETRY LOOP
                </button>
                <button onclick="playCommlock()" style="background:#e2e8f0;color:#000;border:none;padding:7px 4px;font-weight:900;font-size:10px;cursor:pointer;border-radius:2px;letter-spacing:0.5px;">
                    ◈ COMMLOCK BEEP
                </button>
            </div>
            <button onclick="playRedAlert()" style="width:100%;background:#ff2a54;color:#fff;border:none;padding:6px 4px;font-weight:900;font-size:10px;cursor:pointer;border-radius:2px;letter-spacing:1px;">
                ▲ MOONBASE RED ALERT
            </button>
        </div>
        <script>
        let audioCtx = null;
        let telInterval = null;
        let isPlayingTel = false;

        function initCtx() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        function singleAlphaBlip() {
            initCtx();
            const now = audioCtx.currentTime;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            // Space 1999 Main Computer frequencies (classic 1975 modular bleeps)
            const freqs = [980, 1240, 1480, 1760, 2093, 2349, 2637, 1108, 1567];
            const f = freqs[Math.floor(Math.random() * freqs.length)];
            osc.type = Math.random() > 0.35 ? 'square' : 'triangle';
            osc.frequency.setValueAtTime(f, now);

            gain.gain.setValueAtTime(0.06, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.055);

            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.06);
        }

        function toggleTelemetry() {
            initCtx();
            const btn = document.getElementById('btn-tel');
            const led = document.getElementById('st-led');
            if (!isPlayingTel) {
                isPlayingTel = true;
                btn.innerText = '■ STOP TELEMETRY';
                btn.style.background = '#00f0ff';
                led.innerText = 'ACTIVE 1999';
                led.style.color = '#00f0ff';
                telInterval = setInterval(() => {
                    singleAlphaBlip();
                    if (Math.random() > 0.45) {
                        setTimeout(singleAlphaBlip, 65);
                    }
                }, 135);
            } else {
                isPlayingTel = false;
                clearInterval(telInterval);
                btn.innerText = '▶ TELEMETRY LOOP';
                btn.style.background = '#ffb703';
                led.innerText = 'STANDBY';
                led.style.color = '#00ff9d';
            }
        }

        function playCommlock() {
            initCtx();
            const notes = [1975, 2637, 1975, 3135];
            notes.forEach((n, idx) => {
                const now = audioCtx.currentTime + (idx * 0.075);
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(n, now);
                gain.gain.setValueAtTime(0.11, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.065);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.07);
            });
        }

        function playRedAlert() {
            initCtx();
            for (let i = 0; i < 3; i++) {
                const start = audioCtx.currentTime + (i * 0.38);
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(440, start);
                osc.frequency.linearRampToValueAtTime(880, start + 0.28);
                gain.gain.setValueAtTime(0.09, start);
                gain.gain.exponentialRampToValueAtTime(0.001, start + 0.34);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(start);
                osc.stop(start + 0.35);
            }
        }
        </script>
        """
        components.html(sound_console_html, height=122)

        qr_sel = st.selectbox(
            "QR TARGET MODULE:",
            ["06 SOVEREIGN APEX", "01 BOSCHETTO PMS", "05 S.K.A. TECH", "02 LAZERS F&B"],
            label_visibility="collapsed"
        )
        qr_map = {
            "06 SOVEREIGN APEX": "https://sovereign-apex.streamlit.app",
            "01 BOSCHETTO PMS": "https://boschetto.streamlit.app",
            "05 S.K.A. TECH": "https://sovereign-kinetic-architecture.streamlit.app",
            "02 LAZERS F&B": "https://bemask-sovereign-lazers.streamlit.app"
        }
        target_qr_url = qr_map[qr_sel]
        encoded_url = urllib.parse.quote(target_qr_url, safe="")
        qr_img_src = f"https://api.qrserver.com/v1/create-qr-code/?size=130x130&color=ffb703&bgcolor=060b14&margin=2&data={encoded_url}"

        tower_html = (
            f"<div class='right-tower'>"
            f"<div class='tower-header'>COMMLOCK // QR TELEPORT</div>"
            f"<div class='qr-holo-box'>"
            f"<img src='{qr_img_src}' width='115' height='115' alt='QR Access'/>"
            f"<div style='font-family:Orbitron,monospace;font-size:0.62rem;font-weight:800;color:#ffb703;margin-top:5px;'>{qr_sel}</div>"
            f"<div style='font-family:Share Tech Mono,monospace;font-size:0.54rem;color:#94a3b8;'>{target_qr_url.replace('https://', '')}</div>"
            f"</div>"
            f"</div>"
        )
        st.markdown(tower_html, unsafe_allow_html=True)

        with st.expander("+ ADD EAGLE NODE"):
            new_idx = len(all_squares) + 1
            new_t1 = st.text_input("Sector Number", value=f"0{new_idx}")
            new_t2 = st.text_input("Sector Name", value="EAGLE HANGAR")
            new_totem = st.selectbox("Select Totem", ["EAGLE", "COMMLOCK", "ROOK", "KNIGHT", "QUEEN", "BISHOP", "KING"])
            new_th = st.selectbox("Color", ["AMBER", "CYAN", "EMERALD", "RED", "PURPLE"])
            if st.button("DEPLOY SECTOR", use_container_width=True):
                st.session_state.custom_squares.append({
                    "id": f"SQ0{new_idx}", "theme": new_th, "totem": new_totem,
                    "title": f"{new_t1}\n{new_t2}", "url": "https://sovereign-apex.streamlit.app",
                    "rows": ["1. Launch Sector", "2. Telemetry", "3. Crew Log", "4. Config", "5. Sync"]
                })
                st.rerun()

# ==============================================================================
# 8. INTERNAL SECTOR VIEW & DIRECT LAUNCH BRIDGE
# ==============================================================================
else:
    sid = st.session_state.opened_sq_id
    r_num = st.session_state.opened_row_num
    sq_obj = next(x for x in all_squares if x["id"] == sid)
    clean_name = sq_obj["title"].replace("\n", " - ")
    row_label = sq_obj["rows"][r_num - 1]
    target_url = sq_obj.get("url", "https://sovereign-apex.streamlit.app")

    if st.button(f"⬅ RETURN TO MAIN MISSION ({clean_name})", type="secondary", use_container_width=True):
        st.session_state.opened_sq_id = None
        st.session_state.expanded_sq_id = None
        st.rerun()

    st.markdown(f"#### {clean_name} // {row_label}")
    st.markdown(
        f"<div style='background:#080d18;border:1.5px solid #ffb703;border-left:6px solid #ffb703;padding:18px;border-radius:4px;margin-top:10px;'>"
        f"<div style='font-family:Michroma,Orbitron,sans-serif;font-size:0.85rem;color:#ffb703;'>DIRECT HYPER-BRIDGE READY</div>"
        f"<div style='font-family:Share Tech Mono,monospace;font-size:0.8rem;color:#e2e8f0;margin:8px 0 14px 0;'>Target Module: <b>{target_url}</b></div>"
        f"<a href='{target_url}' target='_blank' style='display:inline-block;background:#ffb703;color:#000;font-family:Orbitron,sans-serif;font-weight:900;padding:10px 20px;border-radius:3px;text-decoration:none;letter-spacing:0.08em;'>"
        f"🚀 OPEN {clean_name} IN FULL SCREEN</a>"
        f"</div>",
        unsafe_allow_html=True
    )
