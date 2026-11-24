import os
import io
import glob
import base64
import streamlit as st
import streamlit.components.v1 as components

try:
    from PIL import Image
except Exception:
    Image = None

# ==============================================================================
# BEMASK - A.L.P.H.A. // MOTORE GRAFICO, ASSET & ARCHITETTURA VISIVA
# CONCEIVED, DIRECTED & ENGINEERED BY ENRICO BRAGLIA
# ==============================================================================

HERO_CRAFT_SVG = """
<svg width="105" height="52" viewBox="0 0 180 86" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="48" y="16" width="84" height="12" fill="#1E293B" stroke="#94A3B8" stroke-width="2"/>
  <path d="M48 28L62 16L76 28L90 16L104 28L118 16L132 28" stroke="#CBD5E1" stroke-width="1.8"/>
  <polygon points="36,36 58,36 62,58 32,58" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
  <polygon points="122,36 144,36 148,58 118,58" fill="#334155" stroke="#E2E8F0" stroke-width="2"/>
  <rect x="30" y="58" width="34" height="5" fill="#F59E0B"/>
  <rect x="116" y="58" width="34" height="5" fill="#F59E0B"/>
  <rect x="58" y="30" width="64" height="24" fill="#1E293B" stroke="#38BDF8" stroke-width="2"/>
  <polygon points="90,22 122,42 112,68 68,68 58,42" fill="#E2E8F0" stroke="#FFFFFF" stroke-width="2.2"/>
  <polygon points="87,34 65,44 72,54 87,49" fill="#F59E0B"/>
  <polygon points="93,34 115,44 108,54 93,49" fill="#F59E0B"/>
  <circle cx="22" cy="46" r="6" fill="#EF4444" stroke="#FDE047" stroke-width="2"/>
  <circle cx="158" cy="46" r="6" fill="#EF4444" stroke="#FDE047" stroke-width="2"/>
</svg>
"""

SECTOR_SVGS = {
    "01": '<svg width="84" height="62" viewBox="0 0 120 84" fill="none"><rect x="24" y="10" width="72" height="12" fill="#1E293B" stroke="#94A3B8" stroke-width="2"/><path d="M24 22L38 10L52 22L66 10L80 22L96 10" stroke="#E2E8F0" stroke-width="2"/><polygon points="60,20 92,42 82,70 38,70 28,42" fill="#E2E8F0" stroke="#F59E0B" stroke-width="2.5"/><polygon points="57,34 35,44 42,56 57,50" fill="#F59E0B"/><polygon points="63,34 85,44 78,56 63,50" fill="#F59E0B"/></svg>',
    "02": '<svg width="82" height="62" viewBox="0 0 110 84" fill="none"><rect x="10" y="8" width="90" height="68" rx="4" fill="#0F172A" stroke="#10B981" stroke-width="2.5"/><rect x="18" y="16" width="20" height="12" fill="#F59E0B"/><rect x="44" y="16" width="20" height="12" fill="#F8FAFC"/><rect x="70" y="16" width="22" height="12" fill="#10B981"/><rect x="18" y="54" width="74" height="14" fill="#1E293B" stroke="#34D399" stroke-width="1.8"/><path d="M22 61H40L45 56L52 66L58 58L64 61H88" stroke="#10B981" stroke-width="2.2"/></svg>',
    "03": '<svg width="82" height="62" viewBox="0 0 110 84" fill="none"><circle cx="55" cy="42" r="32" fill="#0F293A" stroke="#38BDF8" stroke-width="2.5"/><circle cx="55" cy="42" r="20" stroke="#38BDF8" stroke-width="1.5" stroke-dasharray="4 3"/><line x1="55" y1="10" x2="55" y2="74" stroke="#38BDF8" stroke-width="1.5"/><line x1="23" y1="42" x2="87" y2="42" stroke="#38BDF8" stroke-width="1.5"/><circle cx="65" cy="32" r="5" fill="#F59E0B"/></svg>',
    "04": '<svg width="74" height="62" viewBox="0 0 100 86" fill="none"><rect x="26" y="6" width="48" height="74" rx="5" fill="#1E1B2E" stroke="#A855F7" stroke-width="2.8"/><rect x="33" y="13" width="34" height="26" rx="2" fill="#090D16" stroke="#38BDF8" stroke-width="2"/><circle cx="50" cy="26" r="7" fill="#F59E0B"/><rect x="34" y="45" width="9" height="7" fill="#F59E0B"/><rect x="46" y="45" width="9" height="7" fill="#E2E8F0"/><rect x="57" y="45" width="9" height="7" fill="#EF4444"/></svg>',
    "05": '<svg width="82" height="62" viewBox="0 0 110 84" fill="none"><rect x="14" y="12" width="82" height="60" rx="6" fill="#2A121F" stroke="#F43F5E" stroke-width="2.5"/><path d="M22 44H38L45 24L55 62L64 34L70 44H88" stroke="#F43F5E" stroke-width="3"/><circle cx="28" cy="24" r="4" fill="#F59E0B"/><circle cx="82" cy="24" r="4" fill="#10B981"/></svg>',
    "06": '<svg width="84" height="62" viewBox="0 0 114 84" fill="none"><polygon points="18,76 28,10 86,10 96,76" fill="#161A22" stroke="#F59E0B" stroke-width="2.8"/><polygon points="22,74 30,13 54,13 48,74" fill="#334155" stroke="#E2E8F0" stroke-width="2"/><polygon points="66,74 62,13 84,13 92,74" fill="#334155" stroke="#E2E8F0" stroke-width="2"/><rect x="100" y="34" width="8" height="16" fill="#F59E0B"/></svg>',
    "07": '<svg width="82" height="62" viewBox="0 0 110 84" fill="none"><polygon points="24,20 86,20 96,42 86,66 24,66 14,42" fill="#0F2E26" stroke="#10B981" stroke-width="2.5"/><rect x="34" y="30" width="42" height="24" fill="#1E293B" stroke="#F59E0B" stroke-width="2"/><circle cx="55" cy="42" r="6" fill="#F59E0B"/></svg>',
    "08": '<svg width="82" height="62" viewBox="0 0 110 84" fill="none"><polygon points="55,8 92,22 84,64 55,78 26,64 18,22" fill="#0E2A36" stroke="#06B6D4" stroke-width="2.5"/><circle cx="55" cy="42" r="18" fill="#161E29" stroke="#38BDF8" stroke-width="2"/><path d="M55 30V54M43 42H67" stroke="#10B981" stroke-width="3.5"/></svg>',
    "09": '<svg width="82" height="62" viewBox="0 0 110 84" fill="none"><line x1="55" y1="10" x2="55" y2="74" stroke="#F59E0B" stroke-width="4"/><ellipse cx="55" cy="26" rx="28" ry="8" stroke="#38BDF8" stroke-width="2.2" fill="rgba(56,189,248,0.15)"/><ellipse cx="55" cy="46" rx="36" ry="10" stroke="#F59E0B" stroke-width="2.5" fill="rgba(245,158,11,0.18)"/><circle cx="55" cy="12" r="6" fill="#EF4444"/></svg>',
    "10": '<svg width="84" height="62" viewBox="0 0 114 84" fill="none"><rect x="12" y="10" width="90" height="64" rx="4" fill="#0B2922" stroke="#10B981" stroke-width="2.8"/><rect x="20" y="18" width="46" height="22" fill="#091318" stroke="#34D399" stroke-width="2"/><circle cx="82" cy="29" r="10" fill="#1E293B" stroke="#F59E0B" stroke-width="2.5"/><rect x="20" y="48" width="14" height="16" fill="#F59E0B"/><rect x="38" y="48" width="14" height="16" fill="#E2E8F0"/><rect x="56" y="48" width="14" height="16" fill="#10B981"/><rect x="74" y="48" width="20" height="16" fill="#EF4444"/></svg>',
    "11": '<svg width="86" height="62" viewBox="0 0 118 84" fill="none"><path d="M18 26H86L96 32L86 40H52L40 72H22L32 40H18V26Z" fill="#CBD5E1" stroke="#EF4444" stroke-width="2.5"/><rect x="26" y="30" width="22" height="6" fill="#EF4444"/><rect x="54" y="30" width="18" height="6" fill="#F59E0B"/><line x1="102" y1="33" x2="116" y2="33" stroke="#EF4444" stroke-width="4" stroke-dasharray="3 2"/></svg>',
    "12": '<svg width="88" height="62" viewBox="0 0 130 84" fill="none"><circle cx="65" cy="42" r="35" fill="#0B192C" stroke="#38BDF8" stroke-width="2.2" stroke-dasharray="5 3"/><rect x="12" y="26" width="106" height="32" rx="16" fill="#1E293B" stroke="#F59E0B" stroke-width="2.8"/><rect x="28" y="32" width="20" height="13" rx="3" fill="#090D16" stroke="#38BDF8" stroke-width="1.8"/><rect x="55" y="32" width="20" height="13" rx="3" fill="#090D16" stroke="#38BDF8" stroke-width="1.8"/><rect x="82" y="32" width="20" height="13" rx="3" fill="#090D16" stroke="#38BDF8" stroke-width="1.8"/></svg>'
}

BASE_VECTORS = [
    {"bit": 0, "code": "01", "short": "01 FRONT", "name": "FRONT & APEX", "artifact": "BEMASK ORBITAL CARRIER", "staff_allowed": False,
     "border": "#F59E0B", "glow": "rgba(245,158,11,0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #3D2B14 0%, #14161D 78%)",
     "kpi": "OCC: 88% | ADR: € 165 | 140 COMB BAR", "url": "https://bemask-sovereign-zero.streamlit.app",
     "subs": ["1. Dynamic Pricing 140 Comb", "2. Controllo Allotment & OTA", "3. Check-in & Upselling", "4. Forecast 24 Fasce BAR", "5. Export CSV Passepartout"]},
    {"bit": 1, "code": "02", "short": "02 BEV", "name": "LAZERS BEV", "artifact": "ALPHA CONTROL MATRIX", "staff_allowed": False,
     "border": "#10B981", "glow": "rgba(16,185,129,0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #113A32 0%, #12181F 78%)",
     "kpi": "POURING: 21% | MARGINE CANTINA: +79%", "url": "https://bemask-lazers.streamlit.app",
     "subs": ["1. Pouring Calici & Vini", "2. Spinta Aperitivi Meteo", "3. Margine Bottiglie", "4. Usura Cristalleria", "5. Inventario Cantina Live"]},
    {"bit": 2, "code": "03", "short": "03 FOOD", "name": "LAZERS FOOD", "artifact": "TELEMETRY RADAR DESK", "staff_allowed": False,
     "border": "#38BDF8", "glow": "rgba(56,189,248,0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #13334C 0%, #121720 78%)",
     "kpi": "COPERTI: 84/105 | FOOD COST: 28.5%", "url": "https://bemask-lazers.streamlit.app",
     "subs": ["1. Capienza Sala & Cucina", "2. Scorporo Quote HB / FB", "3. Sfridi & Rese Carni", "4. Semaforo Zero-Fee", "5. Floor Industriale Pasto"]},
    {"bit": 3, "code": "04", "short": "04 BEACH", "name": "BEACH & POOL", "artifact": "ALPHA FIELD LINK", "staff_allowed": True,
     "border": "#A855F7", "glow": "rgba(168,85,247,0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #2B244D 0%, #141522 78%)",
     "kpi": "SATURAZIONE LIDO: 92% | VENTO: 11 KT", "url": "https://ska-boschetto.streamlit.app",
     "subs": ["1. Mappa Ombrelloni & Cabine", "2. Soglia Vento Grounding", "3. Light Lunch all'Ombrellone", "4. Presidio Bagnini", "5. Chiusura Cassa Lido"]},
    {"bit": 4, "code": "05", "short": "05 SPA", "name": "SPA & AYURVEDA", "artifact": "BEMASK BIO-SCANNER", "staff_allowed": True,
     "border": "#F43F5E", "glow": "rgba(244,63,94,0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #3F1D2B 0%, #16141C 78%)",
     "kpi": "SLOT CABINE: 14/16 | FALLBACK PIOGGIA ON", "url": "https://ska-boschetto.streamlit.app",
     "subs": ["1. Conversione Pioggia (S1/S2)", "2. Agenda Cabine & Massaggi", "3. Percorso Private Spa VIP", "4. Vendita Linea Cosmetica", "5. Turni Operatori"]},
    {"bit": 5, "code": "06", "short": "06 SKA", "name": "S.K.A. & ROOMS", "artifact": "ALPHA BULKHEAD GATE", "staff_allowed": True,
     "border": "#F59E0B", "glow": "rgba(245,158,11,0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #382B19 0%, #15161C 78%)",
     "kpi": "CAMERE PRONTE: 58/60 | SEGNALAZIONI: 0", "url": "https://ska-boschetto.streamlit.app",
     "subs": ["1. Stato Pulizia Camere", "2. Ticket Manutenzione", "3. Presidio Brigata Piani", "4. Dotazioni & Biancheria", "5. Ispezione Governante"]},
    {"bit": 6, "code": "07", "short": "07 ACQUISTO", "name": "PUNTO ACQUISTO & ROP", "artifact": "CARGO SHIELD POD 96H", "staff_allowed": False,
     "border": "#10B981", "glow": "rgba(16,185,129,0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #13392E 0%, #12171D 78%)",
     "kpi": "ROP: SCORTA OK | SCUDO AUTONOMIA: 96H", "url": "https://bemask-lazers.streamlit.app",
     "subs": ["1. Calcolatore Punto Riordino (ROP)", "2. Scudo Dispensa 96 Ore", "3. Lead Time Fornitori", "4. Controllo Fatture XML", "5. Lista Ordini Urgenti"]},
    {"bit": 7, "code": "08", "short": "08 HACCP", "name": "HACCP & REGISTRO ASL", "artifact": "THERMAL BIOSENSOR", "staff_allowed": True,
     "border": "#06B6D4", "glow": "rgba(6,182,212,0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #123440 0%, #12171E 78%)",
     "kpi": "CELLE FRIGO: 21/21 OK | FIRME PIN: 6", "url": "https://ska-boschetto.streamlit.app",
     "subs": ["1. Temperature Celle (-18°C / +4°C)", "2. Firma Digitale con PIN", "3. Lotti & Sgocciolato", "4. Sanificazione Cucina", "5. Scarica Stampa ASL (.HTML)"]},
    {"bit": 8, "code": "09", "short": "09 GOPPAR", "name": "OPEX / CAPEX & P.IVA", "artifact": "ALPHA YIELD PYLON", "staff_allowed": False,
     "border": "#F59E0B", "glow": "rgba(245,158,11,0.38)", "bg_grad": "radial-gradient(circle at 50% 42%, #3B2816 0%, #14161D 78%)",
     "kpi": "MOL NETTO OGGI: € 4.820 | GOP: +34%", "url": "https://bemask-lazers.streamlit.app",
     "subs": ["1. Split Multi-P.IVA Casa Madre", "2. OPEX vs CAPEX Real-Time", "3. Incidenza Costo Brigate", "4. Cashflow Consolidato", "5. Ponte Dati Revisore"]},
    {"bit": 9, "code": "10", "short": "10 BAR DDT", "name": "BAR & DDT SENTINEL", "artifact": "X5-7 CORE CONSOLE", "staff_allowed": False,
     "border": "#10B981", "glow": "rgba(16,185,129,0.42)", "bg_grad": "radial-gradient(circle at 50% 42%, #0F3D33 0%, #10171D 78%)",
     "kpi": "RAGGI-X SCONTRINO | CONTABILITÀ A-O | +1KG CAFFÈ", "url": "https://bemask-lazers.streamlit.app",
     "subs": ["1. 📸 Scanner & Voci Scontrino", "2. 🎹 Contabilità Rapida (A-O)", "3. 🏁 Chiusura Cassa / Turno", "4. ❄️ Frigo Bar 1-Click", "5. 📅 Bilancio & Calendario"]},
    {"bit": 10, "code": "11", "short": "11 VAMPIRE", "name": "BANK VAMPIRE SCANNER", "artifact": "BEMASK PULSE INTERCEPTOR", "staff_allowed": False,
     "border": "#EF4444", "glow": "rgba(239,68,68,0.42)", "bg_grad": "radial-gradient(circle at 50% 42%, #421820 0%, #151319 78%)",
     "kpi": "AUTOPSIA CONTO | POS REALE & SDD ALERT", "url": "https://bemask-lazers.streamlit.app",
     "subs": ["1. 📸 Scanner E/C & POS Reale", "2. Vero Tasso POS Effettivo", "3. Impatto Costi su Caffetteria", "4. Anti-Doppio Addebito SDD", "5. 📅 Bilancio & Calendario"]},
    {"bit": 11, "code": "12", "short": "12 TUBE", "name": "TRAVEL TUBE SHIELD", "artifact": "HIGH-SPEED VECTOR POD", "staff_allowed": False,
     "border": "#38BDF8", "glow": "rgba(56,189,248,0.45)", "bg_grad": "radial-gradient(circle at 50% 42%, #0F344C 0%, #10151D 78%)",
     "kpi": "FONDO CASSA | MULTI-POS vs RT | SEMANTICA A-O", "url": "https://bemask-travel-tube.streamlit.app",
     "subs": ["1. 🛡️ Pareggio Cassa & POS", "2. 🧠 Motore Semantico A-O", "3. ⚡ Giustificativo 3-Sec", "4. 🖨️ Distinta Ispettiva .TXT", "5. 📅 Bilancio & Calendario"]}
]

WEATHER_5_DAYS = [
    {"day": "GIORNO 1 · 19°C", "icon": "☀️", "status": "NOMINAL ORBIT", "rain": "PIOGGIA: 8%", "hum": "UR: 54%", "wind": "VENTO: 7 KT NW", "directive": "☀️ SPINTA DEHORS, APERITIVI & LIDO", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "GIORNO 2 · 17°C", "icon": "🌤️", "status": "NOMINAL ORBIT", "rain": "PIOGGIA: 14%", "hum": "UR: 61%", "wind": "VENTO: 11 KT W", "directive": "🌤️ REGIME STANDARD ESTERNO/INTERNO", "border": "#F59E0B", "text_col": "#F59E0B"},
    {"day": "GIORNO 3 · 17°C", "icon": "⛈️", "status": "SOLAR STORM", "rain": "PIOGGIA: 91%", "hum": "UR: 88%", "wind": "VENTO: 29 KT SW", "directive": "⚡ FALLBACK SPA, SALA INTERNA & S2", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "GIORNO 4 · 20°C", "icon": "⛈️", "status": "SOLAR STORM", "rain": "PIOGGIA: 94%", "hum": "UR: 92%", "wind": "VENTO: 33 KT S", "directive": "🚨 SCUDO 96H & CHIUSURA OMBRELLONI", "border": "#EF4444", "text_col": "#EF4444"},
    {"day": "GIORNO 5 · 21°C", "icon": "☀️", "status": "NOMINAL ORBIT", "rain": "PIOGGIA: 22%", "hum": "UR: 58%", "wind": "VENTO: 9 KT NE", "directive": "🛸 RIAPERTURA COMPLETA SETTORI ESTERNI", "border": "#38BDF8", "text_col": "#38BDF8"}
]


def play_ems_synth(effect_type):
    js_code = f"""
    <script>
    (function() {{
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        const now = ctx.currentTime;
        const mode = "{effect_type}";
        if (mode === "burst") {{
            [523.25, 659.25, 783.99, 1046.50, 880.0, 1174.66].forEach((f, i) => {{
                const o = ctx.createOscillator(), g = ctx.createGain();
                o.type = "sawtooth"; o.frequency.setValueAtTime(f, now + i * 0.06);
                g.gain.setValueAtTime(0.08, now + i * 0.06);
                g.gain.exponentialRampToValueAtTime(0.001, now + i * 0.06 + 0.055);
                o.connect(g); g.connect(ctx.destination);
                o.start(now + i * 0.06); o.stop(now + i * 0.06 + 0.06);
            }});
        }} else if (mode === "commlock") {{
            [987.77, 1318.51].forEach((f, i) => {{
                const o = ctx.createOscillator(), g = ctx.createGain();
                o.type = "sine"; o.frequency.setValueAtTime(f, now + i * 0.11);
                g.gain.setValueAtTime(0.12, now + i * 0.11);
                g.gain.exponentialRampToValueAtTime(0.001, now + i * 0.11 + 0.10);
                o.connect(g); g.connect(ctx.destination);
                o.start(now + i * 0.11); o.stop(now + i * 0.11 + 0.11);
            }});
        }} else if (mode === "klaxon") {{
            const o = ctx.createOscillator(), g = ctx.createGain();
            o.type = "square";
            o.frequency.setValueAtTime(440, now);
            o.frequency.linearRampToValueAtTime(880, now + 0.25);
            o.frequency.linearRampToValueAtTime(440, now + 0.50);
            g.gain.setValueAtTime(0.12, now);
            g.gain.exponentialRampToValueAtTime(0.001, now + 0.52);
            o.connect(g); g.connect(ctx.destination);
            o.start(now); o.stop(now + 0.52);
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0)


def inject_alpha_css():
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
        background-image: radial-gradient(circle at 50% 32%, rgba(245, 158, 11, 0.07) 0%, rgba(16, 19, 25, 0.96) 72%);
        color: #F8FAFC;
        font-family: 'Orbitron', sans-serif;
    }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 0.6rem; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 97% !important; }

    [data-testid="stStatusWidget"] {
        background-color: rgba(16, 19, 25, 0.92) !important;
        border: 1px solid #F59E0B !important;
        border-radius: 3px !important;
        padding: 3px 10px !important;
        color: #F59E0B !important;
        font-family: 'Share Tech Mono', monospace !important;
    }

    @keyframes monolithPulse {
        0%, 100% { box-shadow: 0 0 42px rgba(245,158,11,0.38), inset 0 0 34px rgba(245,158,11,0.22); border-color: #F59E0B; }
        50% { box-shadow: 0 0 60px rgba(56,189,248,0.50), inset 0 0 44px rgba(56,189,248,0.30); border-color: #38BDF8; }
    }
    @keyframes hudPhase1 { 0%,3%{opacity:0} 7%,30%{opacity:1} 34%,100%{opacity:0} }
    @keyframes hudPhase2 { 0%,33%{opacity:0} 37%,64%{opacity:1} 68%,100%{opacity:0} }
    @keyframes hudPhase3 { 0%,67%{opacity:0} 71%,96%{opacity:1} 100%{opacity:0} }
    @keyframes telemetryScan {
        0%, 100% { box-shadow: inset 0 0 18px rgba(56,189,248,0.45), 0 0 18px rgba(245,158,11,0.45); }
        50% { box-shadow: inset 0 0 42px rgba(245,158,11,0.75), 0 0 36px rgba(56,189,248,0.75); }
    }

    .soglia-wrap { width: 486px; max-width: 92vw; margin: 18px auto 10px auto; }
    .soglia-monolith {
        position: relative; width: 486px; height: 486px; max-width: 92vw; max-height: 92vw;
        background: radial-gradient(circle at 72% 30%, rgba(56,189,248,0.20) 0%, #07090E 66%);
        border: 2px solid #F59E0B; border-radius: 4px; overflow: hidden;
        animation: monolithPulse 5s ease-in-out infinite; pointer-events: none;
    }
    .soglia-monolith video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: 1; }
    .soglia-vignette {
        position: absolute; inset: 0; z-index: 2;
        background: linear-gradient(135deg, rgba(7,9,14,0.82) 0%, rgba(7,9,14,0.12) 50%, rgba(7,9,14,0.05) 100%),
                    linear-gradient(180deg, rgba(7,9,14,0.35) 0%, rgba(7,9,14,0.05) 54%, rgba(7,9,14,0.92) 100%);
    }
    .soglia-top-zone { position: absolute; top: 16px; left: 18px; right: 18px; z-index: 3; }
    .soglia-alpha-3of5 {
        width: 60%; display: flex; justify-content: space-between; align-items: baseline;
        font-size: 26px; font-weight: 900; color: #FFFFFF; line-height: 1;
        text-shadow: 0 0 16px rgba(245,158,11,0.55);
    }
    .soglia-alpha-3of5 .dot-sep { color: #F59E0B; font-size: 22px; }
    .soglia-list-2of5 {
        width: 40%; margin-top: 8px; padding-top: 7px;
        border-top: 1.5px solid rgba(245,158,11,0.55);
        display: flex; flex-direction: column; gap: 4px; text-align: left;
    }
    .soglia-list-row {
        font-family: 'Share Tech Mono', monospace; font-size: 13.5px; font-weight: 700;
        color: #F8FAFC; letter-spacing: 0.9px; white-space: nowrap; text-shadow: 0 1px 6px rgba(0,0,0,0.9);
    }
    .soglia-list-row .row-dot { color: #94A3B8; margin: 0 4px; }
    .soglia-hud-bottom {
        position: absolute; bottom: 34px; left: 16px; right: 16px; min-height: 52px; z-index: 3;
        display: flex; align-items: flex-end; justify-content: center; text-align: center;
    }
    .hud-seq { position: absolute; left: 0; right: 0; bottom: 0; opacity: 0; }
    .hud-seq-1 { animation: hudPhase1 10s infinite; }
    .hud-seq-2 { animation: hudPhase2 10s infinite; }
    .hud-seq-3 { animation: hudPhase3 10s infinite; }
    .soglia-inner-footer {
        position: absolute; bottom: 8px; left: 14px; right: 14px; z-index: 3;
        border-top: 1px solid rgba(245,158,11,0.32); padding-top: 5px; text-align: center;
        font-family: 'Share Tech Mono', monospace; font-size: 9px; color: #CBD5E1; letter-spacing: 0.65px;
    }

    div[class*="st-key-soglia_pad_click"] { width: 486px !important; max-width: 92vw !important; margin: -496px auto 10px auto !important; position: relative; z-index: 15; }
    div[class*="st-key-soglia_pad_click"] > div > button {
        height: 486px !important; width: 100% !important; background: transparent !important;
        border: none !important; color: transparent !important; box-shadow: none !important; cursor: pointer !important;
    }
    div[class*="st-key-soglia_pad_click"] > div > button:hover {
        background: rgba(255,255,255,0.02) !important; border: 1.5px solid rgba(56,189,248,0.80) !important;
    }

    .gate6-tile {
        height: 156px; border-radius: 3px; position: relative; overflow: hidden;
        display: flex; flex-direction: column; justify-content: flex-end; align-items: center;
        text-align: center; padding: 10px 8px; margin-bottom: 10px; pointer-events: none;
    }
    .gate6-tile-input { justify-content: flex-start !important; padding-top: 8px !important; }
    .gate6-vignette {
        position: absolute; inset: 0; z-index: 1;
        background: linear-gradient(180deg, rgba(9,12,18,0.18) 0%, rgba(9,12,18,0.44) 54%, rgba(9,12,18,0.90) 100%);
    }
    .gate6-tile-input .gate6-vignette {
        background: linear-gradient(180deg, rgba(7,10,16,0.74) 0%, rgba(7,10,16,0.12) 52%, rgba(7,10,16,0.22) 100%) !important;
    }
    .gate6-content { position: relative; z-index: 2; width: 100%; }
    .gate6-code { font-size: 9.5px; font-weight: 800; letter-spacing: 1.5px; }
    .gate6-name { font-size: 12.5px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px; margin-top: 2px; text-shadow: 0 2px 8px rgba(0,0,0,0.98); }
    .gate6-art { font-size: 8.5px; font-weight: 700; color: #E2E8F0; font-family: 'Share Tech Mono', monospace; letter-spacing: 0.8px; margin-top: 2px; text-shadow: 0 1px 6px rgba(0,0,0,0.98); }

    div[class*="st-key-gate6_btn_"] { margin-top: -166px !important; margin-bottom: 10px !important; position: relative; z-index: 12; }
    div[class*="st-key-gate6_btn_"] > div > button {
        height: 156px !important; width: 100% !important; background: transparent !important;
        border: none !important; color: transparent !important; box-shadow: none !important; cursor: pointer !important;
    }
    div[class*="st-key-gate6_btn_"] > div > button:hover {
        background: rgba(255,255,255,0.04) !important; border: 1.5px solid rgba(245,158,11,0.88) !important;
        box-shadow: 0 0 28px rgba(245,158,11,0.42) !important;
    }

    /* TRASPARENZA ASSOLUTA 100% SU TESSERE 02 E 03 (ZERO PILLOLA GRIGIA) */
    div[class*="st-key-gate6_in_"] {
        margin-top: -64px !important;
        margin-bottom: 24px !important;
        padding: 0 16px !important;
        position: relative;
        z-index: 16;
        background: transparent !important;
    }
    div[class*="st-key-gate6_in_"] *,
    div[class*="st-key-gate6_in_"] [data-testid="stTextInput"],
    div[class*="st-key-gate6_in_"] [data-testid="stTextInputRootElement"],
    div[class*="st-key-gate6_in_"] [data-baseweb="input"],
    div[class*="st-key-gate6_in_"] [data-baseweb="base-input"] {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        border-color: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    div[class*="st-key-gate6_in_"] button,
    div[class*="st-key-gate6_in_"] [data-testid="InputInstructions"] {
        display: none !important;
    }
    div[class*="st-key-gate6_in_"] input {
        text-align: center !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 26px !important;
        font-weight: 900 !important;
        padding: 2px 0 !important;
    }
    div[class*="st-key-gate6_in_"] input:-webkit-autofill,
    div[class*="st-key-gate6_in_"] input:-webkit-autofill:hover,
    div[class*="st-key-gate6_in_"] input:-webkit-autofill:focus {
        transition: background-color 99999s ease-in-out 0s !important;
        -webkit-box-shadow: 0 0 0px 1000px transparent inset !important;
    }

    div[class*="st-key-gate6_in_pin"] input,
    div[class*="st-key-gate6_in_pin"] input::placeholder {
        color: #10B981 !important;
        -webkit-text-fill-color: #10B981 !important;
        caret-color: #10B981 !important;
        opacity: 1 !important;
        letter-spacing: 12px !important;
        text-shadow: 0 0 14px rgba(16,185,129,1), 0 2px 6px rgba(0,0,0,0.98) !important;
    }
    div[class*="st-key-gate6_in_pin"] input:focus::placeholder { opacity: 0.22 !important; }

    div[class*="st-key-gate6_in_2fa"] input,
    div[class*="st-key-gate6_in_2fa"] input::placeholder {
        color: #38BDF8 !important;
        -webkit-text-fill-color: #38BDF8 !important;
        caret-color: #38BDF8 !important;
        opacity: 1 !important;
        letter-spacing: 9px !important;
        text-shadow: 0 0 14px rgba(56,189,248,1), 0 2px 6px rgba(0,0,0,0.98) !important;
    }
    div[class*="st-key-gate6_in_2fa"] input:focus::placeholder { opacity: 0.22 !important; }

    .alpha-top-strip {
        background-color: #1A1E26; border: 1px solid #323946; border-left: 5px solid #F59E0B;
        padding: 8px 14px; margin-bottom: 8px; border-radius: 2px;
    }
    .badge-amber { background-color: #F59E0B; color: #0B0E14; font-weight: 900; font-size: 10px; padding: 3px 8px; margin-right: 6px; display: inline-block; margin-bottom: 3px; }
    .badge-white { background-color: #F1F5F9; color: #0F172A; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }
    .badge-red { background-color: #7F1D1D; border: 1px solid #EF4444; color: #FCA5A5; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }
    .badge-green { background-color: #064E3B; border: 1px solid #10B981; color: #6EE7B7; font-weight: 800; font-size: 10px; padding: 2px 8px; margin-right: 6px; font-family: 'Share Tech Mono', monospace; display: inline-block; margin-bottom: 3px; }

    .mission-bar {
        background: linear-gradient(90deg, #161C24 0%, #1E2836 50%, #161C24 100%);
        border: 1px solid #3A4B5E; border-left: 5px solid #F59E0B;
        padding: 10px 16px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 10px;
    }
    .mission-title { font-size: 19px; font-weight: 900; color: #F59E0B; letter-spacing: 1.5px; }
    .mission-sub { font-size: 10.5px; color: #38BDF8; font-family: 'Share Tech Mono', monospace; letter-spacing: 0.9px; margin-top: 2px; }
    .nixie-group { display: flex; align-items: center; gap: 10px; }
    .nixie-label { font-size: 10px; color: #94A3B8; font-weight: 700; letter-spacing: 1px; }
    .nixie-digits {
        background-color: #0D1015; border: 1px solid #F59E0B; color: #F59E0B;
        font-family: 'Share Tech Mono', monospace; font-size: 17px; font-weight: 900;
        padding: 3px 10px; letter-spacing: 3px; border-radius: 2px; box-shadow: inset 0 0 8px rgba(245,158,11,0.4);
    }

    .weather-card { background-color: #151922; border: 1px solid #2B3340; padding: 9px 11px; border-radius: 3px; margin-bottom: 8px; }
    .w-header { display: flex; justify-content: space-between; align-items: center; }
    .w-day { font-size: 10px; font-weight: 900; color: #FFFFFF; }
    .w-icon { font-size: 17px; line-height: 1; }
    .w-status { font-size: 10px; font-weight: 900; margin-top: 3px; }
    .w-telemetry { display: flex; justify-content: space-between; margin-top: 5px; padding-top: 4px; border-top: 1px dashed #2E3846; font-family: 'Share Tech Mono', monospace; font-size: 9px; color: #E2E8F0; font-weight: 700; }
    .w-directive { margin-top: 4px; font-family: 'Share Tech Mono', monospace; font-size: 9px; color: #94A3B8; }

    .alpha-tile {
        height: 220px; border-radius: 3px; padding: 15px;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        text-align: center; position: relative; margin-bottom: 14px; pointer-events: none;
    }
    .tile-code { font-size: 11px; font-weight: 800; color: #F59E0B; margin-top: 9px; letter-spacing: 1.5px; }
    .tile-name { font-size: 14px; font-weight: 900; color: #FFFFFF; letter-spacing: 1.1px; margin-top: 3px; }
    .tile-artifact { font-size: 9px; font-weight: 700; color: #94A3B8; font-family: 'Share Tech Mono', monospace; letter-spacing: 0.9px; margin-top: 4px; }

    div[class*="st-key-blum_click_"] { margin-top: -234px !important; margin-bottom: 14px !important; position: relative; z-index: 10; }
    div[class*="st-key-blum_click_"] > div > button {
        height: 220px !important; width: 100% !important; background: transparent !important;
        border: none !important; color: transparent !important; box-shadow: none !important;
    }
    div[class*="st-key-blum_click_"] > div > button:hover {
        background: rgba(255,255,255,0.05) !important; border: 1.5px solid rgba(245,158,11,0.75) !important;
        box-shadow: 0 0 32px rgba(245,158,11,0.4) !important;
    }

    div.stButton > button {
        background-color: #1A212B !important; color: #F8FAFC !important;
        border: 1px solid #2F3E50 !important; border-radius: 3px !important;
        font-family: 'Orbitron', sans-serif !important; font-size: 10px !important;
        font-weight: 800 !important; letter-spacing: 0.8px !important; min-height: 40px !important;
    }
    div.stButton > button:hover { border-color: #F59E0B !important; color: #F59E0B !important; }

    .ems-panel { background-color: #161A22; border: 2px solid #F59E0B; padding: 12px; border-radius: 3px; margin-bottom: 10px; }
    .commlock-panel { background-color: #161A22; border: 1px solid #F59E0B; padding: 14px; border-radius: 3px; text-align: center; margin-top: 8px; }
    .blum-stage { background: radial-gradient(circle at 50% 20%, #1A2432 0%, #0E1218 85%); padding: 18px; border-radius: 4px; margin-bottom: 12px; }
    .kpi-custom-box { background-color: #141A23; border: 1px solid #2B394A; border-left: 4px solid #F59E0B; padding: 14px; border-radius: 3px; margin-top: 6px; margin-bottom: 8px; }
    .kpi-custom-title { font-size: 10px; font-weight: 800; color: #94A3B8; letter-spacing: 1.1px; margin-bottom: 6px; font-family: 'Share Tech Mono', monospace; }
    .kpi-custom-value { font-size: 23px; font-weight: 900; color: #FFFFFF; letter-spacing: 0.9px; line-height: 1.2; }
    .kpi-custom-sub { font-size: 11px; font-weight: 700; margin-top: 6px; font-family: 'Share Tech Mono', monospace; }
    .xray-desk { background: linear-gradient(135deg, #0D1622 0%, #132232 100%); border: 2px solid #10B981; border-left: 6px solid #F59E0B; padding: 16px; border-radius: 4px; margin: 10px 0 14px 0; }

    @media (max-width: 768px) {
        .mission-title { font-size: 14px !important; }
        .soglia-wrap, .soglia-monolith { width: 340px !important; height: 340px !important; }
        div[class*="st-key-soglia_pad_click"] { width: 340px !important; margin: -350px auto 8px auto !important; }
        div[class*="st-key-soglia_pad_click"] > div > button { height: 340px !important; }
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_soglia_video_b64():
    base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
    for name in ["eagle_loop.mp4", "eagle_loop.mp4.mp4", "eagle_loop..mp4", "soglia_zero.mp4", "alpha_loop.mp4"]:
        for p in [name, os.path.join(base_dir, name)]:
            if os.path.exists(p):
                try:
                    with open(p, "rb") as vf:
                        return base64.b64encode(vf.read()).decode("utf-8")
                except Exception:
                    pass
    for p in sorted(set(glob.glob("*.mp4") + glob.glob(os.path.join(base_dir, "*.mp4")))):
        low = os.path.basename(p).lower()
        if "manifesto" not in low and any(k in low for k in ["eagle", "loop", "soglia"]):
            try:
                with open(p, "rb") as vf:
                    return base64.b64encode(vf.read()).decode("utf-8")
            except Exception:
                pass
    return None


@st.cache_data(show_spinner=False)
def load_eagle_grid_sprite_uri():
    base_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
    candidates = []
    for ext in ["jpg", "jpeg", "png", "webp"]:
        candidates.extend(glob.glob(f"*.{ext}") + glob.glob(os.path.join(base_dir, f"*.{ext}")))
    prio = [p for p in sorted(set(candidates)) if any(k in os.path.basename(p).lower() for k in ["grid", "6", "tiles", "mosaic", "parts", "watermarked"])]
    rest = [p for p in sorted(set(candidates)) if "eagle" in os.path.basename(p).lower() and p not in prio]
    for target in (prio + rest):
        try:
            with open(target, "rb") as f:
                raw_bytes = f.read()
            if Image is not None:
                img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                if img.width > 960:
                    img = img.resize((960, int(img.height * (960.0 / img.width))), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85, optimize=True)
                return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
            mime = "image/png" if target.lower().endswith(".png") else "image/jpeg"
            return f"data:{mime};base64,{base64.b64encode(raw_bytes).decode('utf-8')}"
        except Exception:
            continue
    return None


def build_gate6_tile_html(code, title, subtitle, border_hex, glow_rgba, fallback_grad, bg_pos, has_sprite, is_input=False):
    cls_extra = (" gate6-tile-input" if is_input else "") + (" gate6-has-sprite" if has_sprite else "")
    bg_css = f"background-position: {bg_pos};" if has_sprite else f"background: {fallback_grad};"
    return (
        f'<div class="gate6-tile{cls_extra}" style="{bg_css} border: 1.5px solid {border_hex}; '
        f'border-left: 5px solid {border_hex}; box-shadow: inset 0 0 26px {glow_rgba}, 0 0 16px {glow_rgba};">'
        f'<div class="gate6-vignette"></div><div class="gate6-content">'
        f'<div class="gate6-code" style="color:{border_hex};">{code}</div>'
        f'<div class="gate6-name">{title}</div><div class="gate6-art">{subtitle}</div>'
        f'</div></div>'
    )


def build_soglia_monolith_html():
    video_b64 = load_soglia_video_b64()
    visual_core = (
        f'<video autoplay loop muted playsinline src="data:video/mp4;base64,{video_b64}"></video>'
        if video_b64 else
        '<svg viewBox="0 0 500 500" width="100%" height="100%" style="position:absolute;inset:0;z-index:1;">'
        '<circle cx="380" cy="150" r="60" fill="rgba(56,189,248,0.25)"/>'
        '<ellipse cx="220" cy="520" rx="420" ry="190" fill="#131B26" stroke="#10B981" stroke-width="1.2"/></svg>'
    )
    return (
        f'<div class="soglia-wrap"><div class="soglia-monolith">{visual_core}<div class="soglia-vignette"></div>'
        '<div class="soglia-top-zone"><div class="soglia-alpha-3of5">'
        '<span>A</span><span class="dot-sep">.</span><span>L</span><span class="dot-sep">.</span>'
        '<span>P</span><span class="dot-sep">.</span><span>H</span><span class="dot-sep">.</span>'
        '<span>A</span><span class="dot-sep">.</span></div>'
        '<div class="soglia-list-2of5">'
        '<div class="soglia-list-row"><span style="color:#F59E0B;">A</span><span class="row-dot">·</span>ANALYTICS</div>'
        '<div class="soglia-list-row"><span style="color:#38BDF8;">L</span><span class="row-dot">·</span>LINEARITY</div>'
        '<div class="soglia-list-row"><span style="color:#10B981;">P</span><span class="row-dot">·</span>POWER</div>'
        '<div class="soglia-list-row"><span style="color:#F59E0B;">H</span><span class="row-dot">·</span>HYPER-SCALE</div>'
        '<div class="soglia-list-row"><span style="color:#38BDF8;">A</span><span class="row-dot">·</span>AUTOMATION</div>'
        '</div></div>'
        '<div class="soglia-hud-bottom">'
        '<div class="hud-seq hud-seq-1"><div style="font-size:10.5px;color:#38BDF8;font-family:\'Share Tech Mono\';letter-spacing:2px;">SOVEREIGN ZERO · ECOSYSTEM</div><div style="font-size:19px;font-weight:900;color:#FFF;letter-spacing:2.2px;margin-top:3px;">BEMASK · A.L.P.H.A.</div></div>'
        '<div class="hud-seq hud-seq-2"><div style="font-size:10.5px;color:#F59E0B;font-family:\'Share Tech Mono\';letter-spacing:1.6px;">◈ ORBITAL TELEMETRY · 3-AXIS RAM ◈</div><div style="font-size:15px;font-weight:900;color:#FFF;letter-spacing:1.6px;margin-top:4px;">ARCHITECT · ENRICO BRAGLIA</div></div>'
        '<div class="hud-seq hud-seq-3"><div style="font-size:10.5px;color:#10B981;font-family:\'Share Tech Mono\';letter-spacing:1.8px;">◈ ZERO-TRUST ARCHITECTURE ◈</div><div style="font-size:13.5px;font-weight:900;color:#FFF;letter-spacing:1.6px;margin-top:4px;">BEMASK · A.L.P.H.A. · COMMAND</div></div>'
        '</div>'
        '<div class="soglia-inner-footer">◈ <strong style="color:#F59E0B;">BEMASK SOVEREIGN ARCHITECTURE</strong> · <strong style="color:#FFFFFF;">ENRICO BRAGLIA</strong> · <span style="color:#38BDF8;">ZERO-TRUST RAM</span> ◈</div>'
        '</div></div>'
    )


def render_architect_dossier_content():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0B0E14 0%,#161C26 100%);border:1.5px solid #F59E0B;border-left:6px solid #F59E0B;padding:18px;border-radius:4px;margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <span class="badge-amber">ORIGIN SEAL // INTELLECTUAL PROPERTY</span>
            <span style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#38BDF8;">3-AXIS FRACTAL CORE // ZERO-TRUST RAM</span>
        </div>
        <div style="font-size:21px;font-weight:900;color:#FFFFFF;letter-spacing:1.5px;margin-top:8px;">ENRICO BRAGLIA — SYSTEM ARCHITECT & CREATOR</div>
        <div style="font-size:11px;color:#F59E0B;font-family:'Share Tech Mono',monospace;letter-spacing:1px;margin-top:3px;">30+ YEARS HOSPITALITY DIRECTION · REVENUE INTELLIGENCE · BEMASK SOUND & AI LAB</div>
    </div>
    """, unsafe_allow_html=True)

    v_col, m_col = st.columns([1.25, 1.55])
    with v_col:
        if os.path.exists("architect_manifesto..mp4"):
            st.video("architect_manifesto..mp4", autoplay=True, loop=True, muted=False)
        elif os.path.exists("architect_manifesto.mp4"):
            st.video("architect_manifesto.mp4", autoplay=True, loop=True, muted=False)
        else:
            st.markdown("""
            <div style="background:#090C12;border:1px solid #2B394A;border-radius:4px;padding:22px 14px;text-align:center;">
                <div style="font-size:12px;font-weight:800;color:#F59E0B;letter-spacing:1.2px;">27TH CUBE // 3-AXIS CORE ACTIVE</div>
                <div style="font-size:10px;color:#94A3B8;font-family:'Share Tech Mono',monospace;margin-top:6px;">Carica 'architect_manifesto.mp4' nel repository per il Video Manifesto</div>
            </div>
            """, unsafe_allow_html=True)

        vcard = "MECARD:N:Braglia,Enrico;ORG:BEMASK Sovereign Architecture;NOTE:Creator, Musician & System Architect;;"
        st.markdown(f"""
        <div style="background:#0D1118;border:1px solid #263244;padding:10px;border-radius:4px;margin-top:10px;display:flex;align-items:center;gap:12px;">
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=110x110&color=F59E0B&bgcolor=0D1118&data={vcard}" width="72" style="border:1px solid #F59E0B;padding:3px;" />
            <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#CBD5E1;line-height:1.4;">
                <strong style="color:#F59E0B;">VERIFICA DIRETTA CREATORE</strong><br>
                Inquadra per salvare il contatto ufficiale dell'Architetto.<br>
                <span style="color:#10B981;">ID: EB-BEMASK-2026-ALPHA</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with m_col:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:12.5px;color:#E2E8F0;line-height:1.65;background:#111620;border:1px solid #243042;padding:16px;border-radius:4px;">
            <div style="color:#F59E0B;font-weight:900;font-family:'Orbitron',sans-serif;font-size:12px;margin-bottom:8px;">PERCHÉ QUESTA ARCHITETTURA È DIVERSA</div>
            <p style="margin-bottom:10px;"><strong>BEMASK Sovereign Zero</strong> nasce dall'incontro tra <strong>oltre 30 anni di Direzione Alberghiera, Revenue Management e F&B sul campo</strong>, elettronica industriale, produzione sonora e sintesi AI.</p>
            <ul style="padding-left:18px;margin-bottom:10px;color:#CBD5E1;">
                <li><strong>Il Perno Centrale (3 Assi X·Y·Z):</strong> ogni gesto operativo (<em>Materia</em>) si traduce all'istante in controllo di cassa e margine (<em>Energia</em>) sincronizzato col contesto reale e meteo (<em>Tempo</em>).</li>
                <li><strong>Mitosi Computazionale:</strong> pod leggeri da 1 secondo su smartphone per hotel, bar, reparti diretti o singole P.IVA.</li>
                <li><strong>Sovranità in RAM (0 Byte su Cloud):</strong> nessun dato sensibile salvato sui server remoti.</li>
            </ul>
            <div style="border-top:1px dashed #334155;padding-top:8px;margin-top:8px;font-size:11px;color:#10B981;">
                ◈ Conceived, Directed & Engineered by <strong>Enrico Braglia</strong> // BEMASK Creative & System Lab
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
