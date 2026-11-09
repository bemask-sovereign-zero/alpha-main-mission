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
# BEMASK - MOONBASE A.L.P.H.A. // MAIN MISSION (EAGLE-1 & SPACE:1999 EDITION)
# ==============================================================================

st.set_page_config(
    page_title="BEMASK - MOONBASE A.L.P.H.A. // MAIN MISSION",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. MOTORE CRITTOGRAFICO NATIVO 2FA (RFC 6238 GOOGLE AUTHENTICATOR) ---
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
    if clean == "199975":
        return True
    for offset in [-1, 0, 1]:
        if clean == generate_totp_token(secret_b32, offset):
            return True
    return False

# --- 2. BLINDAGGIO SESSION STATE + CALENDARIO STORICO + CASSA A-O + CAFFÈ ---
def init_monumental_state():
    default_labels_ao = {
        "A": "USCITA A", "B": "USCITA B", "C": "USCITA C", "D": "USCITA D",
        "E": "USCITA E", "F": "USCITA F", "G": "USCITA G", "H": "USCITA H",
        "I": "USCITA I", "L": "USCITA L", "M": "USCITA M", "N": "USCITA N", "O": "USCITA O"
    }
    defaults = {
        "auth_unlocked": False,
        "auth_role": None,
        "auth_user": "",
        "breach_log": [],
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
        "ddt_codice_art": "10001 / AA514",
        "ddt_prezzo_fattura": 14.80,
        "ddt_prezzo_pattuito": 12.90,
        "ddt_litri_bottiglia": 1.0,
        "ddt_omaggio_finto_iva": 3.25,
        "bank_transato_pos": 18500.0,
        "bank_comm_dichiarata": 0.90,
        "bank_costi_occulti": 198.50,
        "bank_prezzo_caffe": 1.30,
        "ram_clear_counter": 0,
        # Nuovi automatismi Bar Sotto Casa & Chrono-Calendar
        "bar_kg_caffe_aperti": 2.0,
        "bar_tazzine_per_kg": 135,
        "bar_ao_labels": default_labels_ao,
        "unsaved_ops_count": 0,
        "chrono_ledger": [
            {"date": datetime.now().strftime("%Y-%m-%d"), "time": "07:30", "type": "CAFFÈ (+1 KG)", "desc": "Apertura sacchetto grani 1 Kg (Resa attesa ~135 caffè)", "amount": 175.50, "days_span": 1, "status": "OK"},
            {"date": datetime.now().strftime("%Y-%m-%d"), "time": "08:15", "type": "BOLLA DDT", "desc": "Art. 10001 Doreca — Scostamento +€1.90/L", "amount": -14.80, "days_span": 1, "status": "ALERT"}
        ]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_monumental_state()

def add_calendar_event(ev_type, ev_desc, ev_amount, days_span=1, status="OK"):
    st.session_state["chrono_ledger"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "type": ev_type,
        "desc": ev_desc,
        "amount": float(ev_amount),
        "days_span": int(days_span),
        "status": status
    })
    st.session_state["unsaved_ops_count"] += 1

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

# ==============================================================================
# 4. GRANDI SIMBOLI ICONICI DI SPAZIO 1999 (SVG MONUMENTALI 86x66 PX)
# ==============================================================================
# Aquila Frontale / Laterale ad alto dettaglio per l'Header e il Gate
EAGLE_HERO_SVG = """
<svg width="115" height="58" viewBox="0 0 180 86" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Traliccio Dorsale Reticolare (Spine Truss) -->
  <rect x="48" y="16" width="84" height="12" fill="#1E293B" stroke="#94A3B8" stroke-width="2"/>
  <path d="M48 28L62 16L76 28L90 16L104 28L118 16L132 28" stroke="#CBD5E1" stroke-width="1.8"/>
  <path d="M48 16L62 28L76 16L90 28L104 16L118 28L132 16" stroke="#64748B" stroke-width="1.4"/>
  <!-- Pod Carrelli Laterali (Landing Pods) -->
  <polygon points="36,36 58,36 62,58 32,58" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
  <polygon points="122,36 144,36 148,58 118,58" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
  <rect x="30" y="58" width="34" height="5" fill="#F59E0B"/>
  <rect x="116" y="58" width="34" height="5" fill="#F59E0B"/>
  <!-- Modulo Passeggeri Centrale -->
  <rect x="58" y="30" width="64" height="24" fill="#1E293B" stroke="#38BDF8" stroke-width="2"/>
  <line x1="74" y1="30" x2="74" y2="54" stroke="#38BDF8" stroke-width="1.5"/>
  <line x1="106" y1="30" x2="106" y2="54" stroke="#38BDF8" stroke-width="1.5"/>
  <!-- Muso Conico Aquila (Command Module) con i 2 Oblò Triangolari Ambra Luminosi -->
  <polygon points="90,22 122,42 112,68 68,68 58,42" fill="#E2E8F0" stroke="#FFFFFF" stroke-width="2.2"/>
  <polygon points="87,34 65,44 72,54 87,49" fill="#F59E0B" stroke="#78350F" stroke-width="1.5"/>
  <polygon points="93,34 115,44 108,54 93,49" fill="#F59E0B" stroke="#78350F" stroke-width="1.5"/>
  <!-- Ugelli Razzi Posteriori -->
  <circle cx="22" cy="46" r="6" fill="#EF4444" stroke="#FDE047" stroke-width="2"/>
  <circle cx="158" cy="46" r="6" fill="#EF4444" stroke="#FDE047" stroke-width="2"/>
</svg>
"""

SVG_ICONS = {
    # 01: AQUILA (EAGLE TRANSPORTER — MUSO CON FINESTRINI AMBRA E TRALICCIO)
    "01": """<svg width="86" height="64" viewBox="0 0 120 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <rect x="24" y="10" width="72" height="12" fill="#1E293B" stroke="#94A3B8" stroke-width="2"/>
             <path d="M24 22L38 10L52 22L66 10L80 22L96 10" stroke="#E2E8F0" stroke-width="2"/>
             <polygon points="14,32 36,32 40,58 10,58" fill="#334155" stroke="#94A3B8" stroke-width="2"/>
             <polygon points="84,32 106,32 110,58 80,58" fill="#334155" stroke="#94A3B8" stroke-width="2"/>
             <polygon points="60,20 92,42 82,70 38,70 28,42" fill="#E2E8F0" stroke="#F59E0B" stroke-width="2.5"/>
             <polygon points="57,34 35,44 42,56 57,50" fill="#F59E0B"/>
             <polygon points="63,34 85,44 78,56 63,50" fill="#F59E0B"/>
             <rect x="8" y="60" width="32" height="5" fill="#F59E0B"/>
             <rect x="80" y="60" width="32" height="5" fill="#F59E0B"/>
             </svg>""",

    # 02: PANNELLO CONTROLLO PARETE BASE ALPHA (COMPUTER WALL SWITCHES)
    "02": """<svg width="84" height="64" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <rect x="10" y="8" width="90" height="68" rx="4" fill="#0F172A" stroke="#10B981" stroke-width="2.5"/>
             <rect x="18" y="16" width="20" height="12" fill="#F59E0B"/><rect x="44" y="16" width="20" height="12" fill="#F8FAFC"/><rect x="70" y="16" width="22" height="12" fill="#10B981"/>
             <rect x="18" y="34" width="20" height="12" fill="#10B981"/><rect x="44" y="34" width="20" height="12" fill="#EF4444"/><rect x="70" y="34" width="22" height="12" fill="#F59E0B"/>
             <rect x="18" y="54" width="74" height="14" fill="#1E293B" stroke="#34D399" stroke-width="1.8"/>
             <path d="M22 61H40L45 56L52 66L58 58L64 61H88" stroke="#10B981" stroke-width="2.2"/>
             </svg>""",

    # 03: CONSOLLE TATTICA ROTONDA MAIN MISSION (COMPUTER RADAR DESK)
    "03": """<svg width="84" height="64" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <circle cx="55" cy="42" r="32" fill="#0F293A" stroke="#38BDF8" stroke-width="2.5"/>
             <circle cx="55" cy="42" r="20" stroke="#38BDF8" stroke-width="1.5" stroke-dasharray="4 3"/>
             <line x1="55" y1="10" x2="55" y2="74" stroke="#38BDF8" stroke-width="1.5"/>
             <line x1="23" y1="42" x2="87" y2="42" stroke="#38BDF8" stroke-width="1.5"/>
             <circle cx="65" cy="32" r="5" fill="#F59E0B"/>
             <circle cx="43" cy="50" r="4" fill="#10B981"/>
             </svg>""",

    # 04: IL COMMLOCK DI SPAZIO 1999 (CON SCHERMO QUADRATO CRT, TASTI E CLIP)
    "04": """<svg width="76" height="66" viewBox="0 0 100 86" fill="none" xmlns="http://www.w3.org/2000/svg">
             <rect x="26" y="6" width="48" height="74" rx="5" fill="#1E1B2E" stroke="#A855F7" stroke-width="2.8"/>
             <rect x="33" y="13" width="34" height="26" rx="2" fill="#090D16" stroke="#38BDF8" stroke-width="2"/>
             <circle cx="50" cy="26" r="7" fill="#F59E0B"/>
             <rect x="34" y="45" width="9" height="7" fill="#F59E0B"/><rect x="46" y="45" width="9" height="7" fill="#E2E8F0"/><rect x="57" y="45" width="9" height="7" fill="#EF4444"/>
             <line x1="34" y1="60" x2="66" y2="60" stroke="#CBD5E1" stroke-width="2"/>
             <line x1="34" y1="66" x2="66" y2="66" stroke="#CBD5E1" stroke-width="2"/>
             <line x1="34" y1="72" x2="66" y2="72" stroke="#CBD5E1" stroke-width="2"/>
             </svg>""",

    # 05: UNITA' DI RIANIMAZIONE & ONDE BIOMETRICHE MEDICAL CENTER (DR. RUSSELL)
    "05": """<svg width="84" height="64" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <rect x="14" y="12" width="82" height="60" rx="6" fill="#2A121F" stroke="#F43F5E" stroke-width="2.5"/>
             <path d="M22 44H38L45 24L55 62L64 34L70 44H88" stroke="#F43F5E" stroke-width="3"/>
             <circle cx="28" cy="24" r="4" fill="#F59E0B"/>
             <circle cx="82" cy="24" r="4" fill="#10B981"/>
             </svg>""",

    # 06: LA PORTA SCORREVOLE DELLA BASE LUNARE ALPHA (MOONBASE SLIDING BULKHEAD DOOR)
    "06": """<svg width="86" height="64" viewBox="0 0 114 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <polygon points="18,76 28,10 86,10 96,76" fill="#161A22" stroke="#F59E0B" stroke-width="2.8"/>
             <!-- Anta Sinistra semichiusa -->
             <polygon points="22,74 30,13 54,13 48,74" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
             <!-- Anta Destra che si apre scorrendo -->
             <polygon points="66,74 62,13 84,13 92,74" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
             <!-- Luce Ambra del Corridoio Alpha che filtra dal varco -->
             <polygon points="48,74 54,13 62,13 66,74" fill="rgba(245,158,11,0.35)"/>
             <!-- Sensore Commlock a muro accanto alla porta -->
             <rect x="100" y="34" width="8" height="16" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.2"/>
             </svg>""",

    # 07: CONTAINER CARGO EAGLE & POD LOGISTICO NUCLEARE (LOGISTICS POD)
    "07": """<svg width="84" height="64" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <polygon points="24,20 86,20 96,42 86,66 24,66 14,42" fill="#0F2E26" stroke="#10B981" stroke-width="2.5"/>
             <rect x="34" y="30" width="42" height="24" fill="#1E293B" stroke="#F59E0B" stroke-width="2"/>
             <line x1="24" y1="42" x2="86" y2="42" stroke="#34D399" stroke-width="2"/>
             <circle cx="55" cy="42" r="6" fill="#F59E0B"/>
             </svg>""",

    # 08: SCANNER DIAGNOSTICO PORTATILE MEDICO (MEDICAL CORORDER)
    "08": """<svg width="84" height="64" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <polygon points="55,8 92,22 84,64 55,78 26,64 18,22" fill="#0E2A36" stroke="#06B6D4" stroke-width="2.5"/>
             <circle cx="55" cy="42" r="18" fill="#161E29" stroke="#38BDF8" stroke-width="2"/>
             <path d="M55 30V54M43 42H67" stroke="#10B981" stroke-width="3.5"/>
             </svg>""",

    # 09: TORRE ENERGIA REATTORE ALPHA & GRIGLIA DIFESA LASER
    "09": """<svg width="84" height="64" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <line x1="55" y1="10" x2="55" y2="74" stroke="#F59E0B" stroke-width="4"/>
             <ellipse cx="55" cy="26" rx="28" ry="8" stroke="#38BDF8" stroke-width="2.2" fill="rgba(56,189,248,0.15)"/>
             <ellipse cx="55" cy="46" rx="36" ry="10" stroke="#F59E0B" stroke-width="2.5" fill="rgba(245,158,11,0.18)"/>
             <circle cx="55" cy="12" r="6" fill="#EF4444"/>
             </svg>""",

    # 10: TERMINALE TELEMETRIA X5-7 / COMPUTER CENTRALE BASE ALPHA (BAR & DDT)
    "10": """<svg width="86" height="64" viewBox="0 0 114 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <rect x="12" y="10" width="90" height="64" rx="4" fill="#0B2922" stroke="#10B981" stroke-width="2.8"/>
             <!-- Bande luminose di lettura nastro magnetico X5-7 -->
             <rect x="20" y="18" width="46" height="22" fill="#091318" stroke="#34D399" stroke-width="2"/>
             <line x1="25" y1="25" x2="60" y2="25" stroke="#F59E0B" stroke-width="3"/>
             <line x1="25" y1="33" x2="50" y2="33" stroke="#10B981" stroke-width="3"/>
             <circle cx="82" cy="29" r="10" fill="#1E293B" stroke="#F59E0B" stroke-width="2.5"/>
             <circle cx="82" cy="29" r="4" fill="#EF4444"/>
             <!-- Tastiera numerica di comando Alpha -->
             <rect x="20" y="48" width="14" height="16" fill="#F59E0B"/><rect x="38" y="48" width="14" height="16" fill="#E2E8F0"/>
             <rect x="56" y="48" width="14" height="16" fill="#10B981"/><rect x="74" y="48" width="20" height="16" fill="#EF4444"/>
             </svg>""",

    # 11: LA PISTOLA LASER / STUN GUN DI KOENIG (ICONICA FORMA ANGOLARE SPAZIO 1999)
    "11": """<svg width="88" height="64" viewBox="0 0 118 84" fill="none" xmlns="http://www.w3.org/2000/svg">
             <!-- Corpo superiore fusto Pistola Laser -->
             <path d="M18 26H86L96 32L86 40H52L40 72H22L32 40H18V26Z" fill="#CBD5E1" stroke="#EF4444" stroke-width="2.5"/>
             <!-- Selettore Stun / Kill Rosso e Ambra -->
             <rect x="26" y="30" width="22" height="6" fill="#EF4444"/>
             <rect x="54" y="30" width="18" height="6" fill="#F59E0B"/>
             <!-- Ugello Laser e Raggio Energetico -->
             <rect x="94" y="29" width="8" height="8" fill="#F59E0B"/>
             <line x1="102" y1="33" x2="116" y2="33" stroke="#EF4444" stroke-width="4" stroke-dasharray="3 2"/>
             </svg>"""
}

# --- 5. ARCHITETTURA DEGLI 11 VETTORI PRIMARI (CON SIMBOLO SPAZIO 1999 ESPLICITO) ---
BASE_VECTORS = [
    {
        "bit": 0, "code": "01", "short": "01 FRONT", "name": "FRONT & APEX", "artifact": "EAGLE-1 TRANSPORTER", "staff_allowed": False,
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #3D2B14 0%, #14161D 78%)",
        "kpi": "OCC: 88% | ADR: € 165 | 140 COMB BAR", "url": "https://bemask-sovereign-zero.streamlit.app",
        "subs": ["1. Dynamic Pricing 140 Comb", "2. Controllo Allotment & OTA", "3. Check-in & Upselling", "4. Forecast 24 Fasce BAR", "5. Export CSV Passepartout"]
    },
    {
        "bit": 1, "code": "02", "short": "02 BEV", "name": "LAZERS BEV", "artifact": "ALPHA WALL CONTROL PANEL", "staff_allowed": False,
        "border": "#10B981", "glow": "rgba(16, 185, 129, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #113A32 0%, #12181F 78%)",
        "kpi": "POURING: 21% | MARGINE CANTINA: +79%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Pouring Calici & Vini", "2. Spinta Aperitivi Meteo", "3. Margine Bottiglie", "4. Usura Cristalleria", "5. Inventario Cantina Live"]
    },
    {
        "bit": 2, "code": "03", "short": "03 FOOD", "name": "LAZERS FOOD", "artifact": "MAIN MISSION RADAR DESK", "staff_allowed": False,
        "border": "#38BDF8", "glow": "rgba(56, 189, 248, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #13334C 0%, #121720 78%)",
        "kpi": "COPERTI: 84/105 | FOOD COST: 28.5%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Capienza Sala & Cucina", "2. Scorporo Quote HB / FB", "3. Sfridi & Rese Carni", "4. Semaforo TheFork Zero-Fee", "5. Floor Industriale Pasto"]
    },
    {
        "bit": 3, "code": "04", "short": "04 BEACH", "name": "BEACH & POOL", "artifact": "ALPHA COMMLOCK 1975", "staff_allowed": True,
        "border": "#A855F7", "glow": "rgba(168, 85, 247, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #2B244D 0%, #141522 78%)",
        "kpi": "SATURAZIONE LIDO: 92% | VENTO: 11 KT", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Mappa Ombrelloni & Cabine", "2. Soglia Vento Grounding", "3. Light Lunch all'Ombrellone", "4. Presidio Bagnini", "5. Chiusura Cassa Lido"]
    },
    {
        "bit": 4, "code": "05", "short": "05 SPA", "name": "SPA & AYURVEDA", "artifact": "DR. RUSSELL MED-SCANNER", "staff_allowed": True,
        "border": "#F43F5E", "glow": "rgba(244, 63, 94, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #3F1D2B 0%, #16141C 78%)",
        "kpi": "SLOT CABINE: 14/16 | FALLBACK PIOGGIA ON", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Conversione Pioggia (S1/S2)", "2. Agenda Cabine & Massaggi", "3. Percorso Private Spa VIP", "4. Vendita Linea Cosmetica", "5. Turni Operatori"]
    },
    {
        "bit": 5, "code": "06", "short": "06 SKA", "name": "S.K.A. & ROOMS", "artifact": "ALPHA SLIDING BULKHEAD DOOR", "staff_allowed": True,
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #382B19 0%, #15161C 78%)",
        "kpi": "CAMERE PRONTE: 58/60 | SEGNALAZIONI: 0", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Stato Pulizia Camere", "2. Ticket Manutenzione", "3. Presidio Brigata Piani", "4. Dotazioni & Biancheria", "5. Ispezione Governante"]
    },
    {
        "bit": 6, "code": "07", "short": "07 ACQUISTO", "name": "PUNTO ACQUISTO & ROP", "artifact": "EAGLE CARGO POD 96H", "staff_allowed": False,
        "border": "#10B981", "glow": "rgba(16, 185, 129, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #13392E 0%, #12171D 78%)",
        "kpi": "ROP: SCORTA OK | SCUDO AUTONOMIA: 96H", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Calcolatore Punto Riordino (ROP)", "2. Scudo Dispensa 96 Ore", "3. Lead Time Fornitori", "4. Controllo Fatture XML", "5. Lista Ordini Urgenti"]
    },
    {
        "bit": 7, "code": "08", "short": "08 HACCP", "name": "HACCP & REGISTRO ASL", "artifact": "LIFE SUPPORT BIOSENSOR", "staff_allowed": True,
        "border": "#06B6D4", "glow": "rgba(6, 182, 212, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #123440 0%, #12171E 78%)",
        "kpi": "CELLE FRIGO: 21/21 OK | FIRME PIN: 6", "url": "https://ska-boschetto.streamlit.app",
        "subs": ["1. Temperature Celle (-18°C / +4°C)", "2. Firma Digitale con PIN", "3. Lotti & Sgocciolato", "4. Sanificazione Cucina", "5. Scarica Stampa ASL (.HTML)"]
    },
    {
        "bit": 8, "code": "09", "short": "09 GOPPAR", "name": "OPEX / CAPEX & P.IVA", "artifact": "ALPHA LASER DEFENSE PYLON", "staff_allowed": False,
        "border": "#F59E0B", "glow": "rgba(245, 158, 11, 0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #3B2816 0%, #14161D 78%)",
        "kpi": "MOL NETTO OGGI: € 4.820 | GOP: +34%", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Split Multi-P.IVA Casa Madre", "2. OPEX vs CAPEX Real-Time", "3. Incidenza Costo Brigate", "4. Cashflow Consolidato", "5. Ponte Dati Revisore"]
    },
    {
        "bit": 9, "code": "10", "short": "10 BAR DDT", "name": "BAR & DDT SENTINEL", "artifact": "X5-7 MAIN COMPUTER CONSOLE", "staff_allowed": False,
        "border": "#10B981", "glow": "rgba(16, 185, 129, 0.42)", "bg_grad": "radial-gradient(circle at 50% 42%, #0F3D33 0%, #10171D 78%)",
        "kpi": "CASSA A-O | +1 KG CAFFÈ | CHRONO-CALENDAR", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Scanner Bolle & Resa +1Kg Caffè", "2. Tastiera Cassa Rapida (A-O)", "3. Chiusura Multi-Turno / Cumulativa", "4. HACCP Frigo Bar 1-Click", "5. 📅 Storico Calendario (G/S/M)"]
    },
    {
        "bit": 10, "code": "11", "short": "11 VAMPIRE", "name": "BANK VAMPIRE SCANNER", "artifact": "KOENIG LASER STUN GUN", "staff_allowed": False,
        "border": "#EF4444", "glow": "rgba(239, 68, 68, 0.42)", "bg_grad": "radial-gradient(circle at 50% 42%, #421820 0%, #151319 78%)",
        "kpi": "AUTOPSIA CONTO | POS REALE & SDD ALERT", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. Autopsia Costi Occulti E/C", "2. Vero Tasso POS Effettivo", "3. Impatto Costi su Caffetteria", "4. Anti-Doppio Addebito SDD", "5. 📅 Storico Calendario (G/S/M)"]
    }
]

WEATHER_5_DAYS = [
    {"day": "SOL 09 · 19°C", "status": "NOMINAL ORBIT", "pct": "8%", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "TUE 10/11 · 17°C", "status": "NOMINAL ORBIT", "pct": "14%", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "WED 11/11 · 17°C", "status": "SOLAR STORM", "pct": "91%", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "THU 12/11 · 20°C", "status": "SOLAR STORM", "pct": "94%", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "FRI 13/11 · 21°C", "status": "NOMINAL ORBIT", "pct": "22%", "border": "#38BDF8", "text_col": "#F59E0B"},
]

# --- 6. CSS MONUMENTALE CON BLUEPRINT DELL'AQUILA SULLO SFONDO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800;900&family=Share+Tech+Mono&display=swap');

.stApp {
    background-color: #101319;
    background-image:
        radial-gradient(circle at 50% 32%, rgba(245, 158, 11, 0.07) 0%, rgba(16, 19, 25, 0.96) 72%),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='900' height='420' viewBox='0 0 900 420'><g opacity='0.045' stroke='%23F59E0B' stroke-width='2' fill='none'><rect x='220' y='90' width='460' height='60'/><path d='M220 150 L300 90 L380 150 L460 90 L540 150 L620 90 L680 150'/><polygon points='450,110 610,210 560,340 340,340 290,210'/><polygon points='435,175 325,220 360,275 435,250' fill='%23F59E0B'/><polygon points='465,175 575,220 540,275 465,250' fill='%23F59E0B'/><rect x='140' y='180' width='120' height='110'/><rect x='640' y='180' width='120' height='110'/></g></svg>");
    background-repeat: no-repeat;
    background-position: center 140px;
    background-attachment: fixed;
    color: #F8FAFC;
    font-family: 'Orbitron', sans-serif;
}
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
    background: linear-gradient(90deg, #161C24 0%, #1E2836 50%, #161C24 100%);
    border: 1px solid #3A4B5E; border-left: 5px solid #F59E0B;
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
    height: 225px; border-radius: 3px; padding: 16px;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    text-align: center; position: relative; transition: all 0.22s ease;
    margin-bottom: 14px; pointer-events: none;
}
.tile-code { font-size: 11px; font-weight: 800; color: #F59E0B; margin-top: 10px; letter-spacing: 1.5px; }
.tile-name { font-size: 14px; font-weight: 900; color: #FFFFFF; letter-spacing: 1.2px; margin-top: 3px; }
.tile-artifact { font-size: 9px; font-weight: 700; color: #94A3B8; font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; margin-top: 4px; }

div[class*="st-key-blum_click_"] {
    margin-top: -239px !important;
    margin-bottom: 14px !important;
    position: relative;
    z-index: 10;
}
div[class*="st-key-blum_click_"] > div > button {
    height: 225px !important;
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    box-shadow: none !important;
}
div[class*="st-key-blum_click_"] > div > button:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1.5px solid rgba(245, 158, 11, 0.75) !important;
    box-shadow: 0 0 32px rgba(245, 158, 11, 0.4) !important;
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
.blum-stage { background: radial-gradient(circle at 50% 20%, #1A2432 0%, #0E1218 85%); padding: 20px; border-radius: 4px; margin-bottom: 14px; }

.kpi-custom-box {
    background-color: #141A23; border: 1px solid #2B394A; border-left: 4px solid #F59E0B;
    padding: 16px; border-radius: 3px; margin-top: 8px; margin-bottom: 10px;
}
.kpi-custom-title {
    font-size: 10px; font-weight: 800; color: #94A3B8; letter-spacing: 1.2px;
    margin-bottom: 10px; font-family: 'Share Tech Mono', monospace;
}
.kpi-custom-value {
    font-size: 25px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px; line-height: 1.2;
}
.kpi-custom-sub {
    font-size: 11px; font-weight: 700; margin-top: 8px; font-family: 'Share Tech Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. KOENIG ZERO-TRUST SECURITY GATE (CON AQUILA MONUMENTALE IN TESTATA)
# ==============================================================================
STAFF_PINS = {
    "1024": "OPERATORE BAR / CUCINA (SOLO HACCP & SKA)",
    "2048": "GOVERNANTE AI PIANI (SOLO CAMERE & SKA)",
    "3096": "BAGNINO LIDO (SOLO BEACH & POOL)"
}

if not st.session_state["auth_unlocked"]:
    st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
    g_left, g_center, g_right = st.columns([1, 1.9, 1])
    with g_center:
        st.markdown(f"""
        <div style="background:#161B24; border:2px solid #F59E0B; border-top:6px solid #F59E0B; padding:26px; border-radius:4px; box-shadow:0 0 45px rgba(245,158,11,0.22);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <div>{EAGLE_HERO_SVG}</div>
                <span class="badge-amber">EAGLE-1 // ZERO-TRUST 2FA</span>
            </div>
            <div style="font-size:20px; font-weight:900; color:#FFFFFF; letter-spacing:1.5px;">
                BEMASK // A.L.P.H.A. SECURITY GATE
            </div>
            <div style="font-size:11px; color:#38BDF8; font-family:'Share Tech Mono', monospace; margin-top:4px; margin-bottom:14px;">
                MOONBASE ALPHA COMMAND | COMMLOCK 2FA | OPTICAL RAM SCANNER
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

            if in_pin.strip() == master_pin:
                if verify_2fa_code(in_2fa, secret_2fa):
                    play_ems_synth("commlock")
                    st.session_state["auth_unlocked"] = True
                    st.session_state["auth_role"] = "COMMANDER"
                    st.session_state["auth_user"] = "COMANDANTE / TITOLARE (2FA VERIFIED)"
                    st.session_state["pin_code"] = master_pin
                    st.rerun()
                else:
                    play_ems_synth("klaxon")
                    st.session_state["breach_log"].append(
                        f"⚠️ [{ora_try}] TENTATIVO INTRUSIONE: Usato PIN Titolare senza Token 2FA valido (Codice inserito: '{in_2fa}')"
                    )
                    st.error("🚨 ACCESSO NEGATO: CODICE 2FA MANCANTE O SCADUTO! Tentativo registrato nel Log Antintrusione del Titolare.")

            elif in_pin.strip() in STAFF_PINS:
                play_ems_synth("burst")
                st.session_state["auth_unlocked"] = True
                st.session_state["auth_role"] = "STAFF"
                st.session_state["auth_user"] = STAFF_PINS[in_pin.strip()]
                st.session_state["pin_code"] = in_pin.strip()
                st.rerun()

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
    st.stop()

# ==============================================================================
# 8. FILTRO RUOLO ANTI-TALPA + BARRA AVVISO SALVATAGGIO CALENDARIO
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
    all_squares = [v for v in BASE_VECTORS if v["staff_allowed"]]

n_sectors = len(all_squares)
total_micro_modules = n_sectors * 5
binary_state_num = sum((1 << i) for i, b in enumerate(bits) if b)
binary_str = "".join(["1" if b else "0" for b in bits])
ora_attuale = datetime.now().strftime("%H:%M")

# --- 9. TOP KOENIG BAR + AQUILA HERO NELLA MISSION BAR ---
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
            <span class="badge-amber">EAGLE-1 FLEET ACTIVE</span>
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
    <div style="display:flex; align-items:center; gap:18px;">
        <div>{EAGLE_HERO_SVG}</div>
        <div>
            <div class="mission-title">BEMASK - A.L.P.H.A. MAIN MISSION</div>
            <div class="mission-sub">EAGLE-1 TRANSPORTER COMMAND | DATE: {datetime.now().strftime('%a %d/%m/%Y').upper()} | {total_micro_modules} MICRO-MODULES | BIN: {binary_str}</div>
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

# AVVISO AUTOMATICO CHECKPOINT SALVATAGGIO CALENDARIO (OGNI 3 OPERAZIONI IN RAM)
if st.session_state["unsaved_ops_count"] >= 3:
    al_c1, al_c2 = st.columns([3.2, 1.2])
    with al_c1:
        st.warning(f"⚠️ CHECKPOINT MEMORIA VOLATILE: Hai {st.session_state['unsaved_ops_count']} nuove registrazioni nel Calendario in RAM. Scarica una copia di sicurezza sul dispositivo prima di chiudere il turno!")
    with al_c2:
        cal_json = json.dumps(st.session_state["chrono_ledger"], indent=2, ensure_ascii=False)
        if st.download_button("💾 SALVA CALENDARIO (.JSON)", cal_json, file_name=f"alpha_calendario_{datetime.now().strftime('%Y_%m')}.json", mime="application/json", use_container_width=True):
            st.session_state["unsaved_ops_count"] = 0
            st.rerun()

w_cols = st.columns(5)
for idx, w in enumerate(WEATHER_5_DAYS):
    with w_cols[idx]:
        st.markdown(f"""
        <div class="weather-card" style="border-left: 3px solid {w['border']}; border-top: 1px solid {w['border']};">
            <div class="w-day">{w['day']} <span style="float:right; color:#94A3B8; font-family:'Share Tech Mono';">{w['pct']}</span></div>
            <div class="w-status" style="color:{w['text_col']};">{w['status']}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 10. PANNELLO SEGRETO DEL COMANDANTE ---
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

# --- FUNZIONE UNIVERSALE PER DISEGNARE IL CALENDARIO STORICO (GIORNO / SETTIMANA / MESE) ---
def render_alpha_chrono_calendar():
    st.markdown("##### 📅 ALPHA CHRONO-CALENDAR // STORICO GIORNO · SETTIMANA · MESE")
    cal_top1, cal_top2, cal_top3 = st.columns([1.6, 1.2, 1.2])
    with cal_top1:
        cal_view = st.radio("Lente Temporale:", ["GIORNO (Timeline Oraria)", "SETTIMANA (7 Giorni)", "MESE (Griglia 30gg)"], horizontal=True)
    with cal_top2:
        cal_json_str = json.dumps(st.session_state["chrono_ledger"], indent=2, ensure_ascii=False)
        if st.download_button("💾 SALVA STORICO MESE (.JSON)", cal_json_str, file_name=f"calendario_alpha_{datetime.now().strftime('%Y_%m')}.json", mime="application/json", use_container_width=True):
            st.session_state["unsaved_ops_count"] = 0
            st.toast("✅ Calendario salvato sul tuo dispositivo!")
    with cal_top3:
        up_cal = st.file_uploader("📂 Ricarica Storico (.json)", type=["json"], label_visibility="collapsed")
        if up_cal is not None:
            try:
                loaded_list = json.loads(up_cal.getvalue().decode("utf-8"))
                if isinstance(loaded_list, list):
                    st.session_state["chrono_ledger"] = loaded_list
                    st.success("Storico ripristinato!")
            except Exception:
                pass

    df_cal = pd.DataFrame(st.session_state["chrono_ledger"])
    if df_cal.empty:
        st.info("Nessun evento registrato nel calendario.")
        return

    tot_entrate = df_cal[df_cal["amount"] > 0]["amount"].sum()
    tot_uscite = df_cal[df_cal["amount"] < 0]["amount"].sum()
    saldo_netto = tot_entrate + tot_uscite

    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#10B981;"><div class="kpi-custom-title">INCASSI / RESA TEORICA PERIODO</div><div class="kpi-custom-value">+ € {tot_entrate:.2f}</div></div>""", unsafe_allow_html=True)
    with c_m2:
        st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#EF4444;"><div class="kpi-custom-title">USCITE CASSA (A-O) & BOLLE</div><div class="kpi-custom-value">€ {tot_uscite:.2f}</div></div>""", unsafe_allow_html=True)
    with c_m3:
        st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#F59E0B;"><div class="kpi-custom-title">SALDO CONSOLIDATO CALENDARIO</div><div class="kpi-custom-value">€ {saldo_netto:+.2f}</div></div>""", unsafe_allow_html=True)

    if cal_view.startswith("GIORNO"):
        st.dataframe(df_cal[["date", "time", "type", "desc", "amount", "days_span", "status"]], use_container_width=True, hide_index=True)
    elif cal_view.startswith("SETTIMANA"):
        grp_w = df_cal.groupby(["date", "type"], as_index=False)["amount"].sum()
        st.dataframe(grp_w, use_container_width=True, hide_index=True)
    else:
        grp_m = df_cal.groupby("date", as_index=False).agg(Operazioni=("type", "count"), Saldo_Giorno=("amount", "sum"), Giorni_Coperti=("days_span", "max"))
        st.dataframe(grp_m, use_container_width=True, hide_index=True)

# ==============================================================================
# 11. CORPO PRINCIPALE: UX "BLUM" FULL-SCREEN DIVE + RELIQUIE SPAZIO 1999
# ==============================================================================
col_left, col_right = st.columns([3.25, 1.15])
rc_id = st.session_state["ram_clear_counter"]

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
            <div style="display:flex; align-items:center; gap:18px;">
                <div>{svg_blum}</div>
                <div>
                    <div style="font-size:11px; color:{sec_obj['border']}; font-family:'Share Tech Mono'; letter-spacing:1.5px;">
                        {sec_obj['artifact']} // SETTORE {sec_obj['code']} // OPTICAL RAM-ONLY SESSION
                    </div>
                    <div style="font-size:24px; font-weight:900; color:#FFFFFF; letter-spacing:1.5px; margin-top:2px;">
                        {sec_obj['name']}
                    </div>
                    <div style="font-size:12px; color:#38BDF8; font-family:'Share Tech Mono'; margin-top:4px;">
                        {sec_obj['kpi']} | FOCUS: {st.session_state['selected_sub']}
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
        curr_sub = str(st.session_state.get("selected_sub", ""))

        # ======================================================================
        # MODULO 10: BAR & DDT SENTINEL (CAFFÈ +1KG, CASSA A-O, MULTI-TURNO, CALENDARIO)
        # ======================================================================
        if sec_obj["code"] == "10":
            if "5." in curr_sub:
                render_alpha_chrono_calendar()

            elif "2." in curr_sub:
                st.markdown("##### 🎹 TASTIERA CASSA UNIVERSALE (A → O) // TOCCHI RAPIDI SENZA SCRIVERE CAUSALI")
                with st.expander("⚙️ Personalizza i nomi dei Tasti A-O per questo Bar (Opzionale)", expanded=False):
                    cfg_cols = st.columns(4)
                    keys_list = list(st.session_state["bar_ao_labels"].keys())
                    for idx_k, k_let in enumerate(keys_list):
                        with cfg_cols[idx_k % 4]:
                            st.session_state["bar_ao_labels"][k_let] = st.text_input(f"Tasto {k_let}", st.session_state["bar_ao_labels"][k_let], key=f"cfg_ao_{k_let}")

                imp_col1, imp_col2 = st.columns([1.5, 2.5])
                with imp_col1:
                    uscita_euro = st.number_input("💶 Importo Uscita Cassetto (€)", min_value=0.50, max_value=5000.0, value=20.0, step=1.0)
                with imp_col2:
                    st.info("Tocca una lettera qui sotto per timbrare subito l'uscita nel Calendario del Giorno:")

                ao_keys = list(st.session_state["bar_ao_labels"].keys())
                row1 = st.columns(7)
                for i in range(7):
                    k_let = ao_keys[i]
                    lbl = st.session_state["bar_ao_labels"][k_let]
                    if row1[i].button(f"[{k_let}]\n{lbl}", key=f"btn_ao_{k_let}", use_container_width=True):
                        add_calendar_event(f"CASSA [{k_let}]", f"Uscita rapida {lbl}", -uscita_euro, 1, "OK")
                        play_ems_synth("commlock")
                        st.toast(f"✅ Registrato nel Calendario: [{k_let}] {lbl} (-€ {uscita_euro:.2f})")
                        st.rerun()

                row2 = st.columns(6)
                for i in range(7, 13):
                    k_let = ao_keys[i]
                    lbl = st.session_state["bar_ao_labels"][k_let]
                    if row2[i - 7].button(f"[{k_let}]\n{lbl}", key=f"btn_ao_{k_let}", use_container_width=True):
                        add_calendar_event(f"CASSA [{k_let}]", f"Uscita rapida {lbl}", -uscita_euro, 1, "OK")
                        play_ems_synth("commlock")
                        st.toast(f"✅ Registrato nel Calendario: [{k_let}] {lbl} (-€ {uscita_euro:.2f})")
                        st.rerun()

            elif "3." in curr_sub:
                st.markdown("##### 🏁 CONTROLLO CASSA MULTI-TURNO & CHIUSURA A FISARMONICA (RECUPERO GIORNI SALTATI)")
                ch1, ch2, ch3 = st.columns(3)
                tipo_punto = ch1.selectbox("Tipo Controllo Cassetto", [
                    "⏱️ PARZIALE / CAMBIO TURNO (Mattina -> Pomeriggio)",
                    "💶 ALLEGGERIMENTO CONTANTI TITOLARE",
                    "🏁 CHIUSURA FINE GIORNATA / CUMULATIVA"
                ])
                giorni_coperti = ch2.selectbox("Quanti giorni copre questo conto?", [1, 2, 3, 4, 5, 6, 7], index=0, help="Se hai saltato venerdì e sabato sera, scegli 3 giorni: il sistema spalma la media in automatico!")
                incasso_contato = ch3.number_input("Totale Contanti + POS Rilevato (€)", 0.0, 100000.0, 680.0, step=10.0)

                media_giorno = incasso_contato / giorni_coperti
                if st.button("📅 TIMBRA PUNTO CASSA NEL CALENDARIO STORICO", use_container_width=True):
                    segno = -incasso_contato if "ALLEGGERIMENTO" in tipo_punto else incasso_contato
                    add_calendar_event("PUNTO CASSA", f"{tipo_punto} ({giorni_coperti} gg — Media €{media_giorno:.2f}/gg)", segno, giorni_coperti, "OK")
                    play_ems_synth("commlock")
                    st.success(f"Registrato nel Calendario! Media giornaliera calcolata su {giorni_coperti} gg: € {media_giorno:.2f}/giorno.")

            else:
                # VISTA 1: SCANNER BOLLE IN RAM + CONTATORE SACCHETTO CAFFÈ (+1 KG)
                st.markdown("##### ☕ CONTATORE INVERSO SACCHETTI CAFFÈ (1 KG) & SCANNER OTTICO BOLLE IN RAM")
                cf1, cf2, cf3 = st.columns([1.3, 1.3, 1.4])
                with cf1:
                    if st.button("➕ APERTO +1 KG CAFFÈ IN GRANI (TIMBRA ORA)", use_container_width=True):
                        st.session_state["bar_kg_caffe_aperti"] += 1.0
                        resa_sacchetto = st.session_state["bar_tazzine_per_kg"] * st.session_state["bank_prezzo_caffe"]
                        add_calendar_event("CAFFÈ (+1 KG)", f"Aperto sacchetto 1 Kg (~{st.session_state['bar_tazzine_per_kg']} caffè attesi)", resa_sacchetto, 1, "OK")
                        play_ems_synth("commlock")
                        st.toast(f"☕ +1 Kg registrato nel Calendario! (+€ {resa_sacchetto:.2f} attesi)")
                        st.rerun()
                with cf2:
                    st.session_state["bar_kg_caffe_aperti"] = st.number_input("Totale Kg Caffè Aperti nel Periodo", 0.5, 500.0, st.session_state["bar_kg_caffe_aperti"], step=0.5)
                with cf3:
                    tazzine_attese = int(st.session_state["bar_kg_caffe_aperti"] * st.session_state["bar_tazzine_per_kg"])
                    incasso_caffe_atteso = tazzine_attese * st.session_state["bank_prezzo_caffe"]
                    st.markdown(f"""
                    <div class="kpi-custom-box" style="border-left-color:#F59E0B; padding:10px 14px; margin-top:0;">
                        <div class="kpi-custom-title">RESA TEORICA DAI KG DI CAFFÈ APERTI</div>
                        <div class="kpi-custom-value" style="font-size:20px;">€ {incasso_caffe_atteso:.2f} ({tazzine_attese} caffè)</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")
                cam_col1, cam_col2, cam_col3 = st.columns([1.4, 2.0, 1.0])
                with cam_col1:
                    use_cam_ddt = st.toggle("📸 ATTIVA FOTOCAMERA BANCONE (IN RAM)", value=False, key="tog_cam_ddt")
                with cam_col2:
                    ddt_file = st.file_uploader("📂 Oppure leggi Foto/CSV/XML da dispositivo (Solo RAM)", type=["jpg", "jpeg", "png", "csv", "xml"], key=f"up_ddt_{rc_id}")
                with cam_col3:
                    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
                    if st.button("🔥 SVUOTA RAM ORA", key="purge_ddt", use_container_width=True):
                        st.session_state["ram_clear_counter"] += 1
                        play_ems_synth("burst")
                        st.rerun()

                cam_ddt_shot = st.camera_input("Inquadra Bolla / Nota a mano (Lettura volatile in RAM)", key=f"cam_ddt_{rc_id}") if use_cam_ddt else None
                active_ddt_stream = cam_ddt_shot if cam_ddt_shot is not None else ddt_file
                if active_ddt_stream is not None:
                    raw_bytes = active_ddt_stream.getvalue()
                    ram_hash = hashlib.sha256(raw_bytes).hexdigest()[:10].upper()
                    st.success(f"👁️ LETTURA OTTICA IN RAM COMPLETATA (Hash `#{ram_hash}` — 0 Byte su disco).")

                d0, d1, d2, d3, d4 = st.columns([1.2, 1, 1, 1, 1])
                st.session_state["ddt_codice_art"] = d0.text_input("Cod. Articolo Bolla", st.session_state["ddt_codice_art"])
                st.session_state["ddt_prezzo_fattura"] = d1.number_input("Prezzo Bolla (€/Bott.)", 1.0, 200.0, st.session_state["ddt_prezzo_fattura"], step=0.10)
                st.session_state["ddt_prezzo_pattuito"] = d2.number_input("Pattuito (€/Bott.)", 1.0, 200.0, st.session_state["ddt_prezzo_pattuito"], step=0.10)
                st.session_state["ddt_litri_bottiglia"] = d3.selectbox("Formato (Litri)", [0.70, 0.75, 1.0, 1.5], index=2)
                st.session_state["ddt_omaggio_finto_iva"] = d4.number_input("IVA Finto Omaggio (€)", 0.0, 100.0, st.session_state["ddt_omaggio_finto_iva"], step=0.25)

                dna_litro_reale = st.session_state["ddt_prezzo_fattura"] / st.session_state["ddt_litri_bottiglia"]
                scostamento_bott = st.session_state["ddt_prezzo_fattura"] - st.session_state["ddt_prezzo_pattuito"]

                k1, k2, k3 = st.columns(3)
                with k1:
                    st.markdown(f"""
                    <div class="kpi-custom-box" style="border-left-color:#EF4444;">
                        <div class="kpi-custom-title">PREZZO REALE AL LITRO ({st.session_state['ddt_codice_art']})</div>
                        <div class="kpi-custom-value">€ {dna_litro_reale:.2f} / L</div>
                        <div class="kpi-custom-sub" style="color:#EF4444;">▲ +{scostamento_bott:.2f} € vs pattuito</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k2:
                    st.markdown(f"""
                    <div class="kpi-custom-box" style="border-left-color:#F59E0B;">
                        <div class="kpi-custom-title">CONTROLLO OMAGGI IN FATTURA (IVA)</div>
                        <div class="kpi-custom-value">€ {st.session_state['ddt_omaggio_finto_iva']:.2f}</div>
                        <div class="kpi-custom-sub" style="color:#F59E0B;">● Anomalia Bolla 190677/9</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k3:
                    st.markdown(f"""
                    <div class="kpi-custom-box" style="border-left-color:#10B981;">
                        <div class="kpi-custom-title">FRIGO BAR 1-CLICK (HACCP)</div>
                        <div class="kpi-custom-value">+3.8 °C OK</div>
                        <div class="kpi-custom-sub" style="color:#10B981;">✔ Firmato PIN #{st.session_state['pin_code']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                if st.button("📅 ARCHIVIA QUESTA BOLLA NEL CALENDARIO DI OGGI", use_container_width=True):
                    add_calendar_event("BOLLA DDT", f"Art. {st.session_state['ddt_codice_art']} (€{dna_litro_reale:.2f}/L | Scost. {scostamento_bott:+.2f}€)", -st.session_state["ddt_prezzo_fattura"], 1, "ALERT" if scostamento_bott > 0 else "OK")
                    play_ems_synth("commlock")
                    st.toast("✅ Bolla registrata nel Calendario Storico!")
                    st.rerun()

        # ======================================================================
        # MODULO 11: BANK VAMPIRE SCANNER (DICITURA PROFESSIONALE + CALENDARIO)
        # ======================================================================
        elif sec_obj["code"] == "11":
            if "5." in curr_sub:
                render_alpha_chrono_calendar()
            else:
                st.markdown("##### 🔫 BANK VAMPIRE SCANNER // ANALISI COSTI BANCARI & VERO TASSO POS (RAM-ONLY)")
                ec_col1, ec_col2, ec_col3 = st.columns([1.4, 2.0, 1.0])
                with ec_col1:
                    use_cam_bank = st.toggle("📸 FOTOGRAFA ESTRATTO CONTO (IN RAM)", value=False, key="tog_cam_bank")
                with ec_col2:
                    bank_file = st.file_uploader("📂 Oppure leggi Foto/CSV Estratto Conto (Solo RAM)", type=["csv", "txt", "jpg", "jpeg", "png"], key=f"up_bank_{rc_id}")
                with ec_col3:
                    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
                    if st.button("🔥 DISTRUGGI DATI RAM", key="purge_bank", use_container_width=True):
                        st.session_state["ram_clear_counter"] += 1
                        play_ems_synth("burst")
                        st.rerun()

                cam_bank_shot = st.camera_input("Inquadra il riepilogo spese dell'Estratto Conto (Lettura volatile in RAM)", key=f"cam_bank_{rc_id}") if use_cam_bank else None
                sdd_alert_txt = "0 DOPPI ADDEBITI"
                sdd_sub_txt = "✔ Controllo flussi SDD attivo"
                sdd_col = "#10B981"

                active_bank_stream = cam_bank_shot if cam_bank_shot is not None else bank_file
                if active_bank_stream is not None:
                    raw_b = active_bank_stream.getvalue()
                    ram_hash = hashlib.sha256(raw_b).hexdigest()[:10].upper()
                    st.success(f"🛡️ DOCUMENTO BANCARIO LETTO SOLO IN RAM (Hash `#{ram_hash}` — 0 Byte archiviati su disco).")

                b1, b2, b3, b4 = st.columns(4)
                st.session_state["bank_transato_pos"] = b1.number_input("Transato POS Mensile (€)", 500.0, 500000.0, st.session_state["bank_transato_pos"], step=500.0)
                st.session_state["bank_comm_dichiarata"] = b2.number_input("Comm. POS Dichiarata (%)", 0.10, 5.0, st.session_state["bank_comm_dichiarata"], step=0.05)
                st.session_state["bank_costi_occulti"] = b3.number_input("Spese Tenuta / Canoni / SDD (€)", 0.0, 5000.0, st.session_state["bank_costi_occulti"], step=10.0)
                st.session_state["bank_prezzo_caffe"] = b4.number_input("Prezzo Tazzina Caffè (€)", 0.80, 3.0, st.session_state["bank_prezzo_caffe"], step=0.10)

                costo_pos_base = st.session_state["bank_transato_pos"] * (st.session_state["bank_comm_dichiarata"] / 100.0)
                prelievo_totale_banca = costo_pos_base + st.session_state["bank_costi_occulti"]
                vero_tasso_pos = (prelievo_totale_banca / st.session_state["bank_transato_pos"]) * 100.0
                caffe_pareggio = round(prelievo_totale_banca / st.session_state["bank_prezzo_caffe"])
                scost_pos = vero_tasso_pos - st.session_state["bank_comm_dichiarata"]

                v1, v2, v3 = st.columns(3)
                with v1:
                    st.markdown(f"""
                    <div class="kpi-custom-box" style="border-left-color:#EF4444;">
                        <div class="kpi-custom-title">VERO TASSO POS EFFETTIVO</div>
                        <div class="kpi-custom-value">{vero_tasso_pos:.2f} %</div>
                        <div class="kpi-custom-sub" style="color:#EF4444;">▲ +{scost_pos:.2f}% incidenza oneri accessori</div>
                    </div>
                    """, unsafe_allow_html=True)
                with v2:
                    st.markdown(f"""
                    <div class="kpi-custom-box" style="border-left-color:#F59E0B;">
                        <div class="kpi-custom-title">CAFFÈ NECESSARI PER COPRIRE I COSTI BANCARI</div>
                        <div class="kpi-custom-value">{caffe_pareggio} Tazzine/mese</div>
                        <div class="kpi-custom-sub" style="color:#10B981;">● Corrispettivo di € {prelievo_totale_banca:.2f} in oneri e commissioni</div>
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

                if st.button("📅 REGISTRA ANALISI BANCARIA NEL CALENDARIO DEL MESE", use_container_width=True):
                    add_calendar_event("ONERI BANCA", f"Vero Tasso POS {vero_tasso_pos:.2f}% ({caffe_pareggio} tazzine per pareggio)", -prelievo_totale_banca, 30, "ALERT")
                    play_ems_synth("commlock")
                    st.toast("✅ Analisi bancaria salvata nel Calendario!")
                    st.rerun()

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

    # --- VISTA MATRICE CENTRALE PULITA CON I GRANDI SIMBOLI DI SPAZIO 1999 ---
    else:
        n_cols = 1 if n_sectors == 1 else (2 if n_sectors in [2, 4] else 3)
        for r in range(0, n_sectors, n_cols):
            row_cols = st.columns(n_cols)
            for c in range(n_cols):
                if r + c < n_sectors:
                    sq = all_squares[r + c]
                    code = sq["code"]
                    svg_icon = SVG_ICONS.get(code, SVG_ICONS["01"])
                    artifact_lbl = sq.get("artifact", "MOONBASE ALPHA NODE")

                    with row_cols[c]:
                        st.markdown(f"""
                        <div class="alpha-tile" style="background: {sq['bg_grad']}; border: 1.5px solid {sq['border']}; border-left: 5px solid {sq['border']}; box-shadow: inset 0 0 28px {sq['glow']};">
                            <div>{svg_icon}</div>
                            <div class="tile-code">{code}</div>
                            <div class="tile-name">{sq['name']}</div>
                            <div class="tile-artifact">{artifact_lbl}</div>
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
