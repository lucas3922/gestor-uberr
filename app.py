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

    /* Forçar colunas lado a lado no celular */
    [data-testid="column"] {
        width: 33% !important;
        flex: 1 1 30% !important;
        min-width: 30% !important;
    }

    /* Cartões Coloridos Estilo Print */
    .card-faturamento { background-color: #00FF00; color: black; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; width: 100% !important; }
    .card-despesa { background-color: #FF0000; color: white; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    .card-saldo { background-color: #800080; color: white; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    
    .big-val { font-size: 22px; font-weight: bold; }
    .label-card { font-size: 11px; font-weight: 600; text-transform: uppercase; }

    /* Grade de métricas em quadrados */
    .grid-item {
        background-color: #1C1C1E;
        border-radius: 12px;
        padding: 10px 2px;
        text-align: center;
        border: 1px solid #2C2C2E;
        margin-bottom: 5px;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .grid-label { color: #8E8E93; font-size: 9px; font-weight: bold; text-transform: uppercase; }
    .grid-value { color: #FFFFFF; font-size: 15px; font-weight: bold; }

    /* Estilo das Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1C1C1E;
        border-radius: 8px;
        color: #8E8E93;
        padding: 0 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"])

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏠 Contas Fixas")
    luz = st.number_input("Luz", 0.0)
    agua = st.number_input("Água", 0.0)
    internet = st.number_input("Internet", 0.0)
    aluguel = st.number_input("Aluguel", 0.0)
    mercado = st.number_input("Mercado", 0.0)
    outros = st.number_input("Outros", 0.0)
    total_casa = luz + agua + internet + aluguel + mercado + outros

# --- ESTADO DOS INPUTS ---
if 'bruto' not in st.session_state: st.session_state.bruto = 0.0
if 'km' not in st.session_state: st.session_state.km = 1.0
if 'horas' not in st.session_state: st.session_state.horas = 1.0
if 'comb' not in st.session_state: st.session_state.comb = 0.0

# --- CÁLCULOS ---
liq = st.session_state.bruto - st.session_state.comb
km_b = st.session_state.bruto / st.session_state.km if st.session_state.km > 0 else 0
km_l = liq / st.session_state.km if st.session_state.km > 0 else 0
hr_l = liq / st.session_state.horas if st.session_state.horas > 0 else 0
viagens = max(1, round(st.session_state.bruto / 35)) if st.session_state.bruto > 0 else 0

# --- NAVEGAÇÃO ---
tab_res, tab_lan, tab_hist = st.tabs(["📊 RESULTADOS", "➕ LANÇAR", "📅 HISTÓRICO"])

with tab_res:
    # Topo
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento Dia</div><div class='big-val'>R$ {st.session_state.bruto:.2f}</div></div>", unsafe_allow_html=True)
    
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Despesas</div><div class='big-val'>R$ {st.session_state.comb:.2f}</div></div>", unsafe_allow_html=True)
    with c_sub2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo</div><div class='big-val'>R$ {liq:.2f}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    
    # GRADE QUADRADA (Forçada via CSS)
    g1, g2, g3 = st.columns(3)
    with g1: st.markdown(f"<div class='grid-item'><div class='grid-label'>Viagens</div><div class='grid-value'>{viagens}</div></div>", unsafe_allow_html=True)
    with g2: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Bruto</div><div class='grid-value'>R$ {km_b:.2f}</div></div>", unsafe_allow_html=True)
    with g3: 
        h, m = int(st.session_state.horas), int((st.session_state.horas - int(st.session_state.horas)) * 60)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Tempo</div><div class='grid-value'>{h:02d}:{m:02d}</div></div>", unsafe_allow_html=True)

    g4, g5, g6 = st.columns(3)
    with g4: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/Hora</div><div class='grid-value'>R$ {hr_l:.2f}</div></div>", unsafe_allow_html=True)
    with g5: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Rodado</div><div class='grid-value'>{st.session_state.km}</div></div>", unsafe_allow_html=True)
    with g6: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/KM</div><div class='grid-value'>R$ {km_l:.2f}</div></div>", unsafe_allow_html=True)

    if total_casa > 0:
        prog = min(max(0.0, liq / total_casa), 1.0)
        st.write(f"🏠 *Meta Casa:* {prog*100:.1f}%")
        st.progress(prog)

with tab_lan:
    st.subheader("Entrada de Dados")
    st.session_state.bruto = st.number_input("Ganho Bruto", value=st.session_state.bruto)
    st.session_state.km = st.number_input("KM Total", value=st.session_state.km)
    st.session_state.horas = st.number_input("Horas", value=st.session_state.horas)
    st.session_state.comb = st.number_input("Combustível", value=st.session_state.comb)
    
    if st.button("💾 SALVAR DIA", use_container_width=True):
        novo = {"Data": datetime.now().strftime("%d/%m/%Y"), "Bruto": st.session_state.bruto, "Líquido": liq, "KM": st.session_state.km, "Horas": st.session_state.horas, "KM_Liq": km_l, "Hora_Liq": hr_l}
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo])], ignore_index=True)
        st.success("Salvo!")

with tab_hist:
    if not st.session_state.historico.empty:
        st.dataframe(st.session_state.historico, use_container_width=True)
        if st.button("Zerar Histórico"):
            st.session_state.historico = pd.DataFrame(columns=st.session_state.historico.columns)
            st.rerun()
