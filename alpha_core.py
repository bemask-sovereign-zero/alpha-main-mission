import os
import json
from datetime import datetime
import streamlit as st

# ==============================================================================
# 6. THE 9 VECTORS x 5 ROWS = 1 TO 2^9 (512 STATES / 45 CHANNELS) OF MOONBASE A.L.P.H.A.
# ==============================================================================
base_squares = [
    {
        "id": "SQ01", "bit": 0, "short": "B1 FRONT", "theme": "AMBER", "totem": "EAGLE",
        "title": "01\nFRONT & APEX",
        "rows": [
            {"lbl": "1. Sovereign Apex", "url": "https://sovereign-apex.streamlit.app", "desc": "7 Room Tiers x 24 Yield Bands Dynamic Pricing Engine"},
            {"lbl": "2. Boschetto PMS", "url": "https://boschetto.streamlit.app", "desc": "Front Desk Arrivals, Departures, Room Rack & Guest Ledger"},
            {"lbl": "3. Fast Quote & Grp", "url": "https://sovereign-apex.streamlit.app/?module=quote", "desc": "Instant Multi-Room & Group Quotation Calculator"},
            {"lbl": "4. Night Audit Safe", "url": "https://boschetto.streamlit.app/?module=audit", "desc": "End-of-Day Cash Closure, City Tax & Shift Handover"},
            {"lbl": "5. FO Supplies Buy", "url": "https://boschetto.streamlit.app/?module=fo_supply", "desc": "Front Office Hardware, Keycards, Stationery & Toner Procurement"}
        ]
    },
    {
        "id": "SQ02", "bit": 1, "short": "B2 BEV", "theme": "EMERALD", "totem": "QUEEN",
        "title": "02\nLAZERS BEV",
        "rows": [
            {"lbl": "1. Mixology & Pour", "url": "https://bemask-lazers.streamlit.app/?sub=mixology", "desc": "Cocktail Recipe Pour Cost (ml), Drink Margins & Bar List"},
            {"lbl": "2. Wine & Sommelier", "url": "https://bemask-lazers.streamlit.app/?sub=wine", "desc": "Wine Cellar Rotation, Bottle Mark-up & Pairing Matrix"},
            {"lbl": "3. Bar Consumables", "url": "https://bemask-lazers.streamlit.app/?sub=bev_opex", "desc": "OPEX Purchasing: Spirits, Beer Kegs, Coffee, Garnish & Disposables"},
            {"lbl": "4. Bar Equipment", "url": "https://bemask-lazers.streamlit.app/?sub=bev_capex", "desc": "CAPEX Purchasing: Glassware, Crystal, Shakers, Blenders & Breakage"},
            {"lbl": "5. Minibar & Kiosk", "url": "https://bemask-lazers.streamlit.app/?sub=minibar", "desc": "Room Minibar Restocking & Pool/Beach Liquid Kiosks"}
        ]
    },
    {
        "id": "SQ03", "bit": 2, "short": "B3 FOOD", "theme": "CYAN", "totem": "BISHOP",
        "title": "03\nLAZERS FOOD",
        "rows": [
            {"lbl": "1. Kitchen FoodCost", "url": "https://bemask-lazers.streamlit.app/?sub=foodcost", "desc": "Dish Recipes, Grammage, Yield Waste % & Kasavana Matrix"},
            {"lbl": "2. Board BB/HB/FB", "url": "https://bemask-lazers.streamlit.app/?sub=boards", "desc": "Real Buffet & Pension Meal Cost Synced with Sovereign Apex"},
            {"lbl": "3. Food Consumables", "url": "https://bemask-lazers.streamlit.app/?sub=food_opex", "desc": "OPEX Purchasing: Fresh/Dry Food, Vacuum Bags, Foil & Kitchen Chemicals"},
            {"lbl": "4. Food Equipment", "url": "https://bemask-lazers.streamlit.app/?sub=food_capex", "desc": "CAPEX Purchasing: Porcelain Plates, Cutlery, Cookware & Table Linen"},
            {"lbl": "5. Banquet & Events", "url": "https://bemask-lazers.streamlit.app/?sub=banquet", "desc": "Gala Dinners, Buffet Events & Special Catering Operations"}
        ]
    },
    {
        "id": "SQ04", "bit": 3, "short": "B4 BEACH", "theme": "PURPLE", "totem": "COMMLOCK",
        "title": "04\nBEACH & POOL",
        "rows": [
            {"lbl": "1. Beach Rows 1-4", "url": "https://boschetto.streamlit.app/?module=beach_map", "desc": "Interactive Umbrella Grid: 1st Row VIP, 2nd Row, 3rd Row & Standard"},
            {"lbl": "2. Package & Upgrd", "url": "https://sovereign-apex.streamlit.app/?module=beach_yield", "desc": "Included vs Excluded Arrangement Rules & 1st/2nd Row Upgrade Supplements"},
            {"lbl": "3. Pool & Cabanas", "url": "https://boschetto.streamlit.app/?module=pool_map", "desc": "Waterfront Sunbeds, VIP Bali Beds & External Day-Use Passes"},
            {"lbl": "4. Lido Consumables", "url": "https://boschetto.streamlit.app/?module=beach_opex", "desc": "OPEX Purchasing: Beach Towels, Wristbands, Sunscreen & Pool Chlorine"},
            {"lbl": "5. Lido Hardware", "url": "https://boschetto.streamlit.app/?module=beach_capex", "desc": "CAPEX Purchasing: Sunbeds, Umbrellas, Deckchairs, Gazebos & Walkways"}
        ]
    },
    {
        "id": "SQ05", "bit": 4, "short": "B5 SPA", "theme": "RED", "totem": "KING",
        "title": "05\nSPA & AYURVEDA",
        "rows": [
            {"lbl": "1. Massage & Tibet", "url": "https://boschetto.streamlit.app/?module=spa_cabins", "desc": "Cabin Matrix: Massages, Ayurveda, Five Tibetans & Pirate Detox Specials"},
            {"lbl": "2. Sauna & Steam", "url": "https://boschetto.streamlit.app/?module=thermae", "desc": "Wet Zone Slot Quotas: Finnish Sauna, Turkish Bath, Hydro & Private Spa"},
            {"lbl": "3. Spa Pass & Pack", "url": "https://sovereign-apex.streamlit.app/?module=spa_yield", "desc": "Suite Included Spa Credits, Dynamic Off-Peak Pricing & Day-Spa Vouchers"},
            {"lbl": "4. Spa Oils & Retail", "url": "https://boschetto.streamlit.app/?module=spa_opex", "desc": "OPEX & Boutique: Warm Massage Oils, Essential Oils, Muds & Retail Creams"},
            {"lbl": "5. Spa Equipment", "url": "https://boschetto.streamlit.app/?module=spa_capex", "desc": "CAPEX Purchasing: Massage Tables, Hot Stones, Steamers, Robes & Slippers"}
        ]
    },
    {
        "id": "SQ06", "bit": 5, "short": "B6 SKA", "theme": "AMBER", "totem": "KNIGHT",
        "title": "06\nS.K.A. & ROOMS",
        "rows": [
            {"lbl": "1. Housekeeping", "url": "https://boschetto.streamlit.app/?module=hk", "desc": "Floor Room Status (Clean/Dirty/Priority), Maids Roster & Inspections"},
            {"lbl": "2. Room Consumables", "url": "https://boschetto.streamlit.app/?module=hk_opex", "desc": "OPEX Purchasing: Courtesy Amenities, Cleaning Chemicals, Paper & Linen"},
            {"lbl": "3. S.K.A. Tech Core", "url": "https://sovereign-kinetic-architecture.streamlit.app", "desc": "Facility Maintenance Tickets, Boilers, HVAC & Electrical Shields"},
            {"lbl": "4. HACCP Telemetry", "url": "https://sovereign-kinetic-architecture.streamlit.app/?sub=haccp", "desc": "24/7 Temperature Probes: Kitchen Fridges, Pool Water & Spa Steamers"},
            {"lbl": "5. Tech Hardware", "url": "https://sovereign-kinetic-architecture.streamlit.app/?sub=tech_capex", "desc": "CAPEX Purchasing: Spare Parts, Pumps, LED Bulbs, Filters & Tools"}
        ]
    },
    {
        "id": "SQ07", "bit": 6, "short": "B7 ROP", "theme": "EMERALD", "totem": "ROOK",
        "title": "07\nPUNTO ACQUISTO",
        "rows": [
            {"lbl": "1. Soglia Riordino ROP", "url": "https://bemask-lazers.streamlit.app/?sub=rop", "desc": "Calcolo Automatico Punto Acquisto: (Consumo x Lead Time) + Scudo 96h"},
            {"lbl": "2. Scudo Autonomia 96h", "url": "https://bemask-lazers.streamlit.app/?sub=shield96", "desc": "Copertura Dispensa Emergenza per Ospiti In-House + Staff Alloggiato"},
            {"lbl": "3. Lead Time Fornitori", "url": "https://bemask-lazers.streamlit.app/?sub=vendors", "desc": "Mappa Consegne, Giorni Critici e Semaforo Riordino Immediato"},
            {"lbl": "4. Fatture XML & Rese", "url": "https://bemask-lazers.streamlit.app/?sub=xml", "desc": "Controllo Prezzi Acquisto, Peso Sgocciolato e Sfridi Carni/Pesce"},
            {"lbl": "5. Ordine Rapido", "url": "https://bemask-lazers.streamlit.app/?sub=order", "desc": "Generazione Lista Acquisto Certificata per Economato e Cucina"}
        ]
    },
    {
        "id": "SQ08", "bit": 7, "short": "B8 ASL", "theme": "CYAN", "totem": "QUEEN",
        "title": "08\nHACCP & ASL",
        "rows": [
            {"lbl": "1. Registro Temperature", "url": "https://ska-boschetto.streamlit.app/?sub=asl", "desc": "Certificazione Giornaliera Celle -18°C, Frigo +4°C e Vetrine Buffet"},
            {"lbl": "2. Firme PIN Brigata", "url": "https://ska-boschetto.streamlit.app/?sub=pins", "desc": "Validazione Operatori in Turno con Codice PIN Personale a 4 Cifre"},
            {"lbl": "3. Lotti & Abbattimento", "url": "https://ska-boschetto.streamlit.app/?sub=lots", "desc": "Tracciabilità Materie Prime, Cicli Abbattitore e Scadenze"},
            {"lbl": "4. Piano Sanificazione", "url": "https://ska-boschetto.streamlit.app/?sub=clean", "desc": "Check-list Pulizia Cappa, Linee Cucina, Pasticceria e Bar"},
            {"lbl": "5. Stampa Ufficiale ASL", "url": "https://ska-boschetto.streamlit.app/?sub=print_asl", "desc": "Esportazione Immediata Registro HTML/CSV Pronto per Ispezione"}
        ]
    },
    {
        "id": "SQ09", "bit": 8, "short": "B9 GOP", "theme": "RED", "totem": "EAGLE",
        "title": "09\nMULTI-P.IVA & GOP",
        "rows": [
            {"lbl": "1. Split Multi-P.IVA", "url": "https://bemask-lazers.streamlit.app/?sub=piva", "desc": "Ripartizione Automatica Ricavi e Costi tra Società Gestione e F&B"},
            {"lbl": "2. Floor Pasto HB/FB", "url": "https://bemask-lazers.streamlit.app/?sub=floor", "desc": "Scorporo Industriale Costo Vivo Pasto + Brigata su Sovereign Zero"},
            {"lbl": "3. Semaforo Zero-Fee", "url": "https://bemask-lazers.streamlit.app/?sub=thefork", "desc": "Blocco Automatico Portali Esterni a Sala Satura per Risparmio Commissioni"},
            {"lbl": "4. MOL & GOPPAR Live", "url": "https://sovereign-apex.streamlit.app/?module=goppar", "desc": "Margine Operativo Lordo Giornaliero Consolidato Camere + Ristorante"},
            {"lbl": "5. Export Revisore", "url": "https://sovereign-apex.streamlit.app/?module=audit_export", "desc": "Report Direzionale Completo per Proprietà e Studio Commercialista"}
        ]
    }
]

if "active_bits_9" not in st.session_state:
    # Di default accende i primi 6 settori storici, espandibili da 1 fino a 9 (2^9 = 512 stati)
    st.session_state.active_bits_9 = [True, True, True, True, True, True, False, False, False]
if "alpha_visitors" not in st.session_state:
    st.session_state.alpha_visitors = 34

state_code_512 = sum((1 << i) for i, b in enumerate(st.session_state.active_bits_9) if b)
bin_str_9 = "".join(["1" if b else "0" for b in st.session_state.active_bits_9])
active_base = [sq for i, sq in enumerate(base_squares) if st.session_state.active_bits_9[i]]
if not active_base:
    st.session_state.active_bits_9[0] = True
    active_base = [base_squares[0]]

all_squares = active_base + st.session_state.custom_squares
active_channels = len(all_squares) * 5

with st.expander(f"⚡ SCALABLE ARCHITECTURE 1 → 2⁹ // STATE #{state_code_512}/512 | SIGNATURE: {bin_str_9} ({active_channels} CHANNELS LIVE) | VISITORS: {st.session_state.alpha_visitors}", expanded=False):
    b_cols = st.columns(9)
    for i, sq_item in enumerate(base_squares):
        with b_cols[i]:
            t_val = st.toggle(sq_item["short"], value=st.session_state.active_bits_9[i], key=f"b9_sw_{i}")
            if t_val != st.session_state.active_bits_9[i]:
                st.session_state.active_bits_9[i] = t_val
                st.session_state.expanded_sq_id = None
                st.rerun()
    pr1, pr2, pr3 = st.columns(3)
    if pr1.button("1️⃣ SINGLE NODE (2⁰ = 1 MODULE)", type="secondary", use_container_width=True):
        st.session_state.active_bits_9 = [True] + [False]*8
        st.session_state.expanded_sq_id = None
        st.rerun()
    if pr2.button("6️⃣ CLASSIC ALPHA (6 SECTORS = 30 CHANNELS)", type="secondary", use_container_width=True):
        st.session_state.active_bits_9 = [True]*6 + [False]*3
        st.session_state.expanded_sq_id = None
        st.rerun()
    if pr3.button("9️⃣ FULL MATRIX 2⁹ (STATE #511 = 45 CHANNELS)", type="secondary", use_container_width=True):
        st.session_state.active_bits_9 = [True]*9
        st.session_state.expanded_sq_id = None
        st.rerun()

# ==============================================================================
# 7. CHESSBOARD + EMS-1975 SYNTHESIZER WITH AUTOMATIC TOUCH AUDIO HOOK
# ==============================================================================
if st.session_state.opened_sq_id is None:
    col_grid, col_tower = st.columns([2.85, 1.05], gap="small")

    with col_grid:
        tot_sq = len(all_squares)
        cols_per_row = 1 if tot_sq == 1 else (2 if tot_sq in [2, 4] else 3)
        rows_count = (tot_sq + cols_per_row - 1) // cols_per_row
        for r_i in range(rows_count):
            cols = st.columns(cols_per_row, gap="small")
            for c_i in range(cols_per_row):
                idx = r_i * cols_per_row + c_i
                if idx < tot_sq:
                    sq = all_squares[idx]
                    sid = sq["id"]
                    theme = sq["theme"]
                    t_icon = sq.get("totem", "EAGLE")
                    with cols[c_i]:
                        if st.session_state.expanded_sq_id == sid:
                            for r_num, r_obj in enumerate(sq["rows"], 1):
                                r_txt = r_obj["lbl"] if isinstance(r_obj, dict) else r_obj
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
        sound_console_html = """
        <div style="background:#080c14;border:1.5px solid #ffb703;border-top:4px solid #ffb703;border-radius:4px;padding:8px;font-family:monospace;color:#fff;">
            <div style="font-size:10px;font-weight:900;color:#ffb703;letter-spacing:1.5px;margin-bottom:6px;border-bottom:1px solid #263248;padding-bottom:4px;display:flex;justify-content:space-between;">
                <span>ALPHA EMS-1975 SYNTH</span>
                <span id="st-led" style="color:#00ff9d;">TOUCH ARMED</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:5px;">
                <button onclick="playComputerBurst()" id="btn-tel" style="background:#ffb703;color:#000;border:none;padding:7px 4px;font-weight:900;font-size:10px;cursor:pointer;border-radius:2px;letter-spacing:0.5px;">
                    ▶ X5-7 DATA BURST
                </button>
                <button onclick="playCommlock1975()" style="background:#e2e8f0;color:#000;border:none;padding:7px 4px;font-weight:900;font-size:10px;cursor:pointer;border-radius:2px;letter-spacing:0.5px;">
                    ◈ COMMLOCK 1975
                </button>
            </div>
            <button onclick="playAlphaKlaxon()" style="width:100%;background:#ff2a54;color:#fff;border:none;padding:6px 4px;font-weight:900;font-size:10px;cursor:pointer;border-radius:2px;letter-spacing:1px;">
                ▲ ALPHA KLAXON SIREN
            </button>
        </div>
        <script>
        let audioCtx = null;

        function initCtx() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        function createAnalogChain() {
            const now = audioCtx.currentTime;
            const filter = audioCtx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.setValueAtTime(1650, now);
            filter.Q.setValueAtTime(3.2, now);

            const delay = audioCtx.createDelay();
            delay.delayTime.setValueAtTime(0.065, now);
            const fb = audioCtx.createGain();
            fb.gain.setValueAtTime(0.28, now);

            filter.connect(audioCtx.destination);
            filter.connect(delay);
            delay.connect(fb);
            fb.connect(delay);
            delay.connect(audioCtx.destination);
            return filter;
        }

        function playTouchPulse() {
            try {
                initCtx();
                const now = audioCtx.currentTime;
                const bus = createAnalogChain();
                const freqs = [1480, 1960, 2350];
                freqs.forEach((f, idx) => {
                    const t = now + (idx * 0.045);
                    const o1 = audioCtx.createOscillator();
                    const o2 = audioCtx.createOscillator();
                    const env = audioCtx.createGain();
                    o1.type = 'sine'; o2.type = 'triangle';
                    o1.frequency.setValueAtTime(f, t);
                    o2.frequency.setValueAtTime(f * 1.414, t);
                    env.gain.setValueAtTime(0.001, t);
                    env.gain.linearRampToValueAtTime(0.075, t + 0.005);
                    env.gain.exponentialRampToValueAtTime(0.001, t + 0.042);
                    o1.connect(env); o2.connect(env); env.connect(bus);
                    o1.start(t); o2.start(t);
                    o1.stop(t + 0.044); o2.stop(t + 0.044);
                });
            } catch (e) {}
        }

        try {
            const parentDoc = window.parent.document;
            if (!parentDoc.alphaTouchBound) {
                parentDoc.alphaTouchBound = true;
                parentDoc.addEventListener('pointerdown', (ev) => {
                    const btn = ev.target.closest('button');
                    if (btn) {
                        playTouchPulse();
                    }
                }, true);
            }
        } catch (e) {}

        function playComputerBurst() {
            initCtx();
            const led = document.getElementById('st-led');
            led.innerText = 'COMPUTING...';
            led.style.color = '#00f0ff';

            const now = audioCtx.currentTime;
            const bus = createAnalogChain();

            const hum = audioCtx.createOscillator();
            const humGain = audioCtx.createGain();
            hum.type = 'sawtooth';
            hum.frequency.setValueAtTime(110, now);
            humGain.gain.setValueAtTime(0.025, now);
            humGain.gain.exponentialRampToValueAtTime(0.001, now + 1.25);
            hum.connect(humGain);
            humGain.connect(audioCtx.destination);
            hum.start(now);
            hum.stop(now + 1.26);

            const steps = 24;
            const stepTime = 0.046;
            const alphaFreqs = [1180, 1420, 1680, 1930, 2240, 2580, 1310, 2890, 1540];

            for (let i = 0; i < steps; i++) {
                if (Math.random() < 0.14) continue;
                const t = now + (i * stepTime);
                const osc = audioCtx.createOscillator();
                const mod = audioCtx.createOscillator();
                const modGain = audioCtx.createGain();
                const env = audioCtx.createGain();

                const baseF = alphaFreqs[Math.floor(Math.random() * alphaFreqs.length)];
                osc.type = 'sine';
                osc.frequency.setValueAtTime(baseF, t);

                mod.type = 'triangle';
                mod.frequency.setValueAtTime(baseF * 1.414, t);
                modGain.gain.setValueAtTime(320, t);

                mod.connect(modGain);
                modGain.connect(osc.frequency);

                env.gain.setValueAtTime(0.001, t);
                env.gain.linearRampToValueAtTime(0.09, t + 0.004);
                env.gain.exponentialRampToValueAtTime(0.002, t + stepTime - 0.004);

                osc.connect(env);
                env.connect(bus);

                osc.start(t); mod.start(t);
                osc.stop(t + stepTime); mod.stop(t + stepTime);
            }

            setTimeout(() => {
                led.innerText = 'TOUCH ARMED';
                led.style.color = '#00ff9d';
            }, 1250);
        }

        function playCommlock1975() {
            initCtx();
            const now = audioCtx.currentTime;
            const bus = createAnalogChain();
            const pattern = [
                {t: 0.00, f1: 1480, f2: 2110, d: 0.11},
                {t: 0.13, f1: 1960, f2: 2790, d: 0.18},
                {t: 0.34, f1: 1480, f2: 2110, d: 0.11},
                {t: 0.47, f1: 2350, f2: 3320, d: 0.24}
            ];
            pattern.forEach(p => {
                const start = now + p.t;
                const o1 = audioCtx.createOscillator();
                const o2 = audioCtx.createOscillator();
                const env = audioCtx.createGain();
                o1.type = 'sine'; o2.type = 'sine';
                o1.frequency.setValueAtTime(p.f1, start);
                o2.frequency.setValueAtTime(p.f2, start);
                env.gain.setValueAtTime(0.001, start);
                env.gain.linearRampToValueAtTime(0.08, start + 0.008);
                env.gain.exponentialRampToValueAtTime(0.001, start + p.d);
                o1.connect(env); o2.connect(env); env.connect(bus);
                o1.start(start); o2.start(start);
                o1.stop(start + p.d + 0.01); o2.stop(start + p.d + 0.01);
            });
        }

        function playAlphaKlaxon() {
            initCtx();
            const now = audioCtx.currentTime;
            const filter = audioCtx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(1350, now);
            filter.Q.setValueAtTime(4.0, now);
            filter.connect(audioCtx.destination);

            for (let i = 0; i < 4; i++) {
                const t = now + (i * 0.28);
                const osc1 = audioCtx.createOscillator();
                const osc2 = audioCtx.createOscillator();
                const env = audioCtx.createGain();
                const fBase = (i % 2 === 0) ? 585 : 440;
                osc1.type = 'sawtooth'; osc2.type = 'square';
                osc1.frequency.setValueAtTime(fBase, t);
                osc2.frequency.setValueAtTime(fBase * 1.008, t);
                env.gain.setValueAtTime(0.08, t);
                env.gain.exponentialRampToValueAtTime(0.01, t + 0.25);
                osc1.connect(env); osc2.connect(env); env.connect(filter);
                osc1.start(t); osc2.start(t);
                osc1.stop(t + 0.26); osc2.stop(t + 0.26);
            }
        }
        </script>
        """
        components.html(sound_console_html, height=122)

        qr_sel = st.selectbox(
            "QR TARGET MODULE:",
            [
                "00 ALPHA MAIN MISSION",
                "01 SOVEREIGN APEX",
                "02 LAZERS BEVERAGE",
                "03 LAZERS FOOD",
                "04 BEACH & POOL",
                "05 SPA & AYURVEDA",
                "06 S.K.A. & ROOMS",
                "07 PUNTO ACQUISTO (ROP)",
                "08 HACCP & ASL REGISTRY",
                "09 MULTI-P.IVA & GOPPAR"
            ],
            label_visibility="collapsed"
        )
        qr_map = {
            "00 ALPHA MAIN MISSION": "https://alpha-main-mission.streamlit.app",
            "01 SOVEREIGN APEX": "https://sovereign-apex.streamlit.app",
            "02 LAZERS BEVERAGE": "https://bemask-lazers.streamlit.app/?sub=bev",
            "03 LAZERS FOOD": "https://bemask-lazers.streamlit.app/?sub=food",
            "04 BEACH & POOL": "https://boschetto.streamlit.app/?module=beach",
            "05 SPA & AYURVEDA": "https://boschetto.streamlit.app/?module=spa",
            "06 S.K.A. & ROOMS": "https://sovereign-kinetic-architecture.streamlit.app",
            "07 PUNTO ACQUISTO (ROP)": "https://bemask-lazers.streamlit.app/?sub=rop",
            "08 HACCP & ASL REGISTRY": "https://ska-boschetto.streamlit.app/?sub=asl",
            "09 MULTI-P.IVA & GOPPAR": "https://bemask-lazers.streamlit.app/?sub=piva"
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
            f"<div style='font-family:Share Tech Mono,monospace;font-size:0.54rem;color:#00ff9d;'>STATE #{state_code_512}/512 | VISITORS: {st.session_state.alpha_visitors}</div>"
            f"<div style='font-family:Share Tech Mono,monospace;font-size:0.52rem;color:#94a3b8;'>{target_qr_url.replace('https://', '')}</div>"
            f"</div>"
            f"</div>"
        )
        st.markdown(tower_html, unsafe_allow_html=True)

# ==============================================================================
# 8. INTERNAL 45-BUTTON LAUNCH BRIDGE & TELEMETRY BRIEFING
# ==============================================================================
else:
    sid = st.session_state.opened_sq_id
    r_num = st.session_state.opened_row_num
    sq_obj = next(x for x in all_squares if x["id"] == sid)
    clean_name = sq_obj["title"].replace("\n", " - ")
    row_obj = sq_obj["rows"][r_num - 1]
    row_label = row_obj["lbl"]
    target_url = row_obj["url"]
    row_desc = row_obj["desc"]

    if st.button(f"⬅ RETURN TO MAIN MISSION ({clean_name})", type="secondary", use_container_width=True):
        st.session_state.opened_sq_id = None
        st.session_state.expanded_sq_id = None
        st.rerun()

    st.markdown(f"#### {clean_name} // {row_label}")
    st.markdown(
        f"<div style='background:#080d18;border:1.5px solid #ffb703;border-left:6px solid #ffb703;padding:18px;border-radius:4px;margin-top:10px;'>"
        f"<div style='font-family:Michroma,Orbitron,sans-serif;font-size:0.85rem;color:#ffb703;'>DIRECT HYPER-BRIDGE // NODE {sid}-R0{r_num} (STATE #{state_code_512}/512)</div>"
        f"<div style='font-family:Inter,sans-serif;font-size:0.92rem;color:#ffffff;font-weight:700;margin-top:8px;'>{row_desc}</div>"
        f"<div style='font-family:Share Tech Mono,monospace;font-size:0.78rem;color:#38bdf8;margin:6px 0 16px 0;'>Target Endpoint: <b>{target_url}</b></div>"
        f"<a href='{target_url}' target='_blank' style='display:inline-block;background:#ffb703;color:#000;font-family:Orbitron,sans-serif;font-weight:900;padding:10px 20px;border-radius:3px;text-decoration:none;letter-spacing:0.08em;'>"
        f"🚀 LAUNCH {row_label.upper()} MODULE</a>"
        f"</div>",
        unsafe_allow_html=True
    )
