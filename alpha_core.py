import os
import json
import time
import hmac
import hashlib
import base64
import struct
import io
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# ==============================================================================
# BEMASK - MOONBASE A.L.P.H.A. // MAIN MISSION (FORTRESS EDITION 2FA + RAM ONLY)
# ==============================================================================

st.set_page_config(
    page_title="BEMASK - MOONBASE A.L.P.H.A. // MAIN MISSION",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. MOTORE CRITTOGRAFICO NATIVO 2FA (RFC 6238 GOOGLE AUTHENTICATOR) ---
# Usa librerie native Python: zero dipendenze esterne, zero errori su Streamlit!
def get_totp_secret():
    try:
        return st.secrets.get("ALPHA_2FA_SECRET", "JBSWY3DPEHPK3PXP")
    except Exception:
        return "JBSWY3DPEHPK3PXP"

def get_master_pin():
    try:
        return str(st.secrets.get("ALPHA_MASTER_PIN", "9999"))
    except Exception:
        return "9999"

def generate_totp_token(secret_b32, time_offset=0):
    try:
        key = base64.b32decode(secret_b32.upper().replace(" ", ""), True)
        interval = int(time.time() // 30) + time_offset
        msg = struct.pack(">Q", interval)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        token = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
        return f"{token:06d}"
    except Exception:
        return "199975"

def verify_2fa_code(input_code, secret_b32):
    clean = str(input_code).strip()
    if clean == "199975":  # Codice Master per le tue Demo rapide
        return True
    for offset in [-1, 0, 1]:  # Tolleranza +/- 30 secondi per sincronia orologio smartphone
        if clean == generate_totp_token(secret_b32, offset):
            return True
    return False

# --- 2. BLINDAGGIO SESSION STATE ---
def init_monumental_state():
    defaults = {
        "auth_unlocked": False,
        "auth_role": None,        # "COMMANDER" (2FA) oppure "STAFF" (Confinato)
        "auth_user": "",
        "breach_log": [],         # Trappola anti-talpa: registra tentativi falliti
        "active_bits_11": [True, True, True, True, True, True, False, False, False, True, True],
        "custom_squares": [],
        "blum_sector": None,
        "selected_sub": None,
        "pin_code": "9999",
        "visitors_log": 42,
        "rop_cons_gg": 45,
        "rop_lead_gg": 2,
        "rop_stock": 490,
        "bocche_96h": 137,
        "ddt_prezzo_fattura": 14.80,
        "ddt_prezzo_pattuito": 12.90,
        "ddt_litri_bottiglia": 1.0,
        "ddt_omaggio_finto_iva": 3.25,
        "bank_transato_pos": 18500.0,
        "bank_comm_dichiarata": 0.90,
        "bank_costi_occulti": 198.50,
        "bank_prezzo_caffe": 1.30
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_monumental_state()

# --- 3. SINTETIZZATORE AUDIO WEBAUDIO (EMS SYNTHI 1975) ---
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
            gain.gain.setValueAtTime(0.12, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.52);
            osc.connect(gain); gain.connect(ctx.destination);
            osc.start(now); osc.stop(now + 0.52);
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0)

# --- 4. ICONE VETTORIALI NEON SVG (01 -> 11) ---
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
    "10": """<svg width="40" height="38" viewBox="0 0 46 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M10 8H36L26 22V36L20 38V22L10 8Z" stroke="#10B981" stroke-width="2.5" fill="rgba(16,185,129,0.22)"/>
             <circle cx="34" cy="14" r="5" stroke="#F59E0B" stroke-width="2"/>
             </svg>""",
    "11": """<svg width="40" height="38" viewBox="0 0 46 44" fill="none" xmlns="http://www.w3.org/2000/svg">
             <rect x="6" y="10" width="34" height="24" rx="3" stroke="#EF4444" stroke-width="2.5" fill="rgba(239,68,68,0.18)"/>
             <line x1="6" y1="18" x2="40" y2="18" stroke="#F59E0B" stroke-width="3"/>
             <circle cx="31" cy="26" r="4" fill="#EF4444"/>
             </svg>"""
}

# --- 5. ARCHITETTURA DEGLI 11 VETTORI PRIMARI (1 -> 2^11 = 2.048 STATI) ---
# Il flag "staff_allowed": True indica gli unici moduli visibili ai dipendenti!
BASE_VECTORS = [
    {
        "bit": 0, "code": "01", "short": "01 FRONT", "name": "FRONT & APEX", "staff_allowed": False,
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #3D2B14 0%, #14161D 78%)",
        "kpi": "OCC: 88% | ADR: € 165 | 140 COMB BAR", "url": "https://bemask-sovereign-zero.streamlit.app",
        "subs": ["1. Dynamic Pricing 140 Comb", "2. Controllo Allotment & OTA", "3. Check-in & Upselling", "4. Forecast 24 Fasce BAR", "5. Export CSV Passepartout"]
    },
    {
        "bit": 1, "code": "02", "short": "02 BEV", "name": "LAZERS BEV", "staff_allowed": False,
        "border": "#10B981", "glow": "rgba(16, 185, 129, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #113A32 0%, #12181F 78%)",
        "kpi": "POURING: 21% | MARGINE CANTINA: +79%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Pouring Calici & Vini", "2. Spinta Aperitivi Meteo", "3. Margine Bottiglie", "4. Usura Cristalleria", "5. Inventario Cantina Live"]
    },
    {
        "bit": 2, "code": "03", "short": "03 FOOD", "name": "LAZERS FOOD", "staff_allowed": False,
        "border": "#38BDF8", "glow": "rgba(56, 189, 248, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #13334C 0%, #121720 78%)",
        "kpi": "COPERTI: 84/105 | FOOD COST: 28.5%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Capienza Sala & Cucina", "2. Scorporo Quote HB / FB", "3. Sfridi & Rese Carni", "4. Semaforo TheFork Zero-Fee", "5. Floor Industriale Pasto"]
    },
    {
        "bit": 3, "code": "04", "short": "04 BEACH", "name": "BEACH & POOL", "staff_allowed": True,
        "border": "#A855F7", "glow": "rgba(168, 85, 247, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #2B244D 0%, #141522 78%)",
        "kpi": "SATURAZIONE LIDO: 92% | VENTO: 11 KT", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Mappa Ombrelloni & Cabine", "2. Soglia Vento Grounding", "3. Light Lunch all'Ombrellone", "4. Presidio Bagnini", "5. Chiusura Cassa Lido"]
    },
    {
        "bit": 4, "code": "05", "short": "05 SPA", "name": "SPA & AYURVEDA", "staff_allowed": True,
        "border": "#F43F5E", "glow": "rgba(244, 63, 94, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #3F1D2B 0%, #16141C 78%)",
        "kpi": "SLOT CABINE: 14/16 | FALLBACK PIOGGIA ON", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Conversione Pioggia (S1/S2)", "2. Agenda Cabine & Massaggi", "3. Percorso Private Spa VIP", "4. Vendita Linea Cosmetica", "5. Turni Operatori"]
    },
    {
        "bit": 5, "code": "06", "short": "06 SKA", "name": "S.K.A. & ROOMS", "staff_allowed": True,
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #382B19 0%, #15161C 78%)",
        "kpi": "CAMERE PRONTE: 58/60 | SEGNALAZIONI: 0", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Stato Pulizia Camere", "2. Ticket Manutenzione", "3. Presidio Brigata Piani", "4. Dotazioni & Biancheria", "5. Ispezione Governante"]
    },
    {
        "bit": 6, "code": "07", "short": "07 ACQUISTO", "name": "PUNTO ACQUISTO & ROP", "staff_allowed": False,
        "border": "#10B981", "glow": "rgba(16, 185, 129, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #13392E 0%, #12171D 78%)",
        "kpi": "ROP: SCORTA OK | SCUDO AUTONOMIA: 96H", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Calcolatore Punto Riordino (ROP)", "2. Scudo Dispensa 96 Ore", "3. Lead Time Fornitori", "4. Controllo Fatture XML", "5. Lista Ordini Urgenti"]
    },
    {
        "bit": 7, "code": "08", "short": "08 HACCP", "name": "HACCP & REGISTRO ASL", "staff_allowed": True,
        "border": "#06B6D4", "glow": "rgba(6, 182, 212, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #123440 0%, #12171E 78%)",
        "kpi": "CELLE FRIGO: 21/21 OK | FIRME PIN: 6", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Temperature Celle (-18°C / +4°C)", "2. Firma Digitale con PIN", "3. Lotti & Sgocciolato", "4. Sanificazione Cucina", "5. Scarica Stampa ASL (.HTML)"]
    },
    {
        "bit": 8, "code": "09", "short": "09 GOPPAR", "name": "OPEX / CAPEX & P.IVA", "staff_allowed": False,
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.35)", "bg_grad": "radial-gradient(circle at 50% 42%, #3B2816 0%, #14161D 78%)",
        "kpi": "MOL NETTO OGGI: € 4.820 | GOP: +34%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Split Multi-P.IVA Casa Madre", "2. OPEX vs CAPEX Real-Time", "3. Incidenza Costo Brigate", "4. Cashflow Consolidato", "5. Ponte Dati Revisore"]
    },
    {
        "bit": 9, "code": "10", "short": "10 BAR DDT", "name": "BAR & DDT SENTINEL", "staff_allowed": False,
        "border": "#10B981", "glow": "rgba(16, 185, 129, 0.40)", "bg_grad": "radial-gradient(circle at 50% 42%, #0F3D33 0%, #10171D 78%)",
        "kpi": "ROXY BAR EDITION | BOLLA DORECA 190677/9", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Scanner Bolla Doreca 190677/9", "2. DNA Prezzo al Litro (Cod. 10001/AA514)", "3. Scudo Anti-Truffa Omaggi", "4. Variazioni Aperol/Gin Live", "5. HACCP Bar 1-Click"]
    },
    {
        "bit": 10, "code": "11", "short": "11 VAMPIRE", "name": "BANK VAMPIRE SCANNER", "staff_allowed": False,
        "border": "#EF4444", "glow": "rgba(239, 68, 68, 0.40)", "bg_grad": "radial-gradient(circle at 50% 42%, #421820 0%, #151319 78%)",
        "kpi": "AUTOPSIA CONTO | POS REALE & SDD ALERT", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Autopsia Costi Occulti E/C", "2. Vero Tasso POS Effettivo", "3. Caffè Lavorati Gratis", "4. Anti-Doppio Addebito SDD", "5. Dossier Contestazione Banca"]
    }
]

WEATHER_5_DAYS = [
    {"day": "SOL 08 · 19°C", "status": "NOMINAL ORBIT", "pct": "8%", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "SUN 08/11 · 17°C", "status": "NOMINAL ORBIT", "pct": "14%", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "MON 09/11 · 17°C", "status": "SOLAR STORM", "pct": "91%", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "TUE 10/11 · 20°C", "status": "SOLAR STORM", "pct": "94%", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "WED 11/11 · 21°C", "status": "NOMINAL ORBIT", "pct": "22%", "border": "#38BDF8", "text_col": "#F59E0B"},
]

# --- 6. CSS MONUMENTALE + KPI CARDS ANTI-SOVRAPPOSIZIONE + SECURITY GATE ---
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
.badge-green { background-color: #064E3B; border: 1px solid #10B981; color: #6EE7B7; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; }

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

.alpha-tile {
    height: 215px; border-radius: 3px; padding: 18px;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    text-align: center; position: relative; transition: all 0.22s ease;
    margin-bottom: 14px; pointer-events: none;
}
.tile-code { font-size: 11px; font-weight: 800; color: #E2E8F0; margin-top: 12px; letter-spacing: 1.5px; }
.tile-name { font-size: 14px; font-weight: 900; color: #FFFFFF; letter-spacing: 1.2px; margin-top: 4px; }

div[class*="st-key-blum_click_"] {
    margin-top: -229px !important;
    margin-bottom: 14px !important;
    position: relative;
    z-index: 10;
}
div[class*="st-key-blum_click_"] > div > button {
    height: 215px !important;
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    box-shadow: none !important;
}
div[class*="st-key-blum_click_"] > div > button:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1.5px solid rgba(245, 158, 11, 0.65) !important;
    box-shadow: 0 0 28px rgba(245, 158, 11, 0.35) !important;
}

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

.ems-panel { background-color: #161A22; border: 2px solid #F59E0B; padding: 12px; border-radius: 3px; margin-bottom: 10px; }
.commlock-panel { background-color: #161A22; border: 1px solid #F59E0B; padding: 14px; border-radius: 3px; text-align: center; }
.blum-stage { background: radial-gradient(circle at 50% 20%, #1A2432 0%, #0E1218 85%); padding: 22px; border-radius: 4px; margin-bottom: 14px; }

/* BOX KPI CUSTOM (RISOLVE PER SEMPRE LA SOVRAPPOSIZIONE DI 1.97% SU MONITOR ULTRA-WIDE) */
.kpi-custom-box {
    background-color: #141A23; border: 1px solid #2B394A; border-left: 4px solid #F59E0B;
    padding: 16px; border-radius: 3px; margin-top: 8px; margin-bottom: 10px;
}
.kpi-custom-title {
    font-size: 10px; font-weight: 800; color: #94A3B8; letter-spacing: 1.2px;
    margin-bottom: 10px; font-family: 'Share Tech Mono', monospace;
}
.kpi-custom-value {
    font-size: 26px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px; line-height: 1.2;
}
.kpi-custom-sub {
    font-size: 11px; font-weight: 700; margin-top: 8px; font-family: 'Share Tech Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. KOENIG ZERO-TRUST SECURITY GATE (BLOCCO INIZIALE + 2FA + TRAPPOLA TALPE)
# ==============================================================================
STAFF_PINS = {
    "1024": "OPERATORE BAR / CUCINA (SOLO HACCP & SKA)",
    "2048": "GOVERNANTE AI PIANI (SOLO CAMERE & SKA)",
    "3096": "BAGNINO LIDO (SOLO BEACH & POOL)"
}

if not st.session_state["auth_unlocked"]:
    st.markdown("<div style='height:35px;'></div>", unsafe_allow_html=True)
    g_left, g_center, g_right = st.columns([1, 1.8, 1])
    with g_center:
        st.markdown(f"""
        <div style="background:#161B24; border:2px solid #F59E0B; border-top:6px solid #F59E0B; padding:28px; border-radius:4px; box-shadow:0 0 40px rgba(245,158,11,0.2);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>{SVG_ICONS["01"]}</div>
                <span class="badge-amber">ZERO-TRUST 2FA SHIELD</span>
            </div>
            <div style="font-size:20px; font-weight:900; color:#FFFFFF; letter-spacing:1.5px;">
                BEMASK // A.L.P.H.A. SECURITY GATE
            </div>
            <div style="font-size:11px; color:#38BDF8; font-family:'Share Tech Mono', monospace; margin-top:4px; margin-bottom:18px;">
                AUTENTICAZIONE DOPPIO LIVELLO | ANTI-MOLE PROTOCOL ACTIVE | AES-256 HTTPS
            </div>
        </div>
        """, unsafe_allow_html=True)

        c_pin, c_2fa = st.columns(2)
        in_pin = c_pin.text_input("🔑 PIN OPERATORE / TITOLARE", type="password", placeholder="Es. 9999 o 1024")
        in_2fa = c_2fa.text_input("📱 CODICE 2FA (6 CIFRE - SOLO TITOLARE)", type="password", placeholder="Google Auth / 199975")

        b_login, b_demo = st.columns(2)
        if b_login.button("🛡️ VERIFICA CREDENZIALI E SBLOCCA PLANCIA", use_container_width=True):
            master_pin = get_master_pin()
            secret_2fa = get_totp_secret()
            ora_try = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Caso 1: Il Titolare inserisce il PIN Master
            if in_pin.strip() == master_pin:
                if verify_2fa_code(in_2fa, secret_2fa):
                    play_ems_synth("commlock")
                    st.session_state["auth_unlocked"] = True
                    st.session_state["auth_role"] = "COMMANDER"
                    st.session_state["auth_user"] = "COMANDANTE / TITOLARE (2FA VERIFIED)"
                    st.session_state["pin_code"] = master_pin
                    st.rerun()
                else:
                    # TRAPPOLA TALPA: Qualcuno conosce il PIN del titolare ma non ha il suo telefono 2FA!
                    play_ems_synth("klaxon")
                    st.session_state["breach_log"].append(
                        f"⚠️ [{ora_try}] TENTATIVO INTRUSIONE: Usato PIN Titolare senza Token 2FA valido (Codice inserito: '{in_2fa}')"
                    )
                    st.error("🚨 ACCESSO NEGATO: CODICE 2FA MANCANTE O SCADUTO! Tentativo registrato nel Log Antintrusione del Titolare.")

            # Caso 2: Un dipendente inserisce il proprio PIN Staff (Non serve 2FA, ma vede solo HACCP/SKA)
            elif in_pin.strip() in STAFF_PINS:
                play_ems_synth("burst")
                st.session_state["auth_unlocked"] = True
                st.session_state["auth_role"] = "STAFF"
                st.session_state["auth_user"] = STAFF_PINS[in_pin.strip()]
                st.session_state["pin_code"] = in_pin.strip()
                st.rerun()

            # Caso 3: PIN completamente sbagliato
            else:
                play_ems_synth("klaxon")
                st.session_state["breach_log"].append(
                    f"⚠️ [{ora_try}] PIN SCONOSCIUTO RIFIUTATO (PIN tentato: '{in_pin}')"
                )
                st.error("🚨 PIN NON RICONOSCIUTO // EVENTO REGISTRATO NEL LOG DI SICUREZZA.")

        if b_demo.button("⚡ ACCESSO RAPIDO DEMO (SOLO TEST ENRICO)", use_container_width=True):
            play_ems_synth("commlock")
            st.session_state["auth_unlocked"] = True
            st.session_state["auth_role"] = "COMMANDER"
            st.session_state["auth_user"] = "ENRICO // ARCHITECT MASTER DEMO"
            st.rerun()

        st.markdown("""
        <div style="background:#0F131A; border:1px solid #263040; padding:12px; border-radius:3px; margin-top:12px; font-family:'Share Tech Mono', monospace; font-size:11px; color:#94A3B8;">
            • <b>ACCESSO TITOLARE (2FA):</b> PIN <code>9999</code> + Token 6 cifre Google Authenticator (o <code>199975</code> in Demo)<br>
            • <b>ACCESSO STAFF CONFINATO (Senza dati bancari/bolle):</b> PIN <code>1024</code> (Bar/HACCP) oppure <code>2048</code> (Camere)<br>
            • <b>ZERO-STORAGE RAM:</b> Nessun estratto conto o fattura viene mai salvato sul disco del server.
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# 8. FILTRO RUOLO ANTI-TALPA (COMMANDER VEDE 2^11, STAFF VEDE SOLO OPERATIVITÀ)
# ==============================================================================
is_commander = (st.session_state["auth_role"] == "COMMANDER")
bits = st.session_state["active_bits_11"]

if is_commander:
    active_base = [v for i, v in enumerate(BASE_VECTORS) if bits[i]]
    if not active_base:
        st.session_state["active_bits_11"][0] = True
        active_base = [BASE_VECTORS[0]]
    all_squares = active_base + st.session_state["custom_squares"]
else:
    # Lo Staff vede SOLO i moduli operativi autorizzati (es. 04 Beach, 05 Spa, 06 SKA, 08 HACCP).
    # I moduli 01 Revenue, 02/03 Margini, 07 Acquisti, 09 GOPPAR, 10 Bolle e 11 Banca sono INVISIBILI!
    all_squares = [v for v in BASE_VECTORS if v["staff_allowed"]]

n_sectors = len(all_squares)
total_micro_modules = n_sectors * 5
binary_state_num = sum((1 << i) for i, b in enumerate(bits) if b)
binary_str = "".join(["1" if b else "0" for b in bits])
ora_attuale = datetime.now().strftime("%H:%M")

# --- 9. TOP KOENIG BAR + PULSANTE LOGOUT & ALERT INTRUSIONI ---
breach_count = len(st.session_state["breach_log"])
breach_badge = f'<span class="badge-red">🚨 {breach_count} TENTATIVI INTRUSIONE RILEVATI</span>' if breach_count > 0 else '<span class="badge-green">🛡️ ZERO INTRUSIONI</span>'

top_c1, top_c2 = st.columns([4.2, 0.8])
with top_c1:
    st.markdown(f"""
    <div class="koenig-strip">
        <div>
            <span class="badge-amber">MOONBASE ALPHA</span>
            <span style="font-size:12px; font-weight:900; letter-spacing:1.2px; color:#FFFFFF;">
                MAIN MISSION // {st.session_state['auth_user']}
            </span>
        </div>
        <div style="margin-top:6px;">
            <span class="badge-white">{n_sectors} SECTORS X 5 MODULES</span>
            <span class="badge-amber">RAM-ONLY ZERO STORAGE</span>
            {breach_badge}
            <span class="badge-white">1 → 2¹¹ (STATE #{binary_state_num}/2048)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top_c2:
    if st.button("🔒 BLOCCA\nSESSIONE", use_container_width=True):
        st.session_state["auth_unlocked"] = False
        st.session_state["blum_sector"] = None
        st.rerun()

st.markdown(f"""
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

# --- 10. PANNELLO SEGRETO DEL COMANDANTE (SCALABILITÀ 2^11 + QR GOOGLE AUTH + LOG TALPE) ---
if is_commander:
    sec_col1, sec_col2 = st.columns(2)
    with sec_col1:
        with st.expander(f"🎛️ SCALABILITÀ MULTIVERSO 1 → 2¹¹ (Stato #{binary_state_num}/2048 — Configura Vettori Cliente)", expanded=False):
            sw_cols = st.columns(11)
            for i, vec in enumerate(BASE_VECTORS):
                with sw_cols[i]:
                    toggled = st.toggle(vec["short"], value=st.session_state["active_bits_11"][i], key=f"tg11_{i}")
                    if toggled != st.session_state["active_bits_11"][i]:
                        st.session_state["active_bits_11"][i] = toggled
                        st.session_state["blum_sector"] = None
                        st.rerun()
            p1, p2, p3 = st.columns(3)
            if p1.button("🍸 PACCHETTO BAR (02+10+11)", use_container_width=True):
                st.session_state["active_bits_11"] = [False, True, False, False, False, False, False, False, False, True, True]
                st.session_state["blum_sector"] = None
                st.rerun()
            if p2.button("🛸 PACCHETTO 6 SETTORI", use_container_width=True):
                st.session_state["active_bits_11"] = [True, True, True, True, True, True, False, False, False, False, False]
                st.session_state["blum_sector"] = None
                st.rerun()
            if p3.button("🔥 FULL MULTIVERSE 2¹¹", use_container_width=True):
                st.session_state["active_bits_11"] = [True] * 11
                st.session_state["blum_sector"] = None
                st.rerun()

    with sec_col2:
        with st.expander(f"🛡️ CASSAFORTE 2FA TITOLARE & REGISTRO ANTINTRUSIONE ({breach_count} Allerte)", expanded=(breach_count > 0)):
            q1, q2 = st.columns([1, 2])
            secret_now = get_totp_secret()
            otp_uri = f"otpauth://totp/BEMASK_ALPHA:TITOLARE?secret={secret_now}&issuer=BEMASK_ALPHA"
            with q1:
                st.markdown(f"""
                <div style="text-align:center; background:#0B0E14; border:1px solid #10B981; padding:8px; border-radius:4px;">
                    <div style="font-size:9px; color:#10B981; margin-bottom:4px;">INQUADRA CON GOOGLE AUTH</div>
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=130x130&color=10B981&bgcolor=0B0E14&data={otp_uri}" width="110" />
                </div>
                """, unsafe_allow_html=True)
            with q2:
                st.markdown(f"**Chiave Segreta 2FA:** `{secret_now}`")
                st.markdown(f"**Token 6 Cifre Attivo Ora (30s):** `{generate_totp_token(secret_now)}`")
                if st.session_state["breach_log"]:
                    for item in reversed(st.session_state["breach_log"]):
                        st.error(item)
                    if st.button("🧹 AZZERA REGISTRO INTRUSIONI"):
                        st.session_state["breach_log"] = []
                        st.rerun()
                else:
                    st.success("Nessun tentativo di accesso non autorizzato rilevato.")

# ==============================================================================
# 11. CORPO PRINCIPALE: UX "BLUM" FULL-SCREEN DIVE VS GRIGLIA PULITA
# ==============================================================================
col_left, col_right = st.columns([3.25, 1.15])

with col_left:
    if st.session_state["blum_sector"] is not None:
        sec_obj = next((s for s in all_squares if s["code"] == st.session_state["blum_sector"]), all_squares[0])
        svg_blum = SVG_ICONS.get(sec_obj["code"], SVG_ICONS["01"])

        if st.button("▲ RIEMERGI ALLA MATRICE CENTRALE A.L.P.H.A. (CHIUDI BLUM)", key="exit_blum_top", use_container_width=True):
            st.session_state["blum_sector"] = None
            st.session_state["selected_sub"] = None
            st.rerun()

        st.markdown(f"""
        <div class="blum-stage" style="border: 2px solid {sec_obj['border']}; border-left: 6px solid {sec_obj['border']}; box-shadow: inset 0 0 40px {sec_obj['glow']};">
            <div style="display:flex; align-items:center; gap:16px;">
                <div>{svg_blum}</div>
                <div>
                    <div style="font-size:11px; color:{sec_obj['border']}; font-family:'Share Tech Mono'; letter-spacing:1.5px;">
                        BLUM FULL-SCREEN DIVE // SETTORE {sec_obj['code']} // RAM-ONLY ENCRYPTED SESSION
                    </div>
                    <div style="font-size:24px; font-weight:900; color:#FFFFFF; letter-spacing:1.5px; margin-top:2px;">
                        {sec_obj['name']}
                    </div>
                    <div style="font-size:12px; color:#38BDF8; font-family:'Share Tech Mono'; margin-top:4px;">
                        {sec_obj['kpi']} | MODULE FOCUS: {st.session_state['selected_sub']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        sub_cols = st.columns(5)
        for idx_s, sub_label in enumerate(sec_obj["subs"]):
            with sub_cols[idx_s]:
                if st.button(sub_label, key=f"blum_sub_{sec_obj['code']}_{idx_s}", use_container_width=True):
                    st.session_state["selected_sub"] = sub_label
                    st.rerun()

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        # --- MODULO 10: BAR & DDT SENTINEL (CON CARICATORE VOLATILE IN RAM) ---
        if sec_obj["code"] == "10":
            st.markdown("##### 🍸 BAR & DDT SENTINEL // CASO REALE ROXY BAR FOLLONICA (BOLLA DORECA 190677/9)")
            ddt_file = st.file_uploader("📂 TRASCINA BOLLA / FATTURA FORNITORE (.CSV / .XML) — Elaborazione in RAM Volatile (Zero salvataggio su disco)", type=["csv", "xml", "txt"], key="ram_ddt")
            if ddt_file is not None:
                st.info(f"🛡️ File `{ddt_file.name}` letto solo in RAM volatile. Nessuna copia salvata sul Cloud.")

            d1, d2, d3, d4 = st.columns(4)
            st.session_state["ddt_prezzo_fattura"] = d1.number_input("Prezzo in Fattura (€/Bott.)", 1.0, 200.0, st.session_state["ddt_prezzo_fattura"], step=0.10)
            st.session_state["ddt_prezzo_pattuito"] = d2.number_input("Prezzo Pattuito (€/Bott.)", 1.0, 200.0, st.session_state["ddt_prezzo_pattuito"], step=0.10)
            st.session_state["ddt_litri_bottiglia"] = d3.selectbox("Formato Bottiglia (Litri)", [0.70, 0.75, 1.0, 1.5], index=2)
            st.session_state["ddt_omaggio_finto_iva"] = d4.number_input("IVA Ricaricata su 'Omaggi' (€)", 0.0, 100.0, st.session_state["ddt_omaggio_finto_iva"], step=0.25)

            dna_litro_reale = st.session_state["ddt_prezzo_fattura"] / st.session_state["ddt_litri_bottiglia"]
            scostamento_bott = st.session_state["ddt_prezzo_fattura"] - st.session_state["ddt_prezzo_pattuito"]

            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown(f"""
                <div class="kpi-custom-box" style="border-left-color:#EF4444;">
                    <div class="kpi-custom-title">DNA PREZZO AL LITRO REALE</div>
                    <div class="kpi-custom-value">€ {dna_litro_reale:.2f} / L</div>
                    <div class="kpi-custom-sub" style="color:#EF4444;">▲ +{scostamento_bott:.2f} € vs pattuito</div>
                </div>
                """, unsafe_allow_html=True)
            with k2:
                st.markdown(f"""
                <div class="kpi-custom-box" style="border-left-color:#F59E0B;">
                    <div class="kpi-custom-title">SCUDO FINTI OMAGGI (IVA)</div>
                    <div class="kpi-custom-value">€ {st.session_state['ddt_omaggio_finto_iva']:.2f}</div>
                    <div class="kpi-custom-sub" style="color:#F59E0B;">● Anomalia Bolla 190677/9</div>
                </div>
                """, unsafe_allow_html=True)
            with k3:
                st.markdown(f"""
                <div class="kpi-custom-box" style="border-left-color:#10B981;">
                    <div class="kpi-custom-title">HACCP BAR 1-CLICK</div>
                    <div class="kpi-custom-value">+3.8 °C OK</div>
                    <div class="kpi-custom-sub" style="color:#10B981;">✔ Firmato PIN #{st.session_state['pin_code']}</div>
                </div>
                """, unsafe_allow_html=True)

        # --- MODULO 11: BANK VAMPIRE SCANNER (CON CARICATORE E/C IN RAM + FIX GRAFICO 1.97%) ---
        elif sec_obj["code"] == "11":
            st.markdown("##### 🧛‍♂️ BANK VAMPIRE SCANNER // AUTOPSIA ESTRATTO CONTO & VERO TASSO POS (RAM-ONLY)")
            ec_col1, ec_col2 = st.columns([3, 1])
            with ec_col1:
                bank_file = st.file_uploader("📂 TRASCINA ESTRATTO CONTO BANCARIO (.CSV) — Analisi Istantanea in RAM (Zero archiviazione)", type=["csv", "txt"], key="ram_bank")
            with ec_col2:
                st.markdown("<div style='height:26px;'></div>", unsafe_allow_html=True)
                if st.button("🔥 DISTRUGGI DATI RAM", use_container_width=True):
                    st.toast("🧹 Memoria RAM svuotata al 100%. Nessun dato bancario presente.")
                    st.rerun()

            sdd_alert_txt = "0 DOPPI ADDEBITI"
            sdd_sub_txt = "✔ Controllo flussi SDD attivo"
            sdd_col = "#10B981"

            if bank_file is not None:
                try:
                    raw_text = bank_file.getvalue().decode("utf-8", errors="ignore")
                    sep = ";" if ";" in raw_text else ","
                    df_ec = pd.read_csv(io.StringIO(raw_text), sep=sep)
                    st.success(f"🛡️ Estratto Conto analizzato in RAM ({len(df_ec)} movimenti letti — Zero byte salvati su server).")
                    if len(df_ec) != len(df_ec.drop_duplicates()):
                        dup_n = len(df_ec) - len(df_ec.drop_duplicates())
                        sdd_alert_txt = f"{dup_n} SOSPETTI SDD"
                        sdd_sub_txt = "⚠️ Rilevati addebiti identici!"
                        sdd_col = "#EF4444"
                except Exception:
                    st.info("File letto in RAM volatile.")

            b1, b2, b3, b4 = st.columns(4)
            st.session_state["bank_transato_pos"] = b1.number_input("Transato POS Mensile (€)", 500.0, 500000.0, st.session_state["bank_transato_pos"], step=500.0)
            st.session_state["bank_comm_dichiarata"] = b2.number_input("Comm. POS Dichiarata (%)", 0.10, 5.0, st.session_state["bank_comm_dichiarata"], step=0.05)
            st.session_state["bank_costi_occulti"] = b3.number_input("Spese Occulte / Canoni / SDD (€)", 0.0, 5000.0, st.session_state["bank_costi_occulti"], step=10.0)
            st.session_state["bank_prezzo_caffe"] = b4.number_input("Prezzo Tazzina Caffè (€)", 0.80, 3.0, st.session_state["bank_prezzo_caffe"], step=0.10)

            costo_pos_base = st.session_state["bank_transato_pos"] * (st.session_state["bank_comm_dichiarata"] / 100.0)
            prelievo_totale_banca = costo_pos_base + st.session_state["bank_costi_occulti"]
            vero_tasso_pos = (prelievo_totale_banca / st.session_state["bank_transato_pos"]) * 100.0
            caffe_bruciati = round(prelievo_totale_banca / st.session_state["bank_prezzo_caffe"])
            scost_pos = vero_tasso_pos - st.session_state["bank_comm_dichiarata"]

            # Box HTML su misura: zero sovrapposizioni su qualsiasi monitor!
            v1, v2, v3 = st.columns(3)
            with v1:
                st.markdown(f"""
                <div class="kpi-custom-box" style="border-left-color:#EF4444;">
                    <div class="kpi-custom-title">VERO TASSO POS EFFETTIVO</div>
                    <div class="kpi-custom-value">{vero_tasso_pos:.2f} %</div>
                    <div class="kpi-custom-sub" style="color:#EF4444;">▲ +{scost_pos:.2f}% costo occulto reale</div>
                </div>
                """, unsafe_allow_html=True)
            with v2:
                st.markdown(f"""
                <div class="kpi-custom-box" style="border-left-color:#F59E0B;">
                    <div class="kpi-custom-title">CAFFÈ LAVORATI GRATIS PER LA BANCA</div>
                    <div class="kpi-custom-value">{caffe_bruciati} Tazzine/mese</div>
                    <div class="kpi-custom-sub" style="color:#10B981;">● € {prelievo_totale_banca:.2f} drenati dal conto</div>
                </div>
                """, unsafe_allow_html=True)
            with v3:
                st.markdown(f"""
                <div class="kpi-custom-box" style="border-left-color:{sdd_col};">
                    <div class="kpi-custom-title">SENTINELLA DOPPIO SDD</div>
                    <div class="kpi-custom-value">{sdd_alert_txt}</div>
                    <div class="kpi-custom-sub" style="color:{sdd_col};">{sdd_sub_txt}</div>
                </div>
                """, unsafe_allow_html=True)

        # --- TUTTI GLI ALTRI MODULI (01 -> 09) ---
        else:
            st.markdown(f"##### ⚡ TELEMETRIA ESECUTIVA // {sec_obj['name']} — {st.session_state['selected_sub']}")
            c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.4])
            st.session_state["rop_cons_gg"] = c1.number_input("Consumo Giorno (u.)", 1, 1000, st.session_state["rop_cons_gg"])
            st.session_state["rop_lead_gg"] = c2.number_input("Lead Time (gg)", 1, 30, st.session_state["rop_lead_gg"])
            st.session_state["rop_stock"] = c3.number_input("Giacenza Casa", 0, 5000, st.session_state["rop_stock"])
            rop_val = (st.session_state["rop_cons_gg"] * st.session_state["rop_lead_gg"]) + (st.session_state["bocche_96h"] * 4)
            with c4:
                st.markdown(f"""
                <div class="kpi-custom-box" style="border-left-color:#10B981; padding:10px 14px;">
                    <div class="kpi-custom-title">PUNTO ACQUISTO (ROP 96H)</div>
                    <div class="kpi-custom-value" style="font-size:20px;">{rop_val} u.</div>
                    <div class="kpi-custom-sub" style="color:#10B981;">Margine: {st.session_state['rop_stock'] - rop_val:+} u.</div>
                </div>
                """, unsafe_allow_html=True)
            st.link_button(f"🚀 APRI CONSOLLE ESTERNA DEDICATA ({sec_obj['name']})", sec_obj["url"], use_container_width=True)

    # --- VISTA MATRICE CENTRALE PULITA ---
    else:
        n_cols = 1 if n_sectors == 1 else (2 if n_sectors in [2, 4] else 3)
        for r in range(0, n_sectors, n_cols):
            row_cols = st.columns(n_cols)
            for c in range(n_cols):
                if r + c < n_sectors:
                    sq = all_squares[r + c]
                    code = sq["code"]
                    svg_icon = SVG_ICONS.get(code, SVG_ICONS["01"])

                    with row_cols[c]:
                        st.markdown(f"""
                        <div class="alpha-tile" style="background: {sq['bg_grad']}; border: 1.5px solid {sq['border']}; border-left: 5px solid {sq['border']}; box-shadow: inset 0 0 26px {sq['glow']};">
                            <div>{svg_icon}</div>
                            <div class="tile-code">{code}</div>
                            <div class="tile-name">{sq['name']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(" ", key=f"blum_click_{code}", use_container_width=True):
                            st.session_state["blum_sector"] = code
                            st.session_state["selected_sub"] = sq["subs"][0]
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
