import os
import json
import time
import hmac
import hashlib
import base64
import struct
import io
import re
import urllib.request
import urllib.error
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# ==============================================================================
# BEMASK - MOONBASE A.L.P.H.A. // MOBILE ZERO-CLICK AUTO-SCAN EDITION
# ==============================================================================

st.set_page_config(
    page_title="BEMASK - MOONBASE A.L.P.H.A.",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 1. MOTORE CRITTOGRAFICO NATIVO 2FA ---
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

def get_gemini_api_key():
    for k_name in ["api_key_box_DDT", "api_key_box_BANK", "api_key_box_VAULT", "custom_gemini_key"]:
        val = str(st.session_state.get(k_name, "")).strip()
        if len(val) > 15:
            st.session_state["custom_gemini_key"] = val
            return val
    try:
        sec_k = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        if len(sec_k) > 15:
            return sec_k
    except Exception:
        pass
    return ""

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

# ==============================================================================
# MOTORE OCR VISION IN RAM CON AUTODISCOVERY (ZERO-CLICK AUTO-RUN)
# ==============================================================================
def scan_receipt_in_ram_with_ai(image_bytes, api_key):
    clean_key = str(api_key).strip()
    if not clean_key or len(clean_key) < 15:
        return None, "Chiave API mancante. Inseriscila una sola volta nel box 'Chiave AI' qui sotto."

    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    prompt_txt = (
        "Sei lo scanner contabile automatico di un bar italiano. Leggi questa foto di scontrino, bolla o ricevuta POS. "
        "Estrai esercente (o email), metodo di pagamento, tutte le singole righe dei prodotti acquistati (o la voce del pagamento POS) e il totale reale in euro. "
        "Rispondi SOLO con un JSON valido in questo formato esatto: "
        "{\"esercente\": \"nome o email locale\", \"metodo_pagamento\": \"CARTA DI CREDITO / POS\", "
        "\"righe\": [{\"voce\": \"nome articolo o pagamento\", \"qta\": 1, \"prezzo\": 19.80}], \"totale_euro\": 19.80}"
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_txt},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
            ]
        }]
    }

    candidate_models = []
    for api_ver in ["v1beta", "v1"]:
        try:
            list_url = f"https://generativelanguage.googleapis.com/{api_ver}/models?key={clean_key}"
            req_list = urllib.request.Request(list_url, method="GET")
            with urllib.request.urlopen(req_list, timeout=8) as resp_l:
                models_data = json.loads(resp_l.read().decode("utf-8"))
                for m in models_data.get("models", []):
                    m_name = m.get("name", "").replace("models/", "")
                    methods = m.get("supportedGenerationMethods", [])
                    if "generateContent" in methods and ("flash" in m_name or "pro" in m_name or "gemini" in m_name):
                        if (api_ver, m_name) not in candidate_models:
                            candidate_models.append((api_ver, m_name))
            if candidate_models:
                break
        except urllib.error.HTTPError as he:
            if he.code in [400, 401, 403]:
                return None, f"Chiave API non valida (HTTP {he.code}). Assicurati che inizi con 'AIzaSy...'."
        except Exception:
            continue

    if not candidate_models:
        candidate_models = [
            ("v1beta", "gemini-2.5-flash"),
            ("v1beta", "gemini-2.0-flash"),
            ("v1beta", "gemini-1.5-flash-latest"),
            ("v1", "gemini-2.0-flash"),
            ("v1", "gemini-1.5-flash")
        ]
    else:
        candidate_models.sort(key=lambda x: (0 if "flash" in x[1] else 1))

    last_err = ""
    for api_ver, m_name in candidate_models:
        try:
            url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{m_name}:generateContent?key={clean_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                raw_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                clean_json = re.sub(r"```json|```", "", raw_reply).strip()
                match_j = re.search(r"\{.*\}", clean_json, re.DOTALL)
                if match_j:
                    clean_json = match_j.group(0)
                parsed = json.loads(clean_json)
                return parsed, None
        except Exception as e:
            last_err = f"[{m_name}] {str(e)}"
            continue

    return None, f"Lettura AI non riuscita ({last_err})."

# --- 2. BLINDAGGIO SESSION STATE ---
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
        "keep_multiverse_open": False,
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
        "bar_kg_caffe_aperti": 2.0,
        "bar_tazzine_per_kg": 135,
        "bar_ao_labels": default_labels_ao,
        "unsaved_ops_count": 0,
        "custom_gemini_key": "",
        "processed_ hashes": [],
        "last_auto_saved_banner": None,
        "ocr_esercente": "Pechino Follonica",
        "ocr_metodo": "CARTA DI CREDITO / POS",
        "ocr_items_df": [
            {"voce": "Scontrino / Pagamento POS", "qta": 1, "prezzo": 19.80}
        ],
        "chrono_ledger": [
            {"date": datetime.now().strftime("%Y-%m-%d"), "time": "07:30", "type": "CAFFÈ (+1 KG)", "desc": "Apertura sacchetto grani 1 Kg (~135 caffè)", "amount": 175.50, "days_span": 1, "status": "OK"},
            {"date": datetime.now().strftime("%Y-%m-%d"), "time": "08:15", "type": "BOLLA DDT", "desc": "Art. 10001 Doreca — Scostamento +€1.90/L", "amount": -14.80, "days_span": 1, "status": "ALERT"},
            {"date": datetime.now().strftime("%Y-%m-%d"), "time": "08:58", "type": "SCONTRINO RAM", "desc": "Pechino Follonica (Carta di Credito) — € 19,80", "amount": -19.80, "days_span": 1, "status": "OK"}
        ]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    for idx_b in range(11):
        t_key = f"bit_sw_{idx_b}"
        if t_key not in st.session_state:
            st.session_state[t_key] = st.session_state["active_bits_11"][idx_b]

init_monumental_state()

def apply_multiverse_preset(new_bits_list):
    st.session_state["active_bits_11"] = list(new_bits_list)
    for idx_b, val_b in enumerate(new_bits_list):
        st.session_state[f"bit_sw_{idx_b}"] = bool(val_b)
    st.session_state["blum_sector"] = None
    st.session_state["keep_multiverse_open"] = True

def on_single_bit_toggle(idx_b):
    st.session_state["active_bits_11"][idx_b] = bool(st.session_state[f"bit_sw_{idx_b}"])
    st.session_state["blum_sector"] = None
    st.session_state["keep_multiverse_open"] = True

def add_calendar_event(ev_type, ev_desc, ev_amount, days_span=1, status="OK"):
    st.session_state["chrono_ledger"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "type": ev_type,
        "desc": ev_desc,
        "amount": round(float(ev_amount), 2),
        "days_span": int(days_span),
        "status": status
    })
    st.session_state["unsaved_ops_count"] += 1

# --- 3. SINTETIZZATORE AUDIO WEBAUDIO ---
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
# 4. GRANDI SIMBOLI ICONICI DI SPAZIO 1999 (SVG MONUMENTALI)
# ==============================================================================
EAGLE_HERO_SVG = """
<svg width="95" height="48" viewBox="0 0 180 86" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="48" y="16" width="84" height="12" fill="#1E293B" stroke="#94A3B8" stroke-width="2"/>
  <path d="M48 28L62 16L76 28L90 16L104 28L118 16L132 28" stroke="#CBD5E1" stroke-width="1.8"/>
  <polygon points="36,36 58,36 62,58 32,58" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
  <polygon points="122,36 144,36 148,58 118,58" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
  <rect x="30" y="58" width="34" height="5" fill="#F59E0B"/>
  <rect x="116" y="58" width="34" height="5" fill="#F59E0B"/>
  <rect x="58" y="30" width="64" height="24" fill="#1E293B" stroke="#38BDF8" stroke-width="2"/>
  <polygon points="90,22 122,42 112,68 68,68 58,42" fill="#E2E8F0" stroke="#FFFFFF" stroke-width="2.2"/>
  <polygon points="87,34 65,44 72,54 87,49" fill="#F59E0B" stroke="#78350F" stroke-width="1.5"/>
  <polygon points="93,34 115,44 108,54 93,49" fill="#F59E0B" stroke="#78350F" stroke-width="1.5"/>
</svg>
"""

SVG_ICONS = {
    "01": """<svg width="80" height="60" viewBox="0 0 120 84" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="24" y="10" width="72" height="12" fill="#1E293B" stroke="#94A3B8" stroke-width="2"/><path d="M24 22L38 10L52 22L66 10L80 22L96 10" stroke="#E2E8F0" stroke-width="2"/><polygon points="14,32 36,32 40,58 10,58" fill="#334155" stroke="#94A3B8" stroke-width="2"/><polygon points="84,32 106,32 110,58 80,58" fill="#334155" stroke="#94A3B8" stroke-width="2"/><polygon points="60,20 92,42 82,70 38,70 28,42" fill="#E2E8F0" stroke="#F59E0B" stroke-width="2.5"/><polygon points="57,34 35,44 42,56 57,50" fill="#F59E0B"/><polygon points="63,34 85,44 78,56 63,50" fill="#F59E0B"/><rect x="8" y="60" width="32" height="5" fill="#F59E0B"/><rect x="80" y="60" width="32" height="5" fill="#F59E0B"/></svg>""",
    "02": """<svg width="80" height="60" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="10" y="8" width="90" height="68" rx="4" fill="#0F172A" stroke="#10B981" stroke-width="2.5"/><rect x="18" y="16" width="20" height="12" fill="#F59E0B"/><rect x="44" y="16" width="20" height="12" fill="#F8FAFC"/><rect x="70" y="16" width="22" height="12" fill="#10B981"/><rect x="18" y="34" width="20" height="12" fill="#10B981"/><rect x="44" y="34" width="20" height="12" fill="#EF4444"/><rect x="70" y="34" width="22" height="12" fill="#F59E0B"/><rect x="18" y="54" width="74" height="14" fill="#1E293B" stroke="#34D399" stroke-width="1.8"/><path d="M22 61H40L45 56L52 66L58 58L64 61H88" stroke="#10B981" stroke-width="2.2"/></svg>""",
    "03": """<svg width="80" height="60" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="55" cy="42" r="32" fill="#0F293A" stroke="#38BDF8" stroke-width="2.5"/><circle cx="55" cy="42" r="20" stroke="#38BDF8" stroke-width="1.5" stroke-dasharray="4 3"/><line x1="55" y1="10" x2="55" y2="74" stroke="#38BDF8" stroke-width="1.5"/><line x1="23" y1="42" x2="87" y2="42" stroke="#38BDF8" stroke-width="1.5"/><circle cx="65" cy="32" r="5" fill="#F59E0B"/><circle cx="43" cy="50" r="4" fill="#10B981"/></svg>""",
    "04": """<svg width="72" height="60" viewBox="0 0 100 86" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="26" y="6" width="48" height="74" rx="5" fill="#1E1B2E" stroke="#A855F7" stroke-width="2.8"/><rect x="33" y="13" width="34" height="26" rx="2" fill="#090D16" stroke="#38BDF8" stroke-width="2"/><circle cx="50" cy="26" r="7" fill="#F59E0B"/><rect x="34" y="45" width="9" height="7" fill="#F59E0B"/><rect x="46" y="45" width="9" height="7" fill="#E2E8F0"/><rect x="57" y="45" width="9" height="7" fill="#EF4444"/><line x1="34" y1="60" x2="66" y2="60" stroke="#CBD5E1" stroke-width="2"/><line x1="34" y1="66" x2="66" y2="66" stroke="#CBD5E1" stroke-width="2"/></svg>""",
    "05": """<svg width="80" height="60" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="14" y="12" width="82" height="60" rx="6" fill="#2A121F" stroke="#F43F5E" stroke-width="2.5"/><path d="M22 44H38L45 24L55 62L64 34L70 44H88" stroke="#F43F5E" stroke-width="3"/><circle cx="28" cy="24" r="4" fill="#F59E0B"/><circle cx="82" cy="24" r="4" fill="#10B981"/></svg>""",
    "06": """<svg width="80" height="60" viewBox="0 0 114 84" fill="none" xmlns="http://www.w3.org/2000/svg"><polygon points="18,76 28,10 86,10 96,76" fill="#161A22" stroke="#F59E0B" stroke-width="2.8"/><polygon points="22,74 30,13 54,13 48,74" fill="#334155" stroke="#E2E8F0" stroke-width="2"/><polygon points="66,74 62,13 84,13 92,74" fill="#334155" stroke="#E2E8F0" stroke-width="2"/><polygon points="48,74 54,13 62,13 66,74" fill="rgba(245,158,11,0.35)"/><rect x="100" y="34" width="8" height="16" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.2"/></svg>""",
    "07": """<svg width="80" height="60" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg"><polygon points="24,20 86,20 96,42 86,66 24,66 14,42" fill="#0F2E26" stroke="#10B981" stroke-width="2.5"/><rect x="34" y="30" width="42" height="24" fill="#1E293B" stroke="#F59E0B" stroke-width="2"/><line x1="24" y1="42" x2="86" y2="42" stroke="#34D399" stroke-width="2"/><circle cx="55" cy="42" r="6" fill="#F59E0B"/></svg>""",
    "08": """<svg width="80" height="60" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg"><polygon points="55,8 92,22 84,64 55,78 26,64 18,22" fill="#0E2A36" stroke="#06B6D4" stroke-width="2.5"/><circle cx="55" cy="42" r="18" fill="#161E29" stroke="#38BDF8" stroke-width="2"/><path d="M55 30V54M43 42H67" stroke="#10B981" stroke-width="3.5"/></svg>""",
    "09": """<svg width="80" height="60" viewBox="0 0 110 84" fill="none" xmlns="http://www.w3.org/2000/svg"><line x1="55" y1="10" x2="55" y2="74" stroke="#F59E0B" stroke-width="4"/><ellipse cx="55" cy="26" rx="28" ry="8" stroke="#38BDF8" stroke-width="2.2" fill="rgba(56,189,248,0.15)"/><ellipse cx="55" cy="46" rx="36" ry="10" stroke="#F59E0B" stroke-width="2.5" fill="rgba(245,158,11,0.18)"/><circle cx="55" cy="12" r="6" fill="#EF4444"/></svg>""",
    "10": """<svg width="80" height="60" viewBox="0 0 114 84" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="12" y="10" width="90" height="64" rx="4" fill="#0B2922" stroke="#10B981" stroke-width="2.8"/><rect x="20" y="18" width="46" height="22" fill="#091318" stroke="#34D399" stroke-width="2"/><line x1="25" y1="25" x2="60" y2="25" stroke="#F59E0B" stroke-width="3"/><line x1="25" y1="33" x2="50" y2="33" stroke="#10B981" stroke-width="3"/><circle cx="82" cy="29" r="10" fill="#1E293B" stroke="#F59E0B" stroke-width="2.5"/><circle cx="82" cy="29" r="4" fill="#EF4444"/><rect x="20" y="48" width="14" height="16" fill="#F59E0B"/><rect x="38" y="48" width="14" height="16" fill="#E2E8F0"/><rect x="56" y="48" width="14" height="16" fill="#10B981"/><rect x="74" y="48" width="20" height="16" fill="#EF4444"/></svg>""",
    "11": """<svg width="82" height="60" viewBox="0 0 118 84" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 26H86L96 32L86 40H52L40 72H22L32 40H18V26Z" fill="#CBD5E1" stroke="#EF4444" stroke-width="2.5"/><rect x="26" y="30" width="22" height="6" fill="#EF4444"/><rect x="54" y="30" width="18" height="6" fill="#F59E0B"/><rect x="94" y="29" width="8" height="8" fill="#F59E0B"/><line x1="102" y1="33" x2="116" y2="33" stroke="#EF4444" stroke-width="4" stroke-dasharray="3 2"/></svg>"""
}

# --- 5. ARCHITETTURA DEGLI 11 VETTORI PRIMARI ---
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
        "kpi": "SCATTA E SALVA 1-CLICK | CASSA A-O | +1KG CAFFÈ", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. 📸 Scatta & Salva Automatico", "2. 🎹 Tastiera Cassa (A-O)", "3. 🏁 Chiusura Cassa / Turno", "4. ❄️ Frigo Bar 1-Click", "5. 📅 Calendario Storico"]
    },
    {
        "bit": 10, "code": "11", "short": "11 VAMPIRE", "name": "BANK VAMPIRE SCANNER", "artifact": "KOENIG LASER STUN GUN", "staff_allowed": False,
        "border": "#EF4444", "glow": "rgba(239, 68, 68, 0.42)", "bg_grad": "radial-gradient(circle at 50% 42%, #421820 0%, #151319 78%)",
        "kpi": "AUTOPSIA CONTO | POS REALE & SDD ALERT", "url": "https://bemask-lazers.streamlit.app",
        "subs": ["1. 📸 Scatta E/C & Salva", "2. Vero Tasso POS Effettivo", "3. Impatto Costi su Caffetteria", "4. Anti-Doppio Addebito SDD", "5. 📅 Calendario Storico"]
    }
]

WEATHER_5_DAYS = [
    {"day": "LUN 09/11 · 19°C", "icon": "☀️", "status": "NOMINAL ORBIT", "rain": "PIOGGIA: 8%", "hum": "UR: 54%", "wind": "7 KT NW", "directive": "☀️ SPINTA DEHORS & APERITIVI", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "MAR 10/11 · 17°C", "icon": "🌤️", "status": "NOMINAL ORBIT", "rain": "PIOGGIA: 14%", "hum": "UR: 61%", "wind": "11 KT W", "directive": "🌤️ REGIME STANDARD", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "MER 11/11 · 17°C", "icon": "⛈️", "status": "SOLAR STORM", "rain": "PIOGGIA: 91%", "hum": "UR: 88%", "wind": "29 KT SW", "directive": "⚡ FALLBACK SALA INTERNA", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "GIO 12/11 · 20°C", "icon": "⛈️", "status": "SOLAR STORM", "rain": "PIOGGIA: 94%", "hum": "UR: 92%", "wind": "33 KT S", "directive": "🚨 SCUDO 96H ATTIVO", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "VEN 13/11 · 21°C", "icon": "☀️", "status": "NOMINAL ORBIT", "rain": "PIOGGIA: 22%", "hum": "UR: 58%", "wind": "9 KT NE", "directive": "🛸 RIAPERTURA ESTERNI", "border": "#38BDF8", "text_col": "#38BDF8"},
]

# ==============================================================================
# 6. CSS BLINDATO CONTro LO SPOSTAMENTO COLONNA SU TELEFONINO (ANTI-WOBBLE MOBILE)
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800;900&family=Share+Tech+Mono&display=swap');

/* BLOCCO TOTALE SCORRIMENTO ORIZZONTALE SU TELEFONINO */
html, body, [data-testid="stAppViewContainer"], .stApp, .main, .block-container {
    overflow-x: hidden !important;
    max-width: 100vw !important;
    box-sizing: border-box !important;
}

.stApp {
    background-color: #101319;
    background-image:
        radial-gradient(circle at 50% 32%, rgba(245, 158, 11, 0.07) 0%, rgba(16, 19, 25, 0.96) 72%),
        url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='900' height='420' viewBox='0 0 900 420'><g opacity='0.045' stroke='%23F59E0B' stroke-width='2' fill='none'><rect x='220' y='90' width='460' height='60'/><path d='M220 150 L300 90 L380 150 L460 90 L540 150 L620 90 L680 150'/><polygon points='450,110 610,210 560,340 340,340 290,210'/><polygon points='435,175 325,220 360,275 435,250' fill='%23F59E0B'/><polygon points='465,175 575,220 540,275 465,250' fill='%23F59E0B'/></g></svg>");
    background-repeat: no-repeat;
    background-position: center 140px;
    background-attachment: fixed;
    color: #F8FAFC;
    font-family: 'Orbitron', sans-serif;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 0.6rem; padding-left: 0.8rem !important; padding-right: 0.8rem !important; max-width: 98% !important; }

div[data-baseweb="input"] > div:focus-within {
    border-color: #10B981 !important;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.45) !important;
}

.koenig-strip {
    background-color: #1A1E26; border: 1px solid #323946; border-left: 5px solid #F59E0B;
    padding: 8px 12px; margin-bottom: 8px; border-radius: 2px;
}
.badge-amber { background-color: #F59E0B; color: #0B0E14; font-weight: 900; font-size: 10px; padding: 3px 7px; margin-right: 6px; display: inline-block; margin-bottom: 3px; }
.badge-white { background-color: #F1F5F9; color: #0F172A; font-weight: 800; font-size: 10px; padding: 2px 7px; margin-right: 5px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }
.badge-red { background-color: #7F1D1D; border: 1px solid #EF4444; color: #FCA5A5; font-weight: 800; font-size: 10px; padding: 2px 7px; margin-right: 5px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }
.badge-green { background-color: #064E3B; border: 1px solid #10B981; color: #6EE7B7; font-weight: 800; font-size: 10px; padding: 2px 7px; margin-right: 5px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }

.mission-bar {
    background: linear-gradient(90deg, #161C24 0%, #1E2836 50%, #161C24 100%);
    border: 1px solid #3A4B5E; border-left: 5px solid #F59E0B;
    padding: 10px 14px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 10px;
}
.mission-title { font-size: 17px; font-weight: 900; color: #FFFFFF; letter-spacing: 1.2px; }
.mission-sub { font-size: 10px; color: #38BDF8; font-family: 'Share Tech Mono', monospace; letter-spacing: 0.8px; margin-top: 2px; }
.nixie-group { display: flex; align-items: center; gap: 8px; }
.nixie-label { font-size: 10px; color: #94A3B8; font-weight: 700; }
.nixie-digits {
    background-color: #0D1015; border: 1px solid #F59E0B; color: #F59E0B;
    font-family: 'Share Tech Mono', monospace; font-size: 16px; font-weight: 900;
    padding: 2px 8px; letter-spacing: 2px; border-radius: 2px;
}

.weather-card {
    background-color: #151922; border: 1px solid #2B3340;
    padding: 8px 10px; border-radius: 3px; margin-bottom: 8px;
}
.w-header { display: flex; justify-content: space-between; align-items: center; }
.w-day { font-size: 10px; font-weight: 900; color: #FFFFFF; }
.w-icon { font-size: 16px; }
.w-status { font-size: 9px; font-weight: 900; margin-top: 3px; }
.w-telemetry {
    display: flex; justify-content: space-between; margin-top: 5px; padding-top: 4px;
    border-top: 1px dashed #2E3846; font-family: 'Share Tech Mono', monospace;
    font-size: 9px; color: #E2E8F0; font-weight: 700;
}
.w-directive { margin-top: 4px; font-family: 'Share Tech Mono', monospace; font-size: 9px; color: #94A3B8; }

.alpha-tile {
    height: 215px; border-radius: 3px; padding: 14px;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    text-align: center; position: relative; margin-bottom: 12px; pointer-events: none;
}
.tile-code { font-size: 11px; font-weight: 800; color: #F59E0B; margin-top: 8px; letter-spacing: 1.5px; }
.tile-name { font-size: 14px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px; margin-top: 3px; }
.tile-artifact { font-size: 9px; font-weight: 700; color: #94A3B8; font-family: 'Share Tech Mono', monospace; margin-top: 4px; }

div[class*="st-key-blum_click_"] {
    margin-top: -227px !important;
    margin-bottom: 12px !important;
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

div.stButton > button {
    background-color: #1A212B !important; color: #F8FAFC !important;
    border: 1px solid #2F3E50 !important; border-radius: 3px !important;
    font-family: 'Orbitron', sans-serif !important; font-size: 11px !important;
    font-weight: 800 !important; letter-spacing: 0.8px !important;
    min-height: 42px !important;
}
div.stButton > button:hover {
    border-color: #F59E0B !important; color: #F59E0B !important;
}

.ems-panel { background-color: #161A22; border: 2px solid #F59E0B; padding: 12px; border-radius: 3px; margin-bottom: 10px; }
.commlock-panel { background-color: #161A22; border: 1px solid #F59E0B; padding: 14px; border-radius: 3px; text-align: center; }
.blum-stage { background: radial-gradient(circle at 50% 20%, #1A2432 0%, #0E1218 85%); padding: 16px; border-radius: 4px; margin-bottom: 12px; }

.kpi-custom-box {
    background-color: #141A23; border: 1px solid #2B394A; border-left: 4px solid #F59E0B;
    padding: 14px; border-radius: 3px; margin-top: 6px; margin-bottom: 8px;
}
.kpi-custom-title { font-size: 10px; font-weight: 800; color: #94A3B8; letter-spacing: 1px; margin-bottom: 6px; font-family: 'Share Tech Mono', monospace; }
.kpi-custom-value { font-size: 22px; font-weight: 900; color: #FFFFFF; letter-spacing: 0.8px; line-height: 1.2; }
.kpi-custom-sub { font-size: 11px; font-weight: 700; margin-top: 6px; font-family: 'Share Tech Mono', monospace; }

.autosave-banner {
    background: linear-gradient(90deg, #064E3B 0%, #0F2922 100%);
    border: 2px solid #10B981; border-left: 6px solid #F59E0B;
    padding: 14px; border-radius: 4px; margin-top: 10px; margin-bottom: 12px;
}

/* OTTIMIZZAZIONE SPECIFICA PER SCHERMI TELEFONINO (< 768px) */
@media (max-width: 768px) {
    .mission-title { font-size: 14px !important; }
    .kpi-custom-value { font-size: 19px !important; }
    .blum-stage { padding: 12px !important; }
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. KOENIG ZERO-TRUST SECURITY GATE
# ==============================================================================
STAFF_PINS = {
    "1024": "OPERATORE BAR / CUCINA (SOLO HACCP & SKA)",
    "2048": "GOVERNANTE AI PIANI (SOLO CAMERE & SKA)",
    "3096": "BAGNINO LIDO (SOLO BEACH & POOL)"
}

if not st.session_state["auth_unlocked"]:
    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
    g_left, g_center, g_right = st.columns([0.2, 2.6, 0.2])
    with g_center:
        st.markdown(f"""
        <div style="background:#161B24; border:2px solid #F59E0B; border-top:6px solid #F59E0B; padding:20px; border-radius:4px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div>{EAGLE_HERO_SVG}</div>
                <span class="badge-amber">EAGLE-1 // MOBILE READY</span>
            </div>
            <div style="font-size:18px; font-weight:900; color:#FFFFFF; letter-spacing:1.2px;">
                BEMASK // A.L.P.H.A. SECURITY GATE
            </div>
            <div style="font-size:11px; color:#38BDF8; font-family:'Share Tech Mono', monospace; margin-top:4px;">
                SCATTA E SALVA IN 1 SECONDO | ZERO-CLICK AI OCR
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ ACCESSO RAPIDO DEMO (1-CLICK PER TELEFONINO E TEST)", use_container_width=True):
            play_ems_synth("commlock")
            st.session_state["auth_unlocked"] = True
            st.session_state["auth_role"] = "COMMANDER"
            st.session_state["auth_user"] = "ENRICO // ARCHITECT MASTER"
            st.rerun()

        c_pin, c_2fa = st.columns(2)
        in_pin = c_pin.text_input("🔑 PIN OPERATORE / TITOLARE", type="password", placeholder="9999 o 1024")
        in_2fa = c_2fa.text_input("📱 CODICE 2FA (6 CIFRE)", type="password", placeholder="199975")

        if st.button("🛡️ VERIFICA CREDENZIALI E SBLOCCA PLANCIA", use_container_width=True):
            master_pin = get_master_pin()
            secret_2fa = get_totp_secret()
            if in_pin.strip() == master_pin and verify_2fa_code(in_2fa, secret_2fa):
                play_ems_synth("commlock")
                st.session_state["auth_unlocked"] = True
                st.session_state["auth_role"] = "COMMANDER"
                st.session_state["auth_user"] = "COMANDANTE (2FA VERIFIED)"
                st.rerun()
            elif in_pin.strip() in STAFF_PINS:
                play_ems_synth("burst")
                st.session_state["auth_unlocked"] = True
                st.session_state["auth_role"] = "STAFF"
                st.session_state["auth_user"] = STAFF_PINS[in_pin.strip()]
                st.rerun()
            else:
                st.error("🚨 Credenziali non valide.")
    st.stop()

# ==============================================================================
# 8. FILTRO RUOLO ANTI-TALPA
# ==============================================================================
is_commander = (st.session_state["auth_role"] == "COMMANDER")
bits = st.session_state["active_bits_11"]

if is_commander:
    active_base = [v for i, v in enumerate(BASE_VECTORS) if bits[i]]
    if not active_base:
        apply_multiverse_preset([True] + [False]*10)
        active_base = [BASE_VECTORS[0]]
    all_squares = active_base + st.session_state["custom_squares"]
else:
    all_squares = [v for v in BASE_VECTORS if v["staff_allowed"]]

n_sectors = len(all_squares)
total_micro_modules = n_sectors * 5
binary_state_num = sum((1 << i) for i, b in enumerate(bits) if b)
binary_str = "".join(["1" if b else "0" for b in bits])
ora_attuale = datetime.now().strftime("%H:%M")

# --- 9. TOP KOENIG BAR ---
top_c1, top_c2 = st.columns([4.0, 1.0])
with top_c1:
    st.markdown(f"""
    <div class="koenig-strip">
        <div>
            <span class="badge-amber">MOONBASE ALPHA</span>
            <span style="font-size:11px; font-weight:900; color:#FFFFFF;">{st.session_state['auth_user']}</span>
        </div>
        <div style="margin-top:4px;">
            <span class="badge-white">{n_sectors} SETTORI</span>
            <span class="badge-green">🤖 ZERO-CLICK AUTO-OCR</span>
            <span class="badge-white">STATO #{binary_state_num}/2048</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top_c2:
    if st.button("🔒 ESCI", use_container_width=True):
        st.session_state["auth_unlocked"] = False
        st.session_state["blum_sector"] = None
        st.rerun()

st.markdown(f"""
<div class="mission-bar">
    <div style="display:flex; align-items:center; gap:12px;">
        <div>{EAGLE_HERO_SVG}</div>
        <div>
            <div class="mission-title">BEMASK - A.L.P.H.A. MAIN MISSION</div>
            <div class="mission-sub">DATE: {datetime.now().strftime('%d/%m/%Y')} | {total_micro_modules} MODULI ATTIVI</div>
        </div>
    </div>
    <div class="nixie-group">
        <span class="nixie-label">TIME:</span>
        <span class="nixie-digits">{ora_attuale}</span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state["unsaved_ops_count"] >= 3:
    al_c1, al_c2 = st.columns([3.0, 1.2])
    with al_c1:
        st.warning(f"⚠️ Hai {st.session_state['unsaved_ops_count']} nuove operazioni registrate. Scarica il backup sul telefono!")
    with al_c2:
        cal_json = json.dumps(st.session_state["chrono_ledger"], indent=2, ensure_ascii=False)
        if st.download_button("💾 SALVA STORICO (.JSON)", cal_json, file_name=f"alpha_calendario_{datetime.now().strftime('%Y_%m')}.json", mime="application/json", use_container_width=True):
            st.session_state["unsaved_ops_count"] = 0
            st.rerun()

with st.expander("🌤️ RADAR METEO TELEMETRICO 5 GIORNI (SANDRA BENES / MAYA)", expanded=False):
    w_cols = st.columns(5)
    for idx, w in enumerate(WEATHER_5_DAYS):
        with w_cols[idx]:
            st.markdown(f"""
            <div class="weather-card" style="border-left: 4px solid {w['border']};">
                <div class="w-header"><span class="w-day">{w['day']}</span><span class="w-icon">{w['icon']}</span></div>
                <div class="w-status" style="color:{w['text_col']};">{w['status']}</div>
                <div class="w-telemetry"><span style="color:{w['text_col']};">{w['rain']}</span><span>{w['hum']}</span><span style="color:#38BDF8;">{w['wind']}</span></div>
                <div class="w-directive">{w['directive']}</div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 10. PANNELLO DEL COMANDANTE (COMPATTO SU MOBILE)
# ==============================================================================
if is_commander:
    with st.expander("🎛️ CONFIGURA PACCHETTI & CHIAVE AI (bar / hotel / 2FA)", expanded=st.session_state["keep_multiverse_open"]):
        p1, p2, p3, p4 = st.columns(4)
        p1.button("🍸 PACCHETTO BAR (02+10+11)", on_click=apply_multiverse_preset, args=([False, True, False, False, False, False, False, False, False, True, True],), use_container_width=True)
        p2.button("🛸 PACCHETTO 6 SETTORI", on_click=apply_multiverse_preset, args=([True, True, True, True, True, True, False, False, False, False, False],), use_container_width=True)
        p3.button("🔥 FULL 11 SETTORI", on_click=apply_multiverse_preset, args=([True] * 11,), use_container_width=True)
        p4.button("⚡ SOLO 01", on_click=apply_multiverse_preset, args=([True] + [False] * 10,), use_container_width=True)

        sw_cols = st.columns(11)
        for i, vec in enumerate(BASE_VECTORS):
            with sw_cols[i]:
                st.toggle(vec["short"], key=f"bit_sw_{i}", on_change=on_single_bit_toggle, args=(i,))

# ==============================================================================
# AUTOMAZIONE ZERO-CLICK: APPENA SCATTI LA FOTO, LEGGE E SALVA DA SOLO!
# ==============================================================================
def process_photo_zero_click(stream_obj, module_tag="DDT"):
    raw_bytes = stream_obj.getvalue()
    ram_kb = len(raw_bytes) / 1024.0
    ram_hash = hashlib.sha256(raw_bytes).hexdigest()[:12].upper()

    # Controlla la chiave API
    active_key = get_gemini_api_key()

    # Se questa foto non è ancora stata processata in automatico, la legge e la salva SUBITO!
    if ram_hash not in st.session_state["processed_ hashes"]:
        if active_key:
            with st.spinner("🤖 Lettura automatica scontrino e salvataggio nel Calendario in corso..."):
                parsed_ocr, err_msg = scan_receipt_in_ram_with_ai(raw_bytes, active_key)
                if parsed_ocr:
                    eser = parsed_ocr.get("esercente", "Scontrino / Bolla")
                    met = parsed_ocr.get("metodo_pagamento", "POS / CARTA")
                    tot_letto = float(parsed_ocr.get("totale_euro", 19.80))
                    righe_ai = parsed_ocr.get("righe", [])

                    st.session_state["ocr_esercente"] = eser
                    st.session_state["ocr_metodo"] = met
                    if isinstance(righe_ai, list) and len(righe_ai) > 0:
                        st.session_state["ocr_items_df"] = righe_ai
                        voci_str = " + ".join([f"{r.get('qta',1)}x {r.get('voce','')} (€{r.get('prezzo',0)})" for r in righe_ai])
                    else:
                        voci_str = f"Totale € {tot_letto:.2f}"

                    full_desc = f"{eser} [{met}] -> {voci_str}"[:140]
                    add_calendar_event(f"AUTO-SCAN ({module_tag})", full_desc, -tot_letto, 1, "OK")
                    st.session_state["processed_ hashes"].append(ram_hash)
                    st.session_state["last_auto_saved_banner"] = {
                        "eser": eser, "met": met, "tot": tot_letto, "voci": voci_str, "hash": ram_hash, "kb": ram_kb
                    }
                    play_ems_synth("commlock")
                else:
                    st.warning(f"⚠️ {err_msg}")
        else:
            st.info("👇 Inserisci una sola volta la chiave `AIzaSy...` qui sotto: dal prossimo scatto leggerà e salverà tutto da solo in 1 secondo!")

    # Mostra il Banner Verde Gigante di operazione già completata!
    if st.session_state.get("last_auto_saved_banner") and st.session_state["last_auto_saved_banner"]["hash"] == ram_hash:
        b_info = st.session_state["last_auto_saved_banner"]
        st.markdown(f"""
        <div class="autosave-banner">
            <div style="font-size:12px; color:#F59E0B; font-weight:900;">
                ✅ SCANSIONE E SALVATAGGIO AUTOMATICO COMPLETATI (ZERO-CLICK!)
            </div>
            <div style="font-size:20px; font-weight:900; color:#FFFFFF; margin-top:4px;">
                {b_info['eser']} — € {b_info['tot']:.2f} ({b_info['met']})
            </div>
            <div style="font-size:12px; color:#6EE7B7; font-family:'Share Tech Mono', monospace; margin-top:4px;">
                🧾 Voci registrate nel Calendario: {b_info['voci']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📸 PRONTO PER UN ALTRO SCONTRINO (SVUOTA MIRINO)", key=f"next_shot_{module_tag}", use_container_width=True):
            st.session_state["ram_clear_counter"] += 1
            st.rerun()

    # Cassetto opzionale per chi vuole vedere la foto ingrandita o correggere a mano
    with st.expander("🛠️ Vuoi vedere la foto o correggere una voce a mano? Apri qui", expanded=(not bool(active_key))):
        typed_k = st.text_input(
            "🔑 Chiave Google AI Studio (AIzaSy...):",
            value=st.session_state.get("custom_gemini_key", ""),
            key=f"api_key_box_{module_tag}",
            placeholder="Incolla qui la chiave AIzaSy..."
        )
        if typed_k and len(typed_k.strip()) > 15:
            st.session_state["custom_gemini_key"] = typed_k.strip()

        st.image(raw_bytes, caption=f"📸 Foto in RAM ({ram_kb:.1f} KB)", use_container_width=True)

        df_items = pd.DataFrame(st.session_state["ocr_items_df"])
        edited_items = st.data_editor(
            df_items,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key=f"items_ed_{module_tag}"
        )
        tot_man = sum(float(r.get("prezzo", 0.0) or 0.0) for _, r in edited_items.iterrows()) if not edited_items.empty else 0.0
        if st.button(f"💾 SALVA MODIFICA MANUALE (€ {tot_man:.2f})", key=f"man_save_{module_tag}", use_container_width=True):
            add_calendar_event(f"SCONTRINO ({module_tag})", f"{st.session_state['ocr_esercente']} (€ {tot_man:.2f})", -tot_man, 1, "OK")
            st.session_state["ram_clear_counter"] += 1
            st.toast(f"✅ Registrato € {tot_man:.2f} nel Calendario!")
            st.rerun()

# ==============================================================================
# CALENDARIO STORICO COMPATTO E ANTI-SPOSTAMENTO SU TELEFONINO
# ==============================================================================
def render_alpha_chrono_calendar():
    st.markdown("##### 📅 CALENDARIO STORICO (GIORNO · SETTIMANA · MESE)")
    df_cal = pd.DataFrame(st.session_state["chrono_ledger"])
    if df_cal.empty:
        st.info("Nessun movimento registrato.")
        return

    tot_entrate = df_cal[df_cal["amount"] > 0]["amount"].sum()
    tot_uscite = df_cal[df_cal["amount"] < 0]["amount"].sum()
    saldo_netto = tot_entrate + tot_uscite

    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#10B981;"><div class="kpi-custom-title">INCASSI / RESA CAFFÈ</div><div class="kpi-custom-value">+ € {tot_entrate:.2f}</div></div>""", unsafe_allow_html=True)
    with c_m2:
        st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#EF4444;"><div class="kpi-custom-title">USCITE & SCONTRINI</div><div class="kpi-custom-value">€ {tot_uscite:.2f}</div></div>""", unsafe_allow_html=True)
    with c_m3:
        st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#F59E0B;"><div class="kpi-custom-title">SALDO PERIODO</div><div class="kpi-custom-value">€ {saldo_netto:+.2f}</div></div>""", unsafe_allow_html=True)

    # Vista Schede Mobile (Non fa mai muovere la pagina a destra e sinistra!)
    st.markdown("###### 📋 ULTIMI MOVIMENTI REGISTRATI (VISTA STABILE PER TELEFONINO):")
    for idx_r, row_c in df_cal.iloc[::-1].iterrows():
        col_bar = "#10B981" if row_c["amount"] > 0 else "#EF4444"
        st.markdown(f"""
        <div style="background:#151B24; border:1px solid #283344; border-left:4px solid {col_bar}; padding:10px 12px; border-radius:3px; margin-bottom:6px;">
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#94A3B8; font-family:'Share Tech Mono', monospace;">
                <span>📅 {row_c['date']} · 🕒 {row_c['time']} · <b>{row_c['type']}</b></span>
                <span style="color:{col_bar}; font-size:14px; font-weight:900;">€ {row_c['amount']:+.2f}</span>
            </div>
            <div style="font-size:12px; color:#FFFFFF; margin-top:3px; font-family:'Share Tech Mono', monospace;">
                {row_c['desc']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("✏️ Apri Tabella Modificabile / Esporta o Carica Backup Mensile"):
        edited_df = st.data_editor(df_cal, num_rows="dynamic", use_container_width=True, hide_index=True, key="cal_ed_mob")
        if not edited_df.equals(df_cal):
            st.session_state["chrono_ledger"] = edited_df.to_dict("records")
            st.rerun()

        cal_json_str = json.dumps(st.session_state["chrono_ledger"], indent=2, ensure_ascii=False)
        st.download_button("💾 SCARICA BACKUP MESE (.JSON)", cal_json_str, file_name=f"calendario_alpha_{datetime.now().strftime('%Y_%m')}.json", mime="application/json", use_container_width=True)

# ==============================================================================
# 11. CORPO PRINCIPALE: UX "BLUM" FLUIDA SU MOBILE E DESKTOP
# ==============================================================================
rc_id = st.session_state["ram_clear_counter"]

if st.session_state["blum_sector"] is not None:
    sec_obj = next((s for s in all_squares if s["code"] == st.session_state["blum_sector"]), all_squares[0])
    svg_blum = SVG_ICONS.get(sec_obj["code"], SVG_ICONS["01"])

    if st.button("▲ TORNA ALLA GRIGLIA PRINCIPALE A.L.P.H.A.", key="exit_blum_top", use_container_width=True):
        st.session_state["blum_sector"] = None
        st.session_state["selected_sub"] = None
        st.rerun()

    st.markdown(f"""
    <div class="blum-stage" style="border: 2px solid {sec_obj['border']}; border-left: 6px solid {sec_obj['border']};">
        <div style="display:flex; align-items:center; gap:14px;">
            <div>{svg_blum}</div>
            <div>
                <div style="font-size:10px; color:{sec_obj['border']}; font-family:'Share Tech Mono';">{sec_obj['artifact']} // SETTORE {sec_obj['code']}</div>
                <div style="font-size:20px; font-weight:900; color:#FFFFFF;">{sec_obj['name']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Selettore sottomoduli stabile (non sborda mai su telefonino)
    sub_cols = st.columns(5)
    for idx_s, sub_label in enumerate(sec_obj["subs"]):
        with sub_cols[idx_s]:
            if st.button(sub_label, key=f"blum_sub_{sec_obj['code']}_{idx_s}", use_container_width=True):
                st.session_state["selected_sub"] = sub_label
                st.rerun()

    curr_sub = str(st.session_state.get("selected_sub", sec_obj["subs"][0]))

    # ==========================================================================
    # MODULO 10: BAR & DDT SENTINEL (1-CLICK SCATTA E SALVA!)
    # ==========================================================================
    if sec_obj["code"] == "10":
        if "5." in curr_sub:
            render_alpha_chrono_calendar()

        elif "2." in curr_sub:
            st.markdown("##### 🎹 TASTIERA CASSA RAPIDA (A → O)")
            uscita_euro = st.number_input("💶 Importo Uscita Cassetto (€):", min_value=0.50, max_value=5000.0, value=19.80, step=0.50, format="%.2f")
            ao_keys = list(st.session_state["bar_ao_labels"].keys())
            row1 = st.columns(4)
            for i, k_let in enumerate(ao_keys):
                lbl = st.session_state["bar_ao_labels"][k_let]
                if row1[i % 4].button(f"[{k_let}] {lbl}", key=f"btn_ao_{k_let}", use_container_width=True):
                    add_calendar_event(f"CASSA [{k_let}]", f"Uscita {lbl}", -uscita_euro, 1, "OK")
                    play_ems_synth("commlock")
                    st.toast(f"✅ Registrato: [{k_let}] -€ {uscita_euro:.2f}")
                    st.rerun()

        elif "3." in curr_sub:
            st.markdown("##### 🏁 CHIUSURA CASSA / CAMBIO TURNO (ANCHE SU PIÙ GIORNI)")
            tipo_punto = st.selectbox("Tipo Controllo:", ["🏁 CHIUSURA FINE GIORNATA", "⏱️ PARZIALE CAMBIO TURNO", "💶 ALLEGGERIMENTO TITOLARE"])
            giorni_coperti = st.selectbox("Giorni coperti da questo incasso:", [1, 2, 3, 4, 5, 6, 7], index=0)
            incasso_contato = st.number_input("Totale Contanti + POS (€):", 0.0, 100000.0, 680.0, step=10.0)
            if st.button("📅 REGISTRA CHIUSURA NEL CALENDARIO", use_container_width=True):
                segno = -incasso_contato if "ALLEGGERIMENTO" in tipo_punto else incasso_contato
                add_calendar_event("PUNTO CASSA", f"{tipo_punto} ({giorni_coperti} gg)", segno, giorni_coperti, "OK")
                play_ems_synth("commlock")
                st.success("✅ Chiusura registrata nel Calendario!")

        else:
            # VISTA PRINCIPALE SEMPLIFICATA PER TELEFONINO: SCATTA -> LEGGE -> SALVA DA SOLO!
            st.markdown("##### 📸 PASSO UNICO: SCATTA LA FOTO ALLO SCONTRINO / BOLLA (FA TUTTO DA SOLO)")

            c_cam1, c_cam2 = st.columns(2)
            with c_cam1:
                use_cam_ddt = st.toggle("📸 APRI FOTOCAMERA TELEFONO", value=True, key="tog_cam_ddt")
            with c_cam2:
                if st.button("☕ +1 KG CAFFÈ APERTO (TIMBRA ORA)", use_container_width=True):
                    st.session_state["bar_kg_caffe_aperti"] += 1.0
                    resa_sacchetto = st.session_state["bar_tazzine_per_kg"] * st.session_state["bank_prezzo_caffe"]
                    add_calendar_event("CAFFÈ (+1 KG)", f"Sacchetto 1 Kg (~135 caffè)", resa_sacchetto, 1, "OK")
                    play_ems_synth("commlock")
                    st.toast(f"☕ +1 Kg Caffè registrato (+€ {resa_sacchetto:.2f})!")
                    st.rerun()

            cam_ddt_shot = st.camera_input("Tocca 'Take Photo': legge e salva nel Calendario in automatico!", key=f"cam_ddt_{rc_id}") if use_cam_ddt else None
            ddt_file = st.file_uploader("📂 Oppure scegli una foto dalla galleria del telefono", type=["jpg", "jpeg", "png", "csv", "xml"], key=f"up_ddt_{rc_id}")

            active_ddt_stream = cam_ddt_shot if cam_ddt_shot is not None else ddt_file
            if active_ddt_stream is not None:
                process_photo_zero_click(active_ddt_stream, module_tag="DDT")

    # ==========================================================================
    # MODULO 11: BANK VAMPIRE SCANNER
    # ==========================================================================
    elif sec_obj["code"] == "11":
        if "5." in curr_sub:
            render_alpha_chrono_calendar()
        else:
            st.markdown("##### 🔫 BANK VAMPIRE // SCATTA FOTO ESTRATTO CONTO O CALCOLA COSTI POS")
            use_cam_bank = st.toggle("📸 APRI FOTOCAMERA PER ESTRATTO CONTO", value=False, key="tog_cam_bank")
            cam_bank_shot = st.camera_input("Scatta foto al riepilogo spese banca", key=f"cam_bank_{rc_id}") if use_cam_bank else None
            bank_file = st.file_uploader("📂 Oppure carica foto/CSV Estratto Conto", type=["csv", "txt", "jpg", "jpeg", "png"], key=f"up_bank_{rc_id}")

            active_bank_stream = cam_bank_shot if cam_bank_shot is not None else bank_file
            if active_bank_stream is not None:
                process_photo_zero_click(active_bank_stream, module_tag="BANK")

            b1, b2 = st.columns(2)
            st.session_state["bank_transato_pos"] = b1.number_input("Transato POS Mensile (€)", 500.0, 500000.0, st.session_state["bank_transato_pos"], step=500.0)
            st.session_state["bank_comm_dichiarata"] = b2.number_input("Comm. POS Dichiarata (%)", 0.10, 5.0, st.session_state["bank_comm_dichiarata"], step=0.05)
            b3, b4 = st.columns(2)
            st.session_state["bank_costi_occulti"] = b3.number_input("Spese Tenuta / Canoni / SDD (€)", 0.0, 5000.0, st.session_state["bank_costi_occulti"], step=10.0)
            st.session_state["bank_prezzo_caffe"] = b4.number_input("Prezzo Tazzina Caffè (€)", 0.80, 3.0, st.session_state["bank_prezzo_caffe"], step=0.10)

            costo_pos_base = st.session_state["bank_transato_pos"] * (st.session_state["bank_comm_dichiarata"] / 100.0)
            prelievo_totale_banca = costo_pos_base + st.session_state["bank_costi_occulti"]
            vero_tasso_pos = (prelievo_totale_banca / st.session_state["bank_transato_pos"]) * 100.0
            caffe_pareggio = round(prelievo_totale_banca / st.session_state["bank_prezzo_caffe"])

            v1, v2 = st.columns(2)
            with v1:
                st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#EF4444;"><div class="kpi-custom-title">VERO TASSO POS EFFETTIVO</div><div class="kpi-custom-value">{vero_tasso_pos:.2f} %</div></div>""", unsafe_allow_html=True)
            with v2:
                st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#F59E0B;"><div class="kpi-custom-title">CAFFÈ NECESSARI PER COPRIRE I COSTI BANCARI</div><div class="kpi-custom-value">{caffe_pareggio} Tazzine/mese</div><div class="kpi-custom-sub" style="color:#10B981;">● Corrispettivo di € {prelievo_totale_banca:.2f}</div></div>""", unsafe_allow_html=True)

    # --- TUTTI GLI ALTRI MODULI (01 -> 09) ---
    else:
        st.markdown(f"##### ⚡ TELEMETRIA // {sec_obj['name']} — {curr_sub}")
        st.link_button(f"🚀 APRI CONSOLLE ESTERNA ({sec_obj['name']})", sec_obj["url"], use_container_width=True)

# --- VISTA MATRICE CENTRALE PULITA ---
else:
    col_left, col_right = st.columns([3.2, 1.1])
    with col_left:
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
        st.markdown("""<div class="ems-panel"><span style="font-size:11px; font-weight:900; color:#FFFFFF;">ALPHA EMS-1975 SYNTH</span></div>""", unsafe_allow_html=True)
        if st.button("▶ X5-7 DATA BURST", use_container_width=True):
            play_ems_synth("burst")
        if st.button("◈ COMMLOCK 1975", use_container_width=True):
            play_ems_synth("commlock")
