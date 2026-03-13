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

    /* Forçar colunas lado a lado no celular (Grade de Quadrados) */
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
        min-height: 85px;
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
    st.session_state.contas = {"Luz": 0.0, "Água": 0.0, "Internet": 0.0, "Aluguel": 0.0, "Mercado": 0.0, "Outros": 0.0}

if 'bruto' not in st.session_state: st.session_state.bruto = 0.0
if 'km' not in st.session_state: st.session_state.km = 1.0
if 'horas' not in st.session_state: st.session_state.horas = 1.0
if 'comb' not in st.session_state: st.session_state.comb = 0.0

# --- CÁLCULOS ---
total_casa = sum(st.session_state.contas.values())
liq = st.session_state.bruto - st.session_state.comb
km_b = st.session_state.bruto / st.session_state.km if st.session_state.km > 0 else 0
km_l = liq / st.session_state.km if st.session_state.km > 0 else 0
hr_l = liq / st.session_state.horas if st.session_state.horas > 0 else 0
viagens = max(1, round(st.session_state.bruto / 35)) if st.session_state.bruto > 0 else 0

# --- NAVEGAÇÃO POR ABAS ---
tab_res, tab_lan, tab_hist, tab_contas = st.tabs(["📊 RESULTADOS", "➕ LANÇAR", "📅 HISTÓRICO", "🏠 CONTAS"])

# --- ABA 1: RESULTADOS ---
with tab_res:
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento Dia</div><div class='big-val'>R$ {st.session_state.bruto:.2f}</div></div>", unsafe_allow_html=True)
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Despesas</div><div class='big-val'>R$ {st.session_state.comb:.2f}</div></div>", unsafe_allow_html=True)
    with c_sub2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo</div><div class='big-val'>R$ {liq:.2f}</div></div>", unsafe_allow_html=True)
    st.write("")
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
        st.write(f"🏠 *Progresso Meta Mensal (Casa):* {prog*100:.1f}%")
        st.progress(prog)

# --- ABA 2: LANÇAR ---
with tab_lan:
    st.subheader("Lançar Dia")
    st.session_state.bruto = st.number_input("Ganho Bruto", value=st.session_state.bruto)
    st.session_state.km = st.number_input("KM Total", value=st.session_state.km)
    st.session_state.horas = st.number_input("Tempo Total (ex: 8.5)", value=st.session_state.horas)
    st.session_state.comb = st.number_input("Gasto Combustível", value=st.session_state.comb)
    if st.button("💾 SALVAR GANHO DIÁRIO", use_container_width=True):
        novo = {"Data": datetime.now().strftime("%d/%m/%Y"), "Bruto": st.session_state.bruto, "Líquido": liq, "KM": st.session_state.km, "Horas": st.session_state.horas, "KM_Liq": km_l, "Hora_Liq": hr_l}
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo])], ignore_index=True)
        st.success("Ganho salvo!")

# --- ABA 3: HISTÓRICO (Com opções de Período) ---
with tab_hist:
    st.subheader("Resumo de Performance")
    if not st.session_state.historico.empty:
        df = st.session_state.historico
        # Conversão de data para cálculos de período
        df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
        hoje = datetime.now()
        
        # Filtros de períodos (Últimos 7 dias, Mês Atual, Ano Atual)
        ganho_7d = df[df['Data_dt'] > (hoje - pd.Timedelta(days=7))]['Líquido'].sum()
        ganho_mes = df[df['Data_dt'].dt.month == hoje.month]['Líquido'].sum()
        ganho_ano = df[df['Data_dt'].dt.year == hoje.year]['Líquido'].sum()

        # Exibição dos ganhos por período em colunas
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1: st.metric("Semanal (7d)", f"R$ {ganho_7d:.2f}")
        with c_p2: st.metric("Mensal", f"R$ {ganho_mes:.2f}")
        with c_p3: st.metric("Anual", f"R$ {ganho_ano:.2f}")
        
        st.divider()
        st.write("📊 *Histórico Detalhado (Diário)*")
        st.dataframe(df.drop(columns=['Data_dt']), use_container_width=True)
        
        if st.button("Limpar Tudo"):
            st.session_state.historico = pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"])
            st.rerun()
    else:
        st.info("Lance dados para ver os resumos por período.")

# --- ABA 4: CONTAS ---
with tab_contas:
    st.subheader("🏠 Gestão de Contas")
    c_casa1, c_casa2 = st.columns(2)
    with c_casa1:
        st.session_state.contas["Luz"] = st.number_input("Luz", value=st.session_state.contas["Luz"])
        st.session_state.contas["Água"] = st.number_input("Água", value=st.session_state.contas["Água"])
        st.session_state.contas["Internet"] = st.number_input("Internet", value=st.session_state.contas["Internet"])
    with c_casa2:
        st.session_state.contas["Aluguel"] = st.number_input("Aluguel", value=st.session_state.contas["Aluguel"])
        st.session_state.contas["Mercado"] = st.number_input("Mercado", value=st.session_state.contas["Mercado"])
        st.session_state.contas["Outros"] = st.number_input("Outros", value=st.session_state.contas["Outros"])
    st.divider()
    st.metric("Total de Contas", f"R$ {total_casa:.2f}")
