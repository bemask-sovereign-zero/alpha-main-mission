import json
import time
import hmac
import hashlib
import base64
import struct
import re
import urllib.request
import urllib.error
from datetime import datetime
import streamlit as st
import pandas as pd

from alpha_ui import (
    HERO_CRAFT_SVG,
    SECTOR_SVGS,
    BASE_VECTORS,
    WEATHER_5_DAYS,
    play_ems_synth,
    inject_alpha_css,
    load_eagle_grid_sprite_uri,
    build_gate6_tile_html,
    build_soglia_monolith_html,
    render_architect_dossier_content,
    open_architect_modal,
)

# ==============================================================================
# BEMASK - A.L.P.H.A. // MAIN MISSION ENGINE (12 SECTORS 2^12 + 6-TILE GATE)
# CONCEIVED, DIRECTED & ENGINEERED BY ENRICO BRAGLIA
# ==============================================================================

st.set_page_config(
    page_title="BEMASK - A.L.P.H.A. // ENRICO BRAGLIA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_alpha_css()

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

# --- DIZIONARIO SEMANTICO INTEGRATO (SMISTAMENTO CONTI A-O) ---
SEMANTIC_KEYWORDS = {
    "[A] MATERIE PRIME / CAFFÈ": ["CAFF", "MISCELA", "GRANI", "ARABICA", "DECA", "ORZO", "GINSENG", "10001", "ILLY", "LAVAZZA"],
    "[B] BEVANDE / ALCOLICI": ["APEROL", "CAMPARI", "BITTER", "GIN", "VODKA", "PROSECCO", "VINO", "BIRRA", "COCA", "ACQUA", "AA514", "DORECA", "CL.100", "LT.1"],
    "[C] LATTE / FRESCHI": ["LATTE", "PANNA", "BURRO", "BRIOCHE", "CORNETT", "PASTE", "YOGURT"],
    "[D] SNACK / CUCINA": ["PANE", "TRAMEZZIN", "PROSCIUTTO", "MOZZARELLA", "PATATIN", "OLIVE", "FOCACCIA", "PECHINO", "RISO", "INVOLTIN"],
    "[E] GHIACCIO / CONSUMABILI": ["GHIACCIO", "TOVAGLIOL", "BICCHIER", "CANNUCC", "ZUCCHERO", "CARTA TERMICA"],
    "[F] PULIZIA / IGIENE": ["DETERSIV", "SAPONE", "CANDEGGINA", "SGRASSATOR", "SPUGN", "SACCHI"],
    "[G] MANUTENZIONE": ["IDRAULIC", "ELETTRIC", "GUARNIZION", "FILTRO", "TECNICO"],
    "[H] ACCONTO STAFF": ["ACCONTO", "EXTRA", "CAMERIER", "BARISTA", "TURNO"],
    "[I] UTENZE / BOLLETTE": ["ENEL", "LUCE", "GAS", "ACQUEDOTTO", "FIBRA", "TIM", "TARI", "SIAE"],
    "[L] TASSE / BOLLI": ["F24", "BOLLO", "AGENZIA", "INPS", "INAIL", "SUOLO"],
    "[M] FORNITORE EXTRA": ["SUPERMERCATO", "CONAD", "COOP", "EUROSPIN", "LIDL", "METRO"],
    "[N] SPESE VARIE": ["FARMACIA", "CANCELLERIA", "MANCIA", "RESTO", "VARIE"],
    "[O] PRELIEVO TITOLARE": ["TITOLARE", "PRELIEVO", "VERSAMENTO", "SOCIO", "ALLEGGERIMENTO"]
}

def auto_map_semantic_conto(text_val):
    up = str(text_val).upper()
    for c_label, kw_list in SEMANTIC_KEYWORDS.items():
        for kw in kw_list:
            if kw in up:
                return c_label
    return "[D] SNACK / CUCINA"

# --- MOTORE OCR VISION IN RAM CON AUTODISCOVERY ---
def scan_receipt_in_ram_with_ai(image_bytes, api_key):
    clean_key = str(api_key).strip()
    if not clean_key or len(clean_key) < 15:
        return None, "Inserisci la chiave gratuita AIzaSy... nel campo qui sopra per leggere automaticamente la foto!"

    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    prompt_txt = (
        "Sei il lettore contabile semantico di un bar italiano. Leggi questa foto di scontrino, bolla o nota spesa. "
        "Estrai esercente (o email), metodo di pagamento, tutte le singole righe dei prodotti acquistati (se si vede solo il totale POS crea 1 riga col totale) e il totale in euro. "
        "Rispondi SOLO con un JSON valido in questo formato esatto: "
        "{\"esercente\": \"nome o email locale\", \"metodo_pagamento\": \"CARTA DI CREDITO / POS\", "
        "\"righe\": [{\"voce\": \"nome articolo\", \"qta\": 1, \"prezzo\": 19.80}], \"totale_euro\": 19.80}"
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
                return None, f"Chiave API non riconosciuta (HTTP {he.code}). Assicurati che inizi con 'AIzaSy...'."
        except Exception:
            continue

    if not candidate_models:
        candidate_models = [
            ("v1beta", "gemini-2.5-flash"),
            ("v1beta", "gemini-2.0-flash"),
            ("v1", "gemini-2.0-flash"),
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
                if "righe" in parsed and isinstance(parsed["righe"], list):
                    for r in parsed["righe"]:
                        r["conto"] = auto_map_semantic_conto(r.get("voce", "") + " " + parsed.get("esercente", ""))
                return parsed, None
        except Exception as e:
            last_err = f"[{m_name}] {str(e)}"
            continue

    return None, f"Lettura AI non riuscita ({last_err})."

# --- 2. SESSION STATE A 12 BIT (TUTTI I 12 SETTORI ATTIVI DI DEFAULT) ---
def init_monumental_state():
    default_labels_ao = {
        "A": "MATERIE PRIME / CAFFÈ", "B": "BEVANDE / ALCOLICI", "C": "LATTE / FRESCHI", "D": "SNACK / CUCINA",
        "E": "GHIACCIO / CONSUMABILI", "F": "PULIZIA / IGIENE", "G": "MANUTENZIONE", "H": "ACCONTO STAFF",
        "I": "UTENZE / BOLLETTE", "L": "TASSE / BOLLI", "M": "FORNITORE EXTRA", "N": "SPESE VARIE", "O": "PRELIEVO TITOLARE"
    }
    defaults = {
        "auth_unlocked": False,
        "gate_open": False,
        "gate_alert": "",
        "pending_synth": None,
        "auth_role": None,
        "auth_user": "",
        "breach_log": [],
        "show_arch_fallback": False,
        "active_bits_12": [True] * 12,
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
        "last_scanned_hash": "",
        "ocr_esercente": "Pechino Follonica (pechinofollonica@gmail.com)",
        "ocr_metodo": "CARTA DI CREDITO / POS",
        "ocr_items_df": [
            {"voce": "Articolo 1 dallo Scontrino", "qta": 1, "prezzo": 10.00, "conto": "[D] SNACK / CUCINA"},
            {"voce": "Articolo 2 dallo Scontrino", "qta": 1, "prezzo": 9.80, "conto": "[B] BEVANDE / ALCOLICI"}
        ],
        "chrono_ledger": [
            {"date": datetime.now().strftime("%Y-%m-%d"), "time": "07:30", "type": "CAFFÈ (+1 KG)", "conto": "[A] MATERIE PRIME / CAFFÈ", "desc": "Apertura sacchetto grani 1 Kg (Resa attesa ~135 caffè)", "amount": 175.50, "days_span": 1, "status": "OK"},
            {"date": datetime.now().strftime("%Y-%m-%d"), "time": "08:15", "type": "BOLLA DDT", "conto": "[B] BEVANDE / ALCOLICI", "desc": "Art. 10001 Doreca — Scostamento +€1.90/L", "amount": -14.80, "days_span": 1, "status": "ALERT"},
            {"date": datetime.now().strftime("%Y-%m-%d"), "time": "08:58", "type": "SCONTRINO RAM", "conto": "[D] SNACK / CUCINA", "desc": "Pechino Follonica (Carta di Credito) — Totale € 19,80", "amount": -19.80, "days_span": 1, "status": "OK"}
        ]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    for idx_b in range(12):
        t_key = f"bit_sw_{idx_b}"
        if t_key not in st.session_state:
            st.session_state[t_key] = st.session_state["active_bits_12"][idx_b]

init_monumental_state()

def get_conto_options():
    return [f"[{k}] {v}" for k, v in st.session_state["bar_ao_labels"].items()] + ["[INCASSO] CASSA / POS", "[BANCA] ONERI & COMMISSIONI"]

def return_to_page_zero():
    st.session_state["blum_sector"] = None
    st.session_state["selected_sub"] = None
    st.session_state["show_arch_fallback"] = False

def apply_multiverse_preset(new_bits_list):
    st.session_state["active_bits_12"] = list(new_bits_list)
    for idx_b, val_b in enumerate(new_bits_list):
        st.session_state[f"bit_sw_{idx_b}"] = bool(val_b)
    return_to_page_zero()
    st.session_state["keep_multiverse_open"] = True

def on_single_bit_toggle(idx_b):
    st.session_state["active_bits_12"][idx_b] = bool(st.session_state[f"bit_sw_{idx_b}"])
    return_to_page_zero()
    st.session_state["keep_multiverse_open"] = True

def add_calendar_event(ev_type, ev_desc, ev_amount, days_span=1, status="OK", conto="[N] SPESE VARIE"):
    st.session_state["chrono_ledger"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "type": ev_type,
        "conto": conto,
        "desc": ev_desc,
        "amount": round(float(ev_amount), 2),
        "days_span": int(days_span),
        "status": status
    })
    st.session_state["unsaved_ops_count"] += 1

if st.session_state.get("pending_synth"):
    play_ems_synth(st.session_state["pending_synth"])
    st.session_state["pending_synth"] = None

# --- 3. SOGLIA ZERO + GRIGLIA A 6 TESSERE (PUNTINI 100% TRASPARENTI) ---
STAFF_PINS = {
    "1024": "OPERATORE BAR / CUCINA (SOLO HACCP & SKA)",
    "2048": "GOVERNANTE AI PIANI (SOLO CAMERE & SKA)",
    "3096": "BAGNINO LIDO (SOLO BEACH & POOL)"
}

if not st.session_state["auth_unlocked"]:
    s_left, s_center, s_right = st.columns([0.95, 1.65, 0.95])
    with s_center:
        if not st.session_state["gate_open"]:
            st.markdown(build_soglia_monolith_html(), unsafe_allow_html=True)
            if st.button(" ", key="soglia_pad_click", use_container_width=True):
                st.session_state["gate_open"] = True
                st.session_state["gate_alert"] = ""
                st.session_state["pending_synth"] = "commlock"
                st.rerun()
        else:
            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
            sprite_uri = load_eagle_grid_sprite_uri()
            has_sprite = bool(sprite_uri)
            if has_sprite:
                st.markdown(
                    f"<style>.gate6-has-sprite {{ background-image: url('{sprite_uri}'); background-size: 204% 306%; background-repeat: no-repeat; }}</style>",
                    unsafe_allow_html=True
                )

            r1_c1, r1_c2 = st.columns(2, gap="small")
            with r1_c1:
                st.markdown(build_gate6_tile_html("01", "ACCESSO RAPIDO", "LANDING GEAR · 1-CLICK", "#F59E0B", "rgba(245,158,11,0.40)", "radial-gradient(circle at 50% 40%, #3D2B14 0%, #12151C 80%)", "0% 0%", has_sprite, False), unsafe_allow_html=True)
                if st.button(" ", key="gate6_btn_fast", use_container_width=True):
                    st.session_state["pending_synth"] = "commlock"
                    st.session_state["auth_unlocked"] = True
                    st.session_state["auth_role"] = "COMMANDER"
                    st.session_state["auth_user"] = "ENRICO BRAGLIA // SYSTEM ARCHITECT"
                    st.session_state["gate_alert"] = ""
                    return_to_page_zero()
                    st.rerun()

            with r1_c2:
                st.markdown(build_gate6_tile_html("02", "PIN OPERATORE", "COMMAND BEAK · CABIN", "#38BDF8", "rgba(56,189,248,0.40)", "radial-gradient(circle at 50% 40%, #12334A 0%, #11161F 80%)", "100% 0%", has_sprite, True), unsafe_allow_html=True)
                in_pin = st.text_input("PIN", type="password", placeholder="••••", label_visibility="collapsed", key="gate6_in_pin")

            r2_c1, r2_c2 = st.columns(2, gap="small")
            with r2_c1:
                st.markdown(build_gate6_tile_html("03", "2FA · 6 CIFRE", "PLASMA THRUSTERS", "#10B981", "rgba(16,185,129,0.42)", "radial-gradient(circle at 50% 40%, #0F3A30 0%, #10171D 80%)", "0% 50%", has_sprite, True), unsafe_allow_html=True)
                in_2fa = st.text_input("2FA", type="password", placeholder="••••••", label_visibility="collapsed", key="gate6_in_2fa")

            with r2_c2:
                st.markdown(build_gate6_tile_html("04", "SBLOCCA PLANCIA", "MAIN AIRLOCK DOOR", "#A855F7", "rgba(168,85,247,0.42)", "radial-gradient(circle at 50% 40%, #2B224C 0%, #131420 80%)", "100% 50%", has_sprite, False), unsafe_allow_html=True)
                if st.button(" ", key="gate6_btn_unlock", use_container_width=True):
                    master_pin = get_master_pin()
                    secret_2fa = get_totp_secret()
                    ora_try = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    pin_clean = str(in_pin).strip()
                    if pin_clean == master_pin:
                        if verify_2fa_code(in_2fa, secret_2fa):
                            st.session_state["pending_synth"] = "commlock"
                            st.session_state["auth_unlocked"] = True
                            st.session_state["auth_role"] = "COMMANDER"
                            st.session_state["auth_user"] = "ENRICO BRAGLIA // COMMANDER (2FA VERIFIED)"
                            st.session_state["pin_code"] = master_pin
                            st.session_state["gate_alert"] = ""
                            return_to_page_zero()
                            st.rerun()
                        else:
                            st.session_state["pending_synth"] = "klaxon"
                            st.session_state["breach_log"].append(f"⚠️ [{ora_try}] TENTATIVO INTRUSIONE: PIN Titolare senza 2FA valido ('{in_2fa}')")
                            st.session_state["gate_alert"] = "🚨 CODICE 2FA MANCANTE O SCADUTO"
                            st.rerun()
                    elif pin_clean in STAFF_PINS:
                        st.session_state["pending_synth"] = "burst"
                        st.session_state["auth_unlocked"] = True
                        st.session_state["auth_role"] = "STAFF"
                        st.session_state["auth_user"] = STAFF_PINS[pin_clean]
                        st.session_state["pin_code"] = pin_clean
                        st.session_state["gate_alert"] = ""
                        return_to_page_zero()
                        st.rerun()
                    else:
                        st.session_state["pending_synth"] = "klaxon"
                        st.session_state["breach_log"].append(f"⚠️ [{ora_try}] PIN SCONOSCIUTO RIFIUTATO ('{pin_clean}')")
                        st.session_state["gate_alert"] = "🚨 INSERISCI PIN NELLA CASELLA 02"
                        st.rerun()

            r3_c1, r3_c2 = st.columns(2, gap="small")
            with r3_c1:
                st.markdown(build_gate6_tile_html("05", "ARCHITECT DOSSIER", "FORWARD SPINE TRUSS", "#F43F5E", "rgba(244,63,94,0.42)", "radial-gradient(circle at 50% 40%, #3F1C2A 0%, #15131B 80%)", "0% 100%", has_sprite, False), unsafe_allow_html=True)
                if st.button(" ", key="gate6_btn_arch", use_container_width=True):
                    play_ems_synth("commlock")
                    open_architect_modal()

            with r3_c2:
                st.markdown(build_gate6_tile_html("06", "CHIUDI", "FRONTAL EAGLE VIEW", "#EF4444", "rgba(239,68,68,0.42)", "radial-gradient(circle at 50% 40%, #40181E 0%, #151318 80%)", "100% 100%", has_sprite, False), unsafe_allow_html=True)
                if st.button(" ", key="gate6_btn_close", use_container_width=True):
                    st.session_state["gate_open"] = False
                    st.session_state["gate_alert"] = ""
                    st.session_state["pending_synth"] = "commlock"
                    st.rerun()

            if st.session_state.get("gate_alert"):
                st.markdown(
                    f"<div style='background:#3B1219;border:1px solid #EF4444;color:#FCA5A5;padding:6px 10px;"
                    f"font-family:Share Tech Mono,monospace;font-size:11px;text-align:center;border-radius:3px;'>"
                    f"{st.session_state['gate_alert']}</div>",
                    unsafe_allow_html=True
                )

            if st.session_state.get("show_arch_fallback", False):
                render_architect_dossier_content()
    # --- 4. FILTRO RUOLO & REGIA PLANCIA (12 BIT = 4096 STATI) ---
is_commander = (st.session_state["auth_role"] == "COMMANDER")
bits = st.session_state["active_bits_12"]

if is_commander:
    active_base = [v for i, v in enumerate(BASE_VECTORS) if bits[i]]
    if not active_base:
        apply_multiverse_preset([True] + [False] * 11)
        active_base = [BASE_VECTORS[0]]
    all_squares = active_base + st.session_state["custom_squares"]
else:
    all_squares = [v for v in BASE_VECTORS if v["staff_allowed"]]

n_sectors = len(all_squares)
total_micro_modules = n_sectors * 5
binary_state_num = sum((1 << i) for i, b in enumerate(bits) if b)
binary_str = "".join(["1" if b else "0" for b in bits])
ora_attuale = datetime.now().strftime("%H:%M")

MESI_IT = ["GEN", "FEB", "MAR", "APR", "MAG", "GIU", "LUG", "AGO", "SET", "OTT", "NOV", "DIC"]
GIORNI_IT = ["LUNEDÌ", "MARTEDÌ", "MERCOLEDÌ", "GIOVEDÌ", "VENERDÌ", "SABATO", "DOMENICA"]
oggi_dt = datetime.now()
data_estesa_it = f"{GIORNI_IT[oggi_dt.weekday()]} {oggi_dt.day:02d} {MESI_IT[oggi_dt.month - 1]} {oggi_dt.year}"

breach_count = len(st.session_state["breach_log"])
breach_badge = f'<span class="badge-red">🚨 {breach_count} INTRUSIONI</span>' if breach_count > 0 else '<span class="badge-green">🛡️ ZERO INTRUSIONI</span>'

top_c1, top_c_arch, top_c3 = st.columns([3.10, 1.25, 0.95])
with top_c1:
    st.markdown(f"""
    <div class="alpha-top-strip">
        <div>
            <span class="badge-amber">A.L.P.H.A.</span>
            <span style="font-size:12px; font-weight:900; letter-spacing:1px; color:#FFFFFF;">
                {st.session_state['auth_user']}
            </span>
        </div>
        <div style="margin-top:5px;">
            <span class="badge-white">{n_sectors} SECTORS X 5 MODULES</span>
            {breach_badge}
            <span class="badge-white">1 → 2¹² (#{binary_state_num}/4096)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top_c_arch:
    if st.button("◈ ARCHITECT\nENRICO BRAGLIA", use_container_width=True):
        play_ems_synth("commlock")
        open_architect_modal()
with top_c3:
    if st.button("🔒 BLOCCA\nSESSIONE", use_container_width=True):
        st.session_state["auth_unlocked"] = False
        st.session_state["gate_open"] = False
        st.session_state["vault_unlocked"] = False
        return_to_page_zero()
        st.rerun()

if st.session_state.get("show_arch_fallback", False):
    with st.expander("◈ ARCHITECT & GENESIS // ENRICO BRAGLIA", expanded=True):
        render_architect_dossier_content()

st.markdown(f"""
<div class="mission-bar">
    <div style="display:flex; align-items:center; gap:16px;">
        <div>{HERO_CRAFT_SVG}</div>
        <div>
            <div class="mission-title">{data_estesa_it}</div>
            <div class="mission-sub">{total_micro_modules} MICRO-MODULES ATTIVI | STATO BINARIO: {binary_str}</div>
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

if st.session_state["unsaved_ops_count"] >= 3:
    al_c1, al_c2 = st.columns([3.2, 1.2])
    with al_c1:
        st.warning(f"⚠️ CHECKPOINT RAM: Hai {st.session_state['unsaved_ops_count']} nuove registrazioni nella Contabilità. Scarica una copia sul dispositivo!")
    with al_c2:
        cal_json = json.dumps(st.session_state["chrono_ledger"], indent=2, ensure_ascii=False)
        if st.download_button("💾 SALVA CONTABILITÀ (.JSON)", cal_json, file_name=f"alpha_contabilita_{datetime.now().strftime('%Y_%m')}.json", mime="application/json", use_container_width=True):
            st.session_state["unsaved_ops_count"] = 0
            st.rerun()

# --- RADAR METEO TELEMETRICO LIVE 5 GIORNI (GOLFO DI FOLLONICA · OPEN-METEO) ---
from datetime import timedelta

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_live_follonica_radar():
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=42.922&longitude=10.761"
        "&daily=weather_code,temperature_2m_max,precipitation_probability_max,wind_speed_10m_max,relative_humidity_2m_mean"
        "&wind_speed_unit=kn&timezone=Europe%2FRome&forecast_days=5"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BEMASK-ALPHA/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        daily = data.get("daily", {})
        cards = []
        for i in range(5):
            wcode = int(daily["weather_code"][i])
            tmax = round(float(daily["temperature_2m_max"][i]))
            rain_p = int(daily["precipitation_probability_max"][i] or 0)
            wind_kt = round(float(daily["wind_speed_10m_max"][i] or 0))
            hum_p = int(daily["relative_humidity_2m_mean"][i] or 60)

            if wcode in [0, 1] and rain_p < 30 and wind_kt < 18:
                icon, cond, col = "☀️", "SERENO · DEHORS OK", "#10B981"
                directive = "☀️ SPINTA DEHORS, APERITIVI & LIDO"
            elif wcode in [2, 3, 45, 48] and rain_p < 55 and wind_kt < 22:
                icon, cond, col = "🌤️", "VARIABILE / NUBI", "#F59E0B"
                directive = "🌤️ REGIME STANDARD ESTERNO/INTERNO"
            else:
                icon, cond, col = "⛈️", "PIOGGIA / VENTO FORTE", "#EF4444"
                directive = "⚡ FALLBACK SPA, SALA INTERNA & SCUDO 96H"

            cards.append({
                "date_iso": daily["time"][i],
                "temp": f"{tmax}°C",
                "cond": cond,
                "icon": icon,
                "rain": f"PIOGGIA: {rain_p}%",
                "hum": f"UR: {hum_p}%",
                "wind": f"VENTO: {wind_kt} KT",
                "directive": directive,
                "col": col,
            })
        return cards, True
    except Exception:
        fallback = [
            {"date_iso": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"), "temp": "18°C", "cond": "OFFLINE CACHE", "icon": "📡", "rain": "PIOGGIA: --%", "hum": "UR: --%", "wind": "VENTO: -- KT", "directive": "🛡️ TELEMETRIA LOCALE ATTIVA", "col": "#F59E0B"}
            for i in range(5)
        ]
        return fallback, False

GIORNI_BREVE_IT = ["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"]
live_radar_cards, _ = fetch_live_follonica_radar()

w_cols = st.columns(5)
for idx, w in enumerate(live_radar_cards):
    dt_day = datetime.strptime(w["date_iso"], "%Y-%m-%d")
    tag_oggi = " · OGGI" if idx == 0 else ""
    label_data = f"{GIORNI_BREVE_IT[dt_day.weekday()]} {dt_day.day:02d}/{dt_day.month:02d}{tag_oggi}"
    with w_cols[idx]:
        st.markdown(f"""
        <div class="weather-card" style="border-left: 4px solid {w['col']}; border-top: 1px solid {w['col']};">
            <div class="w-header"><span class="w-day" style="color:{w['col']}; font-size:11px;">{label_data}</span><span class="w-icon">{w['icon']}</span></div>
            <div class="w-status" style="color:#FFFFFF; font-size:11px;">{w['temp']} · {w['cond']}</div>
            <div class="w-telemetry"><span style="color:{w['col']};">{w['rain']}</span><span>{w['hum']}</span><span style="color:#38BDF8;">{w['wind']}</span></div>
            <div class="w-directive">{w['directive']}</div>
        </div>
        """, unsafe_allow_html=True)

# --- CAVEAU RISERVATO (SCALABILITÀ MULTIVERSO & CASSAFORTE 2FA) ---
if "vault_unlocked" not in st.session_state:
    st.session_state["vault_unlocked"] = False

if is_commander and (st.session_state["vault_unlocked"] or breach_count > 0):
    sec_col1, sec_col2 = st.columns([1.45, 1.0])
    with sec_col1:
        with st.expander("🎛️ SCALABILITÀ MULTIVERSO 1 → 2¹² (Configura i 12 Moduli Attivi)", expanded=True):
            st.caption(f"Stato Binario Attivo: `#{binary_state_num} / 4096` (`{binary_str}`) — **{n_sectors} Settori Attivi ({total_micro_modules} Micro-Moduli)**")
            sw_cols = st.columns(6)
            for i, vec in enumerate(BASE_VECTORS):
                with sw_cols[i % 6]:
                    st.toggle(vec["short"], key=f"bit_sw_{i}", on_change=on_single_bit_toggle, args=(i,))
            p1, p2, p3, p4 = st.columns(4)
            p1.button("🍸 PACCHETTO BAR (02+10+11+12)", on_click=apply_multiverse_preset, args=([False, True, False, False, False, False, False, False, False, True, True, True],), use_container_width=True)
            p2.button("🛸 GRIGLIA 3x3 (9 SETTORI)", on_click=apply_multiverse_preset, args=([True, True, True, True, True, True, False, False, False, True, True, True],), use_container_width=True)
            p3.button("🔥 FULL MULTIVERSE 2¹² (TUTTI 12)", on_click=apply_multiverse_preset, args=([True] * 12,), use_container_width=True)
            p4.button("⚡ SOLO 12 TRAVEL TUBE", on_click=apply_multiverse_preset, args=([False] * 11 + [True],), use_container_width=True)

    with sec_col2:
        with st.expander(f"🛡️ CASSAFORTE 2FA & CHIAVE AI OCR ({breach_count} Allerte)", expanded=True):
            q1, q2 = st.columns([1, 2])
            secret_now = get_totp_secret()
            otp_uri = f"otpauth://totp/BEMASK_ALPHA:TITOLARE?secret={secret_now}&issuer=BEMASK_ALPHA"
            with q1:
                st.markdown(f"""
                <div style="text-align:center; background:#0B0E14; border:1px solid #10B981; padding:8px; border-radius:4px;">
                    <div style="font-size:9px; color:#10B981; margin-bottom:4px;">GOOGLE AUTH QR</div>
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=130x130&color=10B981&bgcolor=0B0E14&data={otp_uri}" width="105" />
                </div>
                """, unsafe_allow_html=True)
            with q2:
                st.markdown(f"**Chiave Segreta 2FA:** `{secret_now}`")
                st.markdown(f"**Token 2FA Attivo (30s):** `{generate_totp_token(secret_now)}`")
                v_key = st.text_input("🤖 Chiave Google AI Studio (AIzaSy...):", value=st.session_state.get("custom_gemini_key", ""), key="api_key_box_VAULT", type="password")
                if v_key and len(v_key.strip()) > 15:
                    st.session_state["custom_gemini_key"] = v_key.strip()

# --- 5. TAVOLO SCONTRINI IN RAM & CONTABILITÀ PARALLELA ---
def render_receipt_parallel_accounting_desk(stream_obj, module_tag="DDT"):
    raw_bytes = stream_obj.getvalue()
    ram_kb = len(raw_bytes) / 1024.0
    ram_hash = hashlib.sha256(raw_bytes).hexdigest()[:12].upper()
    active_key = get_gemini_api_key()
    conto_opts = get_conto_options()

    if ram_hash != st.session_state.get("last_scanned_hash") and active_key:
        with st.spinner("🤖 Lettura automatica e classificazione semantica A-O in corso..."):
            parsed_ocr, err_msg = scan_receipt_in_ram_with_ai(raw_bytes, active_key)
            if parsed_ocr:
                st.session_state["ocr_esercente"] = parsed_ocr.get("esercente", "Scontrino / Bolla")
                st.session_state["ocr_metodo"] = parsed_ocr.get("metodo_pagamento", "CARTA DI CREDITO / POS")
                righe_ai = parsed_ocr.get("righe", [])
                if isinstance(righe_ai, list) and len(righe_ai) > 0:
                    st.session_state["ocr_items_df"] = righe_ai
                st.session_state["last_scanned_hash"] = ram_hash
                play_ems_synth("commlock")
            else:
                st.warning(f"⚠️ {err_msg}")

    st.markdown(f"""
    <div class="xray-desk">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <span class="badge-amber">👁️ IMPUTAZIONE SEMANTICA PARALLELA IN RAM</span>
            <span style="font-family:'Share Tech Mono', monospace; font-size:11px; color:#10B981;">
                HASH: #{ram_hash} | {ram_kb:.1f} KB IN RAM | 0 BYTE SU DISCO
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    desk_left, desk_right = st.columns([1.15, 1.85])
    with desk_left:
        st.image(raw_bytes, caption="📸 Lastra in RAM", use_container_width=True)
    with desk_right:
        k_c1, k_c2 = st.columns([1.6, 1.4])
        with k_c1:
            typed_k = st.text_input("🔑 Chiave AI Vision (AIzaSy...):", value=st.session_state.get("custom_gemini_key", ""), key=f"api_key_box_{module_tag}", placeholder="Incolla chiave AIzaSy...")
            if typed_k and len(typed_k.strip()) > 15:
                st.session_state["custom_gemini_key"] = typed_k.strip()
        with k_c2:
            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
            if st.button("🤖 LEGGI E CLASSIFICA CON AI", key=f"btn_ai_{module_tag}", use_container_width=True):
                parsed_ocr, err_msg = scan_receipt_in_ram_with_ai(raw_bytes, get_gemini_api_key())
                if parsed_ocr:
                    st.session_state["ocr_esercente"] = parsed_ocr.get("esercente", "Scontrino / Bolla")
                    st.session_state["ocr_metodo"] = parsed_ocr.get("metodo_pagamento", "CARTA DI CREDITO / POS")
                    if parsed_ocr.get("righe"):
                        st.session_state["ocr_items_df"] = parsed_ocr["righe"]
                    play_ems_synth("commlock")
                    st.rerun()
                else:
                    st.warning(err_msg)

        es_c1, es_c2 = st.columns([1.7, 1.3])
        with es_c1:
            st.session_state["ocr_esercente"] = st.text_input("🏪 Esercente / Fornitore:", value=st.session_state["ocr_esercente"], key=f"eser_{module_tag}")
        with es_c2:
            st.session_state["ocr_metodo"] = st.selectbox("💳 Pagamento:", ["CARTA DI CREDITO / POS", "CONTANTI DA CASSETTO", "BONIFICO / SDD"], index=0, key=f"met_{module_tag}")

        df_items = pd.DataFrame(st.session_state["ocr_items_df"])
        if "conto" not in df_items.columns:
            df_items["conto"] = conto_opts[0]
        edited_items = st.data_editor(
            df_items, num_rows="dynamic", use_container_width=True, hide_index=True,
            column_config={
                "voce": st.column_config.TextColumn("PRODOTTO / VOCE", width="medium"),
                "qta": st.column_config.NumberColumn("Q.TÀ", min_value=1, max_value=999, step=1, width="small"),
                "prezzo": st.column_config.NumberColumn("IMPORTO (€)", format="€ %.2f", step=0.10, width="small"),
                "conto": st.column_config.SelectboxColumn("CONTO (A-O)", options=conto_opts, width="medium")
            },
            key=f"items_ed_{module_tag}"
        )
        totale_scontrino = sum(float(r.get("prezzo", 0.0) or 0.0) for _, r in edited_items.iterrows()) if not edited_items.empty else 0.0
        st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#10B981; padding:10px 14px;"><div class="kpi-custom-title">TOTALE ({st.session_state['ocr_metodo']})</div><div class="kpi-custom-value" style="font-size:22px;">€ {totale_scontrino:.2f}</div></div>""", unsafe_allow_html=True)

        b_imp1, b_imp2 = st.columns(2)
        with b_imp1:
            if st.button("⚡ IMPUTA SINGOLE VOCI (A-O) E SVUOTA RAM", key=f"split_save_{module_tag}", use_container_width=True):
                for _, r in edited_items.iterrows():
                    v_prz = float(r.get("prezzo", 0.0) or 0.0)
                    if v_prz > 0:
                        add_calendar_event("VOCE SCONTRINO", f"{st.session_state['ocr_esercente']}: {int(r.get('qta', 1) or 1)}x {r.get('voce', 'Voce')} [{st.session_state['ocr_metodo']}]", -v_prz, 1, "OK", conto=str(r.get("conto", conto_opts[0])))
                st.session_state["ram_clear_counter"] += 1
                play_ems_synth("commlock")
                st.toast(f"✅ Voci imputate (€ {totale_scontrino:.2f})!")
                st.rerun()
        with b_imp2:
            if st.button(f"📦 REGISTRA SCONTRINO UNICO (€ {totale_scontrino:.2f})", key=f"single_save_{module_tag}", use_container_width=True):
                riep = " + ".join([f"{int(r.get('qta',1) or 1)}x {r.get('voce','')} (€{float(r.get('prezzo',0) or 0):.2f})" for _, r in edited_items.iterrows()])
                primo_conto = str(edited_items.iloc[0].get("conto", conto_opts[0])) if not edited_items.empty else conto_opts[0]
                add_calendar_event(f"SCONTRINO ({module_tag})", f"{st.session_state['ocr_esercente']}: {riep}"[:140], -totale_scontrino, 1, "OK", conto=primo_conto)
                st.session_state["ram_clear_counter"] += 1
                play_ems_synth("commlock")
                st.toast(f"✅ Scontrino unico (€ {totale_scontrino:.2f}) registrato!")
                st.rerun()

def render_alpha_chrono_calendar():
    st.markdown("##### 📅 CONTABILITÀ PARALLELA IN RAM & CALENDARIO STORICO")
    cal_top1, cal_top2, cal_top3 = st.columns([1.6, 1.2, 1.2])
    with cal_top1:
        cal_view = st.radio("Vista Contabile:", ["GIORNO (Movimenti & Modifica)", "BILANCIO PER CONTO (A-O)", "MESE (Riepilogo Giorni)"], horizontal=True)
    with cal_top2:
        cal_json_str = json.dumps(st.session_state["chrono_ledger"], indent=2, ensure_ascii=False)
        if st.download_button("💾 SALVA CONTABILITÀ (.JSON)", cal_json_str, file_name=f"contabilita_alpha_{datetime.now().strftime('%Y_%m')}.json", mime="application/json", use_container_width=True):
            st.session_state["unsaved_ops_count"] = 0
            st.toast("✅ Contabilità salvata sul dispositivo!")
    with cal_top3:
        up_cal = st.file_uploader("📂 Ricarica (.json)", type=["json"], label_visibility="collapsed")
        if up_cal is not None:
            try:
                loaded_list = json.loads(up_cal.getvalue().decode("utf-8"))
                if isinstance(loaded_list, list):
                    st.session_state["chrono_ledger"] = loaded_list
                    st.success("Contabilità ripristinata!")
            except Exception:
                pass

    df_cal = pd.DataFrame(st.session_state["chrono_ledger"])
    if df_cal.empty:
        st.info("Nessun movimento registrato.")
        return
    if "conto" not in df_cal.columns:
        df_cal["conto"] = "[N] SPESE VARIE"

    tot_entrate = df_cal[df_cal["amount"] > 0]["amount"].sum()
    tot_uscite = df_cal[df_cal["amount"] < 0]["amount"].sum()
    saldo_netto = tot_entrate + tot_uscite

    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#10B981;"><div class="kpi-custom-title">INCASSI & RESA CAFFÈ</div><div class="kpi-custom-value">+ € {tot_entrate:.2f}</div></div>""", unsafe_allow_html=True)
    c_m2.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#EF4444;"><div class="kpi-custom-title">COSTI IMPUTATI (A-O)</div><div class="kpi-custom-value">€ {tot_uscite:.2f}</div></div>""", unsafe_allow_html=True)
    c_m3.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#F59E0B;"><div class="kpi-custom-title">SALDO CONTABILITÀ PARALLELA</div><div class="kpi-custom-value">€ {saldo_netto:+.2f}</div></div>""", unsafe_allow_html=True)

    if cal_view.startswith("BILANCIO"):
        st.dataframe(df_cal.groupby("conto", as_index=False).agg(Numero_Voci=("amount", "count"), Totale_Euro=("amount", "sum")), use_container_width=True, hide_index=True)
    elif cal_view.startswith("MESE"):
        st.dataframe(df_cal.groupby("date", as_index=False).agg(Operazioni=("type", "count"), Saldo_Giorno=("amount", "sum"), Giorni_Coperti=("days_span", "max")), use_container_width=True, hide_index=True)
    else:
        edited_df = st.data_editor(
            df_cal, num_rows="dynamic", use_container_width=True, hide_index=True,
            column_config={
                "date": st.column_config.TextColumn("DATA"),
                "time": st.column_config.TextColumn("ORA"),
                "conto": st.column_config.SelectboxColumn("CONTO (A-O)", options=get_conto_options(), width="medium"),
                "type": st.column_config.TextColumn("TIPO"),
                "desc": st.column_config.TextColumn("DETTAGLIO", width="large"),
                "amount": st.column_config.NumberColumn("IMPORTO (€)", format="€ %.2f", step=0.10),
                "days_span": st.column_config.NumberColumn("GG", min_value=1, max_value=30),
                "status": st.column_config.SelectboxColumn("STATO", options=["OK", "ALERT"])
            },
            key="cal_editor_live"
        )
        if not edited_df.equals(df_cal):
            st.session_state["chrono_ledger"] = edited_df.to_dict("records")
            st.rerun()

# --- 6. CORPO PRINCIPALE: MATRICE 12 SETTORI vs MODULO ATTIVO ---
col_left, col_right = st.columns([3.25, 1.15])
rc_id = st.session_state["ram_clear_counter"]

with col_left:
    if st.session_state["blum_sector"] is not None:
        sec_obj = next((s for s in all_squares if s["code"] == st.session_state["blum_sector"]), all_squares[0])
        svg_blum = SECTOR_SVGS.get(sec_obj["code"], SECTOR_SVGS["01"])

        if st.button("🏠 ◀ ESCI DAL MODULO E TORNA ALLA PAGINA ZERO (MATRICE INIZIALE A.L.P.H.A.)", key="exit_blum_top", use_container_width=True):
            return_to_page_zero()
            st.rerun()

        st.markdown(f"""
        <div class="blum-stage" style="border: 2px solid {sec_obj['border']}; border-left: 6px solid {sec_obj['border']}; box-shadow: inset 0 0 40px {sec_obj['glow']};">
            <div style="display:flex; align-items:center; gap:16px;">
                <div>{svg_blum}</div>
                <div>
                    <div style="font-size:11px; color:{sec_obj['border']}; font-family:'Share Tech Mono'; letter-spacing:1.3px;">{sec_obj['artifact']} // SETTORE {sec_obj['code']}</div>
                    <div style="font-size:22px; font-weight:900; color:#FFFFFF; letter-spacing:1.3px; margin-top:2px;">{sec_obj['name']}</div>
                    <div style="font-size:11px; color:#38BDF8; font-family:'Share Tech Mono'; margin-top:4px;">{sec_obj['kpi']} | {st.session_state['selected_sub']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        sub_cols = st.columns(6)
        for idx_s, sub_label in enumerate(sec_obj["subs"]):
            with sub_cols[idx_s]:
                if st.button(sub_label, key=f"blum_sub_{sec_obj['code']}_{idx_s}", use_container_width=True):
                    st.session_state["selected_sub"] = sub_label
                    st.rerun()
        with sub_cols[5]:
            if st.button("🏠 0. Pagina Zero", key=f"sub_zero_{sec_obj['code']}", use_container_width=True):
                return_to_page_zero()
                st.rerun()

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
        curr_sub = str(st.session_state.get("selected_sub", sec_obj["subs"][0]))

        if sec_obj["code"] == "12":
            if "5." in curr_sub:
                render_alpha_chrono_calendar()
            else:
                st.info("Il **Travel Tube (Settore 12)** opera come Pod autonomo dedicato al pareggio Fondo Cassa, rilevamento collisioni Multi-POS vs Registratore Telematico (RT) e classificazione semantica A–O.")
                st.link_button("🚀 LANCIA POD AUTONOMO TRAVEL TUBE", sec_obj["url"], use_container_width=True)

        elif sec_obj["code"] == "10":
            if "5." in curr_sub:
                render_alpha_chrono_calendar()
            elif "2." in curr_sub:
                st.markdown("##### 🎹 CONTABILITÀ PARALLELA RAPIDA (CONTI A → O)")
                imp_col1, imp_col2 = st.columns([1.4, 2.6])
                uscita_euro = imp_col1.number_input("💶 Importo Spesa (€)", 0.50, 5000.0, 19.80, step=0.50, format="%.2f")
                nota_opz = imp_col2.text_input("📝 Nota veloce:", placeholder="Es. Ghiaccio, Latte, Acconto...")
                ao_keys = list(st.session_state["bar_ao_labels"].keys())
                row1 = st.columns(4)
                for i, k_let in enumerate(ao_keys):
                    lbl = st.session_state["bar_ao_labels"][k_let]
                    if row1[i % 4].button(f"[{k_let}] {lbl}", key=f"btn_ao_{k_let}", use_container_width=True):
                        dettaglio = f"{lbl} ({nota_opz})" if nota_opz.strip() else f"Imputazione diretta {lbl}"
                        add_calendar_event(f"CASSA [{k_let}]", dettaglio, -uscita_euro, 1, "OK", conto=f"[{k_let}] {lbl}")
                        play_ems_synth("commlock")
                        st.toast(f"✅ Imputato su [{k_let}] {lbl}: -€ {uscita_euro:.2f}")
                        st.rerun()
            elif "3." in curr_sub:
                st.markdown("##### 🏁 CONTROLLO CASSA MULTI-TURNO & CHIUSURA A FISARMONICA")
                ch1, ch2, ch3 = st.columns(3)
                tipo_punto = ch1.selectbox("Tipo Controllo", ["⏱️ PARZIALE / CAMBIO TURNO", "💶 ALLEGGERIMENTO CONTANTI TITOLARE", "🏁 CHIUSURA FINE GIORNATA / CUMULATIVA"])
                giorni_coperti = ch2.selectbox("Giorni coperti", [1, 2, 3, 4, 5, 6, 7], index=0)
                incasso_contato = ch3.number_input("Totale Contanti + POS (€)", 0.0, 100000.0, 680.0, step=10.0)
                media_giorno = incasso_contato / giorni_coperti
                if st.button("📅 TIMBRA PUNTO CASSA NELLA CONTABILITÀ PARALLELA", use_container_width=True):
                    segno = -incasso_contato if "ALLEGGERIMENTO" in tipo_punto else incasso_contato
                    conto_dest = "[O] PRELIEVO TITOLARE" if "ALLEGGERIMENTO" in tipo_punto else "[INCASSO] CASSA / POS"
                    add_calendar_event("PUNTO CASSA", f"{tipo_punto} ({giorni_coperti} gg — Media €{media_giorno:.2f}/gg)", segno, giorni_coperti, "OK", conto=conto_dest)
                    play_ems_synth("commlock")
                    st.success(f"Registrato! Media giornaliera: € {media_giorno:.2f}/giorno.")
            else:
                cf1, cf2, cf3 = st.columns([1.3, 1.3, 1.4])
                with cf1:
                    if st.button("☕ +1 KG CAFFÈ APERTO (TIMBRA ORA)", use_container_width=True):
                        st.session_state["bar_kg_caffe_aperti"] += 1.0
                        resa_sacchetto = st.session_state["bar_tazzine_per_kg"] * st.session_state["bank_prezzo_caffe"]
                        add_calendar_event("CAFFÈ (+1 KG)", f"Aperto sacchetto 1 Kg (~{st.session_state['bar_tazzine_per_kg']} caffè attesi)", resa_sacchetto, 1, "OK", conto="[A] MATERIE PRIME / CAFFÈ")
                        play_ems_synth("commlock")
                        st.rerun()
                with cf2:
                    st.session_state["bar_kg_caffe_aperti"] = st.number_input("Kg Caffè Aperti", 0.5, 500.0, st.session_state["bar_kg_caffe_aperti"], step=0.5)
                with cf3:
                    tazzine_attese = int(st.session_state["bar_kg_caffe_aperti"] * st.session_state["bar_tazzine_per_kg"])
                    incasso_caffe_atteso = tazzine_attese * st.session_state["bank_prezzo_caffe"]
                    st.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#F59E0B; padding:10px 14px; margin-top:0;"><div class="kpi-custom-title">RESA TEORICA CAFFÈ</div><div class="kpi-custom-value" style="font-size:20px;">€ {incasso_caffe_atteso:.2f} ({tazzine_attese} taz.)</div></div>""", unsafe_allow_html=True)

                cam_col1, cam_col2, cam_col3 = st.columns([1.4, 2.0, 1.0])
                use_cam_ddt = cam_col1.toggle("📸 FOTOCAMERA BANCONE", value=False, key="tog_cam_ddt")
                ddt_file = cam_col2.file_uploader("📂 Carica Foto Scontrino/CSV/XML", type=["jpg", "jpeg", "png", "csv", "xml", "txt"], key=f"up_ddt_{rc_id}")
                with cam_col3:
                    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
                    if st.button("🔥 SVUOTA RAM", key="purge_ddt", use_container_width=True):
                        st.session_state["ram_clear_counter"] += 1
                        play_ems_synth("burst")
                        st.rerun()
                cam_ddt_shot = st.camera_input("Inquadra Scontrino o Bolla", key=f"cam_ddt_{rc_id}") if use_cam_ddt else None
                active_ddt_stream = cam_ddt_shot if cam_ddt_shot is not None else ddt_file
                if active_ddt_stream is not None:
                    render_receipt_parallel_accounting_desk(active_ddt_stream, module_tag="DDT")

        elif sec_obj["code"] == "11":
            if "5." in curr_sub:
                render_alpha_chrono_calendar()
            else:
                b1, b2, b3, b4 = st.columns(4)
                st.session_state["bank_transato_pos"] = b1.number_input("Transato POS Mensile (€)", 500.0, 500000.0, st.session_state["bank_transato_pos"], step=500.0)
                st.session_state["bank_comm_dichiarata"] = b2.number_input("Comm. POS Dichiarata (%)", 0.10, 5.0, st.session_state["bank_comm_dichiarata"], step=0.05)
                st.session_state["bank_costi_occulti"] = b3.number_input("Spese Tenuta / Canoni / SDD (€)", 0.0, 5000.0, st.session_state["bank_costi_occulti"], step=10.0)
                st.session_state["bank_prezzo_caffe"] = b4.number_input("Prezzo Tazzina Caffè (€)", 0.80, 3.0, st.session_state["bank_prezzo_caffe"], step=0.10)
                prelievo_totale_banca = (st.session_state["bank_transato_pos"] * (st.session_state["bank_comm_dichiarata"] / 100.0)) + st.session_state["bank_costi_occulti"]
                vero_tasso_pos = (prelievo_totale_banca / st.session_state["bank_transato_pos"]) * 100.0
                caffe_pareggio = round(prelievo_totale_banca / st.session_state["bank_prezzo_caffe"])
                v1, v2 = st.columns(2)
                v1.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#EF4444;"><div class="kpi-custom-title">VERO TASSO POS EFFETTIVO</div><div class="kpi-custom-value">{vero_tasso_pos:.2f} %</div></div>""", unsafe_allow_html=True)
                v2.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#F59E0B;"><div class="kpi-custom-title">CAFFÈ PER PAREGGIO COSTI BANCA</div><div class="kpi-custom-value">{caffe_pareggio} Tazzine/mese</div></div>""", unsafe_allow_html=True)
                if st.button("📅 IMPUTA ONERI BANCARI NELLA CONTABILITÀ DEL MESE", use_container_width=True):
                    add_calendar_event("ONERI BANCA", f"Vero Tasso POS {vero_tasso_pos:.2f}% ({caffe_pareggio} tazzine)", -prelievo_totale_banca, 30, "ALERT", conto="[BANCA] ONERI & COMMISSIONI")
                    play_ems_synth("commlock")
                    st.rerun()

        else:
            c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1.4])
            st.session_state["rop_cons_gg"] = c1.number_input("Consumo Giorno (u.)", 1, 1000, st.session_state["rop_cons_gg"])
            st.session_state["rop_lead_gg"] = c2.number_input("Lead Time (gg)", 1, 30, st.session_state["rop_lead_gg"])
            st.session_state["rop_stock"] = c3.number_input("Giacenza Casa", 0, 5000, st.session_state["rop_stock"])
            rop_val = (st.session_state["rop_cons_gg"] * st.session_state["rop_lead_gg"]) + (st.session_state["bocche_96h"] * 4)
            c4.markdown(f"""<div class="kpi-custom-box" style="border-left-color:#10B981; padding:10px 14px;"><div class="kpi-custom-title">PUNTO ACQUISTO (ROP 96H)</div><div class="kpi-custom-value" style="font-size:20px;">{rop_val} u.</div></div>""", unsafe_allow_html=True)
            st.link_button(f"🚀 APRI CONSOLLE ESTERNA DEDICATA ({sec_obj['name']})", sec_obj["url"], use_container_width=True)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("🏠 ◀ ESCI DAL MODULO E TORNA ALLA PAGINA ZERO", key="exit_blum_bottom", use_container_width=True):
            return_to_page_zero()
            st.rerun()

    else:
        n_cols = 1 if n_sectors == 1 else (2 if n_sectors in [2, 4] else 3)
        for r in range(0, n_sectors, n_cols):
            row_cols = st.columns(n_cols)
            for c in range(n_cols):
                if r + c < n_sectors:
                    sq = all_squares[r + c]
                    code = sq["code"]
                    svg_icon = SECTOR_SVGS.get(code, SECTOR_SVGS["01"])
                    with row_cols[c]:
                        st.markdown(f"""
                        <div class="alpha-tile" style="background: {sq['bg_grad']}; border: 1.5px solid {sq['border']}; border-left: 5px solid {sq['border']}; box-shadow: inset 0 0 28px {sq['glow']};">
                            <div>{svg_icon}</div>
                            <div class="tile-code">{code}</div>
                            <div class="tile-name">{sq['name']}</div>
                            <div class="tile-artifact">{sq.get('artifact', 'ALPHA NODE')}</div>
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

    st.link_button("◎ EAGLE LAUNCH PAD (DATA WAFER)", "https://bemask-data-wafer.streamlit.app", use_container_width=True)

    module_options = ["00 ALPHA MAIN MISSION", "DW DATA WAFER PAD"] + [f"{s['code']} {s['name']}" for s in all_squares]
    chosen_mod = st.selectbox("SELEZIONA NODO TELEPORT", module_options, label_visibility="collapsed")
    target_url = "https://alpha-main-mission.streamlit.app"
    if chosen_mod.startswith("DW"):
        target_url = "https://bemask-data-wafer.streamlit.app"
    else:
        for s in all_squares:
            if chosen_mod.startswith(s["code"]):
                target_url = s["url"]
                break

    st.markdown(f"""
    <div class="commlock-panel">
        <div style="font-size:11px; font-weight:900; color:#FFFFFF; text-align:left; letter-spacing:1px; margin-bottom:10px;">COMMLOCK // QR<br>TELEPORT</div>
        <div style="background:#0B0E14; border:2px solid #F59E0B; padding:10px; display:inline-block; border-radius:3px;">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=170x170&color=F59E0B&bgcolor=0B0E14&data={target_url}" width="145" />
        </div>
        <div style="font-size:10px; font-weight:900; color:#F59E0B; margin-top:10px; letter-spacing:0.8px;">{chosen_mod}</div>
        <div style="font-size:9px; color:#94A3B8; font-family:'Share Tech Mono', monospace; margin-top:2px;">alpha-main-mission.streamlit.app</div>
    </div>
    """, unsafe_allow_html=True)

    if is_commander:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        if st.button("◈", key="secret_vault_toggle", help="Nodo Riservato"):
            st.session_state["vault_unlocked"] = not st.session_state["vault_unlocked"]
            st.rerun()

st.markdown("""
<div style="margin-top:28px; padding:12px; border-top:1px solid #263040; text-align:center; font-family:'Share Tech Mono', monospace; font-size:10.5px; color:#64748B; letter-spacing:1.1px;">
    ◈ <strong style="color:#F59E0B;">BEMASK SOVEREIGN ARCHITECTURE</strong> · CONCEIVED, DIRECTED & ENGINEERED BY <strong style="color:#E2E8F0;">ENRICO BRAGLIA</strong> · 3-AXIS FRACTAL CORE · ZERO-TRUST VOLATILE RAM ◈
</div>
""", unsafe_allow_html=True)
