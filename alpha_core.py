import os
import json
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# ==============================================================================
# BEMASK - MOONBASE A.L.P.H.A. // MAIN MISSION (MONUMENTAL CORE 1 -> 2^9)
# Space: 1999 Command Matrix | 512 Binary States | EMS-1975 Synth | QR Commlock
# ==============================================================================

st.set_page_config(
    page_title="BEMASK - MOONBASE A.L.P.H.A. // MAIN MISSION",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. BLINDAGGIO TOTALE SESSION STATE (Anti-AttributeError & Anti-KeyError) ---
def init_monumental_state():
    defaults = {
        "active_bits_9": [True, True, True, True, True, True, False, False, False],
        "custom_squares": [],
        "expanded_node": None,
        "selected_sub": None,
        "pin_code": "9999",
        "visitors_log": 34,
        "last_access": datetime.now().strftime("%H:%M"),
        "synth_mode": "READY",
        "rop_cons_gg": 45,
        "rop_lead_gg": 2,
        "rop_stock": 490,
        "bocche_96h": 137
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_monumental_state()

# --- 2. ICONE VETTORIALI NEON SVG (Identiche alla tua foto sul tablet) ---
SVG_ICONS = {
    "01": """<svg width="46" height="32" viewBox="0 0 64 40" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M6 22L18 14H46L58 22L46 26H18L6 22Z" stroke="#F59E0B" stroke-width="2.5" fill="#2A1C08"/>
             <rect x="24" y="16" width="16" height="8" stroke="#38BDF8" stroke-width="2" fill="#06B6D4"/>
             <path d="M2 20L12 16V24L2 20Z" fill="#EF4444"/><path d="M62 20L52 16V24L62 20Z" fill="#10B981"/>
             </svg>""",
    "02": """<svg width="42" height="36" viewBox="0 0 48 42" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M6 34L10 12L19 22L24 8L29 22L38 12L42 34H6Z" stroke="#10B981" stroke-width="2.5" fill="rgba(16,185,129,0.18)"/>
             <line x1="6" y1="38" x2="42" y2="38" stroke="#34D399" stroke-width="3"/>
             </svg>""",
    "03": """<svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M18 6H26V13L31 19V38H13V19L18 13V6Z" stroke="#38BDF8" stroke-width="2.5" fill="rgba(56,189,248,0.18)"/>
             <rect x="16" y="23" width="12" height="9" stroke="#E0F2FE" stroke-width="1.8"/>
             </svg>""",
    "04": """<svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <rect x="14" y="6" width="16" height="32" rx="2" stroke="#A855F7" stroke-width="2.5" fill="rgba(168,85,247,0.18)"/>
             <rect x="17" y="10" width="10" height="8" stroke="#38BDF8" stroke-width="2"/>
             <line x1="17" y1="26" x2="27" y2="26" stroke="#F59E0B" stroke-width="2.5"/>
             </svg>""",
    "05": """<svg width="42" height="38" viewBox="0 0 48 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M24 6V14M20 10H28" stroke="#F43F5E" stroke-width="2.5"/>
             <path d="M8 36L12 18L20 25L24 15L28 25L36 18L40 36H8Z" stroke="#F43F5E" stroke-width="2.5" fill="rgba(244,63,94,0.18)"/>
             </svg>""",
    "06": """<svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M12 36H32L29 22L31 14H13L15 22L12 36Z" stroke="#F59E0B" stroke-width="2.5" fill="rgba(245,158,11,0.18)"/>
             <circle cx="22" cy="10" r="4" stroke="#FDE047" stroke-width="2"/>
             </svg>""",
    "07": """<svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <rect x="8" y="10" width="28" height="24" stroke="#10B981" stroke-width="2.5" fill="rgba(16,185,129,0.18)"/>
             <path d="M14 22L20 28L30 16" stroke="#34D399" stroke-width="3"/>
             </svg>""",
    "08": """<svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M22 6L36 12V22C36 31 22 38 22 38C22 38 8 31 8 22V12L22 6Z" stroke="#06B6D4" stroke-width="2.5" fill="rgba(6,182,212,0.18)"/>
             </svg>""",
    "09": """<svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <polygon points="24,4 10,24 22,24 20,40 34,20 22,20" stroke="#F59E0B" stroke-width="2.5" fill="rgba(245,158,11,0.22)"/>
             </svg>"""
}

# --- 3. ARCHITETTURA DEI 9 VETTORI PRIMARI (1 -> 2^9 = 512 STATI) ---
BASE_VECTORS = [
    {
        "bit": 0, "code": "01", "short": "01 FRONT", "name": "FRONT & APEX",
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #3D2B14 0%, #14161D 78%)",
        "kpi": "OCC: 88% | ADR: € 165 | REVPAR: € 145", "url": "https://bemask-sovereign-zero.streamlit.app",
        "subs": ["1. Dynamic Pricing & Matrix", "2. Controllo Allotment & OTA", "3. Check-in & Upselling", "4. Forecast 30 Giorni", "5. Registro Cassa Front"]
    },
    {
        "bit": 1, "code": "02", "short": "02 BEV", "name": "LAZERS BEV",
        "border": "#10B981", "glow": "rgba(16, 185, 129, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #113A32 0%, #12181F 78%)",
        "kpi": "POURING: 21% | MARGINE CANTINA: +79%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Pouring Calici & Vini", "2. Spinta Aperitivi Meteo", "3. Margine Bottiglie", "4. Usura Cristalleria", "5. Inventario Cantina Live"]
    },
    {
        "bit": 2, "code": "03", "short": "03 FOOD", "name": "LAZERS FOOD",
        "border": "#38BDF8", "glow": "rgba(56, 189, 248, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #13334C 0%, #121720 78%)",
        "kpi": "COPERTI: 84/105 | FOOD COST: 28.5%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Capienza Sala & Cucina", "2. Scorporo Quote HB / FB", "3. Sfridi & Rese Carni", "4. Semaforo TheFork Zero-Fee", "5. Floor Industriale Pasto"]
    },
    {
        "bit": 3, "code": "04", "short": "04 BEACH", "name": "BEACH & POOL",
        "border": "#A855F7", "glow": "rgba(168, 85, 247, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #2B244D 0%, #141522 78%)",
        "kpi": "SATURAZIONE LIDO: 92% | VENTO: 11 KT", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Mappa Ombrelloni & Cabine", "2. Soglia Vento Grounding", "3. Light Lunch all'Ombrellone", "4. Presidio Bagnini", "5. Chiusura Cassa Lido"]
    },
    {
        "bit": 4, "code": "05", "short": "05 SPA", "name": "SPA & AYURVEDA",
        "border": "#F43F5E", "glow": "rgba(244, 63, 94, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #3F1D2B 0%, #16141C 78%)",
        "kpi": "SLOT CABINE: 14/16 | FALLBACK PIOGGIA ON", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Conversione Pioggia (S1/S2)", "2. Agenda Cabine & Massaggi", "3. Percorso Private Spa VIP", "4. Vendita Linea Cosmetica", "5. Turni Operatori"]
    },
    {
        "bit": 5, "code": "06", "short": "06 SKA", "name": "S.K.A. & ROOMS",
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #382B19 0%, #15161C 78%)",
        "kpi": "CAMERE PRONTE: 58/60 | SEGNALAZIONI: 0", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Stato Pulizia Camere", "2. Ticket Manutenzione", "3. Presidio Brigata Piani", "4. Dotazioni & Biancheria", "5. Ispezione Governante"]
    },
    {
        "bit": 6, "code": "07", "short": "07 ACQUISTO", "name": "PUNTO ACQUISTO & ROP",
        "border": "#10B981", "glow": "rgba(16, 185, 129, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #13392E 0%, #12171D 78%)",
        "kpi": "ROP: SCORTA OK | SCUDO AUTONOMIA: 96H", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Calcolatore Punto Riordino (ROP)", "2. Scudo Dispensa 96 Ore", "3. Lead Time Fornitori", "4. Controllo Fatture XML", "5. Lista Ordini Urgenti"]
    },
    {
        "bit": 7, "code": "08", "short": "08 HACCP", "name": "HACCP & REGISTRO ASL",
        "border": "#06B6D4", "glow": "rgba(6, 182, 212, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #123440 0%, #12171E 78%)",
        "kpi": "CELLE FRIGO: 21/21 OK | FIRME PIN: 6", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Temperature Celle (-18°C / +4°C)", "2. Firma Digitale con PIN", "3. Lotti & Sgocciolato", "4. Sanificazione Cucina", "5. Scarica Stampa ASL (.HTML)"]
    },
    {
        "bit": 8, "code": "09", "short": "09 GOPPAR", "name": "OPEX / CAPEX & P.IVA",
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #3B2816 0%, #14161D 78%)",
        "kpi": "MOL NETTO OGGI: € 4.820 | GOP: +34%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Split Multi-P.IVA Casa Madre", "2. OPEX vs CAPEX Real-Time", "3. Incidenza Costo Brigate", "4. Cashflow Consolidato", "5. Ponte Dati Revisore"]
    }
]

WEATHER_5_DAYS = [
    {"day": "SOL 08 · 19°C", "status": "NOMINAL ORBIT", "pct": "8%", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "SUN 08/11 · 17°C", "status": "NOMINAL ORBIT", "pct": "14%", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "MON 09/11 · 17°C", "status": "SOLAR STORM", "pct": "91%", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "TUE 10/11 · 20°C", "status": "SOLAR STORM", "pct": "94%", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "WED 11/11 · 21°C", "status": "NOMINAL ORBIT", "pct": "22%", "border": "#38BDF8", "text_col": "#F59E0B"},
]

# --- 4. SINTETIZZATORE AUDIO REALE WEBAUDIO (EMS SYNTHI 1975) ---
def play_ems_synth(effect_type):
    js_code = f"""
    <script>
    (function() {{
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        const now = ctx.currentTime;
        if ("{effect_type}" === "burst") {{
            const freqs = [523.25, 659.25, 783.99, 1046.50, 880.0, 1174.66];
            freqs.forEach((f, i) => {{
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sawtooth";
                osc.frequency.setValueAtTime(f, now + i * 0.06);
                gain.gain.setValueAtTime(0.08, now + i * 0.06);
                gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.06 + 0.055);
                osc.connect(gain); gain.connect(ctx.destination);
                osc.start(now + i * 0.06); osc.stop(now + i * 0.06 + 0.06);
            }});
        }} else if ("{effect_type}" === "commlock") {{
            [987.77, 1318.51].forEach((f, i) => {{
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(f, now + i * 0.11);
                gain.gain.setValueAtTime(0.12, now + i * 0.11);
                gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.11 + 0.10);
                osc.connect(gain); gain.connect(ctx.destination);
                osc.start(now + i * 0.11); osc.stop(now + i * 0.11 + 0.11);
            }});
        }} else if ("{effect_type}" === "klaxon") {{
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = "square";
            osc.frequency.setValueAtTime(440, now);
            osc.frequency.linearRampToValueAtTime(880, now + 0.25);
            osc.frequency.linearRampToValueAtTime(440, now + 0.50);
            gain.gain.setValueAtTime(0.10, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.52);
            osc.connect(gain); gain.connect(ctx.destination);
            osc.start(now); osc.stop(now + 0.52);
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0)

# --- 5. CSS MONUMENTALE MOONBASE A.L.P.H.A. ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800;900&family=Share+Tech+Mono&display=swap');

.stApp { background-color: #12151B; color: #F8FAFC; font-family: 'Orbitron', sans-serif; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 0.7rem; max-width: 96%; }

/* TOP KOENIG STRIP */
.koenig-strip {
    background-color: #1A1E26; border: 1px solid #323946; border-left: 5px solid #F59E0B;
    padding: 8px 14px; margin-bottom: 10px; border-radius: 2px;
}
.badge-amber { background-color: #F59E0B; color: #0B0E14; font-weight: 900; font-size: 10px; padding: 3px 8px; margin-right: 8px; letter-spacing: 0.8px; display: inline-block; }
.badge-white { background-color: #F1F5F9; color: #0F172A; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; }
.badge-red { background-color: #7F1D1D; border: 1px solid #EF4444; color: #FCA5A5; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; }

/* MAIN ALPHA MISSION BAR */
.mission-bar {
    background: linear-gradient(90deg, #161C24 0%, #192530 100%);
    border: 1px solid #2D3D4E; border-left: 4px solid #38BDF8;
    padding: 12px 18px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;
}
.mission-title { font-size: 19px; font-weight: 900; color: #FFFFFF; letter-spacing: 1.5px; }
.mission-sub { font-size: 10px; color: #38BDF8; font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; margin-top: 2px; }
.nixie-group { display: flex; align-items: center; gap: 10px; }
.nixie-label { font-size: 10px; color: #94A3B8; font-weight: 700; letter-spacing: 1px; }
.nixie-digits {
    background-color: #0D1015; border: 1px solid #F59E0B; color: #F59E0B;
    font-family: 'Share Tech Mono', monospace; font-size: 18px; font-weight: 900;
    padding: 3px 10px; letter-spacing: 3px; border-radius: 2px;
    box-shadow: inset 0 0 8px rgba(245, 158, 11, 0.4);
}

/* WEATHER STRIP */
.weather-card {
    background-color: #161A22; border: 1px solid #2B3340;
    padding: 8px 12px; border-radius: 2px; margin-bottom: 10px;
}
.w-day { font-size: 10px; font-weight: 900; color: #FFFFFF; letter-spacing: 0.6px; }
.w-status { font-size: 9px; font-weight: 800; margin-top: 3px; letter-spacing: 0.8px; }

/* KINETIC MONOLITH TILES (IDENTICHE ALLA FOTO TABLET) */
.alpha-tile {
    height: 195px; border-radius: 3px; padding: 18px;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    text-align: center; position: relative; transition: all 0.24s ease;
    margin-bottom: -10px;
}
.alpha-tile:hover {
    transform: translateY(-4px) scale(1.01);
    filter: brightness(1.14);
}
.tile-code { font-size: 11px; font-weight: 800; color: #E2E8F0; margin-top: 12px; letter-spacing: 1.5px; }
.tile-name { font-size: 14px; font-weight: 900; color: #FFFFFF; letter-spacing: 1.2px; margin-top: 3px; }
.tile-kpi { font-size: 9px; font-family: 'Share Tech Mono', monospace; color: #CBD5E1; margin-top: 8px; opacity: 0.9; }

/* BOTTONI TATTICI SOTTO LE PIASTRELLE E NELLA FISARMONICA */
div.stButton > button {
    background-color: #1A212B !important; color: #F8FAFC !important;
    border: 1px solid #2F3E50 !important; border-radius: 2px !important;
    font-family: 'Orbitron', sans-serif !important; font-size: 10px !important;
    font-weight: 800 !important; letter-spacing: 1px !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    border-color: #F59E0B !important; color: #F59E0B !important;
    box-shadow: 0 0 14px rgba(245, 158, 11, 0.35) !important;
}

/* PANNELLO DESTRO: EMS-1975 SYNTH + QR COMMLOCK */
.ems-panel {
    background-color: #161A22; border: 2px solid #F59E0B;
    padding: 12px; border-radius: 3px; margin-bottom: 10px;
}
.commlock-panel {
    background-color: #161A22; border: 1px solid #F59E0B;
    padding: 14px; border-radius: 3px; text-align: center;
}
</style>
""", unsafe_allow_html=True)

# --- 6. CALCOLO DINAMICO MATRICE BINARIA 1 -> 2^9 (512 COMBINAZIONI) ---
bits = st.session_state["active_bits_9"]
active_base = [v for i, v in enumerate(BASE_VECTORS) if bits[i]]
if not active_base:
    st.session_state["active_bits_9"][0] = True
    active_base = [BASE_VECTORS[0]]

all_squares = active_base + st.session_state["custom_squares"]
n_sectors = len(all_squares)
total_micro_modules = n_sectors * 5
binary_state_num = sum((1 << i) for i, b in enumerate(bits) if b)
binary_str = "".join(["1" if b else "0" for b in bits])
ora_attuale = datetime.now().strftime("%H:%M")

# --- 7. RENDER TOP KOENIG BAR + ALPHA HEADER + STRISCIA METEO 5 GIORNI ---
st.markdown(f"""
<div class="koenig-strip">
    <div>
        <span class="badge-amber">MOONBASE ALPHA</span>
        <span style="font-size:12px; font-weight:900; letter-spacing:1.2px; color:#FFFFFF;">
            MAIN MISSION // {total_micro_modules}-NODE COMMAND MATRIX // KOENIG
        </span>
    </div>
    <div style="margin-top:6px;">
        <span class="badge-white">{n_sectors} SECTORS X 5 MODULES</span>
        <span class="badge-amber">OPEX & CAPEX SPLIT</span>
        <span class="badge-red">{total_micro_modules} CHANNELS LIVE</span>
        <span class="badge-white">SCALABILITY: 1 → 2⁹ (STATE #{binary_state_num}/512)</span>
        <span class="badge-white">VISITORS: {st.session_state['visitors_log']}</span>
    </div>
</div>

<div class="mission-bar">
    <div style="display:flex; align-items:center; gap:14px;">
        <div>{SVG_ICONS["01"]}</div>
        <div>
            <div class="mission-title">BEMASK - A.L.P.H.A. MAIN MISSION</div>
            <div class="mission-sub">SPACE: 1999 COMMAND | DATE: {datetime.now().strftime('%a %d/%m/%Y').upper()} | {total_micro_modules} MICRO-MODULES | BIN: {binary_str}</div>
        </div>
    </div>
    <div class="nixie-group">
        <span class="nixie-label">ALPHA TIME:</span>
        <span class="nixie-digits">{ora_attuale}</span>
        <span class="nixie-label">MATRIX:</span>
        <span class="nixie-digits">{total_micro_modules:02d}</span>
    </div>
</div>
""", unsafe_allow_html=True)

w_cols = st.columns(5)
for idx, w in enumerate(WEATHER_5_DAYS):
    with w_cols[idx]:
        st.markdown(f"""
        <div class="weather-card" style="border-left: 3px solid {w['border']}; border-top: 1px solid {w['border']};">
            <div class="w-day">{w['day']} <span style="float:right; color:#94A3B8; font-family:'Share Tech Mono';">{w['pct']}</span></div>
            <div class="w-status" style="color:{w['text_col']};">{w['status']}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 8. SELETTORE SCALABILITÀ 1 -> 2^9 (DA 1 SINGOLO MODULO A 9 SETTORI) ---
with st.expander(f"🎛️ MATRICE MODULARE 1 → 2⁹ (Stato #{binary_state_num}/512 — Attiva da 1 a 9 Settori o Aggiungi Nodi)", expanded=False):
    sw_cols = st.columns(9)
    for i, vec in enumerate(BASE_VECTORS):
        with sw_cols[i]:
            toggled = st.toggle(vec["short"], value=st.session_state["active_bits_9"][i], key=f"tg_{i}")
            if toggled != st.session_state["active_bits_9"][i]:
                st.session_state["active_bits_9"][i] = toggled
                st.session_state["expanded_node"] = None
                st.rerun()

    pr1, pr2, pr3 = st.columns(3)
    if pr1.button("⚡ 1 NODO SINGOLO (2⁰ — B&B / Bar)", use_container_width=True):
        st.session_state["active_bits_9"] = [True] + [False]*8
        st.rerun()
    if pr2.button("🛸 6 SETTORI (30 Nodi — Assetto Tablet)", use_container_width=True):
        st.session_state["active_bits_9"] = [True, True, True, True, True, True, False, False, False]
        st.rerun()
    if pr3.button("🔥 9 SETTORI COMPLETI (2⁹ = 512 Stati — Full Resort)", use_container_width=True):
        st.session_state["active_bits_9"] = [True]*9
        st.rerun()

# --- 9. CORPO CENTRALE: MATRICE CINETICA (SINISTRA) + SYNTH & QR COMMLOCK (DESTRA) ---
col_left, col_right = st.columns([3.25, 1.15])

with col_left:
    # Se l'utente ha cliccato una delle 5 righe interne, apre la Consolle Operativa (es. Punto Acquisto ROP)
    if st.session_state["selected_sub"] is not None:
        sec_obj, sub_label = st.session_state["selected_sub"]
        b_back1, b_back2 = st.columns(2)
        if b_back1.button(f"← TORNA ALLE 5 RIGHE DI {sec_obj['name']}", use_container_width=True):
            st.session_state["selected_sub"] = None
            st.rerun()
        if b_back2.button("TORNA ALLA MATRICE PRINCIPALE", use_container_width=True):
            st.session_state["selected_sub"] = None
            st.session_state["expanded_node"] = None
            st.rerun()

        st.markdown(f"""
        <div style="background:#161C24; border:1px solid {sec_obj['border']}; border-left:5px solid {sec_obj['border']}; padding:18px; margin:10px 0;">
            <div style="font-size:11px; color:{sec_obj['border']}; font-family:'Share Tech Mono';">SETTORE {sec_obj['code']} // CONSOLLE ESECUTIVA</div>
            <div style="font-size:20px; font-weight:900; margin:4px 0;">{sec_obj['name']} — {sub_label}</div>
            <div style="font-size:12px; color:#38BDF8; font-family:'Share Tech Mono';">{sec_obj['kpi']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Calcolatore Punto Acquisto (ROP) + Scudo 96h sempre disponibile dentro i moduli
        c_rop1, c_rop2, c_rop3 = st.columns(3)
        st.session_state["rop_cons_gg"] = c_rop1.number_input("Consumo Giornaliero (Porzioni/Unità)", 1, 1000, st.session_state["rop_cons_gg"])
        st.session_state["rop_lead_gg"] = c_rop2.number_input("Giorni Consegna Fornitore (Lead Time)", 1, 30, st.session_state["rop_lead_gg"])
        st.session_state["rop_stock"] = c_rop3.number_input("Giacenza Attuale in Casa", 0, 5000, st.session_state["rop_stock"])

        scorta_sicurezza_96h = st.session_state["bocche_96h"] * 4
        punto_acquisto_rop = (st.session_state["rop_cons_gg"] * st.session_state["rop_lead_gg"]) + scorta_sicurezza_96h
        delta_stock = st.session_state["rop_stock"] - punto_acquisto_rop

        if delta_stock >= 0:
            st.success(f"🟢 PUNTO ACQUISTO (ROP): Soglia {punto_acquisto_rop} u. | Giacenza {st.session_state['rop_stock']} u. (+{delta_stock} u. sopra Scudo 96h)")
        else:
            st.error(f"🔴 ALLERTA PUNTO ACQUISTO (ROP): Soglia {punto_acquisto_rop} u. | Ordinare subito {abs(delta_stock)} unità al fornitore!")

        st.link_button(f"🚀 TELEPORT DIRETTO A {sec_obj['name']}", sec_obj["url"], use_container_width=True)

    else:
        # Griglia adattiva: 1 colonna se 1 solo modulo, 2 colonne se 2 o 4 moduli, altrimenti 3 colonne (come nella foto!)
        n_cols = 1 if n_sectors == 1 else (2 if n_sectors in [2, 4] else 3)
        for r in range(0, n_sectors, n_cols):
            row_cols = st.columns(n_cols)
            for c in range(n_cols):
                if r + c < n_sectors:
                    sq = all_squares[r + c]
                    code = sq["code"]
                    svg_icon = SVG_ICONS.get(code, SVG_ICONS["01"])
                    with row_cols[c]:
                        # Se la piastrella è cliccata, si apre a fisarmonica nelle 5 righe + X CHIUDI (Stile Boschetto Pro)
                        if st.session_state["expanded_node"] == code:
                            for sub_item in sq["subs"]:
                                if st.button(sub_item, key=f"sub_{code}_{sub_item}", use_container_width=True):
                                    st.session_state["selected_sub"] = (sq, sub_item)
                                    st.rerun()
                            if st.button(f"✖ CHIUDI {sq['name']}", key=f"close_{code}", use_container_width=True):
                                st.session_state["expanded_node"] = None
                                st.rerun()
                        else:
                            st.markdown(f"""
                            <div class="alpha-tile" style="background: {sq['bg_grad']}; border: 1.5px solid {sq['border']}; border-left: 4px solid {sq['border']}; box-shadow: inset 0 0 24px {sq['glow']};">
                                <div>{svg_icon}</div>
                                <div class="tile-code">{code}</div>
                                <div class="tile-name">{sq['name']}</div>
                                <div class="tile-kpi">{sq['kpi']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"APRI {code} // {sq['name']}", key=f"btn_open_{code}", use_container_width=True):
                                st.session_state["expanded_node"] = code
                                st.rerun()

with col_right:
    st.markdown("""
    <div class="ems-panel">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:11px; font-weight:900; color:#FFFFFF; letter-spacing:1px;">ALPHA EMS-1975<br>SYNTH</span>
            <span style="font-size:10px; font-weight:900; color:#10B981; font-family:'Share Tech Mono';">TOUCH<br>ARMED</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    s_col1, s_col2 = st.columns(2)
    with s_col1:
        if st.button("▶ X5-7 DATA\nBURST", use_container_width=True):
            play_ems_synth("burst")
            st.toast("🔊 EMS-1975: X5-7 Data Burst (95 BPM)")
    with s_col2:
        if st.button("◈ COMMLOCK\n1975", use_container_width=True):
            play_ems_synth("commlock")
            st.session_state["visitors_log"] += 1
            st.toast("📡 Commlock 1975: Visitatore Registrato")

    if st.button("▲ ALPHA KLAXON SIREN", use_container_width=True):
        play_ems_synth("klaxon")
        st.warning("🚨 ALLERTA SOLAR STORM // PROTOCOLLO SCUDO 96H ATTIVO")

    module_options = ["00 ALPHA MAIN MISSION"] + [f"{s['code']} {s['name']}" for s in all_squares]
    chosen_mod = st.selectbox("SELEZIONA NODO TELEPORT", module_options, label_visibility="collapsed")

    target_url = "https://alpha-main-mission.streamlit.app"
    for s in all_squares:
        if chosen_mod.startswith(s["code"]):
            target_url = s["url"]
            break

    st.markdown(f"""
    <div class="commlock-panel">
        <div style="font-size:11px; font-weight:900; color:#FFFFFF; text-align:left; letter-spacing:1px; margin-bottom:10px;">
            COMMLOCK // QR<br>TELEPORT
        </div>
        <div style="background:#0B0E14; border:2px solid #F59E0B; padding:10px; display:inline-block; border-radius:3px;">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=170x170&color=F59E0B&bgcolor=0B0E14&data={target_url}" width="145" />
        </div>
        <div style="font-size:10px; font-weight:900; color:#F59E0B; margin-top:10px; letter-spacing:0.8px;">
            {chosen_mod}
        </div>
        <div style="font-size:9px; color:#94A3B8; font-family:'Share Tech Mono', monospace; margin-top:2px;">
            alpha-main-mission.streamlit.app
        </div>
    </div>
    """, unsafe_allow_html=True)
