#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BEMASK SOVEREIGN ZERO // MICRO-POD TRASVERSALE: DATA WAFER (data_wafer.py)
MANUFATTO: EAGLE LAUNCH PAD & HYDRAULIC HANGAR LIFT (Moonbase Alpha 1975)
================================================================================
Repository : org: bemask-sovereign-zero / bemask-data-wafer
Architetto : ENRICO BRAGLIA (ID: EB-BEMASK-2026-ALPHA)
Esperienza : 30+ anni Direzione Alberghiera, Revenue Management, F&B, Media & AI Lab
Sovranità  : ZERO-TRUST RAM-ONLY (0 byte persistiti su disco o cloud esterno)
Dipendenze : Python Standard Library + Streamlit (Zero librerie terze richieste)
Regola Turno: ZERO pulsanti "Chiama" o "WhatsApp" (Zero distrazioni operative)
================================================================================
"""

import base64
import hashlib
import hmac
import html
import json
import re
import struct
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 0. CONFIGURAZIONE PAGINA STREAMLIT & COSTANTI COSTITUZIONALI
# ==============================================================================
st.set_page_config(
    page_title="BEMASK DATA WAFER // EAGLE LAUNCH PAD",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ARCHITECT_NAME = "ENRICO BRAGLIA"
ARCHITECT_ID = "EB-BEMASK-2026-ALPHA"
POD_CODE = "DW-EAGLE-LIFT"
POD_REPO = "bemask-data-wafer"
POD_VERSION = "1.0.0-SOVEREIGN-RAM"

# Demo Security Defaults (Modificabili in RAM dal Commander)
DEFAULT_COMMANDER_PIN = "1975"
DEFAULT_TOTP_SECRET = "BEMASKALPHA1975SOVEREIGNZERO2026"  # Base32 RFC 4648 valida

# Matrice Frattale 2^12 + Hub Centrale + Pod Trasversale per Dock Rapida & ?mask=
SECTOR_MATRIX = [
    {"bit": 0,  "code": "00", "icon": "◈", "label": "ALPHA HUB",      "repo": "alpha-main-mission"},
    {"bit": 1,  "code": "01", "icon": "▲", "label": "FRONT & APEX",   "repo": "bemask-front-apex"},
    {"bit": 2,  "code": "02", "icon": "⬡", "label": "LAZERS BEV",     "repo": "bemask-lazers-bev"},
    {"bit": 3,  "code": "03", "icon": "⬢", "label": "LAZERS FOOD",    "repo": "bemask-lazers-food"},
    {"bit": 4,  "code": "04", "icon": "☀", "label": "BEACH & POOL",   "repo": "bemask-beach-pool"},
    {"bit": 5,  "code": "05", "icon": "✧", "label": "SPA AYURVEDA",   "repo": "bemask-spa-ayurveda"},
    {"bit": 6,  "code": "06", "icon": "⊞", "label": "S.K.A. ROOMS",   "repo": "bemask-ska-rooms"},
    {"bit": 7,  "code": "07", "icon": "⛟", "label": "ACQUISTI ROP",   "repo": "bemask-rop-procurement"},
    {"bit": 8,  "code": "08", "icon": "❄", "label": "HACCP 1-CLICK",  "repo": "bemask-haccp-shield"},
    {"bit": 9,  "code": "09", "icon": "❖", "label": "GOPPAR P.IVA",   "repo": "bemask-goppar-matrix"},
    {"bit": 10, "code": "10", "icon": "⚿", "label": "BAR & DDT",      "repo": "bemask-ddt-sentinel"},
    {"bit": 11, "code": "11", "icon": "⚡", "label": "BANK VAMPIRE",   "repo": "bemask-bank-vampire"},
    {"bit": 12, "code": "12", "icon": "⟐", "label": "TRAVEL TUBE",    "repo": "bemask-travel-tube"},
    {"bit": 13, "code": "DW", "icon": "◎", "label": "DATA WAFER",     "repo": "bemask-data-wafer"},
]

# I 13 Conti Semantici [A]-[O] (Alfabeto Italiano Classico: A,B,C,D,E,F,G,H,I,L,M,N,O)
SEMANTIC_ACCOUNTS = {
    "[A]": {
        "name": "Caffè, Torrefazione & Materie Prime Bar",
        "sensitive": False,
        "keywords": ["caffè", "caffe", "miscela", "latte", "zucchero", "brioche", "cornetti", "ghiaccio", "sciroppo", "bar"],
    },
    "[B]": {
        "name": "Food, Cucina & Derrate Alimentari Fresche",
        "sensitive": False,
        "keywords": ["cucina", "pesce", "carne", "verdura", "frutta", "farina", "olio", "pasta", "pane", "chef", "dispensa", "frigo"],
    },
    "[C]": {
        "name": "Cantina, Vini, Champagne & Spirits",
        "sensitive": False,
        "keywords": ["vino", "bottiglie", "prosecco", "champagne", "gin", "vodka", "rum", "amaro", "birra", "fusto", "cantina"],
    },
    "[D]": {
        "name": "Materiali Consumo, Monouso & Detergenza",
        "sensitive": False,
        "keywords": ["tovaglioli", "carta", "detergente", "sapone", "guanti", "sacchi", "bicchieri", "cannucce", "pulizia", "chimici"],
    },
    "[E]": {
        "name": "Manutenzione, Ricambi & Impianti Tecnici",
        "sensitive": False,
        "keywords": ["guasto", "rotto", "riparazione", "idraulico", "elettricista", "lampadina", "perdita", "condizionatore", "pompa", "tecnico", "manutenzione"],
    },
    "[F]": {
        "name": "Utenze, Energia, Gas & Connettività",
        "sensitive": True,
        "keywords": ["bolletta", "luce", "enel", "gas", "acqua", "fibra", "internet", "utenza", "kw", "contatore"],
    },
    "[G]": {
        "name": "Personale, Extra Turni & Rimborsi Staff",
        "sensitive": True,
        "keywords": ["acconto", "extra", "turno", "stipendio", "busta", "rimborso", "cameriere", "barista", "bagnino", "ferie"],
    },
    "[H]": {
        "name": "Servizi Esterni, Lavanderia & Vigilanza",
        "sensitive": False,
        "keywords": ["lavanderia", "tovagliato", "lenzuola", "spugne", "vigilanza", "giardiniere", "disinfestazione", "noleggio"],
    },
    "[I]": {
        "name": "Marketing, Eventi, DJ Set & Commissioni",
        "sensitive": True,
        "keywords": ["evento", "musica", "dj", "siae", "locandina", "sponsor", "adv", "commissione", "ota", "promo"],
    },
    "[L]": {
        "name": "Dotazioni Spiaggia, Piscina, Spa & Reparti",
        "sensitive": False,
        "keywords": ["ombrellone", "ombrelloni", "lettino", "sdraio", "cabina", "piscina", "cloro", "massaggio", "olio essenziale", "camera"],
    },
    "[M]": {
        "name": "Imposte, Tasse, Tassa Soggiorno & Licenze",
        "sensitive": True,
        "keywords": ["f24", "iva", "tassa", "soggiorno", "comune", "dogane", "bollo", "demanio", "diritti"],
    },
    "[N]": {
        "name": "Oneri Bancari, Cassa, POS & Differenze RT",
        "sensitive": True,
        "keywords": ["pos", "banca", "commissioni", "fondo cassa", "resto", "chiusura", "scontrino", "rt", "sdd", "bonifico"],
    },
    "[O]": {
        "name": "Prelievo Titolare / Giroconto Holding",
        "sensitive": True,
        "keywords": ["prelievo", "titolare", "proprietà", "holding", "versamento", "cassaforte", "dividendo", "società"],
    },
}

OPERATIONAL_TAGS = [
    "CONSEGNA_TURNO",
    "SPESA_ORDINE",
    "MANUTENZIONE",
    "HACCP_TEMP",
    "INCASSO_EXTRA",
]

# Configurazione dei 3 Assetti Genetici
GENETIC_ASSETS = {
    "STANDALONE": {
        "title": "1) STANDALONE GENERALISTA",
        "badge": "MERCATO APERTO // P.IVA SINGOLA",
        "desc": "Bar, Ristoranti, Stabilimenti, Spa o Imprese esterne (Zero riferimenti a camere/hotel).",
        "departments": ["BAR & BANCO", "CUCINA & LAB", "SALA / SPIAGGIA", "MAGAZZINO", "MANUTENZIONE", "DIREZIONE"],
        "channels": ["NESSUNO (SOLO NOTA)", "CONTANTI", "POS / CARTA", "SDD / BONIFICO"],
    },
    "PARTNER": {
        "title": "2) PARTNER IN CONCESSIONE",
        "badge": "AFFITTO DI RAMO // FEE & COMPENSAZIONE CUBO",
        "desc": "Gestore con propria P.IVA dentro il Resort: attiva Addebiti Camera e calcolo Royalty verso il Cubo Madre.",
        "departments": ["LOUNGE BAR PARTNER", "RISTORANTE PARTNER", "BEACH CLUB", "SPA CONCESSIONE", "MANUTENZIONE", "AMMINISTRAZIONE"],
        "channels": ["NESSUNO (SOLO NOTA)", "ADDEBITO CAMERA (COMPENSAZIONE)", "CONTANTI", "POS PARTNER", "SDD / BONIFICO"],
    },
    "CUBE_DEPT": {
        "title": "3) REPARTO DIRETTO CUBO",
        "badge": "COLLEGAMENTO DIRETTO // ALPHA-MAIN-MISSION",
        "desc": "Reparto interno dell'Albergo Madre / Mega-Resort collegato nativamente al 27° Cubo Centrale.",
        "departments": ["FRONT & CONCIERGE", "F&B LAZERS", "HOUSEKEEPING / S.K.A.", "BEACH & POOL", "SPA & WELLNESS", "TECNICO / ECONOMATO"],
        "channels": ["NESSUNO (SOLO NOTA)", "ADDEBITO CAMERA", "CONTANTI CASSA", "POS HOTEL", "SDD / ECONOMATO"],
    },
}


# ==============================================================================
# 1. UTILITÀ SISTEMA, TOTP NATIVO RFC 6238 & INIZIALIZZAZIONE RAM
# ==============================================================================
def safe_rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def utc_iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def human_time_now() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def normalize_base32(secret: str) -> bytes:
    clean = re.sub(r"[^A-Z2-7]", "", secret.upper())
    if not clean:
        clean = "BEMASKALPHA1975SOVEREIGN"
    padding = (8 - len(clean) % 8) % 8
    return base64.b32decode(clean + ("=" * padding), casefold=True)


def generate_totp_rfc6238(secret: str, for_time: int = None, step: int = 30, digits: int = 6) -> str:
    """Implementazione pura RFC 6238 HMAC-SHA1 in RAM senza librerie esterne."""
    if for_time is None:
        for_time = int(time.time())
    key = normalize_base32(secret)
    counter = int(for_time // step)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code_int = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(code_int % (10 ** digits)).zfill(digits)


def verify_totp_rfc6238(secret: str, user_code: str, window: int = 1) -> bool:
    code_clean = re.sub(r"\D", "", user_code or "")
    if len(code_clean) != 6:
        return False
    now_ts = int(time.time())
    for delta in range(-window, window + 1):
        if hmac.compare_digest(generate_totp_rfc6238(secret, now_ts + delta * 30), code_clean):
            return True
    return False


def parse_url_license_mask() -> dict:
    """Legge i parametri URL (?mask=..., ?asset=..., ?entity=..., ?base_url=...) per licenze su misura."""
    qp = st.query_params if hasattr(st, "query_params") else {}
    raw_mask = str(qp.get("mask", "")).strip()
    raw_asset = str(qp.get("asset", "")).strip().upper()
    raw_entity = str(qp.get("entity", "")).strip()
    raw_royalty = str(qp.get("royalty", "")).strip()
    base_url = str(qp.get("hub", "")).strip()

    allowed_codes = None
    if raw_mask:
        # Supporta sia lista codici (?mask=00,02,08,12,DW) sia bitmask esadecimale/intera 2^12 (?mask=0x1085)
        if "," in raw_mask or raw_mask.upper() in {s["code"] for s in SECTOR_MATRIX}:
            tokens = {t.strip().upper().zfill(2) if t.strip().isdigit() else t.strip().upper() for t in raw_mask.split(",") if t.strip()}
            tokens.add("DW")  # Il pod corrente è sempre attivo
            allowed_codes = tokens
        else:
            try:
                bit_val = int(raw_mask, 16) if raw_mask.lower().startswith("0x") else int(raw_mask)
                codes = {"DW"}
                for s in SECTOR_MATRIX:
                    if s["bit"] == 0 or (bit_val & (1 << (s["bit"] - 1))):
                        codes.add(s["code"])
                allowed_codes = codes
            except ValueError:
                allowed_codes = None

    return {
        "licensed": allowed_codes is not None,
        "allowed_codes": allowed_codes,
        "forced_asset": raw_asset if raw_asset in GENETIC_ASSETS else None,
        "forced_entity": raw_entity if raw_entity else None,
        "forced_royalty": float(raw_royalty) if raw_royalty.replace(".", "", 1).isdigit() else None,
        "base_url": base_url,
        "raw_mask": raw_mask,
    }


def init_ram_state() -> None:
    lic = parse_url_license_mask()
    defaults = {
        "wafers_ram": [],
        "genetic_asset": lic["forced_asset"] or "STANDALONE",
        "entity_id": lic["forced_entity"] or "IT-00000000000-ALPHA",
        "partner_royalty_pct": lic["forced_royalty"] if lic["forced_royalty"] is not None else 12.0,
        "current_shift": "MATTINA",
        "current_weather": "SERENO // FLUSSO REGOLARE",
        "role": "STAFF",  # "STAFF" (filtro anti-talpa attivo) | "COMMANDER" (accesso totale)
        "commander_pin": DEFAULT_COMMANDER_PIN,
        "totp_secret": DEFAULT_TOTP_SECRET,
        "require_totp": False,  # Attivabile dal Commander per blindatura doppia PIN+2FA
        "intrusion_log": [],
        "gemini_api_key": "",
        "gemini_discovered_model": "",
        "audio_synth_enabled": True,
        "sound_trigger_queue": None,
        "lift_descending": False,
        "last_landed_wafer_id": None,
        "show_architect_dossier": False,
        "show_koenig_panel": False,
        "purge_arm": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Se la licenza URL forza asset o entity, riallinea in RAM
    if lic["forced_asset"]:
        st.session_state.genetic_asset = lic["forced_asset"]
    if lic["forced_entity"]:
        st.session_state.entity_id = lic["forced_entity"]


init_ram_state()
LICENSE_CTX = parse_url_license_mask()


# ==============================================================================
# 2. SYNTH ACUSTICO WEBAUDIO EMS-1975 (EFFETTO DISCESA IDRAULICA HANGAR)
# ==============================================================================
def queue_sound(effect_name: str) -> None:
    if st.session_state.audio_synth_enabled:
        st.session_state.sound_trigger_queue = f"{effect_name}:{time.time_ns()}"


def render_ems_1975_synth() -> None:
    trigger = st.session_state.sound_trigger_queue
    if not trigger or not st.session_state.audio_synth_enabled:
        return
    effect = trigger.split(":")[0]
    st.session_state.sound_trigger_queue = None

    js_code = """
    <script>
    (function() {
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;
            const ctx = new AudioCtx();
            const now = ctx.currentTime;
            const effect = "__EFFECT__";

            if (effect === "hydraulic_descent") {
                // 1) Sgancio meccanico pistoni piattaforma Eagle Pad
                const clickOsc = ctx.createOscillator();
                const clickGain = ctx.createGain();
                clickOsc.type = "square";
                clickOsc.frequency.setValueAtTime(190, now);
                clickOsc.frequency.exponentialRampToValueAtTime(48, now + 0.11);
                clickGain.gain.setValueAtTime(0.22, now);
                clickGain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
                clickOsc.connect(clickGain).connect(ctx.destination);
                clickOsc.start(now);
                clickOsc.stop(now + 0.12);

                // 2) Discesa idraulica analogica EMS-1975 (Sub-Bass + Filtro risonante)
                const liftOsc1 = ctx.createOscillator();
                const liftOsc2 = ctx.createOscillator();
                const filter = ctx.createBiquadFilter();
                const liftGain = ctx.createGain();

                liftOsc1.type = "sawtooth";
                liftOsc2.type = "triangle";
                liftOsc1.frequency.setValueAtTime(132, now + 0.08);
                liftOsc1.frequency.exponentialRampToValueAtTime(38, now + 1.35);
                liftOsc2.frequency.setValueAtTime(66, now + 0.08);
                liftOsc2.frequency.exponentialRampToValueAtTime(24, now + 1.35);

                filter.type = "lowpass";
                filter.Q.value = 6.5;
                filter.frequency.setValueAtTime(420, now + 0.08);
                filter.frequency.exponentialRampToValueAtTime(85, now + 1.35);

                liftGain.gain.setValueAtTime(0.001, now);
                liftGain.gain.linearRampToValueAtTime(0.20, now + 0.15);
                liftGain.gain.setValueAtTime(0.18, now + 1.05);
                liftGain.gain.exponentialRampToValueAtTime(0.0001, now + 1.45);

                liftOsc1.connect(filter);
                liftOsc2.connect(filter);
                filter.connect(liftGain).connect(ctx.destination);
                liftOsc1.start(now + 0.08);
                liftOsc2.start(now + 0.08);
                liftOsc1.stop(now + 1.46);
                liftOsc2.stop(now + 1.46);

                // 3) Telemetria aggancio Hangar Base Lunare Alpha (Bip cristallino)
                [987.77, 1318.51].forEach((freq, idx) => {
                    const ping = ctx.createOscillator();
                    const pGain = ctx.createGain();
                    ping.type = "sine";
                    const t0 = now + 1.25 + (idx * 0.11);
                    ping.frequency.setValueAtTime(freq, t0);
                    pGain.gain.setValueAtTime(0.12, t0);
                    pGain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.14);
                    ping.connect(pGain).connect(ctx.destination);
                    ping.start(t0);
                    ping.stop(t0 + 0.15);
                });
            } else if (effect === "telemetry_ack") {
                [1046.5, 1567.98].forEach((f, i) => {
                    const o = ctx.createOscillator();
                    const g = ctx.createGain();
                    o.type = "sine";
                    const t = now + i * 0.07;
                    o.frequency.setValueAtTime(f, t);
                    g.gain.setValueAtTime(0.10, t);
                    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.09);
                    o.connect(g).connect(ctx.destination);
                    o.start(t);
                    o.stop(t + 0.10);
                });
            } else if (effect === "koenig_alarm") {
                [640, 440, 640].forEach((f, i) => {
                    const o = ctx.createOscillator();
                    const g = ctx.createGain();
                    o.type = "sawtooth";
                    const t = now + i * 0.13;
                    o.frequency.setValueAtTime(f, t);
                    g.gain.setValueAtTime(0.16, t);
                    g.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
                    o.connect(g).connect(ctx.destination);
                    o.start(t);
                    o.stop(t + 0.12);
                });
            } else if (effect === "ram_purge") {
                const o = ctx.createOscillator();
                const g = ctx.createGain();
                o.type = "sawtooth";
                o.frequency.setValueAtTime(520, now);
                o.frequency.exponentialRampToValueAtTime(28, now + 0.55);
                g.gain.setValueAtTime(0.20, now);
                g.gain.exponentialRampToValueAtTime(0.0001, now + 0.56);
                o.connect(g).connect(ctx.destination);
                o.start(now);
                o.stop(now + 0.57);
            }
        } catch (e) {}
    })();
    </script>
    """.replace("__EFFECT__", effect)
    components.html(js_code, height=0, width=0)


# ==============================================================================
# 3. MOTORE SEMANTICO [A]-[O] + GEMINI AUTODISCOVERY OCR & AUDIO IN RAM
# ==============================================================================
def discover_gemini_model_in_ram(api_key: str) -> str:
    """Interroga l'endpoint modelli Gemini in RAM e seleziona automaticamente il miglior modello multimodale."""
    if not api_key:
        return ""
    if st.session_state.gemini_discovered_model:
        return st.session_state.gemini_discovered_model

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        models = payload.get("models", [])
        candidates = []
        for m in models:
            methods = m.get("supportedGenerationMethods", [])
            name = m.get("name", "").replace("models/", "")
            if "generateContent" in methods and "gemini" in name.lower():
                candidates.append(name)

        priority_order = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
        for pref in priority_order:
            for c in candidates:
                if c == pref or c.startswith(pref):
                    st.session_state.gemini_discovered_model = c
                    return c
        if candidates:
            st.session_state.gemini_discovered_model = candidates[0]
            return candidates[0]
    except Exception:
        pass
    return "gemini-2.0-flash"


def heuristic_wafer_structurer(raw_text: str, default_dept: str, default_channel: str) -> dict:
    """Motore deterministico locale (Zero-Cloud / Fallback istantaneo) per strutturazione a 3 Assi."""
    clean = re.sub(r"\s+", " ", (raw_text or "").strip())
    lower = clean.lower()

    # 1. Estrazione Valore Finanziario Euro (Asse Y)
    euro_val = 0.0
    euro_patterns = [
        r"(?:€|eur|euro)\s*([0-9]+(?:[.,][0-9]{1,2})?)",
        r"([0-9]+(?:[.,][0-9]{1,2})?)\s*(?:€|eur|euro)",
    ]
    for pat in euro_patterns:
        m = re.search(pat, lower)
        if m:
            try:
                euro_val = float(m.group(1).replace(",", "."))
                break
            except ValueError:
                pass

    # 2. Estrazione Materia Fisica / Temperatura / Unità (Asse X)
    matter_unit = "1 NOTA OPERATIVA"
    temp_match = re.search(r"([+-]?\d+(?:[.,]\d+)?\s*°\s*c)", lower)
    qty_match = re.search(
        r"([+-]?\d+(?:[.,]\d+)?\s*(?:kg|g|lt|l|pz|pezzi|casse| cartoni|fusti|bottiglie|ombrelloni|lettini|camere|sacchi))",
        lower,
    )
    if temp_match:
        matter_unit = temp_match.group(1).upper().replace(" ", "")
    elif qty_match:
        matter_unit = qty_match.group(1).upper()

    # 3. Classificazione Tag Operativo
    op_tag = "CONSEGNA_TURNO"
    if temp_match or any(w in lower for w in ["haccp", "frigo", "cella", "abbattitore", "temperatura"]):
        op_tag = "HACCP_TEMP"
    elif any(w in lower for w in ["rotto", "guasto", "perdita", "riparare", "manutenzione", "idraulico", "lampadina"]):
        op_tag = "MANUTENZIONE"
    elif any(w in lower for w in ["ordinare", "comprare", "manca", "finito", "spesa", "fornitore", "ddt", "fattura"]) or euro_val > 0:
        op_tag = "SPESA_ORDINE"
    if any(w in lower for w in ["incasso", "venduto", "extra", "pagato da", "camera "]) and euro_val > 0:
        op_tag = "INCASSO_EXTRA"

    # 4. Smistamento automatico sui 13 Conti Semantici [A]-[O]
    best_acc = "[A]" if op_tag == "SPESA_ORDINE" else "[E]" if op_tag == "MANUTENZIONE" else "[B]" if op_tag == "HACCP_TEMP" else "[N]"
    best_score = 0
    for acc_code, meta in SEMANTIC_ACCOUNTS.items():
        score = sum(1 for kw in meta["keywords"] if kw in lower)
        if score > best_score:
            best_score = score
            best_acc = acc_code

    # 5. Canale Finanziario
    channel = default_channel
    if euro_val > 0 and channel.startswith("NESSUNO"):
        if "pos" in lower or "carta" in lower:
            channel = "POS / CARTA"
        elif "camera" in lower and st.session_state.genetic_asset != "STANDALONE":
            channel = "ADDEBITO CAMERA (COMPENSAZIONE)" if st.session_state.genetic_asset == "PARTNER" else "ADDEBITO CAMERA"
        elif "bonifico" in lower or "sdd" in lower:
            channel = "SDD / BONIFICO"
        else:
            channel = "CONTANTI"

    priority = "ALTA" if any(w in lower for w in ["urgente", "subito", "allarme", "rotto", "perdita", "critico"]) else "NORMALE"

    return {
        "clean_text": clean if clean else "Nota operativa acquisita senza testo aggiuntivo.",
        "matter_unit": matter_unit,
        "euro_amount": round(euro_val, 2),
        "channel": channel,
        "semantic_account": best_acc,
        "op_tag": op_tag,
        "department": default_dept,
        "priority": priority,
        "engine_used": "LOCAL-HEURISTIC-RAM",
    }


def gemini_multimodal_wafer_in_ram(
    api_key: str,
    raw_text: str = "",
    media_bytes: bytes = None,
    mime_type: str = "",
    default_dept: str = "BAR & BANCO",
    default_channel: str = "NESSUNO (SOLO NOTA)",
) -> dict:
    """
    Elabora Foto Pizzino (OCR) o Voce (Audio) o Testo direttamente in RAM tramite Gemini REST API.
    Nessun file temporaneo su disco. Rilascio immediato dei buffer volatili.
    """
    if not api_key:
        if media_bytes and not raw_text:
            raise RuntimeError(
                "Chiave API Gemini in RAM necessaria per OCR Foto Pizzino o Trascrizione Vocale. "
                "Inseriscila nel pannello Koenig/AI oppure usa la Nota Lampo testuale (attiva anche 100% offline)."
            )
        return heuristic_wafer_structurer(raw_text, default_dept, default_channel)

    model_name = discover_gemini_model_in_ram(api_key)
    asset_cfg = GENETIC_ASSETS[st.session_state.genetic_asset]
    accounts_legend = "; ".join([f"{k}: {v['name']}" for k, v in SEMANTIC_ACCOUNTS.items()])

    system_prompt = (
        "Sei il motore neurale RAM-Only di BEMASK Sovereign Zero (Data Wafer // Eagle Launch Pad). "
        "Trascrivi fedelmente eventuali foto di pizzini scritti a mano o registrazioni vocali di reparto "
        "in italiano pulito, professionale e sintetico, eliminando rumori o esitazioni. "
        "Struttura l'output ESCLUSIVAMENTE come oggetto JSON puro (senza markdown ```json) con queste chiavi esatte:\n"
        "- clean_text: stringa con il testo operativo pulito e chiaro\n"
        "- matter_unit: stringa sintetica dell'Asse X fisico (es. '+2 KG CAFFÈ', '-5 OMBRELLONI', '+3.8°C FRIGO 1', '1 CONSEGNA')\n"
        "- euro_amount: numero float dell'importo in Euro se presente, altrimenti 0.0\n"
        f"- channel: uno tra {json.dumps(asset_cfg['channels'], ensure_ascii=False)}\n"
        f"- semantic_account: codice esatto tra i 13 conti [{accounts_legend}]\n"
        f"- op_tag: uno tra {json.dumps(OPERATIONAL_TAGS)}\n"
        f"- department: uno tra {json.dumps(asset_cfg['departments'], ensure_ascii=False)}\n"
        "- priority: 'ALTA' oppure 'NORMALE'\n"
        f" Assetto genetico attuale: {asset_cfg['title']} (Se STANDALONE non citare mai camere o hotel)."
    )

    parts = [{"text": system_prompt}]
    if raw_text:
        parts.append({"text": f"Nota testuale operatore (Reparto suggerito: {default_dept}): {raw_text}"})
    if media_bytes and mime_type:
        b64_payload = base64.b64encode(media_bytes).decode("ascii")
        parts.append({"inline_data": {"mime_type": mime_type, "data": b64_payload}})

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.15, "responseMimeType": "application/json"},
    }

    url = f"[https://generativelanguage.googleapis.com/v1beta/models/](https://generativelanguage.googleapis.com/v1beta/models/){model_name}:generateContent?key={api_key}"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            resp_json = json.loads(resp.read().decode("utf-8"))
        cand_text = (
            resp_json.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "{}")
        )
        cand_text = re.sub(r"^```(?:json)?|```$", "", cand_text.strip(), flags=re.MULTILINE).strip()
        parsed = json.loads(cand_text)

        acc = str(parsed.get("semantic_account", "[A]")).strip().upper()
        if not acc.startswith("["):
            acc = f"[{acc[:1]}]"
        if acc not in SEMANTIC_ACCOUNTS:
            acc = "[A]"

        tag = str(parsed.get("op_tag", "CONSEGNA_TURNO")).strip().upper()
        if tag not in OPERATIONAL_TAGS:
            tag = "CONSEGNA_TURNO"

        dept = str(parsed.get("department", default_dept)).strip()
        if dept not in asset_cfg["departments"]:
            dept = default_dept

        chan = str(parsed.get("channel", default_channel)).strip()
        if chan not in asset_cfg["channels"]:
            chan = default_channel

        return {
            "clean_text": str(parsed.get("clean_text", "")).strip() or "Nota acquisita in RAM.",
            "matter_unit": str(parsed.get("matter_unit", "1 UNITA")).strip().upper()[:42],
            "euro_amount": round(float(parsed.get("euro_amount", 0.0) or 0.0), 2),
            "channel": chan,
            "semantic_account": acc,
            "op_tag": tag,
            "department": dept,
            "priority": "ALTA" if str(parsed.get("priority", "")).upper() == "ALTA" else "NORMALE",
            "engine_used": f"GEMINI-RAM ({model_name})",
        }
    except urllib.error.HTTPError as e:
        err_detail = e.read().decode("utf-8", errors="ignore")[:220]
        raise RuntimeError(f"Errore API Gemini ({e.code}): {err_detail}")
    finally:
        # Azzeramento esplicito dei riferimenti ai buffer binari in RAM
        media_bytes = None


def forge_3axis_wafer(structured: dict, source_vector: str) -> dict:
    """Costruisce l'Atomo Dati Universale a 3 Assi (Standard JSON X-Y-Z) e lo cala nell'Hangar RAM."""
    asset_mode = st.session_state.genetic_asset
    euro = float(structured.get("euro_amount", 0.0) or 0.0)
    royalty_pct = float(st.session_state.partner_royalty_pct) if asset_mode == "PARTNER" else 0.0
    cube_fee_eur = round(euro * (royalty_pct / 100.0), 2) if asset_mode == "PARTNER" and euro > 0 else 0.0
    is_room_charge = "CAMERA" in structured.get("channel", "").upper()

    wafer_id = f"WAF-{datetime.now().strftime('%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    atom = {
        "wafer_id": wafer_id,
        "schema": "BEMASK-SOVEREIGN-ZERO-XYZ-v1",
        "architect_seal": ARCHITECT_ID,
        "genetic_asset": asset_mode,
        "status": "DA_EVADERE",
        "ack_at": None,
        "ack_by": None,
        "axis_z": {
            "timestamp_iso": utc_iso_now(),
            "timestamp_human": human_time_now(),
            "pod_code": POD_CODE,
            "pod_repo": POD_REPO,
            "entity_id": st.session_state.entity_id,
            "shift": st.session_state.current_shift,
            "weather_context": st.session_state.current_weather,
            "capture_vector": source_vector,
            "engine": structured.get("engine_used", "LOCAL-RAM"),
        },
        "axis_x": {
            "clean_text": structured["clean_text"],
            "matter_unit": structured["matter_unit"],
            "department": structured["department"],
            "op_tag": structured["op_tag"],
            "priority": structured["priority"],
        },
        "axis_y": {
            "euro_amount": euro,
            "currency": "EUR",
            "channel": structured["channel"],
            "semantic_account": structured["semantic_account"],
            "semantic_account_label": SEMANTIC_ACCOUNTS[structured["semantic_account"]]["name"],
            "partner_royalty_pct": royalty_pct,
            "cube_royalty_fee_eur": cube_fee_eur,
            "room_charge_compensation": is_room_charge,
        },
    }
    st.session_state.wafers_ram.insert(0, atom)
    st.session_state.lift_descending = True
    st.session_state.last_landed_wafer_id = wafer_id
    queue_sound("hydraulic_descent")
    return atom


# ==============================================================================
# 4. AUTO-SCANNER BINARIO MP4 IN RAM & GENERATORE MATRICE OTTICA ZERO-CLOUD
# ==============================================================================
def scan_mp4_binary_in_ram(raw_bytes: bytes, filename: str) -> dict:
    """
    Analizzatore forense ISO-BMFF / MP4 100% in RAM:
    estrae impronta SHA-256, box strutturali (ftyp, moov, mdat, udta, meta) e sigilli BEMASK.
    """
    size_bytes = len(raw_bytes)
    sha256_hex = hashlib.sha256(raw_bytes).hexdigest().upper()
    boxes = []
    offset = 0
    major_brand = "N/D"

    while offset + 8 <= size_bytes and len(boxes) < 40:
        box_size = struct.unpack(">I", raw_bytes[offset:offset + 4])[0]
        box_type_raw = raw_bytes[offset + 4:offset + 8]
        box_type = "".join(chr(b) if 32 <= b <= 126 else "?" for b in box_type_raw)

        header_len = 8
        if box_size == 1 and offset + 16 <= size_bytes:
            box_size = struct.unpack(">Q", raw_bytes[offset + 8:offset + 16])[0]
            header_len = 16
        elif box_size == 0:
            box_size = size_bytes - offset

        if box_type == "ftyp" and offset + header_len + 8 <= size_bytes:
            major_brand = raw_bytes[offset + header_len:offset + header_len + 4].decode("ascii", errors="replace")

        boxes.append({"type": box_type, "offset": offset, "size": box_size})
        if box_size < 8:
            break
        offset += box_size

    # Ricerca pattern d'autore nei metadati binari in RAM
    upper_stream = raw_bytes.upper()
    signatures_found = []
    for marker in [b"BEMASK", b"ENRICO BRAGLIA", b"EB-BEMASK", b"SOVEREIGN ZERO"]:
        if marker in upper_stream:
            signatures_found.append(marker.decode("ascii"))

    return {
        "filename": filename,
        "ram_bytes": size_bytes,
        "ram_mb": round(size_bytes / (1024 * 1024), 3),
        "sha256": sha256_hex,
        "major_brand": major_brand.strip(),
        "top_boxes": boxes,
        "bemask_signatures": signatures_found,
        "scanned_at": human_time_now(),
    }


def generate_optical_matrix_svg(payload_text: str, accent_hex: str = "#F59E0B", size: int = 136) -> str:
    """
    Genera una matrice ottica deterministica SVG Zero-Cloud (0 chiamate esterne)
    con finder patterns standard per verifica visiva/sincronizzazione locale e punzonatura.
    """
    digest = hashlib.sha512(payload_text.encode("utf-8")).digest()
    grid_n = 21
    cell = size / grid_n
    rects = []

    def is_finder(r: int, c: int) -> str:
        for fr, fc in [(0, 0), (0, grid_n - 7), (grid_n - 7, 0)]:
            if fr <= r < fr + 7 and fc <= c < fc + 7:
                lr, lc = r - fr, c - fc
                if lr in (0, 6) or lc in (0, 6) or (2 <= lr <= 4 and 2 <= lc <= 4):
                    return "ON"
                return "OFF"
        return "DATA"

    bit_idx = 0
    for r in range(grid_n):
        for c in range(grid_n):
            f_state = is_finder(r, c)
            active = False
            fill = accent_hex
            if f_state == "ON":
                active = True
            elif f_state == "DATA":
                byte_val = digest[(bit_idx // 8) % len(digest)]
                active = bool((byte_val >> (bit_idx % 8)) & 1)
                bit_idx += 1
                fill = "#E2E8F0" if (r + c) % 3 else accent_hex
            if active:
                rects.append(
                    f'<rect x="{c * cell:.2f}" y="{r * cell:.2f}" width="{cell * 0.92:.2f}" '
                    f'height="{cell * 0.92:.2f}" rx="0.8" fill="{fill}" />'
                )

    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        f'xmlns="[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)" style="background:#0B0E14;padding:6px;'
        f'border:1px solid {accent_hex}55;border-radius:6px;">'
        + "".join(rects)
        + "</svg>"
    )


# ==============================================================================
# 5. ESTETICA DARK LUXURY / MOONBASE ALPHA 1975 & BLOCCO SCROLL ORIZZONTALE
# ==============================================================================
def inject_moonbase_1975_css() -> None:
    css = """
    <style>
    @import url('[https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap](https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap)');

    :root {
        --bg-void: #101319;
        --bg-panel: #161B24;
        --bg-elevated: #1D2432;
        --amber: #F59E0B;
        --emerald: #10B981;
        --cyan: #38BDF8;
        --red-alert: #EF4444;
        --text-hi: #F8FAFC;
        --text-dim: #94A3B8;
        --border-tech: rgba(245, 158, 11, 0.28);
    }

    /* Blocco totale scroll orizzontale mobile & pulizia container */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background-color: var(--bg-void) !important;
        color: var(--text-hi) !important;
        font-family: 'Share Tech Mono', monospace !important;
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    .block-container {
        padding-top: 1.1rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1280px !important;
        overflow-x: hidden !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    h1, h2, h3, .orbitron {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 0.06em !important;
    }

    /* Dock Rapida Superiore */
    .bemask-dock {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        padding: 8px 10px;
        background: linear-gradient(180deg, #171C26 0%, #101319 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 4px solid var(--amber);
        border-radius: 6px;
        margin-bottom: 12px;
        align-items: center;
    }
    .dock-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 8px;
        font-size: 0.73rem;
        border-radius: 4px;
        background: #1B2230;
        color: #CBD5E1 !important;
        text-decoration: none !important;
        border: 1px solid rgba(148, 163, 184, 0.2);
        white-space: nowrap;
        transition: all 0.15s ease;
    }
    .dock-chip:hover {
        border-color: var(--cyan);
        color: var(--cyan) !important;
    }
    .dock-chip.active {
        background: rgba(245, 158, 11, 0.18);
        border: 1px solid var(--amber);
        color: var(--amber) !important;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.22);
    }

    /* Header Moonbase Alpha */
    .alpha-banner {
        background: radial-gradient(circle at 85% 20%, rgba(245,158,11,0.10), transparent 55%),
                    linear-gradient(135deg, #151A24 0%, #0D1017 100%);
        border: 1px solid var(--border-tech);
        border-top: 3px solid var(--amber);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 14px;
    }

    /* Card Wafer Hangar Sotterraneo */
    .wafer-card {
        background: linear-gradient(180deg, #171D28 0%, #121720 100%);
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-left: 4px solid var(--amber);
        border-radius: 6px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .wafer-card.done {
        border-left-color: var(--emerald);
        opacity: 0.86;
    }
    .wafer-card.urgent {
        border-left-color: var(--red-alert);
        box-shadow: inset 0 0 12px rgba(239, 68, 68, 0.08);
    }

    .axis-pill {
        display: inline-block;
        padding: 2px 7px;
        font-size: 0.72rem;
        border-radius: 3px;
        margin-right: 5px;
        margin-bottom: 4px;
        border: 1px solid rgba(255,255,255,0.12);
    }
    .pill-z { background: rgba(56, 189, 248, 0.12); color: #38BDF8; border-color: rgba(56,189,248,0.35); }
    .pill-x { background: rgba(245, 158, 11, 0.13); color: #F59E0B; border-color: rgba(245,158,11,0.38); }
    .pill-y { background: rgba(16, 185, 129, 0.13); color: #10B981; border-color: rgba(16,185,129,0.38); }
    .pill-alert { background: rgba(239, 68, 68, 0.16); color: #EF4444; border-color: rgba(239,68,68,0.45); }

    /* Pulsanti Streamlit Moonbase 1975 */
    .stButton > button, .stDownloadButton > button {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 0.76rem !important;
        letter-spacing: 0.05em !important;
        border-radius: 5px !important;
        border: 1px solid rgba(245, 158, 11, 0.45) !important;
        background: linear-gradient(180deg, #1E2636 0%, #141923 100%) !important;
        color: #F8FAFC !important;
        transition: all 0.16s ease !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: #F59E0B !important;
        color: #F59E0B !important;
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.25) !important;
    }

    /* Animazione Piattaforma Idraulica Eagle Launch Pad */
    @keyframes padDescentPulse {
        0%   { transform: translateY(0px) scale(1.0); opacity: 1; }
        45%  { transform: translateY(10px) scale(0.95); opacity: 0.88; }
        100% { transform: translateY(0px) scale(1.0); opacity: 1; }
    }
    .hydraulic-active {
        animation: padDescentPulse 1.35s ease-in-out 1;
    }

    /* Punzone Metallico d'Autore in Calce */
    .metallic-punch {
        margin-top: 28px;
        padding: 14px 18px;
        background: linear-gradient(135deg, #0D1016 0%, #1A212E 50%, #0D1016 100%);
        border: 1px solid rgba(245, 158, 11, 0.40);
        border-top: 2px solid #F59E0B;
        border-bottom: 2px solid #38BDF8;
        border-radius: 6px;
        text-align: center;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 6px 20px rgba(0,0,0,0.55);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_eagle_launch_pad_svg(descending: bool, total_wafers: int, pending_wafers: int) -> None:
    """Manufatto Space: 1999 - Piattaforma Circolare Eagle Launch Pad & Hydraulic Hangar Lift."""
    ring_color = "#10B981" if descending else "#F59E0B"
    elevation_txt = "ELEVATOR: -18.4m HANGAR LOCK" if descending else "SURFACE PAD: 0.0m READY"
    anim_class = "hydraulic-active" if descending else ""
    status_led = "#EF4444" if pending_wafers > 0 else "#10B981"

    svg_html = f"""
    <div style="background:#0C0F15;border:1px solid rgba(245,158,11,0.30);border-radius:8px;padding:10px;text-align:center;">
        <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">
            <span>MOONBASE ALPHA // PAD-01</span>
            <span style="color:{ring_color};font-weight:bold;">{elevation_txt}</span>
        </div>
        <svg viewBox="0 0 360 210" width="100%" style="max-height:205px;" xmlns="[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)">
            <defs>
                <radialGradient id="hangarGlow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="{ring_color}" stop-opacity="0.24"/>
                    <stop offset="70%" stop-color="#38BDF8" stop-opacity="0.06"/>
                    <stop offset="100%" stop-color="#0C0F15" stop-opacity="0"/>
                </radialGradient>
            </defs>

            <!-- Pozzo Cilindrico Sotterraneo Hangar -->
            <ellipse cx="180" cy="152" rx="124" ry="38" fill="#080A0E" stroke="#38BDF8" stroke-width="1.2" stroke-dasharray="5,4" opacity="0.75"/>
            <line x1="56" y1="88" x2="56" y2="152" stroke="#334155" stroke-width="2"/>
            <line x1="304" y1="88" x2="304" y2="152" stroke="#334155" stroke-width="2"/>

            <!-- 4 Pistoni Idraulici Verticali -->
            <rect x="92"  y="96" width="8" height="62" fill="#1E293B" stroke="{ring_color}" stroke-width="0.9"/>
            <rect x="148" y="108" width="8" height="62" fill="#1E293B" stroke="{ring_color}" stroke-width="0.9"/>
            <rect x="204" y="108" width="8" height="62" fill="#1E293B" stroke="{ring_color}" stroke-width="0.9"/>
            <rect x="260" y="96" width="8" height="62" fill="#1E293B" stroke="{ring_color}" stroke-width="0.9"/>

            <!-- Piattaforma Circolare Mobile Eagle Launch Pad -->
            <g class="{anim_class}">
                <ellipse cx="180" cy="92" rx="128" ry="42" fill="url(#hangarGlow)" stroke="{ring_color}" stroke-width="2.2"/>
                <ellipse cx="180" cy="92" rx="104" ry="33" fill="#131924" stroke="#F59E0B" stroke-width="1.3" stroke-dasharray="10,5"/>
                <ellipse cx="180" cy="92" rx="68" ry="21" fill="#0E131C" stroke="#38BDF8" stroke-width="1.2"/>

                <!-- Croce di Centraggio Aquila -->
                <line x1="72" y1="92" x2="288" y2="92" stroke="#F59E0B" stroke-width="0.9" opacity="0.65"/>
                <line x1="180" y1="54" x2="180" y2="130" stroke="#F59E0B" stroke-width="0.9" opacity="0.65"/>

                <!-- Nucleo Centrale Wafer -->
                <ellipse cx="180" cy="92" rx="26" ry="9" fill="{ring_color}" fill-opacity="0.22" stroke="{ring_color}" stroke-width="1.5"/>
                <text x="180" y="95" fill="#F8FAFC" font-size="9" font-family="Orbitron, monospace" text-anchor="middle" font-weight="bold">EAGLE-DW</text>
            </g>

            <!-- Telemetria Base Hangar RAM -->
            <circle cx="28" cy="192" r="5" fill="{status_led}"/>
            <text x="40" y="196" fill="#CBD5E1" font-size="10" font-family="Share Tech Mono, monospace">
                HANGAR RAM: {total_wafers} WAFER // DA EVADERE: {pending_wafers}
            </text>
            <text x="342" y="196" fill="#38BDF8" font-size="9.5" font-family="Share Tech Mono, monospace" text-anchor="end">
                ZERO-CLOUD 0 BYTE
            </text>
        </svg>
    </div>
    """
    st.markdown(svg_html, unsafe_allow_html=True)
    if st.session_state.lift_descending:
        st.session_state.lift_descending = False


# ==============================================================================
# 6. DOCK RAPIDA SUPERIORE, KOENIG SECURITY GATE & DOSSIER ARCHITETTO
# ==============================================================================
def render_top_quick_dock() -> None:
    allowed = LICENSE_CTX["allowed_codes"]
    base_hub = LICENSE_CTX["base_url"].rstrip("/")
    chips_html = []

    for sec in SECTOR_MATRIX:
        code = sec["code"]
        if allowed is not None and code not in allowed:
            continue
        is_current = code == "DW"
        cls = "dock-chip active" if is_current else "dock-chip"
        if is_current:
            href = "#"
        elif base_hub:
            href = f"{base_hub}/{sec['repo']}"
        else:
            href = f"?pod={sec['repo']}" + (f"&mask={LICENSE_CTX['raw_mask']}" if LICENSE_CTX["raw_mask"] else "")
        chips_html.append(
            f'<a class="{cls}" href="{html.escape(href)}" title="Settore {code}: {html.escape(sec["label"])}">'
            f'<span>{sec["icon"]}</span><span>{code}·{html.escape(sec["label"])}</span></a>'
        )

    lic_badge = (
        f'<span style="margin-left:auto;font-size:0.70rem;color:#10B981;border:1px solid #10B98155;'
        f'padding:2px 7px;border-radius:4px;">LICENZA FILTRATA (?mask={html.escape(LICENSE_CTX["raw_mask"])})</span>'
        if LICENSE_CTX["licensed"]
        else '<span style="margin-left:auto;font-size:0.70rem;color:#38BDF8;">MATRICE 2^12 COMPLETA</span>'
    )

    st.markdown(
        f'<div class="bemask-dock">{"".join(chips_html)}{lic_badge}</div>',
        unsafe_allow_html=True,
    )


def render_architect_dossier_body() -> None:
    st.markdown(
        f"""
        <div style="background:#121722;border:1px solid #F59E0B88;border-left:5px solid #F59E0B;padding:14px;border-radius:6px;margin-bottom:12px;">
            <div class="orbitron" style="color:#F59E0B;font-size:1.05rem;font-weight:700;">
                ◈ ARCHITECT & CREATOR: {ARCHITECT_NAME}
            </div>
            <div style="color:#38BDF8;font-size:0.82rem;margin-top:3px;">
                SIGILLO ID: <b>{ARCHITECT_ID}</b> // ECOSISTEMA: BEMASK SOVEREIGN ZERO
            </div>
            <p style="color:#CBD5E1;font-size:0.84rem;margin-top:8px;margin-bottom:0;">
                30+ anni in Direzione Alberghiera, Revenue Management, TRevPAR Optimization, F&B Direction, Media & AI Lab.<br/>
                Architettura frattale 3x3x3 basata sulla meccanica del Cubo di Rubik: dal singolo esercizio autonomo fino al Mega-Resort integrato e Holding multi-societaria, governata dal principio non negoziabile di <b>Sovranità Assoluta Zero-Trust RAM-Only</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_qr, col_manifesto = st.columns([1, 2.2])
    with col_qr:
        qr_payload = (
            f"BEMASK_ARCHITECT|{ARCHITECT_NAME}|ID:{ARCHITECT_ID}|"
            f"ORG:bemask-sovereign-zero|POD:{POD_REPO}|ZERO_TRUST_RAM"
        )
        st.markdown(
            "<div style='text-align:center;'>"
            + generate_optical_matrix_svg(qr_payload, "#F59E0B", 148)
            + "<div style='font-size:0.72rem;color:#94A3B8;margin-top:6px;'>MATRICE IDENTITÀ OTTICA<br/>(Zero-Cloud Offline Seal)</div></div>",
            unsafe_allow_html=True,
        )
    with col_manifesto:
        st.markdown("**MANIFESTO TECNICO COSTITUZIONALE**")
        st.code(
            f"ARCHITECT_ID : {ARCHITECT_ID}\n"
            f"CREATOR      : {ARCHITECT_NAME}\n"
            f"CENTRAL_HUB  : alpha-main-mission (27° Cubo Invisibile)\n"
            f"ACTIVE_POD   : {POD_REPO} ({POD_CODE})\n"
            f"DATA_ATOM    : 3-Axis Universal JSON [Z:Time/Ctx | X:Matter | Y:EUR A-O]\n"
            f"SOVEREIGNTY  : 0 Bytes Cloud Persistence // Volatile RAM Execution",
            language="yaml",
        )

    st.markdown("---")
    st.markdown("#### 🎞️ AUTO-SCANNER BINARIO MP4 IN RAM (FORENSIC BRAND VERIFIER)")
    st.caption(
        "Ispeziona in memoria volatile la struttura atomica ISO-BMFF (`ftyp`, `moov`, `mdat`, `meta`), "
        "calcola l'impronta crittografica SHA-256 e rileva il punzone binario BEMASK senza salvare alcun file su disco."
    )
    mp4_file = st.file_uploader(
        "Carica file video .MP4 / .MOV per scansione binaria istantanea in RAM",
        type=["mp4", "mov", "m4v"],
        key="architect_mp4_scanner",
    )
    if mp4_file is not None:
        raw_video = mp4_file.getvalue()
        report = scan_mp4_binary_in_ram(raw_video, mp4_file.name)
        raw_video = None  # Rilascio immediato buffer RAM
        c1, c2, c3 = st.columns(3)
        c1.metric("Dimensione in RAM", f"{report['ram_mb']} MB")
        c2.metric("Major Brand ISO", report["major_brand"])
        c3.metric("Punzone BEMASK", "RILEVATO ✓" if report["bemask_signatures"] else "ESTERNO / RAW")
        st.code(
            f"FILE     : {report['filename']}\n"
            f"SHA-256  : {report['sha256']}\n"
            f"SIGNATURES: {', '.join(report['bemask_signatures']) if report['bemask_signatures'] else 'Nessun marker ASCII BEMASK incorporato'}\n"
            f"ISO BOXES : " + " -> ".join([f"[{b['type']}:{b['size']}B]" for b in report["top_boxes"][:10]]),
            language="text",
        )


if hasattr(st, "dialog"):
    @st.dialog("◈ ARCHITECT DOSSIER // ENRICO BRAGLIA")
    def open_architect_modal():
        render_architect_dossier_body()
else:
    open_architect_modal = None


def render_koenig_security_and_genetics() -> None:
    """Pannello Koenig Security Gate (PIN + 2FA RFC 6238 + Log Antintrusione) + Selettore Genetico + Gemini Key RAM."""
    with st.container():
        st.markdown(
            "<div style='background:#141923;border:1px solid #38BDF855;border-radius:6px;padding:12px;margin-bottom:14px;'>"
            "<span class='orbitron' style='color:#38BDF8;font-size:0.9rem;'>🛡️ KOENIG SECURITY GATE & CONFIGURAZIONE GENETICA POD</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        k_col1, k_col2, k_col3 = st.columns([1.2, 1.2, 1.3])

        # --- Colonna 1: Autenticazione Ruolo Staff vs Commander ---
        with k_col1:
            st.markdown("**1. RUOLO & FILTRO ANTI-TALPA**")
            st.caption(
                f"Stato attuale: **{'COMMANDER (Sbloccato)' if st.session_state.role == 'COMMANDER' else 'STAFF (Valori sensibili Y oscurati)'}**"
            )
            if st.session_state.role != "COMMANDER":
                pin_in = st.text_input("PIN Commander", type="password", placeholder="Default demo: 1975", key="k_pin_in")
                totp_in = ""
                if st.session_state.require_totp:
                    totp_in = st.text_input("Codice 2FA Google Auth (6 cifre)", max_chars=6, key="k_totp_in")
                if st.button("🔓 SBLOCCA COMMANDER", use_container_width=True):
                    pin_ok = hmac.compare_digest(pin_in or "", st.session_state.commander_pin)
                    totp_ok = verify_totp_rfc6238(st.session_state.totp_secret, totp_in) if st.session_state.require_totp else True
                    if pin_ok and totp_ok:
                        st.session_state.role = "COMMANDER"
                        queue_sound("telemetry_ack")
                        safe_rerun()
                    else:
                        st.session_state.intrusion_log.insert(
                            0,
                            {
                                "ts": human_time_now(),
                                "event": "TENTATIVO ACCESSO FALLITO",
                                "detail": "PIN errato" if not pin_ok else "2FA RFC 6238 non valida",
                            },
                        )
                        queue_sound("koenig_alarm")
                        st.error("Accesso respinto da Koenig Gate. Evento registrato in RAM.")
            else:
                if st.button("🔒 TORNA A RUOLO STAFF (ANTI-TALPA)", use_container_width=True):
                    st.session_state.role = "STAFF"
                    safe_rerun()
                st.session_state.require_totp = st.checkbox(
                    "Richiedi 2FA RFC 6238 (Google Auth) oltre al PIN",
                    value=st.session_state.require_totp,
                )
                new_pin = st.text_input("Aggiorna PIN in RAM", value=st.session_state.commander_pin, type="password")
                if new_pin and new_pin != st.session_state.commander_pin:
                    st.session_state.commander_pin = new_pin
                otpauth_uri = (
                    f"otpauth://totp/BEMASK_DataWafer:{st.session_state.entity_id}"
                    f"?secret={st.session_state.totp_secret}&issuer=BEMASK_Sovereign_Zero"
                )
                st.caption(f"Segreto Base32 2FA: `{st.session_state.totp_secret}`")
                st.caption(f"Token RFC 6238 attivo (verifica): `{generate_totp_rfc6238(st.session_state.totp_secret)}`")
                with st.expander("URI Provisioning Google Authenticator"):
                    st.code(otpauth_uri, language="text")

        # --- Colonna 2: Selettore Genetico a 3 Assetti (Nascosto se licenza URL bloccata e non Commander) ---
        with k_col2:
            st.markdown("**2. SELETTORE GENETICO A 3 ASSETTI**")
            if LICENSE_CTX["licensed"] and st.session_state.role != "COMMANDER":
                st.info(
                    f"Assetto vincolato da Licenza URL:\n**{GENETIC_ASSETS[st.session_state.genetic_asset]['title']}**"
                )
            else:
                asset_keys = list(GENETIC_ASSETS.keys())
                sel_asset = st.radio(
                    "Modalità operativa del Micro-Pod",
                    options=asset_keys,
                    index=asset_keys.index(st.session_state.genetic_asset),
                    format_func=lambda k: GENETIC_ASSETS[k]["title"],
                )
                if sel_asset != st.session_state.genetic_asset:
                    st.session_state.genetic_asset = sel_asset
                    safe_rerun()

                st.session_state.entity_id = st.text_input(
                    "Codice Societario / Entity ID (P.IVA)",
                    value=st.session_state.entity_id,
                )
                if st.session_state.genetic_asset == "PARTNER":
                    st.session_state.partner_royalty_pct = st.number_input(
                        "Fee / Royalty verso Cubo Madre (%)",
                        min_value=0.0,
                        max_value=60.0,
                        value=float(st.session_state.partner_royalty_pct),
                        step=0.5,
                    )

        # --- Colonna 3: Motore Gemini OCR/Voce in RAM & Log Antintrusione ---
        with k_col3:
            st.markdown("**3. MOTORE AI GEMINI IN RAM & TELEMETRIA**")
            api_in = st.text_input(
                "Gemini API Key (Volatile in RAM - OCR Foto & Audio)",
                value=st.session_state.gemini_api_key,
                type="password",
                placeholder="AIza... (Opzionale per testo, richiesta per Foto/Voce)",
            )
            if api_in != st.session_state.gemini_api_key:
                st.session_state.gemini_api_key = api_in.strip()
                st.session_state.gemini_discovered_model = ""
                if st.session_state.gemini_api_key:
                    discover_gemini_model_in_ram(st.session_state.gemini_api_key)

            if st.session_state.gemini_api_key:
                mod = discover_gemini_model_in_ram(st.session_state.gemini_api_key)
                st.success(f"Autodiscovery Gemini attiva: `{mod}`")
            else:
                st.caption("Modalità Offline Euristica attiva per Note Testuali. Inserisci API Key per Foto OCR e Voce.")

            if st.session_state.intrusion_log:
                st.markdown(f"**⚠️ LOG ANTINTRUSIONE ({len(st.session_state.intrusion_log)})**")
                for entry in st.session_state.intrusion_log[:3]:
                    st.caption(f"🔴 `{entry['ts']}` — {entry['detail']}")


# ==============================================================================
# 7. GENERAZIONE EXPORT LOCALI (.JSON A 3 ASSI, .TXT CONSEGNA, .HTML DOSSIER)
# ==============================================================================
def export_wafers_json() -> str:
    payload = {
        "protocol": "BEMASK_SOVEREIGN_ZERO_DATA_WAFER",
        "architect": ARCHITECT_NAME,
        "architect_id": ARCHITECT_ID,
        "exported_at": utc_iso_now(),
        "entity_id": st.session_state.entity_id,
        "genetic_asset": st.session_state.genetic_asset,
        "total_wafers": len(st.session_state.wafers_ram),
        "wafers": st.session_state.wafers_ram,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def export_wafers_txt(is_commander: bool) -> str:
    lines = [
        "========================================================================",
        f"BEMASK DATA WAFER // EAGLE LAUNCH PAD & HANGAR LIFT ({POD_CODE})",
        f"ARCHITECT: {ARCHITECT_NAME} // ID: {ARCHITECT_ID}",
        f"ENTITY: {st.session_state.entity_id} | ASSETTO: {GENETIC_ASSETS[st.session_state.genetic_asset]['title']}",
        f"EXPORT: {human_time_now()} | TOTALE WAFER: {len(st.session_state.wafers_ram)}",
        "========================================================================",
        "",
    ]
    for w in st.session_state.wafers_ram:
        z, x, y = w["axis_z"], w["axis_x"], w["axis_y"]
        acc_code = y["semantic_account"]
        hide_y = (not is_commander) and (SEMANTIC_ACCOUNTS.get(acc_code, {}).get("sensitive", False) or y["euro_amount"] > 0)
        y_str = (
            "[RISERVATO COMMANDER]"
            if hide_y
            else f"EUR {y['euro_amount']:.2f} | {y['channel']} | {acc_code} {y['semantic_account_label']}"
        )
        status_flag = f"EVASO ({w['ack_at']})" if w["status"] == "EVASO" else "DA EVADERE"
        lines.append(f"[{w['wafer_id']}] {z['timestamp_human']} | {z['shift']} | STATO: {status_flag}")
        lines.append(f"  ASSE X (MATERIA) : [{x['department']}] [{x['op_tag']}] ({x['matter_unit']}) -> {x['clean_text']}")
        lines.append(f"  ASSE Y (ENERGIA) : {y_str}")
        lines.append("-" * 72)
    return "\n".join(lines)


def export_wafers_html(is_commander: bool) -> str:
    rows = []
    for w in st.session_state.wafers_ram:
        z, x, y = w["axis_z"], w["axis_x"], w["axis_y"]
        acc_code = y["semantic_account"]
        hide_y = (not is_commander) and (SEMANTIC_ACCOUNTS.get(acc_code, {}).get("sensitive", False) or y["euro_amount"] > 0)
        y_cell = "RISERVATO COMMANDER" if hide_y else f"€ {y['euro_amount']:.2f} • {html.escape(y['channel'])} • {html.escape(acc_code)}"
        rows.append(
            f"<tr>"
            f"<td>{html.escape(w['wafer_id'])}<br/><small>{html.escape(z['timestamp_human'])}</small></td>"
            f"<td>{html.escape(x['department'])}<br/><b>{html.escape(x['op_tag'])}</b></td>"
            f"<td><b>[{html.escape(x['matter_unit'])}]</b> {html.escape(x['clean_text'])}</td>"
            f"<td>{y_cell}</td>"
            f"<td>{html.escape(w['status'])}</td>"
            f"</tr>"
        )
    return f"""<!DOCTYPE html>
<html lang="it"><head><meta charset="utf-8"/>
<title>BEMASK DATA WAFER REPORT - {html.escape(st.session_state.entity_id)}</title>
<style>
body {{ background:#101319; color:#F8FAFC; font-family:monospace; padding:24px; }}
h1 {{ color:#F59E0B; border-bottom:2px solid #F59E0B; padding-bottom:8px; }}
table {{ width:100%; border-collapse:collapse; margin-top:16px; }}
th, td {{ border:1px solid #334155; padding:8px 10px; text-align:left; font-size:13px; }}
th {{ background:#1D2432; color:#38BDF8; }}
.footer {{ margin-top:24px; padding:12px; border:1px solid #F59E0B; text-align:center; color:#94A3B8; font-size:12px; }}
</style></head><body>
<h1>◈ BEMASK DATA WAFER // HANGAR RAM REPORT</h1>
<p>Entity: <b>{html.escape(st.session_state.entity_id)}</b> | Assetto: <b>{html.escape(GENETIC_ASSETS[st.session_state.genetic_asset]['title'])}</b> | Data: {human_time_now()}</p>
<table><thead><tr><th>Wafer / Asse Z</th><th>Reparto / Tag</th><th>Asse X (Materia & Testo Pulito)</th><th>Asse Y (Energia & Conto)</th><th>Stato</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<div class="footer">◈ ARCHITECT & CREATOR: {ARCHITECT_NAME} // ID: {ARCHITECT_ID} // SOVEREIGN ZERO RAM-ONLY</div>
</body></html>"""


# ==============================================================================
# 8. INTERFACCIA OPERATIVA PRINCIPALE SU 2 LIVELLI (SUPERFICIE + HANGAR RAM)
# ==============================================================================
inject_moonbase_1975_css()
render_ems_1975_synth()

# --- Barra Dock Rapida Multi-Modulo ---
render_top_quick_dock()

# --- Testata Comando Eagle Launch Pad ---
asset_info = GENETIC_ASSETS[st.session_state.genetic_asset]
hdr_left, hdr_right = st.columns([2.6, 1.4])

with hdr_left:
    st.markdown(
        f"""
        <div class="alpha-banner">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                <span class="orbitron" style="color:#F59E0B;font-size:1.18rem;font-weight:900;">
                    ◎ BEMASK DATA WAFER // EAGLE LAUNCH PAD
                </span>
                <span style="font-size:0.74rem;padding:3px 8px;border-radius:4px;background:rgba(16,185,129,0.14);color:#10B981;border:1px solid #10B98155;">
                    {html.escape(asset_info['badge'])}
                </span>
            </div>
            <div style="color:#94A3B8;font-size:0.80rem;margin-top:5px;">
                Piattaforma Anti-Pizzini Volanti • Foto OCR + Voce + Nota Lampo → Discesa Idraulica Hangar RAM a 3 Assi (Zero Cloud • Zero Distrazioni)
            </div>
            <div style="margin-top:7px;font-size:0.74rem;color:#38BDF8;">
                ENTITY: <b>{html.escape(st.session_state.entity_id)}</b>  | 
                RUOLO: <b style="color:{'#10B981' if st.session_state.role == 'COMMANDER' else '#F59E0B'};">{st.session_state.role}</b>  | 
                SOVRANITÀ: <b>0 BYTE CLOUD</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hdr_right:
    b_col1, b_col2, b_col3 = st.columns([1.15, 1.15, 0.7])
    with b_col1:
        if st.button("🛡️ KOENIG / ASSET", use_container_width=True):
            st.session_state.show_koenig_panel = not st.session_state.show_koenig_panel
            safe_rerun()
    with b_col2:
        if st.button("◈ ARCHITECT", use_container_width=True):
            if open_architect_modal is not None:
                open_architect_modal()
            else:
                st.session_state.show_architect_dossier = not st.session_state.show_architect_dossier
    with b_col3:
        sound_lbl = "🔊 EMS" if st.session_state.audio_synth_enabled else "🔇 OFF"
        if st.button(sound_lbl, use_container_width=True, help="Attiva/Disattiva Synth WebAudio EMS-1975"):
            st.session_state.audio_synth_enabled = not st.session_state.audio_synth_enabled
            if st.session_state.audio_synth_enabled:
                queue_sound("telemetry_ack")
            safe_rerun()

if st.session_state.show_koenig_panel:
    render_koenig_security_and_genetics()

if open_architect_modal is None and st.session_state.show_architect_dossier:
    with st.expander("◈ ARCHITECT DOSSIER // ENRICO BRAGLIA", expanded=True):
        render_architect_dossier_body()

# ==============================================================================
# LIVELLO 1: SUPERFICIE — ATTERRAGGIO RAPIDO SULL'EAGLE LAUNCH PAD (1-3 SECONDI)
# ==============================================================================
pending_count = sum(1 for w in st.session_state.wafers_ram if w["status"] != "EVASO")
surf_left, surf_right = st.columns([1.25, 1.95])

with surf_left:
    render_eagle_launch_pad_svg(
        descending=bool(st.session_state.last_landed_wafer_id),
        total_wafers=len(st.session_state.wafers_ram),
        pending_wafers=pending_count,
    )
    # Selettori rapidi Asse Z (Turno, Contesto, Reparto Predefinito)
    z_c1, z_c2 = st.columns(2)
    with z_c1:
        st.session_state.current_shift = st.selectbox(
            "Turno Attivo (Asse Z)",
            options=["MATTINA", "POMERIGGIO", "SERA / NOTTE", "CHIUSURA"],
            index=["MATTINA", "POMERIGGIO", "SERA / NOTTE", "CHIUSURA"].index(st.session_state.current_shift)
            if st.session_state.current_shift in ["MATTINA", "POMERIGGIO", "SERA / NOTTE", "CHIUSURA"]
            else 0,
        )
    with z_c2:
        st.session_state.current_weather = st.selectbox(
            "Contesto / Flusso",
            options=[
                "SERENO // FLUSSO REGOLARE",
                "PICCO ALTA AFFLUENZA",
                "METEO INSTABILE / VENTO",
                "EVENTO / GALA SPECIALE",
            ],
        )

    active_dept = st.selectbox(
        "Reparto Operativo di Atterraggio",
        options=asset_info["departments"],
        key="surface_dept_selector",
    )

with surf_right:
    st.markdown(
        "<div class='orbitron' style='color:#F59E0B;font-size:0.92rem;margin-bottom:6px;'>"
        "▲ LIVELLO SUPERFICIE // ATTERRAGGIO RAPIDO ANTI-PIZZINO"
        "</div>",
        unsafe_allow_html=True,
    )

    tab_photo, tab_voice, tab_flash = st.tabs([
        "📷 1) FOTO PIZZINO (OCR RAM)",
        "🎙️ 2) DETTATURA VOCALE (RAM)",
        "⚡ 3) NOTA LAMPO 3-ASSI",
    ])

    # --- VETTORE 1: FOTO AL FOGLIETTO SCRITTO A MANO -> OCR AI IN RAM ---
    with tab_photo:
        st.caption(
            "Inquadra il foglietto volante scritto a mano o carica uno scatto rapido: "
            "Gemini converte la grafia in RAM e cala l'atomo pulito nell'Hangar."
        )
        cam_mode = st.toggle("Attiva Fotocamera Diretta Smartphone/PC", value=False, key="toggle_cam_pad")
        img_source = None
        if cam_mode:
            img_source = st.camera_input("Scatta Foto al Pizzino", key="pad_camera_shot")
        uploaded_img = st.file_uploader(
            "Oppure seleziona foto rapida dalla galleria",
            type=["jpg", "jpeg", "png", "webp"],
            key="pad_photo_upload",
        )
        effective_img = img_source or uploaded_img
        photo_hint = st.text_input(
            "Nota integrativa opzionale (es. pagato cassa 2 / urgente)",
            key="photo_extra_hint",
        )
        if st.button("⬇ SCENDI NELL'HANGAR RAM (OCR FOTO)", use_container_width=True, key="btn_land_photo"):
            if effective_img is None:
                st.warning("Acquisisci o seleziona prima la foto del pizzino.")
            else:
                try:
                    with st.spinner("Scansione ottica pizzino in RAM e discesa idraulica..."):
                        img_bytes = effective_img.getvalue()
                        mime = effective_img.type or "image/jpeg"
                        structured = gemini_multimodal_wafer_in_ram(
                            api_key=st.session_state.gemini_api_key,
                            raw_text=photo_hint,
                            media_bytes=img_bytes,
                            mime_type=mime,
                            default_dept=active_dept,
                            default_channel=asset_info["channels"][0],
                        )
                        img_bytes = None
                        atom = forge_3axis_wafer(structured, "FOTO_OCR_RAM")
                    st.success(f"Wafer `{atom['wafer_id']}` calato nell'Hangar RAM!")
                    safe_rerun()
                except Exception as exc:
                    queue_sound("koenig_alarm")
                    st.error(str(exc))

    # --- VETTORE 2: DETTATURA VOCALE RAPIDA -> TRASCRIZIONE AI IN RAM ---
    with tab_voice:
        st.caption(
            "Detta a voce la consegna, l'ordine fornitore o l'anomalia tecnica in 3 secondi: "
            "trascrizione neurale in RAM e classificazione automatica [A]-[O]."
        )
        voice_clip = None
        if hasattr(st, "audio_input"):
            voice_clip = st.audio_input("Premi il microfono e detta il Wafer vocale", key="pad_voice_input")
        else:
            voice_clip = st.file_uploader(
                "Carica nota vocale rapida (.wav, .mp3, .m4a, .ogg)",
                type=["wav", "mp3", "m4a", "ogg", "webm"],
                key="pad_voice_fallback",
            )
        voice_hint = st.text_input("Contesto extra opzionale", key="voice_extra_hint")
        if st.button("⬇ SCENDI NELL'HANGAR RAM (TRASCRIZIONE VOCE)", use_container_width=True, key="btn_land_voice"):
            if voice_clip is None:
                st.warning("Registra prima una breve nota vocale sul Launch Pad.")
            else:
                try:
                    with st.spinner("Trascrizione vocale in RAM e smistamento [A]-[O]..."):
                        aud_bytes = voice_clip.getvalue()
                        aud_mime = getattr(voice_clip, "type", "") or "audio/wav"
                        structured = gemini_multimodal_wafer_in_ram(
                            api_key=st.session_state.gemini_api_key,
                            raw_text=voice_hint,
                            media_bytes=aud_bytes,
                            mime_type=aud_mime,
                            default_dept=active_dept,
                            default_channel=asset_info["channels"][0],
                        )
                        aud_bytes = None
                        atom = forge_3axis_wafer(structured, "VOCE_AUDIO_RAM")
                    st.success(f"Wafer vocale `{atom['wafer_id']}` trascritto e archiviato nell'Hangar RAM!")
                    safe_rerun()
                except Exception as exc:
                    queue_sound("koenig_alarm")
                    st.error(str(exc))

    # --- VETTORE 3: NOTA LAMPO TESTUALE (ATTIVA ANCHE 100% OFFLINE) ---
    with tab_flash:
        st.caption(
            "Scrittura lampo in 1 gesto: riconosce automaticamente quantità, temperature °C, Euro e conto [A]-[O] "
            "(100% operativa anche offline senza API key)."
        )
        flash_text = st.text_area(
            "Testo lampo (es. 'Aperti +2 kg caffè miscela oro, frigo latte +3.6°C' oppure 'Pagato idraulico € 85 contanti perdita lavabo')",
            height=82,
            key="pad_flash_text",
        )
        ov_c1, ov_c2, ov_c3 = st.columns(3)
        with ov_c1:
            manual_eur = st.number_input("Forza Euro € (Opz.)", min_value=0.0, value=0.0, step=1.0, key="flash_eur")
        with ov_c2:
            manual_chan = st.selectbox("Canale Y", options=asset_info["channels"], key="flash_chan")
        with ov_c3:
            acc_opts = ["AUTO [A]-[O]"] + [f"{k} {v['name'][:20]}" for k, v in SEMANTIC_ACCOUNTS.items()]
            manual_acc = st.selectbox("Conto Semantico", options=acc_opts, key="flash_acc")

        if st.button("⬇ CALA WAFER LAMPO NELL'HANGAR RAM", use_container_width=True, key="btn_land_flash"):
            if not (flash_text or "").strip() and manual_eur <= 0:
                st.warning("Inserisci il testo della nota lampo o un valore operativo.")
            else:
                try:
                    with st.spinner("Discesa idraulica nell'Hangar RAM..."):
                        if st.session_state.gemini_api_key:
                            structured = gemini_multimodal_wafer_in_ram(
                                api_key=st.session_state.gemini_api_key,
                                raw_text=flash_text,
                                default_dept=active_dept,
                                default_channel=manual_chan,
                            )
                        else:
                            structured = heuristic_wafer_structurer(flash_text, active_dept, manual_chan)

                        if manual_eur > 0:
                            structured["euro_amount"] = round(float(manual_eur), 2)
                        if manual_chan != asset_info["channels"][0]:
                            structured["channel"] = manual_chan
                        if not manual_acc.startswith("AUTO"):
                            structured["semantic_account"] = manual_acc.split(" ")[0]

                        atom = forge_3axis_wafer(structured, "NOTA_LAMPO_RAM")
                    st.success(f"Wafer `{atom['wafer_id']}` agganciato nell'Hangar Sotterraneo!")
                    safe_rerun()
                except Exception as exc:
                    queue_sound("koenig_alarm")
                    st.error(str(exc))


# ==============================================================================
# LIVELLO 2: HANGAR SOTTERRANEO RAM — SMISTAMENTO, SPUNTA & EXPORT ZERO-CLOUD
# ==============================================================================
st.markdown("---")
st.markdown(
    "<div class='orbitron' style='color:#38BDF8;font-size:1.0rem;margin-bottom:8px;'>"
    "▼ LIVELLO INFERIORE // HYDRAULIC HANGAR RAM (ATOMI STRUTTURATI X-Y-Z)"
    "</div>",
    unsafe_allow_html=True,
)

is_commander = st.session_state.role == "COMMANDER"
all_wafers = st.session_state.wafers_ram

# --- Striscia Telemetria Hangar (con rispetto Filtro Anti-Talpa Staff vs Commander) ---
total_euro_ram = sum(w["axis_y"]["euro_amount"] for w in all_wafers)
total_royalty_ram = sum(w["axis_y"]["cube_royalty_fee_eur"] for w in all_wafers)
total_room_comp = sum(
    w["axis_y"]["euro_amount"] for w in all_wafers if w["axis_y"].get("room_charge_compensation")
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Wafer Totali in RAM", len(all_wafers))
kpi2.metric("Da Prendere in Carico", pending_count)
kpi3.metric("Energia Finanziaria Y", f"€ {total_euro_ram:,.2f}" if is_commander else "🔒 PROTETTO (STAFF)")
if st.session_state.genetic_asset == "PARTNER":
    kpi4.metric(
        "Compensazione Camera / Fee Cubo",
        f"€ {total_room_comp:,.2f} / -€ {total_royalty_ram:,.2f}" if is_commander else "🔒 PROTETTO (STAFF)",
    )
elif st.session_state.genetic_asset == "CUBE_DEPT":
    kpi4.metric("Sync Alpha-Main-Mission", "PRONTO (.JSON X-Y-Z)")
else:
    evasi_cnt = len(all_wafers) - pending_count
    kpi4.metric("Wafer Evasi nel Turno", evasi_cnt)

# --- Barra Filtri Rapidi Hangar ---
f_c1, f_c2, f_c3, f_c4, f_c5 = st.columns([1.1, 1.1, 1.1, 1.0, 1.3])
with f_c1:
    flt_status = st.selectbox("Stato Spunta", ["TUTTI", "DA_EVADERE", "EVASO"])
with f_c2:
    flt_dept = st.selectbox("Filtra Reparto", ["TUTTI"] + asset_info["departments"])
with f_c3:
    flt_tag = st.selectbox("Filtra Tag", ["TUTTI"] + OPERATIONAL_TAGS)
with f_c4:
    flt_acc = st.selectbox("Filtra Conto [A]-[O]", ["TUTTI"] + list(SEMANTIC_ACCOUNTS.keys()))
with f_c5:
    flt_query = st.text_input("Ricerca Testo / Wafer ID", placeholder="Cerca nell'Hangar RAM...")

filtered_wafers = []
for w in all_wafers:
    if flt_status != "TUTTI" and w["status"] != flt_status:
        continue
    if flt_dept != "TUTTI" and w["axis_x"]["department"] != flt_dept:
        continue
    if flt_tag != "TUTTI" and w["axis_x"]["op_tag"] != flt_tag:
        continue
    if flt_acc != "TUTTI" and w["axis_y"]["semantic_account"] != flt_acc:
        continue
    if flt_query:
        q = flt_query.lower()
        haystack = f"{w['wafer_id']} {w['axis_x']['clean_text']} {w['axis_x']['matter_unit']} {w['axis_x']['department']}".lower()
        if q not in haystack:
            continue
    filtered_wafers.append(w)

# --- Lista Operativa dei Wafer nell'Hangar ---
if not filtered_wafers:
    st.markdown(
        "<div style='background:#131822;border:1px dashed #334155;border-radius:6px;padding:22px;text-align:center;color:#94A3B8;'>"
        "HANGAR SOTTERRANEO VUOTO O NESSUN WAFER CORRISPONDENTE AI FILTRI.<br/>"
        "<small>Atterra una Foto Pizzino, una Nota Vocale o una Nota Lampo sulla piattaforma superiore per attivare l'elevatore idraulico.</small>"
        "</div>",
        unsafe_allow_html=True,
    )
else:
    for idx, w in enumerate(filtered_wafers):
        wid = w["wafer_id"]
        z, x, y = w["axis_z"], w["axis_x"], w["axis_y"]
        is_done = w["status"] == "EVASO"
        is_urgent = x.get("priority") == "ALTA" and not is_done
        card_cls = "wafer-card done" if is_done else ("wafer-card urgent" if is_urgent else "wafer-card")

        acc_code = y["semantic_account"]
        acc_sensitive = SEMANTIC_ACCOUNTS.get(acc_code, {}).get("sensitive", False)
        mask_financial = (not is_commander) and (acc_sensitive or y["euro_amount"] > 0)

        if mask_financial:
            y_badge_html = '<span class="axis-pill pill-y">ASSE Y: 🔒 PROTETTO ANTI-TALPA</span>'
        else:
            royalty_note = (
                f" • Fee Cubo: €{y['cube_royalty_fee_eur']:.2f}"
                if w.get("genetic_asset") == "PARTNER" and y["cube_royalty_fee_eur"] > 0
                else ""
            )
            y_badge_html = (
                f'<span class="axis-pill pill-y">ASSE Y: € {y["euro_amount"]:.2f} | '
                f'{html.escape(y["channel"])} | {html.escape(acc_code)} {html.escape(y["semantic_account_label"])}{royalty_note}</span>'
            )

        urgent_html = '<span class="axis-pill pill-alert">⚡ PRIORITÀ ALTA</span>' if is_urgent else ""
        ack_html = (
            f"<div style='font-size:0.73rem;color:#10B981;margin-top:4px;'>✓ PRESA IN CARICO: {html.escape(str(w['ack_at']))} ({html.escape(str(w['ack_by']))})</div>"
            if is_done
            else ""
        )

        row_left, row_right = st.columns([4.1, 1.1])
        with row_left:
            st.markdown(
                f"""
                <div class="{card_cls}">
                    <div>
                        <span class="axis-pill pill-z">Z: {html.escape(wid)} • {html.escape(z['timestamp_human'])} • {html.escape(z['shift'])} • {html.escape(z['capture_vector'])}</span>
                        <span class="axis-pill pill-x">X: [{html.escape(x['department'])}] {html.escape(x['op_tag'])} • {html.escape(x['matter_unit'])}</span>
                        {y_badge_html}
                        {urgent_html}
                    </div>
                    <div style="font-size:0.96rem;color:#F8FAFC;margin-top:6px;line-height:1.4;">
                        {html.escape(x['clean_text'])}
                    </div>
                    {ack_html}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with row_right:
            toggle_lbl = "↩ RIAPRI" if is_done else "✓ PRENDI IN CARICO"
            if st.button(toggle_lbl, key=f"ack_{wid}", use_container_width=True):
                if is_done:
                    w["status"] = "DA_EVADERE"
                    w["ack_at"] = None
                    w["ack_by"] = None
                else:
                    w["status"] = "EVASO"
                    w["ack_at"] = human_time_now()
                    w["ack_by"] = st.session_state.role
                queue_sound("telemetry_ack")
                safe_rerun()

            with st.expander("◎ QR / JSON"):
                compact_atom = json.dumps(
                    {
                        "id": wid,
                        "z": z["timestamp_iso"],
                        "ent": z["entity_id"],
                        "x": x["matter_unit"],
                        "txt": x["clean_text"][:90],
                        "y": 0 if mask_financial else y["euro_amount"],
                        "acc": acc_code,
                    },
                    ensure_ascii=False,
                )
                st.markdown(
                    "<div style='text-align:center;'>"
                    + generate_optical_matrix_svg(compact_atom, "#38BDF8", 112)
                    + "</div>",
                    unsafe_allow_html=True,
                )
                if not mask_financial:
                    st.code(json.dumps(w, indent=2, ensure_ascii=False), language="json")
                if is_commander and st.button("🗑️ ELIMINA", key=f"del_{wid}", use_container_width=True):
                    st.session_state.wafers_ram = [item for item in st.session_state.wafers_ram if item["wafer_id"] != wid]
                    safe_rerun()

# ==============================================================================
# 9. SCAMBIO DATI ZERO-CLOUD, BACKUP LOCALE & DISTRUZIONE VOLATILE RAM
# ==============================================================================
st.markdown("---")
st.markdown(
    "<div class='orbitron' style='color:#10B981;font-size:0.88rem;margin-bottom:8px;'>"
    "⟐ PONTE DATI ZERO-CLOUD (EXPORT .JSON / .TXT / .HTML • IMPORT LOCALE • PURGE RAM)"
    "</div>",
    unsafe_allow_html=True,
)

ex_c1, ex_c2, ex_c3, ex_c4 = st.columns(4)
stamp_file = datetime.now().strftime("%Y%m%d_%H%M")

with ex_c1:
    st.download_button(
        label="⬇ EXPORT .JSON (3-ASSI CUBO)",
        data=export_wafers_json().encode("utf-8"),
        file_name=f"bemask_data_wafer_{stamp_file}.json",
        mime="application/json",
        use_container_width=True,
        disabled=len(all_wafers) == 0,
    )

with ex_c2:
    st.download_button(
        label="⬇ EXPORT .TXT (CONSEGNA TURNO)",
        data=export_wafers_txt(is_commander).encode("utf-8"),
        file_name=f"bemask_consegna_{stamp_file}.txt",
        mime="text/plain",
        use_container_width=True,
        disabled=len(all_wafers) == 0,
    )

with ex_c3:
    st.download_button(
        label="⬇ EXPORT .HTML (REPORT OFFLINE)",
        data=export_wafers_html(is_commander).encode("utf-8"),
        file_name=f"bemask_hangar_report_{stamp_file}.html",
        mime="text/html",
        use_container_width=True,
        disabled=len(all_wafers) == 0,
    )

with ex_c4:
    if not st.session_state.purge_arm:
        if st.button("☢ DISTRUZIONE TOTALE RAM", use_container_width=True):
            st.session_state.purge_arm = True
            safe_rerun()
    else:
        p_yes, p_no = st.columns(2)
        with p_yes:
            if st.button("🔥 CONFERMA", use_container_width=True):
                st.session_state.wafers_ram = []
                st.session_state.last_landed_wafer_id = None
                st.session_state.purge_arm = False
                queue_sound("ram_purge")
                safe_rerun()
        with p_no:
            if st.button("✖ ANNULLA", use_container_width=True):
                st.session_state.purge_arm = False
                safe_rerun()

with st.expander("📥 IMPORTA PACCHETTO WAFER .JSON TRA DISPOSITIVI (ZERO-CLOUD SYNC IN RAM)"):
    imp_file = st.file_uploader("Seleziona micro-file .JSON generato da un altro dispositivo o reparto", type=["json"], key="wafer_json_import")
    if imp_file is not None and st.button("⚡ FONDI ATOMI NELL'HANGAR RAM", use_container_width=True):
        try:
            imp_data = json.loads(imp_file.getvalue().decode("utf-8"))
            incoming = imp_data.get("wafers", imp_data if isinstance(imp_data, list) else [])
            existing_ids = {w["wafer_id"] for w in st.session_state.wafers_ram}
            added = 0
            for item in incoming:
                if isinstance(item, dict) and "axis_x" in item and "axis_y" in item and "axis_z" in item:
                    if item.get("wafer_id") not in existing_ids:
                        st.session_state.wafers_ram.append(item)
                        existing_ids.add(item.get("wafer_id"))
                        added += 1
            queue_sound("telemetry_ack")
            st.success(f"Sincronizzati {added} nuovi Wafer in RAM (0 byte cloud).")
            safe_rerun()
        except Exception as exc:
            st.error(f"Formato JSON non valido: {exc}")

# ==============================================================================
# 10. PUNZONE METALLICO IN CALCE (SIGILLO D'AUTORE OBBLIGATORIO SU OGNI SCHERMATA)
# ==============================================================================
st.markdown(
    f"""
    <div class="metallic-punch">
        <div class="orbitron" style="color:#F59E0B;font-size:0.86rem;font-weight:700;letter-spacing:0.10em;">
            ◈ ARCHITECT: {ARCHITECT_NAME}  //  ID: {ARCHITECT_ID}
        </div>
        <div style="color:#94A3B8;font-size:0.74rem;margin-top:4px;">
            BEMASK SOVEREIGN ZERO • POD: {POD_REPO} ({POD_VERSION}) • MOONBASE ALPHA 1975 TELEMETRY • ZERO-TRUST RAM-ONLY SOVEREIGNTY
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
