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

# --- CSS PARA INTERFACE DE APP (FIXA E SEM SCROLL) ---
st.markdown("""
<style>
    /* Estilo do Fundo e Container */
    .stApp { background-color: #000000; color: #ffffff; }
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    
    /* Esconder elementos do Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Cartões Coloridos (Estilo seu print) */
    .card-faturamento { background-color: #00FF00; color: black; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 10px; }
    .card-despesa { background-color: #FF0000; color: white; border-radius: 10px; padding: 15px; text-align: center; }
    .card-saldo { background-color: #800080; color: white; border-radius: 10px; padding: 15px; text-align: center; }
    
    .big-val { font-size: 26px; font-weight: bold; }
    .label-card { font-size: 14px; font-weight: 500; }

    /* Grade de métricas cinzas */
    .grid-item {
        background-color: #1C1C1E;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        border: 1px solid #2C2C2E;
        margin-bottom: 8px;
    }
    .grid-label { color: #8E8E93; font-size: 11px; text-transform: uppercase; }
    .grid-value { color: #FFFFFF; font-size: 18px; font-weight: bold; }

    /* Estilização das Tabs para parecer menu de App */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #2C2C2E;
        border-radius: 10px;
        color: white;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4500 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"])

# --- SIDEBAR (CONTAS DA CASA) ---
with st.sidebar:
    st.header("🏠 Configurar Contas")
    luz = st.number_input("Luz", 0.0)
    agua = st.number_input("Água", 0.0)
    internet = st.number_input("Internet", 0.0)
    aluguel = st.number_input("Aluguel", 0.0)
    mercado = st.number_input("Mercado", 0.0)
    outros = st.number_input("Outros", 0.0)
    total_casa = luz + agua + internet + aluguel + mercado + outros

# --- VARIÁVEIS DE CÁLCULO (INICIALIZAÇÃO) ---
if 'input_bruto' not in st.session_state: st.session_state.input_bruto = 0.0
if 'input_km' not in st.session_state: st.session_state.input_km = 1.0
if 'input_horas' not in st.session_state: st.session_state.input_horas = 1.0
if 'input_comb' not in st.session_state: st.session_state.input_comb = 0.0

# Cálculos Base
liq_v = st.session_state.input_bruto - st.session_state.input_comb
km_liq_v = liq_v / st.session_state.input_km if st.session_state.input_km > 0 else 0
hr_liq_v = liq_v / st.session_state.input_horas if st.session_state.input_horas > 0 else 0

# --- NAVEGAÇÃO POR TABS ---
tab_res, tab_lan, tab_hist = st.tabs(["📊 RESULTADOS", "➕ LANÇAR", "📅 HISTÓRICO"])

# --- TAB 1: RESULTADOS (A PRIMEIRA QUE APARECE) ---
with tab_res:
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento Dia</div><div class='big-val'>R$ {st.session_state.input_bruto:.2f}</div></div>", unsafe_allow_html=True)
    
    col_mid1, col_mid2 = st.columns(2)
    with col_mid1:
        st.markdown(f"<div class='card-despesa'><div class='label-card'>Despesas</div><div class='big-val'>R$ {st.session_state.input_comb:.2f}</div></div>", unsafe_allow_html=True)
    with col_mid2:
        st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo</div><div class='big-val'>R$ {liq_v:.2f}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    # Grade de detalhes
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Viagens</div><div class='grid-value'>{max(1, round(st.session_state.input_bruto/30))}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Bruto</div><div class='grid-value'>R$ {st.session_state.input_bruto/st.session_state.input_km:.2f}</div></div>", unsafe_allow_html=True)
    with g2:
        h, m = int(st.session_state.input_horas), int((st.session_state.input_horas - int(st.session_state.input_horas)) * 60)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Tempo</div><div class='grid-value'>{h:02d}:{m:02d}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/Hora</div><div class='grid-value'>R$ {hr_liq_v:.2f}</div></div>", unsafe_allow_html=True)
    with g3:
        st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Rodado</div><div class='grid-value'>{st.session_state.input_km}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/KM</div><div class='grid-value'>R$ {km_liq_v:.2f}</div></div>", unsafe_allow_html=True)

    if total_casa > 0:
        perc = min(max(0.0, liq_v / total_casa), 1.0)
        st.write(f"🏠 *Meta Casa:* {perc*100:.1f}% concluído")
        st.progress(perc)

# --- TAB 2: LANÇAMENTOS ---
with tab_lan:
    st.markdown("### Inserir Dados do Turno")
    st.session_state.input_bruto = st.number_input("Quanto ganhou bruto? (R$)", value=st.session_state.input_bruto, step=10.0)
    st.session_state.input_km = st.number_input("Quantos KMs rodou?", value=st.session_state.input_km, min_value=1.0)
    st.session_state.input_horas = st.number_input("Quantas horas trabalhou?", value=st.session_state.input_horas, min_value=0.1)
    st.session_state.input_comb = st.number_input("Gasto com Combustível (R$)", value=st.session_state.input_comb)
    
    if st.button("💾 SALVAR E ARQUIVAR DIA", use_container_width=True):
        novo = {"Data": datetime.now().strftime("%d/%m/%Y"), "Bruto": st.session_state.input_bruto, 
                "Líquido": liq_v, "KM": st.session_state.input_km, "Horas": st.session_state.input_horas, 
                "KM_Liq": km_liq_v, "Hora_Liq": hr_liq_v}
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo])], ignore_index=True)
        st.success("Dados salvos no histórico!")

# --- TAB 3: HISTÓRICO E CONTAS ---
with tab_hist:
    st.subheader("Histórico Semanal")
    if not st.session_state.historico.empty:
        df = st.session_state.historico
        st.metric("Total Líquido Acumulado", f"R$ {df['Líquido'].sum():.2f}")
        st.dataframe(df, use_container_width=True, height=250)
        if st.button("Zerar Histórico"):
            st.session_state.historico = pd.DataFrame(columns=df.columns)
            st.rerun()
    else:
        st.info("Nenhum dado salvo.")
