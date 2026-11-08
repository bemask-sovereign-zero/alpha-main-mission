import os
import json
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# BEMASK - MOONBASE A.L.P.H.A. // MAIN MISSION (2^11 MATRIX + BOTTOM DRAWER)
# ==============================================================================

st.set_page_config(
    page_title="BEMASK - MOONBASE A.L.P.H.A. // MAIN MISSION",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. INIZIALIZZAZIONE STATO & DATABASE SQLITE ROXY BAR (BOLLA DORECA) ---
def init_monumental_state():
    defaults = {
        # I primi 9 accesi + i 2 nuovi (10 Bar Sentinel e 11 Bank Scanner) ATTIVI!
        "active_bits_11": [True, True, True, True, True, True, True, True, True, True, True],
        "custom_squares": [],
        "active_sector": None,
        "selected_sub": None,
        "pin_code": "9999",
        "visitors_log": 34,
        "rop_cons_gg": 45,
        "rop_lead_gg": 2,
        "rop_stock": 490,
        "bocche_96h": 137
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def init_roxy_doreca_db():
    conn = sqlite3.connect("alpha_bar_memory.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dna_prezzi_roxy (
                    dna_key TEXT PRIMARY KEY,
                    cod_fornitore TEXT,
                    nome_standard TEXT,
                    categoria TEXT,
                    formato_litri REAL,
                    prezzo_unitario REAL,
                    ultimo_prezzo_litro REAL,
                    data_aggiornamento TEXT,
                    fornitore TEXT)''')
    c.execute("SELECT COUNT(*) FROM dna_prezzi_roxy")
    if c.fetchone()[0] < 10:
        c.execute("DELETE FROM dna_prezzi_roxy")
        dati_doreca = [
            ("MONTENEGRO_1.5L", "21093", "AMARO MONTENEGRO 23° 1,5L", "BEVERAGE", 1.50, 29.40, 19.60, "08/10/2026", "DORECA SCARLINO"),
            ("APEROL_1L", "18163", "APERITIVO APEROL 11° 1L", "BEVERAGE", 1.00, 9.70, 9.70, "08/10/2026", "DORECA SCARLINO"),
            ("BECKS_0.33L", "452260", "BIRRA BECK'S 33CL VAP (x24)", "BEVERAGE", 0.33, 0.68, 2.06, "08/10/2026", "DORECA SCARLINO"),
            ("HEINEKEN_0.33L", "452215", "BIRRA HEINEKEN 33CL VAP (x24)", "BEVERAGE", 0.33, 0.80, 2.42, "08/10/2026", "DORECA SCARLINO"),
            ("MORETTI_0.33L", "452197", "BIRRA MORETTI RIC. ORIG. 33CL LAT (x24)", "BEVERAGE", 0.33, 0.81, 2.45, "08/10/2026", "DORECA SCARLINO"),
            ("TENNENTS_0.33L", "452380", "BIRRA TENNENT'S SUPER 9% 33CL VAP (x24)", "BEVERAGE", 0.33, 1.35, 4.09, "08/10/2026", "DORECA SCARLINO"),
            ("CRODINO_0.10L", "452436", "CRODINO VAP 10CL (x48)", "BEVERAGE", 0.10, 0.50, 5.00, "08/10/2026", "DORECA SCARLINO"),
            ("SCHWEPPES_0.18L", "452543", "TONICA SCHWEPPES 18CL VAP (x24)", "BEVERAGE", 0.18, 0.69, 3.83, "08/10/2026", "DORECA SCARLINO"),
            ("MOLINARI_1.5L", "21050", "LIQUORE MOLINARI SAMBUCA EXTRA 1,5L", "BEVERAGE", 1.50, 20.19, 13.46, "08/10/2026", "DORECA SCARLINO"),
            ("FABBRI_SAMBUCO_1L", "489887", "SCIROPPO FABBRI MIXYBAR FIORI SAMBUCO 1L", "BEVERAGE", 1.00, 17.90, 17.90, "08/10/2026", "DORECA SCARLINO")
        ]
        c.executemany("INSERT INTO dna_prezzi_roxy VALUES (?,?,?,?,?,?,?,?,?)", dati_doreca)
        conn.commit()
    return conn

init_monumental_state()
conn_roxy = init_roxy_doreca_db()

# --- 2. ICONE VETTORIALI NEON SVG (01 -> 11) ---
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
             </svg>""",
    "10": """<svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M10 8H34L24 22V34H30V38H14V34H20V22L10 8Z" stroke="#10B981" stroke-width="2.5" fill="rgba(16,185,129,0.22)"/>
             <circle cx="25" cy="14" r="2.5" fill="#F59E0B"/>
             </svg>""",
    "11": """<svg width="38" height="38" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <rect x="6" y="10" width="32" height="24" rx="3" stroke="#EF4444" stroke-width="2.5" fill="rgba(239,68,68,0.18)"/>
             <line x1="6" y1="18" x2="38" y2="18" stroke="#F59E0B" stroke-width="3"/>
             <circle cx="29" cy="26" r="3" stroke="#F59E0B" stroke-width="2"/>
             </svg>"""
}

# --- 3. ARCHITETTURA DEGLI 11 VETTORI PRIMARI (1 -> 2^11 = 2.048 STATI) ---
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
        "kpi": "ROP: SCORTA OK | BOLLA DORECA 190677/9", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Calcolatore Punto Riordino (ROP)", "2. Radar Bolla Doreca & DNA Liquidi", "3. Simulatore Anti-Truffa Omaggi", "4. Controllo Fatture XML", "5. Lista Ordini Urgenti"]
    },
    {
        "bit": 7, "code": "08", "short": "08 HACCP", "name": "HACCP & REGISTRO ASL",
        "border": "#06B6D4", "glow": "rgba(6, 182, 212, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #123440 0%, #12171E 78%)",
        "kpi": "CELLE FRIGO: 21/21 OK | LOTTIZZAZIONE BOLLA ON", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Temperature Celle (-18°C / +4°C)", "2. Firma Digitale con PIN", "3. Lotti & Sgocciolato", "4. Sanificazione Cucina", "5. Scarica Stampa ASL (.HTML)"]
    },
    {
        "bit": 8, "code": "09", "short": "09 GOPPAR", "name": "OPEX / CAPEX & P.IVA",
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #3B2816 0%, #14161D 78%)",
        "kpi": "MOL NETTO OGGI: € 4.820 | GOP: +34%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Split Multi-P.IVA Casa Madre", "2. OPEX vs CAPEX Real-Time", "3. Autopsia Bancaria & POS Reale", "4. Cashflow Consolidato", "5. Ponte Dati Revisore"]
    },
    {
        "bit": 9, "code": "10", "short": "10 BAR UNIT", "name": "BAR & DDT SENTINEL",
        "border": "#10B981", "glow": "rgba(16, 185, 129, 0.40)", "bg_grad": "radial-gradient(circle at 50% 42%, #0D3B2E 0%, #11171D 78%)",
        "kpi": "ROXY BAR // BOLLA DORECA: 10 COLLI REALI SU 21", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Radar Bolle & DNA Liquidi", "2. Simulatore Anti-Truffa Omaggi", "3. Scudo HACCP (1-Click)", "4. Semaforo Incassi vs Spese", "5. Allerta Vuoti & Cauzioni"]
    },
    {
        "bit": 10, "code": "11", "short": "11 BANK SCAN", "name": "BANK VAMPIRE SCANNER",
        "border": "#EF4444", "glow": "rgba(239, 68, 68, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #3F161D 0%, #15131A 78%)",
        "kpi": "TASSO POS REALE: 3.68% | 300 CAFFÈ BRUCIATI/MESE", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Autopsia Costo Righe Estratto", "2. Vero Tasso POS vs Promesso", "3. Contatore Caffè Lavorati Gratis", "4. Anti-Doppio Addebito SDD (379,19€)", "5. Perizia PDF per Rinegoziazione"]
    }
]

WEATHER_5_DAYS = [
    {"day": "SOL 08 · 19°C", "status": "NOMINAL ORBIT", "pct": "8%", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "SUN 08/11 · 17°C", "status": "NOMINAL ORBIT", "pct": "14%", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "MON 09/11 · 17°C", "status": "SOLAR STORM", "pct": "91%", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "TUE 10/11 · 20°C", "status": "SOLAR STORM", "pct": "94%", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "WED 11/11 · 21°C", "status": "NOMINAL ORBIT", "pct": "22%", "border": "#38BDF8", "text_col": "#F59E0B"},
]

# --- 4. SINTETIZZATORE AUDIO WEBAUDIO (EMS SYNTHI 1975) ---
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

# --- 5. CSS MONUMENTALE PULITO (ZERO BOTTONI SOTTO LE PIASTRELLE) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800;900&family=Share+Tech+Mono&display=swap');

.stApp { background-color: #12151B; color: #F8FAFC; font-family: 'Orbitron', sans-serif; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 0.7rem; max-width: 96%; }

.koenig-strip {
    background-color: #1A1E26; border: 1px solid #323946; border-left: 5px solid #F59E0B;
    padding: 8px 14px; margin-bottom: 10px; border-radius: 2px;
}
.badge-amber { background-color: #F59E0B; color: #0B0E14; font-weight: 900; font-size: 10px; padding: 3px 8px; margin-right: 8px; letter-spacing: 0.8px; display: inline-block; }
.badge-white { background-color: #F1F5F9; color: #0F172A; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; }
.badge-red { background-color: #7F1D1D; border: 1px solid #EF4444; color: #FCA5A5; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; }

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

.weather-card {
    background-color: #161A22; border: 1px solid #2B3340;
    padding: 8px 12px; border-radius: 2px; margin-bottom: 10px;
}
.w-day { font-size: 10px; font-weight: 900; color: #FFFFFF; letter-spacing: 0.6px; }
.w-status { font-size: 9px; font-weight: 800; margin-top: 3px; letter-spacing: 0.8px; }

/* PIASTRELLE PULITE COME NELLA TUA FOTO SUL TABLET */
.alpha-tile {
    height: 215px; border-radius: 3px; padding: 18px;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    text-align: center; position: relative; transition: all 0.22s ease;
    margin-bottom: 14px; pointer-events: none;
}
.tile-code { font-size: 11px; font-weight: 800; color: #E2E8F0; margin-top: 12px; letter-spacing: 1.5px; }
.tile-name { font-size: 14px; font-weight: 900; color: #FFFFFF; letter-spacing: 1.2px; margin-top: 4px; }

/* OVERLAY TRASPARENTE SUL QUADRATO (NIENTE BOTTONI SOTTO!) */
div[class*="st-key-tile_click_"] {
    margin-top: -229px !important;
    margin-bottom: 14px !important;
    position: relative;
    z-index: 10;
}
div[class*="st-key-tile_click_"] > div > button {
    height: 215px !important;
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    box-shadow: none !important;
}
div[class*="st-key-tile_click_"] > div > button:hover {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.35) !important;
    box-shadow: 0 0 22px rgba(245, 158, 11, 0.25) !important;
}

/* STILE BOTTONI NORMALI (SYNTH E SOTTOMENU IN BASSO) */
div.stButton > button {
    background-color: #1A212B !important; color: #F8FAFC !important;
    border: 1px solid #2F3E50 !important; border-radius: 2px !important;
    font-family: 'Orbitron', sans-serif !important; font-size: 10px !important;
    font-weight: 800 !important; letter-spacing: 1px !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    border-color: #F59E0B !important; color: #F59E0B !important;
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.3) !important;
}

.ems-panel {
    background-color: #161A22; border: 2px solid #F59E0B;
    padding: 12px; border-radius: 3px; margin-bottom: 10px;
}
.commlock-panel {
    background-color: #161A22; border: 1px solid #F59E0B;
    padding: 14px; border-radius: 3px; text-align: center;
}
.bottom-drawer {
    background: linear-gradient(180deg, #161D26 0%, #11151C 100%);
    padding: 18px; border-radius: 3px; margin-top: 8px; margin-bottom: 16px;
}
.alert-red-alpha {
    background-color: #1F090D; border: 1px solid #EF4444; border-left: 4px solid #EF4444;
    padding: 12px; border-radius: 3px; color: #FCA5A5; font-family: 'Share Tech Mono', monospace; font-size: 13px; margin-bottom: 10px;
}
.alert-green-alpha {
    background-color: #06241B; border: 1px solid #10B981; border-left: 4px solid #10B981;
    padding: 12px; border-radius: 3px; color: #6EE7B7; font-family: 'Share Tech Mono', monospace; font-size: 13px; margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- 6. CALCOLO DINAMICO MATRICE BINARIA 1 -> 2^11 (2.048 COMBINAZIONI) ---
bits = st.session_state["active_bits_11"]
active_base = [v for i, v in enumerate(BASE_VECTORS) if bits[i]]
if not active_base:
    st.session_state["active_bits_11"][0] = True
    active_base = [BASE_VECTORS[0]]

all_squares = active_base + st.session_state["custom_squares"]
n_sectors = len(all_squares)
total_micro_modules = n_sectors * 5
binary_state_num = sum((1 << i) for i, b in enumerate(bits) if b)
ora_attuale = datetime.now().strftime("%H:%M")

# --- 7. TOP KOENIG BAR + ALPHA HEADER + METEO 5 GIORNI ---
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
        <span class="badge-white">1 → 2¹¹ (STATE #{binary_state_num}/2048)</span>
    </div>
</div>

<div class="mission-bar">
    <div style="display:flex; align-items:center; gap:14px;">
        <div>{SVG_ICONS["01"]}</div>
        <div>
            <div class="mission-title">BEMASK - A.L.P.H.A. MAIN MISSION</div>
            <div class="mission-sub">SPACE: 1999 COMMAND | DATE: {datetime.now().strftime('%a %d/%m/%Y').upper()} | {total_micro_modules} MICRO-MODULES</div>
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

# --- 8. SELETTORE SCALABILITÀ 1 -> 2^11 (DISCRETO E CHIUDIBILE) ---
with st.expander(f"🎛️ SCALABILITÀ ARCHITETTURA 1 → 2¹¹ (Stato #{binary_state_num}/2048 — Configura da 1 a 11 Settori)", expanded=False):
    sw_cols = st.columns(11)
    for i, vec in enumerate(BASE_VECTORS):
        with sw_cols[i]:
            toggled = st.toggle(vec["short"], value=st.session_state["active_bits_11"][i], key=f"tg_{i}")
            if toggled != st.session_state["active_bits_11"][i]:
                st.session_state["active_bits_11"][i] = toggled
                st.session_state["active_sector"] = None
                st.session_state["selected_sub"] = None
                st.rerun()

# --- 9. FUNZIONI INTERNE PER IL BOTTOM DRAWER (MOD-10 BAR & MOD-11 BANK) ---
def render_drawer_bar_sentinel():
    col_sx, col_dx = st.columns([1.25, 1])
    with col_sx:
        st.markdown("##### 📄 ULTIMA BOLLA SCANSIONATA: `DORECA N. 190677/9` (ROXY BAR FOLLONICA)")
        st.markdown("""
        <div class="alert-red-alpha">
            <b>🚨 ANOMALIA COLLI ALLO SCARICO RILEVATA!</b><br>
            • Colli dichiarati in testata bolla: <b>21 Colli</b> (183 Pz • 96,2 kg)<br>
            • Colli fisici reali da scaricare: <b>10 Colli</b> (12 Bt. Aperol 1L battute come 12 colli singoli)<br>
            • <b>PAGAMENTO ALLO SCARICO:</b> Cod. 510 CONSEGNA TASSATIVO — <b>€ 379,19</b> (Imp. € 310,81 + IVA € 68,38)<br>
            • <b>CAUZIONI / VUOTI:</b> Attivo avviso <i>'RITIRARE DDT X VUOTI PERONI'</i> (Stato: CAUZIONATO).
        </div>
        """, unsafe_allow_html=True)
        df_storico = pd.read_sql_query("SELECT cod_fornitore AS 'Cod.', nome_standard AS 'Prodotto (DNA)', prezzo_unitario AS '€/Pz Netto', ultimo_prezzo_litro AS '€/Litro' FROM dna_prezzi_roxy", conn_roxy)
        st.dataframe(df_storico, use_container_width=True, hide_index=True, height=260)

    with col_dx:
        st.markdown("##### 🔍 SIMULATORE ANTI-TRUFFA OMAGGI & CODICI FORNITORE")
        df_prod = pd.read_sql_query("SELECT dna_key, nome_standard, prezzo_unitario FROM dna_prezzi_roxy", conn_roxy)
        opzioni = [f"{r['dna_key']} | {r['nome_standard']} (€ {r['prezzo_unitario']:.2f})" for _, r in df_prod.iterrows()]
        scelta = st.selectbox("Prodotto riconosciuto dal DNA Semantico:", opzioni, index=1, key="drw_prod")
        chiave_sel = scelta.split(" | ")[0]
        riga_sel = df_prod[df_prod["dna_key"] == chiave_sel].iloc[0]
        prezzo_storico_pz = float(riga_sel["prezzo_unitario"])

        cod_forn = st.text_input("Nuovo Codice Articolo Fornitore:", value="AA514-NEW", key="drw_cod")
        k1, k2, k3 = st.columns(3)
        bt_fat = k1.number_input("Pz Fatturati", value=48, step=1, key="drw_fat")
        bt_oma = k2.number_input("Pz Omaggio", value=3, step=1, key="drw_oma")
        tot_riga = k3.number_input("Totale Riga (€)", value=502.35, step=0.50, key="drw_tot")

        bt_tot = bt_fat + bt_oma
        nuovo_p = tot_riga / bt_tot
        diff = nuovo_p - prezzo_storico_pz

        if diff > 0.01:
            danno = diff * bt_tot
            spritz_persi = int(danno / 3.50)
            st.markdown(f"""
            <div class="alert-red-alpha">
                <b>⚠️ TRAPPOLA PREZZO SU [{cod_forn}]!</b><br>
                Anche con <b>{bt_oma} omaggi</b>, il costo reale è salito a <b>€ {nuovo_p:.2f}/Pz</b> (Storico: € {prezzo_storico_pz:.2f}).<br>
                • Perdita su questa consegna: <b>-€ {danno:.2f} (+IVA)</b> (~{spritz_persi} Spritz bruciati).
            </div>
            """, unsafe_allow_html=True)
            msg_wa = f"Ciao Emiliano (Agente 85696), sulla nuova bolla {riga_sel['nome_standard']} (anche coi {bt_oma} omaggi) esce a {nuovo_p:.2f}€ netti contro i {prezzo_storico_pz:.2f}€ del 08/10. Mi allinei con nota credito di {danno:.2f}€?"
            st.code(msg_wa, language="text")
        else:
            st.markdown('<div class="alert-green-alpha"><b>✅ PREZZO ALLINEATO O IN CALO RISPETTO ALLO STORICO.</b></div>', unsafe_allow_html=True)

def render_drawer_bank_scanner():
    b1, b2, b3 = st.columns(3)
    transato_pos = b1.number_input("Incasso POS Mensile (€)", value=9800.0, step=200.0, key="bk_pos")
    comm_promessa = b2.number_input("Commissione Promessa (%)", value=1.10, step=0.1, key="bk_comm")
    righe_ec = b3.number_input("Righe Estratto Conto", value=215, step=10, key="bk_righe")

    b4, b5, b6 = st.columns(3)
    costo_riga = b4.number_input("Costo Occulto per Riga (€)", value=0.65, step=0.05, key="bk_cr")
    canoni_fissi = b5.number_input("Canoni POS + Tenuta Conto (€)", value=48.50, step=5.0, key="bk_can")
    extra_comm = b6.number_input("Maggiorazioni Carte Business/Minimi (€)", value=64.00, step=5.0, key="bk_ext")

    costo_base = transato_pos * (comm_promessa / 100.0)
    tassa_scritture = righe_ec * costo_riga
    totale_prelevato = costo_base + tassa_scritture + canoni_fissi + extra_comm
    tasso_reale = (totale_prelevato / transato_pos) * 100.0
    caffe_gratis = int(totale_prelevato / 1.20)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Costo Promesso (1,10%)", f"€ {costo_base:.2f}")
    m2.metric("Righe + Canoni Occulti", f"€ {(tassa_scritture + canoni_fissi + extra_comm):.2f}")
    m3.metric("TOTALE REALE PRELEVATO", f"€ {totale_prelevato:.2f}/mese")
    m4.metric("TASSO REALE EFFETTIVO", f"{tasso_reale:.2f}%", f"+{(tasso_reale - comm_promessa):.2f}% vs contratto", delta_color="inverse")

    st.markdown(f"""
    <div class="alert-red-alpha">
        <b>🧛‍♂️ DIAGNOSI BANCARIA MENSILE:</b><br>
        • Questo mese hai lavorato e servito <b>{caffe_gratis} CAFFÈ GRATIS</b> solo per pagare balzelli e scritture bancarie.<br>
        • <b>SCUDO ANTI-DOPPIO ADDEBITO:</b> Verificare che la bolla Doreca <b>N. 190677/9 di € 379,19</b> (già saldata allo scarico con cod. <i>510 CONSEGNA TASSATIVO</i>) non venga ri-addebitata via SDD/RIBA a fine mese.
    </div>
    """, unsafe_allow_html=True)

# --- 10. PLANCIA PRINCIPALE PULITA (SENZA BOTTONI SOTTO I QUADRATI) ---
col_left, col_right = st.columns([3.25, 1.15])

with col_left:
    n_cols = 1 if n_sectors == 1 else (2 if n_sectors in [2, 4] else 3)
    for r in range(0, n_sectors, n_cols):
        row_cols = st.columns(n_cols)
        for c in range(n_cols):
            if r + c < n_sectors:
                sq = all_squares[r + c]
                code = sq["code"]
                svg_icon = SVG_ICONS.get(code, SVG_ICONS["01"])
                is_selected = (st.session_state["active_sector"] == code)
                border_w = "3px" if is_selected else "1.5px"

                with row_cols[c]:
                    st.markdown(f"""
                    <div class="alpha-tile" style="background: {sq['bg_grad']}; border: {border_w} solid {sq['border']}; border-left: 5px solid {sq['border']}; box-shadow: inset 0 0 26px {sq['glow']};">
                        <div>{svg_icon}</div>
                        <div class="tile-code">{code}</div>
                        <div class="tile-name">{sq['name']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(" ", key=f"tile_click_{code}", use_container_width=True):
                        if st.session_state["active_sector"] == code:
                            st.session_state["active_sector"] = None
                            st.session_state["selected_sub"] = None
                        else:
                            st.session_state["active_sector"] = code
                            st.session_state["selected_sub"] = sq["subs"][0]
                        st.rerun()

    # --- 11. CASSETTO SOTTOMENU CHE SI APRE SOLO SOTTO LA PLANCIA ---
    if st.session_state["active_sector"] is not None:
        sec_obj = next((s for s in all_squares if s["code"] == st.session_state["active_sector"]), None)
        if sec_obj:
            st.markdown(f"""
            <div class="bottom-drawer" style="border: 1px solid {sec_obj['border']}; border-left: 5px solid {sec_obj['border']};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:11px; color:{sec_obj['border']}; font-family:'Share Tech Mono';">SETTORE {sec_obj['code']} ATTIVO // SOTTOMENU OPERATIVO</span>
                        <div style="font-size:18px; font-weight:900; color:#FFF; margin-top:2px;">{sec_obj['name']} — <span style="color:#38BDF8; font-size:13px; font-family:'Share Tech Mono';">{sec_obj['kpi']}</span></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            sub_cols = st.columns(6)
            for idx_s, sub_label in enumerate(sec_obj["subs"]):
                with sub_cols[idx_s]:
                    if st.button(sub_label, key=f"bsub_{sec_obj['code']}_{idx_s}", use_container_width=True):
                        st.session_state["selected_sub"] = sub_label
                        st.rerun()
            with sub_cols[5]:
                if st.button("✖ CHIUDI PANNELLO", key="close_bottom_drawer", use_container_width=True):
                    st.session_state["active_sector"] = None
                    st.session_state["selected_sub"] = None
                    st.rerun()

            if st.session_state["selected_sub"]:
                st.markdown(f"##### ⚡ {sec_obj['name']} // {st.session_state['selected_sub']}")
                
                # ROUTING INTELLIGENTE NEL BOTTOM DRAWER:
                if sec_obj["code"] == "10" or "Doreca" in st.session_state["selected_sub"] or "Omaggi" in st.session_state["selected_sub"]:
                    render_drawer_bar_sentinel()
                elif sec_obj["code"] == "11" or "Bancaria" in st.session_state["selected_sub"]:
                    render_drawer_bank_scanner()
                elif sec_obj["code"] == "08":
                    f1, f2, f3 = st.columns(3)
                    f1.slider("Frigo Bancone Bibite (°C)", 0.0, 8.0, 3.8, key="hc_1")
                    f2.slider("Frigo Latte & Pasticceria (°C)", 0.0, 6.0, 2.5, key="hc_2")
                    f3.slider("Cella Scorta Birre (°C)", 0.0, 10.0, 4.2, key="hc_3")
                    if st.button("✅ FIRMA CON PIN 9999 E BLINDA REGISTRO GIORNALIERO (LOTTI BOLLA 190677/9 ACQUISITI)"):
                        st.success(f"Registro HACCP validato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} - Pronto per ispezione ASL.")
                else:
                    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.4])
                    st.session_state["rop_cons_gg"] = c1.number_input("Consumo Giorno (u.)", 1, 1000, st.session_state["rop_cons_gg"])
                    st.session_state["rop_lead_gg"] = c2.number_input("Lead Time (gg)", 1, 30, st.session_state["rop_lead_gg"])
                    st.session_state["rop_stock"] = c3.number_input("Giacenza Casa", 0, 5000, st.session_state["rop_stock"])
                    rop_val = (st.session_state["rop_cons_gg"] * st.session_state["rop_lead_gg"]) + (st.session_state["bocche_96h"] * 4)
                    with c4:
                        st.metric("PUNTO ACQUISTO (ROP 96H)", f"{rop_val} u.", f"{st.session_state['rop_stock'] - rop_val} u. margine")
                
                st.link_button(f"🚀 APRI MODULO DEDICATO ({sec_obj['name']})", sec_obj["url"], use_container_width=True)

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
            st.toast("📡 Commlock 1975 Sincronizzato")

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
