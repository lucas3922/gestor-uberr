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

    /* Cartões Coloridos Estilo Print */
    .card-faturamento { background-color: #00FF00; color: black; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; }
    .card-despesa { background-color: #FF0000; color: white; border-radius: 12px; padding: 15px; text-align: center; }
    .card-saldo { background-color: #800080; color: white; border-radius: 12px; padding: 15px; text-align: center; }
    
    .big-val { font-size: 24px; font-weight: bold; }
    .label-card { font-size: 12px; font-weight: 600; text-transform: uppercase; }

    /* Grade de métricas em quadrados (Grid) */
    .grid-item {
        background-color: #1C1C1E;
        border-radius: 12px;
        padding: 15px 5px;
        text-align: center;
        border: 1px solid #2C2C2E;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 90px;
    }
    .grid-label { color: #8E8E93; font-size: 10px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .grid-value { color: #FFFFFF; font-size: 17px; font-weight: bold; }

    /* Tabs Estilo App */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #1C1C1E;
        border-radius: 8px;
        color: #8E8E93;
        padding: 0 15px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4500 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        "Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq", "KM_Bruto", "Hora_Bruta"
    ])

# --- SIDEBAR: GESTÃO DE CONTAS DA CASA ---
with st.sidebar:
    st.header("🏠 Contas da Casa")
    luz = st.number_input("Luz", 0.0)
    agua = st.number_input("Água", 0.0)
    internet = st.number_input("Internet", 0.0)
    aluguel = st.number_input("Aluguel", 0.0)
    mercado = st.number_input("Mercado", 0.0)
    outros = st.number_input("Outros", 0.0)
    total_casa = luz + agua + internet + aluguel + mercado + outros
    st.divider()
    st.metric("Total Mensal", f"R$ {total_casa:.2f}")

# --- ESTADO DOS INPUTS ---
if 'bruto' not in st.session_state: st.session_state.bruto = 0.0
if 'km' not in st.session_state: st.session_state.km = 1.0
if 'horas' not in st.session_state: st.session_state.horas = 1.0
if 'comb' not in st.session_state: st.session_state.comb = 0.0

# --- CÁLCULOS TÉCNICOS ---
liq = st.session_state.bruto - st.session_state.comb
km_b = st.session_state.bruto / st.session_state.km if st.session_state.km > 0 else 0
km_l = liq / st.session_state.km if st.session_state.km > 0 else 0
hr_b = st.session_state.bruto / st.session_state.horas if st.session_state.horas > 0 else 0
hr_l = liq / st.session_state.horas if st.session_state.horas > 0 else 0
viagens = max(1, round(st.session_state.bruto / 35)) if st.session_state.bruto > 0 else 0

# --- NAVEGAÇÃO ---
tab_res, tab_lan, tab_hist = st.tabs(["📊 RESULTADOS", "➕ LANÇAR", "📅 HISTÓRICO"])

# --- ABA 1: RESULTADOS ---
with tab_res:
    # Faturamento destaque
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento Dia</div><div class='big-val'>R$ {st.session_state.bruto:.2f}</div></div>", unsafe_allow_html=True)
    
    # Despesa e Saldo lado a lado
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Despesas</div><div class='big-val'>R$ {st.session_state.comb:.2f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo Líquido</div><div class='big-val'>R$ {liq:.2f}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    
    # --- GRADE EM QUADRADOS (3 COLUNAS) ---
    # Linha 1 da Grade
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Viagens</div><div class='grid-value'>{viagens}</div></div>", unsafe_allow_html=True)
    with g2:
        st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Bruto</div><div class='grid-value'>R$ {km_b:.2f}</div></div>", unsafe_allow_html=True)
    with g3:
        h, m = int(st.session_state.horas), int((st.session_state.horas - int(st.session_state.horas)) * 60)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Tempo</div><div class='grid-value'>{h:02d}:{m:02d}</div></div>", unsafe_allow_html=True)

    # Linha 2 da Grade
    g4, g5, g6 = st.columns(3)
    with g4:
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/Hora</div><div class='grid-value'>R$ {hr_l:.2f}</div></div>", unsafe_allow_html=True)
    with g5:
        st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Rodado</div><div class='grid-value'>{st.session_state.km}</div></div>", unsafe_allow_html=True)
    with g6:
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/KM</div><div class='grid-value'>R$ {km_l:.2f}</div></div>", unsafe_allow_html=True)

    # Meta da Casa
    if total_casa > 0:
        st.write("")
        prog = min(max(0.0, liq / total_casa), 1.0)
        st.write(f"🏠 *Abate das Contas:* {prog*100:.1f}%")
        st.progress(prog)

# --- ABA 2: LANÇAR ---
with tab_lan:
    st.subheader("Entrada de Dados")
    st.session_state.bruto = st.number_input("Ganho Bruto Total", value=st.session_state.bruto, step=10.0)
    st.session_state.km = st.number_input("Kilometragem Total", value=st.session_state.km, min_value=1.0)
    st.session_state.horas = st.number_input("Horas de Trabalho (ex: 8.5)", value=st.session_state.horas, min_value=0.1)
    st.session_state.comb = st.number_input("Gasto com Combustível", value=st.session_state.comb, step=5.0)
    
    if st.button("💾 SALVAR DIA", use_container_width=True):
        novo = {
            "Data": datetime.now().strftime("%d/%m/%Y"), 
            "Bruto": st.session_state.bruto, "Líquido": liq, 
            "KM": st.session_state.km, "Horas": st.session_state.horas, 
            "KM_Liq": km_l, "Hora_Liq": hr_l, "KM_Bruto": km_b, "Hora_Bruta": hr_b
        }
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo])], ignore_index=True)
        st.success("Salvo! Confira na aba Histórico.")

# --- ABA 3: HISTÓRICO ---
with tab_hist:
    st.subheader("Ganhos Acumulados")
    if not st.session_state.historico.empty:
        df = st.session_state.historico
        col_t1, col_t2 = st.columns(2)
        col_t1.metric("Bruto Total", f"R$ {df['Bruto'].sum():.2f}")
        col_t2.metric("Líquido Total", f"R$ {df['Líquido'].sum():.2f}")
        
        st.dataframe(df, use_container_width=True)
        
        if st.button("Zerar Tudo"):
            st.session_state.historico = pd.DataFrame(columns=df.columns)
            st.rerun()
    else:
        st.info("Lance e salve um dia para começar seu histórico.")
