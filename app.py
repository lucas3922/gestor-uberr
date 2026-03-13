import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração de App Mobile
st.set_page_config(
    page_title="UberPro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚗"
)

# --- CSS PARA INTERFACE DE APP DARK MODE ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    .block-container { padding-top: 0.5rem; padding-bottom: 2rem; }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Cor das letras para branco em todo o app */
    label, p, span, h1, h2, h3, .stMarkdown { color: #ffffff !important; }

    /* Forçar colunas lado a lado no celular - Ajustado para 2 colunas */
    [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }

    /* Cartões Coloridos */
    .card-faturamento { background-color: #00FF00; color: black !important; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; width: 100% !important; }
    .card-despesa { background-color: #FF0000; color: white !important; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    .card-saldo { background-color: #800080; color: white !important; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    
    .big-val { font-size: 20px; font-weight: bold; }
    .label-card { font-size: 10px; font-weight: 600; text-transform: uppercase; }

    /* Grade de métricas em quadrados */
    .grid-item {
        background-color: #1C1C1E;
        border-radius: 12px;
        padding: 10px 2px;
        text-align: center;
        border: 1px solid #2C2C2E;
        margin-bottom: 5px;
        min-height: 85px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .grid-label { color: #ffffff !important; font-size: 9px; font-weight: bold; text-transform: uppercase; opacity: 0.8; }
    .grid-value { color: #FFFFFF !important; font-size: 14px; font-weight: bold; }

    /* Estilo das Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1C1C1E;
        border-radius: 8px;
        color: #ffffff !important;
        padding: 0 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4500 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"])

if 'contas' not in st.session_state:
    st.session_state.contas = {
        "Aluguel": None, "Luz": None, "Água": None, "Internet": None, 
        "Cartões": None, "Financiamentos": None, "Outras": None
    }

# --- CÁLCULOS TÉCNICOS ---
# Soma ignorando campos vazios (None)
total_casa = sum(v for v in st.session_state.contas.values() if v is not None)

# --- ABAS ---
tab_res, tab_lan, tab_hist, tab_contas = st.tabs(["📊 RESULTADOS", "➕ LANÇAR", "📅 HISTÓRICO", "🏠 CONTAS"])

# --- ABA 1: RESULTADOS ---
with tab_res:
    # Busca o último lançamento para os resultados em tempo real
    if not st.session_state.historico.empty:
        u = st.session_state.historico.iloc[-1]
        rb, rl, rc, rk, rh = u["Bruto"], u["Líquido"], (u["Bruto"] - u["Líquido"]), u["KM"], u["Horas"]
    else:
        rb, rl, rc, rk, rh = 0.0, 0.0, 0.0, 0.0, 0.0

    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento Dia</div><div class='big-val'>R$ {rb:.2f}</div></div>", unsafe_allow_html=True)
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Despesas</div><div class='big-val'>R$ {rc:.2f}</div></div>", unsafe_allow_html=True)
    with c_sub2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo</div><div class='big-val'>R$ {rl:.2f}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    # Grade em 2 colunas x 3 linhas
    g1, g2 = st.columns(2)
    with g1: st.markdown(f"<div class='grid-item'><div class='grid-label'>Viagens</div><div class='grid-value'>{max(0, round(rb/35)) if rb > 0 else 0}</div></div>", unsafe_allow_html=True)
    with g2: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Bruto</div><div class='grid-value'>R$ {(rb/rk if rk > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)

    g3, g4 = st.columns(2)
    with g3: 
        hi, mi = int(rh), int((rh - int(rh)) * 60)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Tempo</div><div class='grid-value'>{hi:02d}:{mi:02d}</div></div>", unsafe_allow_html=True)
    with g4: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/Hora</div><div class='grid-value'>R$ {(rl/rh if rh > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)

    g5, g6 = st.columns(2)
    with g5: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Rodado</div><div class='grid-value'>{rk}</div></div>", unsafe_allow_html=True)
    with g6: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/KM</div><div class='grid-value'>R$ {(rl/rk if rk > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)

    if total_casa > 0:
        prog = min(max(0.0, rl / total_casa), 1.0)
        restante = total_casa - rl
        meta_d = restante / 20 # Cálculo sugerido de 20 dias
        
        st.write(f"🏠 *Abate das Contas da Casa:* {prog*100:.1f}%")
        st.progress(prog)
        # Resultados reais solicitados
        st.write(f"📉 *Restante da dívida do mês:* R$ {max(0.0, restante):.2f}")
        st.write(f"🎯 *Meta diária para bater a meta:* R$ {max(0.0, meta_d):.2f}")

# --- ABA 2: LANÇAR ---
with tab_lan:
    st.subheader("Lançar Dia")
    b_in = st.number_input("Ganho Bruto", value=None, placeholder=" ")
    k_in = st.number_input("KM Total", value=None, placeholder=" ")
    h_in = st.number_input("Horas", value=None, placeholder=" ")
    c_in = st.number_input("Combustível", value=None, placeholder=" ")
    
    if st.button("💾 SALVAR DIA", use_container_width=True):
        if b_in is not None:
            # Cálculos internos
            l_calc = b_in - (c_in or 0.0)
            k_calc = k_in or 1.0
            h_calc = h_in or 1.0
            
            novo = {
                "Data": datetime.now().strftime("%d/%m/%Y"), 
                "Bruto": b_in, "Líquido": l_calc, 
                "KM": k_calc, "Horas": h_calc, 
                "KM_Liq": l_calc/k_calc, "Hora_Liq": l_calc/h_calc
            }
            st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo])], ignore_index=True)
            st.success("Salvo!")
            st.rerun()

# --- ABA 3: HISTÓRICO ---
with tab_hist:
    if not st.session_state.historico.empty:
        st.dataframe(st.session_state.historico, use_container_width=True)
    else:
        st.info("Sem dados no histórico.")

# --- ABA 4: CONTAS DA CASA ---
with tab_contas:
    st.subheader("🏠 Gestão Financeira da Casa")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.contas["Aluguel"] = st.number_input("Aluguel", value=st.session_state.contas["Aluguel"], placeholder=" ")
        st.session_state.contas["Luz"] = st.number_input("Conta de Luz", value=st.session_state.contas["Luz"], placeholder=" ")
        st.session_state.contas["Água"] = st.number_input("Conta de Água", value=st.session_state.contas["Água"], placeholder=" ")
        st.session_state.contas["Internet"] = st.number_input("Internet", value=st.session_state.contas["Internet"], placeholder=" ")
    with col2:
        st.session_state.contas["Cartões"] = st.number_input("Cartões de Crédito", value=st.session_state.contas["Cartões"], placeholder=" ")
        st.session_state.contas["Financiamentos"] = st.number_input("Financiamentos", value=st.session_state.contas["Financiamentos"], placeholder=" ")
        st.session_state.contas["Outras"] = st.number_input("Outras Contas", value=st.session_state.contas["Outras"], placeholder=" ")
    
    st.divider()
    st.metric("TOTAL DE DESPESAS", f"R$ {total_casa:.2f}")
