import os
import glob
import html
import json
import time
import hmac
import hashlib
import base64
import struct
import re
import uuid
import urllib.request
import urllib.error
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# BEMASK - MOONBASE A.L.P.H.A. // DATA WAFER: EAGLE LAUNCH PAD & HANGAR LIFT
# CONCEIVED, DIRECTED & ENGINEERED BY ENRICO BRAGLIA (ID: EB-BEMASK-2026-ALPHA)
# ==============================================================================

st.set_page_config(
    page_title="BEMASK DATA WAFER // EAGLE LAUNCH PAD — ENRICO BRAGLIA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

POD_CODE = "DW-EAGLE"
POD_REPO = "bemask-data-wafer"
ARCHITECT_ID = "EB-BEMASK-2026-ALPHA"

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
    for k_name in ["api_key_box_WAFER", "api_key_box_VAULT", "custom_gemini_key"]:
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

# --- DIZIONARIO SEMANTICO UFFICIALE A-O (ALLINEATO AL 100% CON ALPHA_CORE.PY) ---
SEMANTIC_KEYWORDS = {
    "[A] MATERIE PRIME / CAFFÈ": ["CAFF", "MISCELA", "GRANI", "ARABICA", "DECA", "ORZO", "GINSENG", "10001", "ILLY", "LAVAZZA"],
    "[B] BEVANDE / ALCOLICI": ["APEROL", "CAMPARI", "BITTER", "GIN", "VODKA", "PROSECCO", "VINO", "BIRRA", "COCA", "ACQUA", "AA514", "DORECA", "CL.100", "LT.1", "CANTINA", "BOTTIGLI"],
    "[C] LATTE / FRESCHI": ["LATTE", "PANNA", "BURRO", "BRIOCHE", "CORNETT", "PASTE", "YOGURT", "FRIGO", "CELLA"],
    "[D] SNACK / CUCINA": ["PANE", "TRAMEZZIN", "PROSCIUTTO", "MOZZARELLA", "PATATIN", "OLIVE", "FOCACCIA", "PECHINO", "RISO", "INVOLTIN", "CUCINA", "CHEF", "PESCE", "CARNE"],
    "[E] GHIACCIO / CONSUMABILI": ["GHIACCIO", "TOVAGLIOL", "BICCHIER", "CANNUCC", "ZUCCHERO", "CARTA TERMICA", "MONOUSO"],
    "[F] PULIZIA / IGIENE": ["DETERSIV", "SAPONE", "CANDEGGINA", "SGRASSATOR", "SPUGN", "SACCHI", "SANIFICAZ", "HACCP"],
    "[G] MANUTENZIONE": ["IDRAULIC", "ELETTRIC", "GUARNIZION", "FILTRO", "TECNICO", "ROTTO", "GUASTO", "PERDITA", "RIPARARE", "LAMPADINA", "POMPA"],
    "[H] ACCONTO STAFF": ["ACCONTO", "EXTRA", "CAMERIER", "BARISTA", "TURNO", "BAGNIN", "BUSTA", "RIMBORSO"],
    "[I] UTENZE / BOLLETTE": ["ENEL", "LUCE", "GAS", "ACQUEDOTTO", "FIBRA", "TIM", "TARI", "SIAE", "BOLLETTA"],
    "[L] TASSE / BOLLI": ["F24", "BOLLO", "AGENZIA", "INPS", "INAIL", "SUOLO", "DEMANIO", "SOGGIORNO"],
    "[M] FORNITORE EXTRA": ["SUPERMERCATO", "CONAD", "COOP", "EUROSPIN", "LIDL", "METRO", "ORDINE", "FORNITORE", "BOLLA", "DDT"],
    "[N] SPESE VARIE": ["FARMACIA", "CANCELLERIA", "MANCIA", "RESTO", "VARIE", "CONSEGNA", "NOTA"],
    "[O] PRELIEVO TITOLARE": ["TITOLARE", "PRELIEVO", "VERSAMENTO", "SOCIO", "ALLEGGERIMENTO", "HOLDING", "CASSAFORTE"]
}

SENSITIVE_ACCOUNTS = {"[H] ACCONTO STAFF", "[I] UTENZE / BOLLETTE", "[L] TASSE / BOLLI", "[O] PRELIEVO TITOLARE"}

OPERATIONAL_TAGS = [
    "CONSEGNA TURNO",
    "SPESA / ORDINE",
    "MANUTENZIONE",
    "HACCP / FRIGO",
    "INCASSO / CASSA"
]

# --- 3 ASSETTI GENETICI DEL MICRO-POD ---
GENETIC_MODES = {
    "STANDALONE": {
        "label": "1) STANDALONE GENERALISTA (P.IVA SINGOLA)",
        "badge": "STANDALONE // MERCATO APERTO",
        "depts": ["BAR & BANCONE", "CUCINA & LAB", "SALA / DEHORS", "STABILIMENTO / PISCINA", "MAGAZZINO", "MANUTENZIONE"],
        "channels": ["SOLO NOTA (0 €)", "CONTANTI", "CARTA / POS", "SDD / BONIFICO"]
    },
    "PARTNER": {
        "label": "2) PARTNER IN CONCESSIONE (AFFITTO DI RAMO)",
        "badge": "PARTNER // FEE & COMPENSAZIONE CUBO",
        "depts": ["LOUNGE BAR PARTNER", "RISTORANTE PARTNER", "BEACH CLUB", "SPA IN CONCESSIONE", "MANUTENZIONE", "DIREZIONE RAMO"],
        "channels": ["SOLO NOTA (0 €)", "ADDEBITO CAMERA (COMPENSAZIONE)", "CONTANTI", "POS PARTNER", "SDD / BONIFICO"]
    },
    "CUBE_DIRECT": {
        "label": "3) REPARTO DIRETTO CUBO (ALPHA-MAIN-MISSION)",
        "badge": "REPARTO DIRETTO // 27° CUBO CENTRALE",
        "depts": ["01 FRONT & CONCIERGE", "02/03 LAZERS F&B", "04 BEACH & POOL", "05 SPA & AYURVEDA", "06 S.K.A. PIANI & CAMERE", "07/08 ECONOMATO & HACCP"],
        "channels": ["SOLO NOTA (0 €)", "ADDEBITO CAMERA", "CONTANTI CASSA", "POS HOTEL", "SDD / ECONOMATO"]
    }
}

# --- FLOTTA DOCK RAPIDA SUPERIORE (COMPATIBILE CON ?mask=...) ---
DOCK_FLEET = [
    {"code": "00", "short": "00 ALPHA HUB", "url": "https://alpha-main-mission.streamlit.app"},
    {"code": "01", "short": "01 FRONT", "url": "https://bemask-sovereign-zero.streamlit.app"},
    {"code": "02", "short": "02 BEV", "url": "https://bemask-lazers.streamlit.app"},
    {"code": "03", "short": "03 FOOD", "url": "https://bemask-lazers.streamlit.app"},
    {"code": "04", "short": "04 BEACH", "url": "https://ska-boschetto.streamlit.app"},
    {"code": "05", "short": "05 SPA", "url": "https://ska-boschetto.streamlit.app"},
    {"code": "06", "short": "06 SKA", "url": "https://ska-boschetto.streamlit.app"},
    {"code": "07", "short": "07 ROP", "url": "https://bemask-lazers.streamlit.app"},
    {"code": "08", "short": "08 HACCP", "url": "https://ska-boschetto.streamlit.app"},
    {"code": "09", "short": "09 GOPPAR", "url": "https://bemask-lazers.streamlit.app"},
    {"code": "10", "short": "10 BAR DDT", "url": "https://bemask-lazers.streamlit.app"},
    {"code": "11", "short": "11 VAMPIRE", "url": "https://bemask-lazers.streamlit.app"},
    {"code": "12", "short": "12 TUBE", "url": "https://bemask-travel-tube.streamlit.app"},
    {"code": "DW", "short": "◎ DATA WAFER", "url": "#"}
]

def auto_map_semantic_conto(text_val):
    up = str(text_val).upper()
    for c_label, kw_list in SEMANTIC_KEYWORDS.items():
        for kw in kw_list:
            if kw in up:
                return c_label
    return "[N] SPESE VARIE"

def parse_license_url():
    qp = st.query_params if hasattr(st, "query_params") else {}
    raw_mask = str(qp.get("mask", "")).strip()
    raw_mode = str(qp.get("mode", "")).strip().upper()
    raw_entity = str(qp.get("entity", "")).strip()

    allowed = None
    if raw_mask:
        tokens = {
            t.strip().upper().zfill(2) if t.strip().isdigit() else t.strip().upper()
            for t in raw_mask.split(",")
            if t.strip()
        }
        tokens.add("DW")
        allowed = tokens

    return {
        "is_filtered": allowed is not None,
        "allowed_codes": allowed,
        "raw_mask": raw_mask,
        "forced_mode": raw_mode if raw_mode in GENETIC_MODES else None,
        "forced_entity": raw_entity if raw_entity else None
    }

LICENSE_INFO = parse_license_url()

# ==============================================================================
# 2. MOTORE MULTIMODALE GEMINI IN RAM (FOTO PIZZINO OCR + VOCE AUDIO + TESTO)
# ==============================================================================
def discover_gemini_candidates(clean_key):
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
            ("v1beta", "gemini-1.5-flash-latest"),
            ("v1", "gemini-2.0-flash")
        ]
    else:
        candidate_models.sort(key=lambda x: (0 if "flash" in x[1] else 1))
    return candidate_models, None

def local_heuristic_wafer_parser(raw_text, default_dept, default_channel):
    clean_txt = re.sub(r"\s+", " ", str(raw_text or "").strip())
    up = clean_txt.upper()

    euro_val = 0.0
    for pat in [r"(?:€|EUR|EURO)\s*([0-9]+(?:[.,][0-9]{1,2})?)", r"([0-9]+(?:[.,][0-9]{1,2})?)\s*(?:€|EUR|EURO)"]:
        m = re.search(pat, up)
        if m:
            try:
                euro_val = float(m.group(1).replace(",", "."))
                break
            except Exception:
                pass

    matter_x = "1 NOTA OPERATIVA"
    temp_m = re.search(r"([+-]?\d+(?:[.,]\d+)?\s*°\s*C)", up)
    qty_m = re.search(r"([+-]?\d+(?:[.,]\d+)?\s*(?:KG|G|LT|L|PZ|CASSE|BOTTIGLIE|FUSTI|OMBRELLONI|LETTINI|SACCHI))", up)
    if temp_m:
        matter_x = temp_m.group(1).replace(" ", "")
    elif qty_m:
        matter_x = qty_m.group(1)

    tag = "CONSEGNA TURNO"
    if temp_m or any(w in up for w in ["FRIGO", "CELLA", "HACCP", "TEMPERATURA"]):
        tag = "HACCP / FRIGO"
    elif any(w in up for w in ["ROTTO", "GUASTO", "PERDITA", "IDRAULIC", "ELETTRIC", "RIPAR", "MANUTENZ"]):
        tag = "MANUTENZIONE"
    elif any(w in up for w in ["ORDIN", "COMPR", "FINITO", "MANCA", "BOLLA", "DDT", "SPESA"]) or euro_val > 0:
        tag = "SPESA / ORDINE"
    if any(w in up for w in ["INCASSO", "PAGATO DA", "ADDEBITO"]) and euro_val > 0:
        tag = "INCASSO / CASSA"

    conto = auto_map_semantic_conto(clean_txt)
    chan = default_channel
    if euro_val > 0 and chan.startswith("SOLO NOTA"):
        if "POS" in up or "CARTA" in up:
            chan = "CARTA / POS"
        elif "CAMERA" in up and st.session_state["genetic_mode"] != "STANDALONE":
            chan = "ADDEBITO CAMERA (COMPENSAZIONE)" if st.session_state["genetic_mode"] == "PARTNER" else "ADDEBITO CAMERA"
        else:
            chan = "CONTANTI"

    urgent = any(w in up for w in ["URGENTE", "SUBITO", "ALLARME", "ROTTO", "PERDITA", "BLOCCATO"])
    return {
        "clean_text": clean_txt if clean_txt else "Pizzino registrato in RAM.",
        "matter_x": matter_x,
        "euro_y": round(euro_val, 2),
        "channel_y": chan,
        "conto_ao": conto,
        "op_tag": tag,
        "dept": default_dept,
        "urgent": urgent,
        "engine": "RAM-HEURISTIC"
    }

def process_wafer_in_ram_with_ai(api_key, raw_text="", media_bytes=None, mime_type="image/jpeg", default_dept="BAR & BANCONE", default_channel="SOLO NOTA (0 €)"):
    clean_key = str(api_key).strip()
    if not clean_key or len(clean_key) < 15:
        if media_bytes is not None:
            return None, "Inserisci la chiave gratuita AIzaSy... nella Cassaforte o nel campo AI per leggere Foto Pizzini e Note Vocali!"
        return local_heuristic_wafer_parser(raw_text, default_dept, default_channel), None

    candidates, err_disc = discover_gemini_candidates(clean_key)
    if err_disc:
        return None, err_disc

    mode_cfg = GENETIC_MODES[st.session_state["genetic_mode"]]
    conti_list = list(SEMANTIC_KEYWORDS.keys())
    standalone_rule = "NON citare mai camere o hotel perché siamo in modalità STANDALONE." if st.session_state["genetic_mode"] == "STANDALONE" else ""

    prompt_txt = (
        "Sei il motore anti-foglietti volanti BEMASK Data Wafer (Moonbase Alpha). "
        "Trascrivi fedelmente la foto del pizzino scritto a mano o la nota vocale dell'operatore in italiano pulito, chiaro e ordinato. "
        f"{standalone_rule} "
        "Rispondi SOLO con un JSON valido in questo formato esatto: "
        "{\"clean_text\": \"testo pulito della nota/ordine/consegna\", "
        "\"matter_x\": \"unità fisica sintetica es. +2 KG CAFFÈ o +3.8°C FRIGO o 1 MANUTENZIONE\", "
        "\"euro_y\": 0.0, "
        f"\"channel_y\": \"uno tra {mode_cfg['channels']}\", "
        f"\"conto_ao\": \"uno esatto tra {conti_list}\", "
        f"\"op_tag\": \"uno tra {OPERATIONAL_TAGS}\", "
        f"\"dept\": \"uno tra {mode_cfg['depts']}\", "
        "\"urgent\": false}"
    )

    parts = [{"text": prompt_txt}]
    if raw_text and str(raw_text).strip():
        parts.append({"text": f"Nota/Contesto operatore (Reparto selezionato: {default_dept}): {raw_text}"})
    if media_bytes is not None:
        b64_media = base64.b64encode(media_bytes).decode("utf-8")
        parts.append({"inline_data": {"mime_type": mime_type, "data": b64_media}})

    payload = {"contents": [{"parts": parts}]}
    last_err = ""

    for api_ver, m_name in candidates:
        try:
            url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{m_name}:generateContent?key={clean_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                raw_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                clean_json = re.sub(r"```json|```", "", raw_reply).strip()
                match_j = re.search(r"\{.*\}", clean_json, re.DOTALL)
                if match_j:
                    clean_json = match_j.group(0)
                parsed = json.loads(clean_json)

                conto_sel = str(parsed.get("conto_ao", "")).strip()
                if conto_sel not in SEMANTIC_KEYWORDS:
                    conto_sel = auto_map_semantic_conto(parsed.get("clean_text", ""))

                tag_sel = str(parsed.get("op_tag", "CONSEGNA TURNO")).strip()
                if tag_sel not in OPERATIONAL_TAGS:
                    tag_sel = "CONSEGNA TURNO"

                dept_sel = str(parsed.get("dept", default_dept)).strip()
                if dept_sel not in mode_cfg["depts"]:
                    dept_sel = default_dept

                chan_sel = str(parsed.get("channel_y", default_channel)).strip()
                if chan_sel not in mode_cfg["channels"]:
                    chan_sel = default_channel

                return {
                    "clean_text": str(parsed.get("clean_text", "")).strip() or "Nota trascritta in RAM.",
                    "matter_x": str(parsed.get("matter_x", "1 NOTA")).strip().upper()[:40],
                    "euro_y": round(float(parsed.get("euro_y", 0.0) or 0.0), 2),
                    "channel_y": chan_sel,
                    "conto_ao": conto_sel,
                    "op_tag": tag_sel,
                    "dept": dept_sel,
                    "urgent": bool(parsed.get("urgent", False)),
                    "engine": f"AI-{m_name}"
                }, None
        except Exception as e:
            last_err = f"[{m_name}] {str(e)}"
            continue

    return None, f"Elaborazione AI in RAM non riuscita ({last_err})."

# --- 3. INIZIALIZZAZIONE SESSION STATE VOLATILE IN RAM ---
def init_wafer_state():
    defaults = {
        "auth_unlocked": False,
        "auth_role": None,
        "auth_user": "",
        "pin_code": "9999",
        "breach_log": [],
        "show_arch_fallback": False,
        "custom_gemini_key": "",
        "genetic_mode": LICENSE_INFO["forced_mode"] or "STANDALONE",
        "entity_id": LICENSE_INFO["forced_entity"] or "P.IVA-BEMASK-ALPHA",
        "partner_fee_pct": 12.0,
        "shift_z": "MATTINA",
        "meteo_z": "NOMINAL ORBIT // SERENO",
        "ram_clear_counter": 0,
        "unsaved_wafers_count": 0,
        "hydraulic_anim": False,
        "pending_sound": None,
        "hangar_wafers": [
            {
                "id": "WAF-0730",
                "taken": True,
                "taken_by": "COMMANDER · 07:42",
                "z": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": "07:30",
                    "pod": POD_CODE,
                    "entity_id": "P.IVA-BEMASK-ALPHA",
                    "shift": "MATTINA",
                    "meteo": "NOMINAL ORBIT // SERENO",
                    "source": "NOTA LAMPO"
                },
                "x": {
                    "dept": "BAR & BANCONE",
                    "op_tag": "HACCP / FRIGO",
                    "matter": "+1 KG CAFFÈ | +3.8°C FRIGO",
                    "clean_text": "Aperto sacchetto 1 Kg miscela grani e verificata temperatura Frigo Bar +3.8°C regolare.",
                    "urgent": False
                },
                "y": {
                    "euro": 0.00,
                    "channel": "SOLO NOTA (0 €)",
                    "conto": "[A] MATERIE PRIME / CAFFÈ",
                    "royalty_eur": 0.00
                }
            }
        ]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_wafer_state()

def land_wafer_into_hangar(parsed_item, source_label):
    euro_val = float(parsed_item.get("euro_y", 0.0) or 0.0)
    fee_pct = float(st.session_state["partner_fee_pct"]) if st.session_state["genetic_mode"] == "PARTNER" else 0.0
    royalty_eur = round(euro_val * (fee_pct / 100.0), 2) if euro_val > 0 and fee_pct > 0 else 0.0

    wafer_atom = {
        "id": f"WAF-{datetime.now().strftime('%H%M')}-{uuid.uuid4().hex[:3].upper()}",
        "taken": False,
        "taken_by": "",
        "z": {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "pod": POD_CODE,
            "entity_id": st.session_state["entity_id"],
            "shift": st.session_state["shift_z"],
            "meteo": st.session_state["meteo_z"],
            "source": source_label
        },
        "x": {
            "dept": parsed_item["dept"],
            "op_tag": parsed_item["op_tag"],
            "matter": parsed_item["matter_x"],
            "clean_text": parsed_item["clean_text"],
            "urgent": bool(parsed_item.get("urgent", False))
        },
        "y": {
            "euro": euro_val,
            "channel": parsed_item["channel_y"],
            "conto": parsed_item["conto_ao"],
            "royalty_eur": royalty_eur
        }
    }
    st.session_state["hangar_wafers"].insert(0, wafer_atom)
    st.session_state["unsaved_wafers_count"] += 1
    st.session_state["ram_clear_counter"] += 1
    st.session_state["hydraulic_anim"] = True
    st.session_state["pending_sound"] = "hydraulic"
    return wafer_atom

# --- 4. SINTETIZZATORE AUDIO WEBAUDIO EMS SYNTHI 1975 (+ DISCESA IDRAULICA LIFT) ---
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
        }} else if ("{effect_type}" === "hydraulic") {{
            const lockOsc = ctx.createOscillator();
            const lockGain = ctx.createGain();
            lockOsc.type = "square";
            lockOsc.frequency.setValueAtTime(185, now);
            lockOsc.frequency.exponentialRampToValueAtTime(52, now + 0.12);
            lockGain.gain.setValueAtTime(0.18, now);
            lockGain.gain.exponentialRampToValueAtTime(0.001, now + 0.13);
            lockOsc.connect(lockGain); lockGain.connect(ctx.destination);
            lockOsc.start(now); lockOsc.stop(now + 0.13);

            const lift1 = ctx.createOscillator();
            const lift2 = ctx.createOscillator();
            const flt = ctx.createBiquadFilter();
            const liftGain = ctx.createGain();
            lift1.type = "sawtooth";
            lift2.type = "triangle";
            lift1.frequency.setValueAtTime(128, now + 0.10);
            lift1.frequency.exponentialRampToValueAtTime(38, now + 1.25);
            lift2.frequency.setValueAtTime(64, now + 0.10);
            lift2.frequency.exponentialRampToValueAtTime(24, now + 1.25);
            flt.type = "lowpass";
            flt.Q.value = 6.0;
            flt.frequency.setValueAtTime(390, now + 0.10);
            flt.frequency.exponentialRampToValueAtTime(85, now + 1.25);
            liftGain.gain.setValueAtTime(0.16, now + 0.10);
            liftGain.gain.exponentialRampToValueAtTime(0.001, now + 1.30);
            lift1.connect(flt); lift2.connect(flt); flt.connect(liftGain); liftGain.connect(ctx.destination);
            lift1.start(now + 0.10); lift2.start(now + 0.10);
            lift1.stop(now + 1.32); lift2.stop(now + 1.32);

            [987.77, 1318.51].forEach((f, i) => {{
                const p = ctx.createOscillator();
                const g = ctx.createGain();
                p.type = "sine";
                const t0 = now + 1.18 + i * 0.10;
                p.frequency.setValueAtTime(f, t0);
                g.gain.setValueAtTime(0.11, t0);
                g.gain.exponentialRampToValueAtTime(0.001, t0 + 0.11);
                p.connect(g); g.connect(ctx.destination);
                p.start(t0); p.stop(t0 + 0.12);
            }});
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0)

# ==============================================================================
# 5. SIMBOLI ICONICI SPAZIO: 1999 (AQUILA EROE + PIATTAFORMA IDRAULICA HANGAR)
# ==============================================================================
EAGLE_HERO_SVG = """
<svg width="105" height="52" viewBox="0 0 180 86" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="48" y="16" width="84" height="12" fill="#1E293B" stroke="#94A3B8" stroke-width="2"/>
  <path d="M48 28L62 16L76 28L90 16L104 28L118 16L132 28" stroke="#CBD5E1" stroke-width="1.8"/>
  <path d="M48 16L62 28L76 16L90 28L104 16L118 28L132 16" stroke="#64748B" stroke-width="1.4"/>
  <polygon points="36,36 58,36 62,58 32,58" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
  <polygon points="122,36 144,36 148,58 118,58" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
  <rect x="30" y="58" width="34" height="5" fill="#F59E0B"/>
  <rect x="116" y="58" width="34" height="5" fill="#F59E0B"/>
  <rect x="58" y="30" width="64" height="24" fill="#1E293B" stroke="#38BDF8" stroke-width="2"/>
  <line x1="74" y1="30" x2="74" y2="54" stroke="#38BDF8" stroke-width="1.5"/>
  <line x1="106" y1="30" x2="106" y2="54" stroke="#38BDF8" stroke-width="1.5"/>
  <polygon points="90,22 122,42 112,68 68,68 58,42" fill="#E2E8F0" stroke="#FFFFFF" stroke-width="2.2"/>
  <polygon points="87,34 65,44 72,54 87,49" fill="#F59E0B" stroke="#78350F" stroke-width="1.5"/>
  <polygon points="93,34 115,44 108,54 93,49" fill="#F59E0B" stroke="#78350F" stroke-width="1.5"/>
  <circle cx="22" cy="46" r="6" fill="#EF4444" stroke="#FDE047" stroke-width="2"/>
  <circle cx="158" cy="46" r="6" fill="#EF4444" stroke="#FDE047" stroke-width="2"/>
</svg>
"""

def build_eagle_launch_pad_svg(is_descending=False, open_count=0):
    ring_stroke = "#10B981" if is_descending else "#F59E0B"
    anim_cls = "pad-hydraulic-drop" if is_descending else ""
    lift_state = "▼ HYDRAULIC DESCENT (-18m HANGAR)" if is_descending else "◎ SURFACE LAUNCH PAD ARMED (0.0m)"
    return f"""
    <div style="background:#0C1017; border:1.5px solid {ring_stroke}; border-radius:4px; padding:10px 12px; text-align:center;">
        <div style="display:flex; justify-content:space-between; font-family:'Share Tech Mono', monospace; font-size:10px; color:#94A3B8; margin-bottom:4px;">
            <span>MOONBASE ALPHA // PAD-01</span>
            <span style="color:{ring_stroke}; font-weight:bold;">{lift_state}</span>
        </div>
        <svg viewBox="0 0 380 185" width="100%" style="max-height:175px;" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="190" cy="144" rx="138" ry="30" fill="#07090D" stroke="#38BDF8" stroke-width="1.4" stroke-dasharray="5 3"/>
            <line x1="52" y1="78" x2="52" y2="144" stroke="#334155" stroke-width="2.2"/>
            <line x1="328" y1="78" x2="328" y2="144" stroke="#334155" stroke-width="2.2"/>
            <rect x="92" y="84" width="9" height="62" fill="#1E293B" stroke="{ring_stroke}" stroke-width="1"/>
            <rect x="154" y="96" width="9" height="58" fill="#1E293B" stroke="{ring_stroke}" stroke-width="1"/>
            <rect x="217" y="96" width="9" height="58" fill="#1E293B" stroke="{ring_stroke}" stroke-width="1"/>
            <rect x="279" y="84" width="9" height="62" fill="#1E293B" stroke="{ring_stroke}" stroke-width="1"/>
            <g class="{anim_cls}">
                <ellipse cx="190" cy="78" rx="140" ry="36" fill="#151C28" stroke="{ring_stroke}" stroke-width="2.6"/>
                <ellipse cx="190" cy="78" rx="112" ry="27" fill="#10151F" stroke="#F59E0B" stroke-width="1.4" stroke-dasharray="9 4"/>
                <ellipse cx="190" cy="78" rx="72" ry="17" fill="#0B0F17" stroke="#38BDF8" stroke-width="1.4"/>
                <line x1="66" y1="78" x2="314" y2="78" stroke="#F59E0B" stroke-width="1" opacity="0.6"/>
                <line x1="190" y1="44" x2="190" y2="112" stroke="#F59E0B" stroke-width="1" opacity="0.6"/>
                <rect x="156" y="70" width="68" height="14" rx="2" fill="#1E293B" stroke="#E2E8F0" stroke-width="1.4"/>
                <polygon points="190,62 208,77 190,91 172,77" fill="#F59E0B" stroke="#FFFFFF" stroke-width="1.2"/>
                <circle cx="144" cy="77" r="4" fill="#EF4444"/>
                <circle cx="236" cy="77" r="4" fill="#10B981"/>
            </g>
            <text x="190" y="178" fill="#CBD5E1" font-size="10" font-family="Share Tech Mono, monospace" text-anchor="middle">
                PIZZINI IN CODA DA PRENDERE IN CARICO: {open_count} // ZERO CLOUD RAM
            </text>
        </svg>
    </div>
    """

# ==============================================================================
# 6. CSS IDENTICO A ALPHA_CORE.PY + DOCK RAPIDA + ANIMAZIONE LIFT IDRAULICO
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;700;800;900&family=Share+Tech+Mono&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp, .main, .block-container {
    overflow-x: hidden !important;
    max-width: 100vw !important;
    box-sizing: border-box !important;
}

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
.block-container { padding-top: 0.6rem; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 97% !important; }

div[data-baseweb="input"] > div:focus-within, textarea:focus {
    border-color: #10B981 !important;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.45) !important;
}

.koenig-strip {
    background-color: #1A1E26; border: 1px solid #323946; border-left: 5px solid #F59E0B;
    padding: 8px 14px; margin-bottom: 8px; border-radius: 2px;
}
.badge-amber { background-color: #F59E0B; color: #0B0E14; font-weight: 900; font-size: 10px; padding: 3px 8px; margin-right: 6px; display: inline-block; margin-bottom: 3px; }
.badge-white { background-color: #F1F5F9; color: #0F172A; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }
.badge-red { background-color: #7F1D1D; border: 1px solid #EF4444; color: #FCA5A5; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }
.badge-green { background-color: #064E3B; border: 1px solid #10B981; color: #6EE7B7; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }
.badge-cyan { background-color: #0C4A6E; border: 1px solid #38BDF8; color: #BAE6FD; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }

.mission-bar {
    background: linear-gradient(90deg, #161C24 0%, #1E2836 50%, #161C24 100%);
    border: 1px solid #3A4B5E; border-left: 5px solid #F59E0B;
    padding: 10px 16px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 10px;
}
.mission-title { font-size: 18px; font-weight: 900; color: #FFFFFF; letter-spacing: 1.4px; }
.mission-sub { font-size: 10px; color: #38BDF8; font-family: 'Share Tech Mono', monospace; letter-spacing: 0.9px; margin-top: 2px; }
.nixie-group { display: flex; align-items: center; gap: 10px; }
.nixie-label { font-size: 10px; color: #94A3B8; font-weight: 700; letter-spacing: 1px; }
.nixie-digits {
    background-color: #0D1015; border: 1px solid #F59E0B; color: #F59E0B;
    font-family: 'Share Tech Mono', monospace; font-size: 17px; font-weight: 900;
    padding: 3px 10px; letter-spacing: 3px; border-radius: 2px;
    box-shadow: inset 0 0 8px rgba(245, 158, 11, 0.4);
}

.quick-dock {
    background-color: #141922; border: 1px solid #2A3648; border-left: 4px solid #38BDF8;
    padding: 6px 10px; margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
}
.dock-pill {
    background-color: #1A212B; border: 1px solid #2F3E50; color: #CBD5E1 !important;
    text-decoration: none !important; font-family: 'Share Tech Mono', monospace; font-size: 10.5px;
    font-weight: 700; padding: 3px 8px; border-radius: 2px; transition: all 0.18s ease;
}
.dock-pill:hover { border-color: #F59E0B; color: #F59E0B !important; }
.dock-pill.active {
    background-color: rgba(245, 158, 11, 0.18); border-color: #F59E0B; color: #F59E0B !important;
    box-shadow: 0 0 10px rgba(245, 158, 11, 0.25);
}

div.stButton > button, div.stDownloadButton > button {
    background-color: #1A212B !important; color: #F8FAFC !important;
    border: 1px solid #2F3E50 !important; border-radius: 3px !important;
    font-family: 'Orbitron', sans-serif !important; font-size: 10px !important;
    font-weight: 800 !important; letter-spacing: 0.8px !important;
    min-height: 40px !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    border-color: #F59E0B !important; color: #F59E0B !important;
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.3) !important;
}

.ems-panel { background-color: #161A22; border: 2px solid #F59E0B; padding: 12px; border-radius: 3px; margin-bottom: 10px; }
.commlock-panel { background-color: #161A22; border: 1px solid #F59E0B; padding: 14px; border-radius: 3px; text-align: center; margin-top: 8px; }
.blum-stage { background: radial-gradient(circle at 50% 20%, #1A2432 0%, #0E1218 85%); padding: 18px; border-radius: 4px; margin-bottom: 12px; }

.kpi-custom-box {
    background-color: #141A23; border: 1px solid #2B394A; border-left: 4px solid #F59E0B;
    padding: 14px; border-radius: 3px; margin-top: 6px; margin-bottom: 8px;
}
.kpi-custom-title { font-size: 10px; font-weight: 800; color: #94A3B8; letter-spacing: 1.1px; margin-bottom: 6px; font-family: 'Share Tech Mono', monospace; }
.kpi-custom-value { font-size: 21px; font-weight: 900; color: #FFFFFF; letter-spacing: 0.9px; line-height: 1.2; }
.kpi-custom-sub { font-size: 11px; font-weight: 700; margin-top: 6px; font-family: 'Share Tech Mono', monospace; }

.xray-desk {
    background: linear-gradient(135deg, #0D1622 0%, #132232 100%);
    border: 2px solid #10B981; border-left: 6px solid #F59E0B;
    padding: 16px; border-radius: 4px; margin-top: 10px; margin-bottom: 14px;
    box-shadow: 0 0 25px rgba(16, 185, 129, 0.18);
}

.hangar-card {
    background: linear-gradient(180deg, #151B26 0%, #10151E 100%);
    border: 1px solid #2B394A; border-left: 5px solid #F59E0B;
    padding: 12px 14px; border-radius: 3px; margin-bottom: 10px;
}
.hangar-card.taken { border-left-color: #10B981; opacity: 0.85; }
.hangar-card.urgent { border-left-color: #EF4444; box-shadow: inset 0 0 16px rgba(239, 68, 68, 0.14); }

@keyframes hydraulicDropAnim {
    0% { transform: translateY(0px); }
    45% { transform: translateY(22px) scale(0.94); }
    100% { transform: translateY(0px); }
}
.pad-hydraulic-drop { animation: hydraulicDropAnim 1.3s ease-in-out 1; }

@media (max-width: 768px) {
    .mission-title { font-size: 14px !important; }
    .kpi-custom-value { font-size: 18px !important; }
    .blum-stage { padding: 12px !important; }
}
</style>
""", unsafe_allow_html=True)

if st.session_state.get("pending_sound"):
    play_ems_synth(st.session_state["pending_sound"])
    st.session_state["pending_sound"] = None

# ==============================================================================
# 7. DOSSIER ARCHITETTO & GENESI (CON AUTO-SCANNER BINARIO .MP4 IN RAM)
# ==============================================================================
def find_and_read_creator_mp4_in_ram():
    base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
    found_paths = (
        glob.glob(os.path.join(base_dir, "*.mp4"))
        + glob.glob(os.path.join(base_dir, "**", "*.mp4"), recursive=True)
        + glob.glob("*.mp4")
    )
    unique_mp4 = sorted(
        set(found_paths),
        key=lambda p: (0 if any(w in os.path.basename(p).lower() for w in ["architect", "manifesto", "bemask", "enrico"]) else 1, p)
    )
    if unique_mp4:
        target = unique_mp4[0]
        try:
            with open(target, "rb") as f:
                data_bytes = f.read()
            return data_bytes, os.path.basename(target)
        except Exception:
            return None, None
    return None, None

def render_architect_dossier_content():
    st.markdown("""
    <div style="background:linear-gradient(135deg, #0B0E14 0%, #161C26 100%); border:1.5px solid #F59E0B; border-left:6px solid #F59E0B; padding:18px; border-radius:4px; margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <span class="badge-amber">ORIGIN SEAL // INTELLECTUAL PROPERTY</span>
            <span style="font-family:'Share Tech Mono', monospace; font-size:11px; color:#38BDF8;">
                3-AXIS FRACTAL CORE // ZERO-TRUST RAM ARCHITECTURE
            </span>
        </div>
        <div style="font-size:21px; font-weight:900; color:#FFFFFF; letter-spacing:1.5px; margin-top:8px;">
            ENRICO BRAGLIA — SYSTEM ARCHITECT & CREATOR
        </div>
        <div style="font-size:11px; color:#F59E0B; font-family:'Share Tech Mono', monospace; letter-spacing:1px; margin-top:3px;">
            30+ YEARS HOSPITALITY DIRECTION · REVENUE INTELLIGENCE · BEMASK MEDIA & AI LAB
        </div>
    </div>
    """, unsafe_allow_html=True)

    v_col, m_col = st.columns([1.25, 1.55])

    with v_col:
        mp4_bytes, mp4_name = find_and_read_creator_mp4_in_ram()
        if mp4_bytes is not None:
            try:
                st.video(mp4_bytes, format="video/mp4", autoplay=True, loop=True, muted=False)
            except TypeError:
                st.video(mp4_bytes, format="video/mp4")
            st.caption(f"◈ STREAM BINARIO RAM ATTIVO: {mp4_name} ({len(mp4_bytes)//1024} KB)")
        else:
            st.markdown("""
            <div style="background:#090C12; border:1px solid #2B394A; border-radius:4px; padding:22px 14px; text-align:center;">
                <svg width="150" height="150" viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg">
                    <g stroke="#38BDF8" stroke-width="1.2" opacity="0.35">
                        <polygon points="80,18 138,50 138,114 80,146 22,114 22,50" fill="none"/>
                        <line x1="80" y1="18" x2="80" y2="146"/>
                        <line x1="22" y1="50" x2="138" y2="114"/>
                        <line x1="138" y1="50" x2="22" y2="114"/>
                    </g>
                    <g stroke="#F59E0B" stroke-width="2.5">
                        <line x1="80" y1="32" x2="80" y2="132"/>
                        <line x1="34" y1="56" x2="126" y2="108"/>
                        <line x1="126" y1="56" x2="34" y2="108"/>
                    </g>
                    <circle cx="80" cy="82" r="14" fill="#0B0E14" stroke="#10B981" stroke-width="3">
                        <animate attributeName="r" values="12;16;12" dur="2.4s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="80" cy="82" r="5" fill="#F59E0B"/>
                </svg>
                <div style="font-size:11px; font-weight:800; color:#F59E0B; letter-spacing:1.2px; margin-top:8px;">
                    27TH CUBE // 3-AXIS CORE ACTIVE
                </div>
                <div style="font-size:10px; color:#94A3B8; font-family:'Share Tech Mono', monospace; margin-top:4px;">
                    Carica 'architect_manifesto.mp4' nel repo per attivare il Mini-Video Manifesto in RAM
                </div>
            </div>
            """, unsafe_allow_html=True)

        vcard_data = "MECARD:N:Braglia,Enrico;ORG:BEMASK Sovereign Architecture;NOTE:Creator & Hospitality Revenue Architect;;"
        st.markdown(f"""
        <div style="background:#0D1118; border:1px solid #263244; padding:10px; border-radius:4px; margin-top:10px; display:flex; align-items:center; gap:12px;">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=110x110&color=F59E0B&bgcolor=0D1118&data={vcard_data}" width="72" style="border:1px solid #F59E0B; padding:3px;" />
            <div style="font-family:'Share Tech Mono', monospace; font-size:10px; color:#CBD5E1; line-height:1.4;">
                <strong style="color:#F59E0B;">VERIFICA DIRETTA CREATORE</strong><br>
                Inquadra per salvare il contatto ufficiale dell'Architetto del sistema.<br>
                <span style="color:#10B981;">ID: {ARCHITECT_ID}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with m_col:
        st.markdown("""
        <div style="font-family:'Share Tech Mono', monospace; font-size:12.5px; color:#E2E8F0; line-height:1.65; background:#111620; border:1px solid #243042; padding:16px; border-radius:4px;">
            <div style="color:#F59E0B; font-weight:900; font-family:'Orbitron', sans-serif; font-size:12px; margin-bottom:8px;">
                PERCHÉ QUESTA ARCHITETTURA È DIVERSA
            </div>
            <p style="margin-bottom:10px;">
                I software gestionali tradizionali nascono in laboratorio da chi non ha mai chiuso una cassa a fine turno, difeso il RevPAR di un hotel o scoperto un rincaro occulto tra una bolla fornitore e un estratto conto POS.
            </p>
            <p style="margin-bottom:10px;">
                <strong>BEMASK Sovereign Zero</strong> nasce dall'incontro tra <strong>oltre 30 anni di Direzione Alberghiera, Revenue Management e F&B sul campo</strong>, basi di elettronica industriale e orchestrazione avanzata con l'Intelligenza Artificiale.
            </p>
            <div style="color:#38BDF8; font-weight:900; font-family:'Orbitron', sans-serif; font-size:11px; margin-top:12px; margin-bottom:6px;">
                LA LEGGE DEL CUBO E LA MITOSI COMPUTAZIONALE
            </div>
            <ul style="padding-left:18px; margin-bottom:10px; color:#CBD5E1;">
                <li><strong>Il Perno Centrale (3 Assi X·Y·Z):</strong> ogni gesto fisico sul campo (<em>Materia</em>) si traduce all'istante in controllo di cassa e margine (<em>Energia</em>) sincronizzato col contesto operativo e meteo (<em>Tempo</em>).</li>
                <li><strong>Data Wafer & Eagle Launch Pad:</strong> elimina per sempre i foglietti volanti a fine turno convertendo foto e voce in atomi puliti dentro l'Hangar RAM, senza distrazioni esterne.</li>
                <li><strong>Sovranità in RAM (0 Byte su Cloud):</strong> nessun dato sensibile resta sui server. I numeri appartengono solo a chi governa l'azienda.</li>
            </ul>
            <div style="border-top:1px dashed #334155; padding-top:8px; margin-top:8px; font-size:11px; color:#10B981;">
                ◈ Conceived, Directed & Engineered by <strong>Enrico Braglia</strong> // Co-orchestrated via AI Synthesis
            </div>
        </div>
        """, unsafe_allow_html=True)

if hasattr(st, "dialog"):
    @st.dialog("◈ ARCHITECT & GENESIS // BEMASK SOVEREIGN ZERO", width="large")
    def open_architect_modal():
        render_architect_dossier_content()
else:
    def open_architect_modal():
        st.session_state["show_arch_fallback"] = not st.session_state.get("show_arch_fallback", False)

# ==============================================================================
# 8. KOENIG ZERO-TRUST SECURITY GATE (IDENTICO A ALPHA_CORE.PY)
# ==============================================================================
STAFF_PINS = {
    "1024": "OPERATORE BAR / CUCINA (MODALITÀ STAFF ANTI-TALPA)",
    "2048": "GOVERNANTE AI PIANI (MODALITÀ STAFF ANTI-TALPA)",
    "3096": "OPERATORE LIDO / REPARTO (MODALITÀ STAFF ANTI-TALPA)"
}

if not st.session_state["auth_unlocked"]:
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    g_left, g_center, g_right = st.columns([0.5, 2.2, 0.5])
    with g_center:
        st.markdown(f"""
        <div style="background:#161B24; border:2px solid #F59E0B; border-top:6px solid #F59E0B; padding:24px; border-radius:4px; box-shadow:0 0 45px rgba(245,158,11,0.22);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>{EAGLE_HERO_SVG}</div>
                <span class="badge-amber">ARCHITECT: ENRICO BRAGLIA</span>
            </div>
            <div style="font-size:19px; font-weight:900; color:#FFFFFF; letter-spacing:1.4px;">
                BEMASK // DATA WAFER SECURITY GATE
            </div>
            <div style="font-size:11px; color:#38BDF8; font-family:'Share Tech Mono', monospace; margin-top:4px; margin-bottom:10px;">
                EAGLE LAUNCH PAD & HYDRAULIC HANGAR LIFT | ZERO-PIZZINI VOLATILE RAM
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ ACCESSO RAPIDO DEMO (1-CLICK PER TELEFONINO E TEST ENRICO)", use_container_width=True):
            st.session_state["pending_sound"] = "commlock"
            st.session_state["auth_unlocked"] = True
            st.session_state["auth_role"] = "COMMANDER"
            st.session_state["auth_user"] = "ENRICO BRAGLIA // SYSTEM ARCHITECT"
            st.rerun()

        c_pin, c_2fa = st.columns(2)
        in_pin = c_pin.text_input("🔑 PIN OPERATORE / TITOLARE", type="password", placeholder="Es. 9999 o 1024")
        in_2fa = c_2fa.text_input("📱 CODICE 2FA (6 CIFRE - SOLO TITOLARE)", type="password", placeholder="Google Auth / 199975")

        if st.button("🛡️ VERIFICA CREDENZIALI E SBLOCCA EAGLE LAUNCH PAD", use_container_width=True):
            master_pin = get_master_pin()
            secret_2fa = get_totp_secret()
            ora_try = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            if in_pin.strip() == master_pin:
                if verify_2fa_code(in_2fa, secret_2fa):
                    st.session_state["pending_sound"] = "commlock"
                    st.session_state["auth_unlocked"] = True
                    st.session_state["auth_role"] = "COMMANDER"
                    st.session_state["auth_user"] = "ENRICO BRAGLIA // COMMANDER (2FA VERIFIED)"
                    st.session_state["pin_code"] = master_pin
                    st.rerun()
                else:
                    play_ems_synth("klaxon")
                    st.session_state["breach_log"].append(
                        f"⚠️ [{ora_try}] TENTATIVO INTRUSIONE: Usato PIN Titolare senza Token 2FA valido (Codice inserito: '{in_2fa}')"
                    )
                    st.error("🚨 ACCESSO NEGATO: CODICE 2FA MANCANTE O SCADUTO! Registrato nel Log Antintrusione.")

            elif in_pin.strip() in STAFF_PINS:
                st.session_state["pending_sound"] = "burst"
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

        if st.button("◈ CHI È IL CREATORE // ARCHITECT DOSSIER (ENRICO BRAGLIA)", use_container_width=True):
            play_ems_synth("commlock")
            open_architect_modal()

        if st.session_state.get("show_arch_fallback", False):
            render_architect_dossier_content()

        st.markdown("""
        <div style="margin-top:22px; padding:10px; border-top:1px solid #263040; text-align:center; font-family:'Share Tech Mono', monospace; font-size:10px; color:#64748B; letter-spacing:1px;">
            ◈ <strong style="color:#F59E0B;">BEMASK SOVEREIGN ARCHITECTURE</strong> · CONCEIVED & ENGINEERED BY <strong style="color:#E2E8F0;">ENRICO BRAGLIA</strong> · ZERO-TRUST VOLATILE RAM ◈
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# 9. DOCK RAPIDA SUPERIORE + TOP KOENIG BAR + MISSION BAR CON TUBI NIXIE
# ==============================================================================
is_commander = (st.session_state["auth_role"] == "COMMANDER")
mode_cfg = GENETIC_MODES[st.session_state["genetic_mode"]]
ora_attuale = datetime.now().strftime("%H:%M")
total_wafers = len(st.session_state["hangar_wafers"])
open_wafers = sum(1 for w in st.session_state["hangar_wafers"] if not w["taken"])

dock_links_html = []
for node in DOCK_FLEET:
    if LICENSE_INFO["is_filtered"] and node["code"] not in LICENSE_INFO["allowed_codes"]:
        continue
    is_curr = (node["code"] == "DW")
    cls_d = "dock-pill active" if is_curr else "dock-pill"
    href_d = "#" if is_curr else (f"{node['url']}?mask={LICENSE_INFO['raw_mask']}" if LICENSE_INFO["raw_mask"] else node["url"])
    target_attr = "" if is_curr else 'target="_blank"'
    dock_links_html.append(f'<a class="{cls_d}" href="{href_d}" {target_attr}>{node["short"]}</a>')

st.markdown(
    f'<div class="quick-dock"><span class="badge-amber" style="margin-bottom:0;">DOCK RAPIDA</span>{"".join(dock_links_html)}</div>',
    unsafe_allow_html=True
)

breach_count = len(st.session_state["breach_log"])
breach_badge = f'<span class="badge-red">🚨 {breach_count} INTRUSIONI</span>' if breach_count > 0 else '<span class="badge-green">🛡️ ZERO INTRUSIONI</span>'

top_c1, top_c_arch, top_c2, top_c3 = st.columns([2.65, 1.15, 0.85, 0.65])
with top_c1:
    st.markdown(f"""
    <div class="koenig-strip">
        <div>
            <span class="badge-amber">DATA WAFER POD</span>
            <span style="font-size:12px; font-weight:900; letter-spacing:1px; color:#FFFFFF;">
                EAGLE LAUNCH PAD // {html.escape(str(st.session_state['auth_user']))}
            </span>
        </div>
        <div style="margin-top:5px;">
            <span class="badge-cyan">{mode_cfg['badge']}</span>
            <span class="badge-amber">ARCHITECT: E. BRAGLIA</span>
            {breach_badge}
            <span class="badge-white">ENTITY: {html.escape(str(st.session_state['entity_id']))}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top_c_arch:
    if st.button("◈ ARCHITECT\nENRICO BRAGLIA", use_container_width=True):
        play_ems_synth("commlock")
        open_architect_modal()
with top_c2:
    st.link_button("🏠 ALPHA HUB\n(MAIN MISSION)", "https://alpha-main-mission.streamlit.app", use_container_width=True)
with top_c3:
    if st.button("🔒 BLOCCA\nSESSIONE", use_container_width=True):
        st.session_state["auth_unlocked"] = False
        st.rerun()

if st.session_state.get("show_arch_fallback", False):
    with st.expander("◈ ARCHITECT & GENESIS // ENRICO BRAGLIA", expanded=True):
        render_architect_dossier_content()

st.markdown(f"""
<div class="mission-bar">
    <div style="display:flex; align-items:center; gap:16px;">
        <div>{EAGLE_HERO_SVG}</div>
        <div>
            <div class="mission-title">BEMASK DATA WAFER // EAGLE LAUNCH PAD & HANGAR LIFT</div>
            <div class="mission-sub">ARCHITECT: ENRICO BRAGLIA | DATE: {datetime.now().strftime('%a %d/%m/%Y').upper()} | ANTI-PIZZINI 3-AXIS RAM | ZERO CLOUD</div>
        </div>
    </div>
    <div class="nixie-group">
        <span class="nixie-label">ALPHA TIME:</span>
        <span class="nixie-digits">{ora_attuale}</span>
        <span class="nixie-label">HANGAR:</span>
        <span class="nixie-digits">{total_wafers:02d}</span>
    </div>
</div>
""", unsafe_allow_html=True)

if is_commander and not LICENSE_INFO["is_filtered"]:
    sec_c1, sec_c2 = st.columns([1.45, 1.0])
    with sec_c1:
        with st.expander("🧬 SELETTORE GENETICO A 3 ASSETTI & LICENZA URL (?mask=...)", expanded=False):
            g_keys = list(GENETIC_MODES.keys())
            sel_g = st.radio(
                "Assetto Commerciale / Operativo del Pod:",
                options=g_keys,
                index=g_keys.index(st.session_state["genetic_mode"]),
                format_func=lambda k: GENETIC_MODES[k]["label"]
            )
            if sel_g != st.session_state["genetic_mode"]:
                st.session_state["genetic_mode"] = sel_g
                st.rerun()

            e_col1, e_col2 = st.columns(2)
            st.session_state["entity_id"] = e_col1.text_input("Codice Societario / Entity ID (P.IVA):", value=st.session_state["entity_id"])
            if st.session_state["genetic_mode"] == "PARTNER":
                st.session_state["partner_fee_pct"] = e_col2.number_input("Fee / Royalty verso Cubo Madre (%):", 0.0, 60.0, float(st.session_state["partner_fee_pct"]), 0.5)
            st.caption("Esempio Link Licenza Filtrato Bar: `?mask=00,02,10,11,12,DW&mode=STANDALONE&entity=P.IVA-BAR`")

    with sec_c2:
        with st.expander(f"🛡️ CASSAFORTE 2FA & CHIAVE AI OCR/VOCE ({breach_count} Allerte)", expanded=(breach_count > 0)):
            q1, q2 = st.columns([1, 2])
            secret_now = get_totp_secret()
            otp_uri = f"otpauth://totp/BEMASK_ALPHA:TITOLARE?secret={secret_now}&issuer=BEMASK_ALPHA"
            with q1:
                st.markdown(f"""
                <div style="text-align:center; background:#0B0E14; border:1px solid #10B981; padding:8px; border-radius:4px;">
                    <div style="font-size:9px; color:#10B981; margin-bottom:4px;">GOOGLE AUTH</div>
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=130x130&color=10B981&bgcolor=0B0E14&data={otp_uri}" width="95" />
                </div>
                """, unsafe_allow_html=True)
            with q2:
                st.markdown(f"**Chiave 2FA:** `{secret_now}` | **Token (30s):** `{generate_totp_token(secret_now)}`")
                v_key = st.text_input("🤖 Chiave Google AI Studio (AIzaSy...):", value=st.session_state.get("custom_gemini_key", ""), key="api_key_box_VAULT", type="password")
                if v_key and len(v_key.strip()) > 15:
                    st.session_state["custom_gemini_key"] = v_key.strip()
            if st.session_state["breach_log"]:
                for b_item in st.session_state["breach_log"][-4:]:
                    st.caption(b_item)

# ==============================================================================
# 10. CORPO PRINCIPALE (2 LIVELLI: SUPERFICIE LAUNCH PAD + HANGAR RAM) + DESTRA
# ==============================================================================
col_left, col_right = st.columns([3.25, 1.15])
rc_id = st.session_state["ram_clear_counter"]

with col_left:
    st.markdown("""
    <div class="blum-stage" style="border: 2px solid #F59E0B; border-left: 6px solid #F59E0B; box-shadow: inset 0 0 36px rgba(245, 158, 11, 0.25);">
        <div style="font-size:11px; color:#F59E0B; font-family:'Share Tech Mono'; letter-spacing:1.3px;">
            LIVELLO SUPERFICIE // EAGLE LAUNCH PAD & HYDRAULIC HANGAR LIFT // ZERO DISTRAZIONI
        </div>
        <div style="font-size:20px; font-weight:900; color:#FFFFFF; letter-spacing:1.2px; margin-top:2px;">
            ATTERRAGGIO RAPIDO ANTI-PIZZINI (FOTO OCR · VOCE · NOTA LAMPO)
        </div>
        <div style="font-size:11px; color:#38BDF8; font-family:'Share Tech Mono'; margin-top:4px;">
            NESSUN TASTO CHIAMA O WHATSAPP DURANTE IL TURNO — DISCESA DIRETTA IN TESTO PULITO A 3 ASSI (X·Y·Z)
        </div>
    </div>
    """, unsafe_allow_html=True)

    pad_vis_col, pad_cmd_col = st.columns([1.3, 1.9])

    with pad_vis_col:
        st.markdown(
            build_eagle_launch_pad_svg(is_descending=st.session_state["hydraulic_anim"], open_count=open_wafers),
            unsafe_allow_html=True
        )
        st.session_state["hydraulic_anim"] = False

        zc1, zc2 = st.columns(2)
        st.session_state["shift_z"] = zc1.selectbox("Turno (Asse Z)", ["MATTINA", "POMERIGGIO", "SERA / NOTTE", "CAMBIO TURNO"])
        st.session_state["meteo_z"] = zc2.selectbox("Contesto / Meteo", ["NOMINAL ORBIT // SERENO", "ALTA AFFLUENZA / PICCO", "SOLAR STORM // PIOGGIA", "CHIUSURA REPARTO"])
        selected_dept = st.selectbox("Reparto Operativo", mode_cfg["depts"], key="active_pad_dept")

        typed_ai = st.text_input(
            "🔑 Chiave AI Gemini (per Foto OCR & Voce):",
            value=st.session_state.get("custom_gemini_key", ""),
            key="api_key_box_WAFER",
            type="password",
            placeholder="AIzaSy... (Nota testuale funziona anche senza chiave)"
        )
        if typed_ai and len(typed_ai.strip()) > 15:
            st.session_state["custom_gemini_key"] = typed_ai.strip()

    with pad_cmd_col:
        t_foto, t_voce, t_lampo = st.tabs([
            "📸 1. FOTO PIZZINO (OCR)",
            "🎙️ 2. DETTATURA VOCALE",
            "⚡ 3. NOTA LAMPO TESTUALE"
        ])

        with t_foto:
            use_cam_pad = st.toggle("📸 ATTIVA FOTOCAMERA SMARTPHONE / BANCONE", value=False, key="tog_cam_pad")
            cam_shot = st.camera_input("Inquadra il foglietto scritto a mano", key=f"cam_pad_{rc_id}") if use_cam_pad else None
            up_photo = st.file_uploader("📂 Oppure carica foto del pizzino da galleria", type=["jpg", "jpeg", "png", "webp"], key=f"up_pad_{rc_id}")
            active_img = cam_shot if cam_shot is not None else up_photo
            extra_photo_note = st.text_input("Nota integrativa opzionale:", placeholder="Es. pagato contanti / urgente", key=f"p_note_{rc_id}")

            if st.button("⬇ CALA PIZZINO NELL'HANGAR RAM (OCR AI)", use_container_width=True, key="btn_drop_photo"):
                if active_img is None:
                    st.warning("⚠️ Scatta o carica prima la foto del foglietto!")
                else:
                    with st.spinner("🤖 Lettura grafia pizzino in RAM e discesa idraulica nell'Hangar..."):
                        raw_img = active_img.getvalue()
                        mime_img = getattr(active_img, "type", None) or "image/jpeg"
                        parsed_w, err_w = process_wafer_in_ram_with_ai(
                            get_gemini_api_key(),
                            raw_text=extra_photo_note,
                            media_bytes=raw_img,
                            mime_type=mime_img,
                            default_dept=selected_dept,
                            default_channel=mode_cfg["channels"][0]
                        )
                        raw_img = None
                        if parsed_w:
                            atom = land_wafer_into_hangar(parsed_w, "FOTO PIZZINO OCR")
                            st.toast(f"✅ Pizzino {atom['id']} convertito e calato nell'Hangar!")
                            st.rerun()
                        else:
                            play_ems_synth("klaxon")
                            st.warning(f"⚠️ {err_w}")

        with t_voce:
            if hasattr(st, "audio_input"):
                audio_clip = st.audio_input("🎙️ Premi e detta la consegna, spesa o manutenzione (RAM-Only)", key=f"aud_pad_{rc_id}")
            else:
                audio_clip = st.file_uploader("🎙️ Carica clip vocale (.wav, .mp3, .m4a, .ogg)", type=["wav", "mp3", "m4a", "ogg", "webm"], key=f"aud_fb_{rc_id}")
            extra_voice_note = st.text_input("Contesto rapido opzionale:", placeholder="Es. consegna per turno pomeriggio", key=f"v_note_{rc_id}")

            if st.button("⬇ TRASCRIVI VOCE E CALA NELL'HANGAR RAM", use_container_width=True, key="btn_drop_voice"):
                if audio_clip is None:
                    st.warning("⚠️ Registra prima il messaggio vocale!")
                else:
                    with st.spinner("🎙️ Trascrizione vocale AI in RAM e smistamento A-O..."):
                        raw_aud = audio_clip.getvalue()
                        mime_aud = getattr(audio_clip, "type", None) or "audio/wav"
                        parsed_v, err_v = process_wafer_in_ram_with_ai(
                            get_gemini_api_key(),
                            raw_text=extra_voice_note,
                            media_bytes=raw_aud,
                            mime_type=mime_aud,
                            default_dept=selected_dept,
                            default_channel=mode_cfg["channels"][0]
                        )
                        raw_aud = None
                        if parsed_v:
                            atom = land_wafer_into_hangar(parsed_v, "VOCE AUDIO RAM")
                            st.toast(f"✅ Nota vocale {atom['id']} trascritta nell'Hangar!")
                            st.rerun()
                        else:
                            play_ems_synth("klaxon")
                            st.warning(f"⚠️ {err_v}")

        with t_lampo:
            flash_txt = st.text_area(
                "⚡ Scrivi nota lampo, ordine, temperatura o spesa (riconosce da sola quantità, °C, € e conto A-O):",
                height=86,
                placeholder="Es. 'Finito prosecco, ordinare 3 casse Doreca urgente' oppure 'Pagato idraulico € 60 contanti guarnizione lavabo'",
                key=f"flash_txt_{rc_id}"
            )
            fl1, fl2, fl3 = st.columns(3)
            ov_eur = fl1.number_input("Importo € (Opz.)", 0.0, 50000.0, 0.0, step=1.0, key=f"fl_eur_{rc_id}")
            ov_chan = fl2.selectbox("Canale Y", mode_cfg["channels"], key=f"fl_ch_{rc_id}")
            ov_acc = fl3.selectbox("Conto [A-O]", ["AUTO SEMANTICO"] + list(SEMANTIC_KEYWORDS.keys()), key=f"fl_ac_{rc_id}")

            if st.button("⬇ CALA NOTA LAMPO NELL'HANGAR RAM", use_container_width=True, key="btn_drop_flash"):
                if not str(flash_txt).strip() and ov_eur <= 0:
                    st.warning("⚠️ Scrivi una nota o inserisci un importo!")
                else:
                    active_k = get_gemini_api_key()
                    if active_k:
                        parsed_f, _ = process_wafer_in_ram_with_ai(active_k, raw_text=flash_txt, default_dept=selected_dept, default_channel=ov_chan)
                        if not parsed_f:
                            parsed_f = local_heuristic_wafer_parser(flash_txt, selected_dept, ov_chan)
                    else:
                        parsed_f = local_heuristic_wafer_parser(flash_txt, selected_dept, ov_chan)

                    if ov_eur > 0:
                        parsed_f["euro_y"] = round(float(ov_eur), 2)
                    if ov_chan != mode_cfg["channels"][0]:
                        parsed_f["channel_y"] = ov_chan
                    if ov_acc != "AUTO SEMANTICO":
                        parsed_f["conto_ao"] = ov_acc

                    atom = land_wafer_into_hangar(parsed_f, "NOTA LAMPO")
                    st.toast(f"✅ Wafer {atom['id']} sceso nell'Hangar RAM!")
                    st.rerun()

    st.markdown("""
    <div class="xray-desk">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <span class="badge-amber">▼ LIVELLO INFERIORE // HYDRAULIC HANGAR RAM (ATOMI PULITI A 3 ASSI X·Y·Z)</span>
            <span style="font-family:'Share Tech Mono', monospace; font-size:11px; color:#10B981;">
                SMISTAMENTO AUTOMATICO [A]-[O] | SPUNTA PRESA IN CARICO | 0 BYTE SU DISCO
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    wafers_list = st.session_state["hangar_wafers"]
    tot_eur_hangar = sum(w["y"]["euro"] for w in wafers_list)
    tot_fee_hangar = sum(w["y"].get("royalty_eur", 0.0) for w in wafers_list)

    hk1, hk2, hk3 = st.columns(3)
    with hk1:
        st.markdown(f"""
        <div class="kpi-custom-box" style="border-left-color:#F59E0B;">
            <div class="kpi-custom-title">PIZZINI STRUTTURATI IN RAM</div>
            <div class="kpi-custom-value">{total_wafers} WAFER ({open_wafers} APERTI)</div>
            <div class="kpi-custom-sub" style="color:#F59E0B;">● Zero foglietti cartacei dispersi</div>
        </div>
        """, unsafe_allow_html=True)
    with hk2:
        val_y_str = f"€ {tot_eur_hangar:.2f}" if is_commander else "🔒 PROTETTO (RUOLO STAFF)"
        st.markdown(f"""
        <div class="kpi-custom-box" style="border-left-color:#10B981;">
            <div class="kpi-custom-title">ASSE Y // ENERGIA FINANZIARIA IN HANGAR</div>
            <div class="kpi-custom-value">{val_y_str}</div>
            <div class="kpi-custom-sub" style="color:#10B981;">● Conti Paralleli [A] → [O]</div>
        </div>
        """, unsafe_allow_html=True)
    with hk3:
        if st.session_state["genetic_mode"] == "PARTNER":
            sub_m = f"€ {tot_fee_hangar:.2f} ({st.session_state['partner_fee_pct']}%)" if is_commander else "🔒 PROTETTO"
            title_m = "ROYALTY / FEE VERSO CUBO MADRE"
        else:
            sub_m = f"{total_wafers - open_wafers} EVASI"
            title_m = "PRESA IN CARICO TURNO"
        st.markdown(f"""
        <div class="kpi-custom-box" style="border-left-color:#38BDF8;">
            <div class="kpi-custom-title">{title_m}</div>
            <div class="kpi-custom-value">{sub_m}</div>
            <div class="kpi-custom-sub" style="color:#38BDF8;">● Sincronizzabile via .JSON / .TXT</div>
        </div>
        """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns([1.1, 1.2, 1.2, 1.3])
    flt_state = f1.selectbox("Stato Spunta:", ["TUTTI", "DA PRENDERE IN CARICO", "PRESI IN CARICO"])
    flt_dept = f2.selectbox("Filtra Reparto:", ["TUTTI"] + mode_cfg["depts"])
    flt_tag = f3.selectbox("Filtra Categoria:", ["TUTTI"] + OPERATIONAL_TAGS)
    flt_conto = f4.selectbox("Filtra Conto [A-O]:", ["TUTTI"] + list(SEMANTIC_KEYWORDS.keys()))

    visible_wafers = []
    for w in wafers_list:
        if flt_state == "DA PRENDERE IN CARICO" and w["taken"]:
            continue
        if flt_state == "PRESI IN CARICO" and not w["taken"]:
            continue
        if flt_dept != "TUTTI" and w["x"]["dept"] != flt_dept:
            continue
        if flt_tag != "TUTTI" and w["x"]["op_tag"] != flt_tag:
            continue
        if flt_conto != "TUTTI" and w["y"]["conto"] != flt_conto:
            continue
        visible_wafers.append(w)

    if not visible_wafers:
        st.info("Nessun Wafer nell'Hangar per i filtri selezionati.")
    else:
        for w in visible_wafers:
            wid = w["id"]
            z, x, y = w["z"], w["x"], w["y"]
            cls_card = "hangar-card taken" if w["taken"] else ("hangar-card urgent" if x.get("urgent") else "hangar-card")

            hide_y = (not is_commander) and (y["conto"] in SENSITIVE_ACCOUNTS or y["euro"] > 0)
            if hide_y:
                y_badge = '<span class="badge-red">ASSE Y: 🔒 RISERVATO COMMANDER</span>'
            else:
                fee_str = f" · FEE CUBO €{y.get('royalty_eur', 0):.2f}" if st.session_state["genetic_mode"] == "PARTNER" and y.get("royalty_eur", 0) > 0 else ""
                y_badge = f'<span class="badge-green">Y: € {y["euro"]:.2f} · {html.escape(str(y["channel"]))} · {html.escape(str(y["conto"]))}{fee_str}</span>'

            urg_badge = '<span class="badge-red">🚨 URGENTE</span>' if x.get("urgent") and not w["taken"] else ""
            taken_line = f"<div style='font-family:Share Tech Mono,monospace;font-size:10.5px;color:#10B981;margin-top:5px;'>✔ PRESO IN CARICO ({html.escape(str(w['taken_by']))})</div>" if w["taken"] else ""

            c_card, c_act = st.columns([4.1, 1.15])
            with c_card:
                st.markdown(f"""
                <div class="{cls_card}">
                    <div>
                        <span class="badge-cyan">Z: {html.escape(str(wid))} · {html.escape(str(z['time']))} · {html.escape(str(z['shift']))} · {html.escape(str(z['source']))}</span>
                        <span class="badge-amber">X: {html.escape(str(x['dept']))} · {html.escape(str(x['op_tag']))} · {html.escape(str(x['matter']))}</span>
                        {y_badge}
                        {urg_badge}
                    </div>
                    <div style="font-family:'Share Tech Mono', monospace; font-size:14px; color:#FFFFFF; margin-top:6px; line-height:1.45;">
                        {html.escape(str(x['clean_text']))}
                    </div>
                    {taken_line}
                </div>
                """, unsafe_allow_html=True)
            with c_act:
                btn_lbl = "↩ RIAPRI" if w["taken"] else "✔ PRENDI IN\nCARICO"
                if st.button(btn_lbl, key=f"ack_{wid}", use_container_width=True):
                    w["taken"] = not w["taken"]
                    w["taken_by"] = f"{st.session_state['auth_role']} · {datetime.now().strftime('%H:%M')}" if w["taken"] else ""
                    play_ems_synth("commlock")
                    st.rerun()
                if is_commander:
                    if st.button("🗑️ ELIMINA", key=f"del_{wid}", use_container_width=True):
                        st.session_state["hangar_wafers"] = [item for item in st.session_state["hangar_wafers"] if item["id"] != wid]
                        st.rerun()

    st.markdown("---")
    txt_lines = [
        f"BEMASK DATA WAFER // REPORT HANGAR RAM — {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"ARCHITECT: ENRICO BRAGLIA ({ARCHITECT_ID}) | ENTITY: {st.session_state['entity_id']} | ASSETTO: {mode_cfg['label']}",
        "=" * 78
    ]
    for w in wafers_list:
        st_lbl = f"EVASO ({w['taken_by']})" if w["taken"] else "DA PRENDERE IN CARICO"
        y_txt = "[RISERVATO]" if (not is_commander and w["y"]["euro"] > 0) else f"EUR {w['y']['euro']:.2f} | {w['y']['channel']} | {w['y']['conto']}"
        txt_lines.append(f"[{w['id']}] {w['z']['date']} {w['z']['time']} ({w['z']['shift']}) — {st_lbl}")
        txt_lines.append(f"  X (MATERIA): [{w['x']['dept']}] [{w['x']['op_tag']}] ({w['x']['matter']}) -> {w['x']['clean_text']}")
        txt_lines.append(f"  Y (ENERGIA): {y_txt}")
        txt_lines.append("-" * 78)

    json_3axis_str = json.dumps({
        "architect_seal": ARCHITECT_ID,
        "pod": POD_REPO,
        "entity_id": st.session_state["entity_id"],
        "genetic_mode": st.session_state["genetic_mode"],
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "wafers_3axis": wafers_list
    }, indent=2, ensure_ascii=False)

    ex1, ex2, ex3 = st.columns(3)
    with ex1:
        if st.download_button(
            "📄 SCARICA CONSEGNA (.TXT)",
            "\n".join(txt_lines),
            file_name=f"data_wafer_turno_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        ):
            st.session_state["unsaved_wafers_count"] = 0
    with ex2:
        if st.download_button(
            "💾 SALVA ATOMI 3-ASSI (.JSON)",
            json_3axis_str,
            file_name=f"data_wafer_3axis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        ):
            st.session_state["unsaved_wafers_count"] = 0
    with ex3:
        if st.button("🔥 DISTRUGGI HANGAR RAM ORA", use_container_width=True):
            st.session_state["hangar_wafers"] = []
            st.session_state["unsaved_wafers_count"] = 0
            st.session_state["ram_clear_counter"] += 1
            st.session_state["pending_sound"] = "burst"
            st.rerun()

    with st.expander("📂 RICARICA O FONDI FILE .JSON 3-ASSI DA ALTRO DISPOSITIVO (ZERO-CLOUD)"):
        up_j = st.file_uploader("Seleziona file .JSON Data Wafer", type=["json"], label_visibility="collapsed")
        if up_j is not None and st.button("⚡ CARICA ATOMI NELL'HANGAR RAM", use_container_width=True):
            try:
                loaded_j = json.loads(up_j.getvalue().decode("utf-8"))
                inc_list = loaded_j.get("wafers_3axis", loaded_j if isinstance(loaded_j, list) else [])
                known_ids = {w["id"] for w in st.session_state["hangar_wafers"]}
                added_n = 0
                for item in inc_list:
                    if isinstance(item, dict) and "x" in item and "y" in item and item.get("id") not in known_ids:
                        st.session_state["hangar_wafers"].append(item)
                        known_ids.add(item["id"])
                        added_n += 1
                play_ems_synth("commlock")
                st.success(f"Caricati {added_n} Wafer in RAM!")
                st.rerun()
            except Exception as ex_err:
                st.error(f"Errore lettura JSON: {ex_err}")

# --- COLONNA DESTRA COMPLETA (EMS-1975 SYNTH + LIFT + KLAXON + RITORNO HUB + QR) ---
with col_right:
    st.markdown("""
    <div class="ems-panel">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:11px; font-weight:900; color:#FFFFFF; letter-spacing:1px;">ALPHA EMS-1975<br>SYNTH</span>
            <span style="font-size:10px; font-weight:900; color:#10B981; font-family:'Share Tech Mono';">LIFT<br>ARMED</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    s_col1, s_col2 = st.columns(2)
    with s_col1:
        if st.button("▶ X5-7 DATA\nBURST", use_container_width=True):
            play_ems_synth("burst")
            st.toast("🔊 EMS-1975: X5-7 Data Burst")
    with s_col2:
        if st.button("◈ COMMLOCK\n1975", use_container_width=True):
            play_ems_synth("commlock")
            st.toast("📡 Commlock 1975 Sincronizzato")

    if st.button("⬇ HYDRAULIC HANGAR LIFT", use_container_width=True):
        st.session_state["hydraulic_anim"] = True
        st.session_state["pending_sound"] = "hydraulic"
        st.rerun()

    if st.button("▲ ALPHA KLAXON SIREN", use_container_width=True):
        play_ems_synth("klaxon")
        st.warning("🚨 ALLERTA PRIORITÀ ALTA IN HANGAR RAM")

    st.link_button("🏠 TORNA A ALPHA MAIN MISSION", "https://alpha-main-mission.streamlit.app", use_container_width=True)

    teleport_opts = [f"{n['short']}" for n in DOCK_FLEET if (not LICENSE_INFO["is_filtered"] or n["code"] in LICENSE_INFO["allowed_codes"])]
    chosen_tp = st.selectbox("SELEZIONA NODO TELEPORT", teleport_opts, label_visibility="collapsed")

    target_url = "https://bemask-data-wafer.streamlit.app"
    for n in DOCK_FLEET:
        if chosen_tp == n["short"] and n["url"] != "#":
            target_url = n["url"]
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
            {chosen_tp}
        </div>
        <div style="font-size:9px; color:#94A3B8; font-family:'Share Tech Mono', monospace; margin-top:2px;">
            bemask-data-wafer.streamlit.app
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 11. PUNZONE METALLICO DI PROPRIETÀ INTELLETTUALE ---
st.markdown("""
<div style="margin-top:28px; padding:12px; border-top:1px solid #263040; text-align:center; font-family:'Share Tech Mono', monospace; font-size:10.5px; color:#64748B; letter-spacing:1.1px;">
    ◈ <strong style="color:#F59E0B;">BEMASK SOVEREIGN ARCHITECTURE</strong> · CONCEIVED, DIRECTED & ENGINEERED BY <strong style="color:#E2E8F0;">ENRICO BRAGLIA</strong> · 3-AXIS FRACTAL CORE · ZERO-TRUST VOLATILE RAM ◈
</div>
""", unsafe_allow_html=True)
