import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração para parecer App Mobile
st.set_page_config(
    page_title="Uber Manager Pro", 
    layout="wide", 
    initial_sidebar_state="expanded", 
    page_icon="📊"
)

# --- ESTILIZAÇÃO CSS COMPLETA ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { font-size: 24px !important; }
    
    /* Cartões de Status (Cores do seu print) */
    .status-card {
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* Grade de Métricas Cinzas */
    .grid-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
    }
    
    .label-gray { font-size: 13px; color: #757575; font-weight: 500; margin-bottom: 5px; }
    .value-bold { font-size: 22px; font-weight: 700; color: #212121; }
    
    /* Ajustes de espaçamento mobile */
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO BANCO DE DADOS (SESSION STATE) ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        "Data", "Bruto", "Líquido", "KM", "Horas", "Viagens", "KM Liq", "Hora Liq"
    ])

# --- SIDEBAR: GESTÃO DE CONTAS DA CASA ---
with st.sidebar:
    st.header("🏠 Contas da Casa")
    luz = st.number_input("Luz", value=0.0, step=10.0)
    agua = st.number_input("Água", value=0.0, step=10.0)
    internet = st.number_input("Internet", value=0.0, step=10.0)
    aluguel = st.number_input("Aluguel", value=0.0, step=10.0)
    mercado = st.number_input("Mercado", value=0.0, step=50.0)
    outros = st.number_input("Outros", value=0.0, step=10.0)
    
    total_casa = luz + agua + internet + aluguel + mercado + outros
    st.markdown("---")
    st.metric("Total de Despesas", f"R$ {total_casa:.2f}")
    meta_dia = total_casa / 22 if total_casa > 0 else 0
    st.info(f"Sua meta diária para quitar a casa é R$ {meta_dia:.2f} (base 22 dias).")

# --- ÁREA DE LANÇAMENTO ---
st.markdown("<h2 style='text-align: center;'>🚗 Lançamento Diário</h2>", unsafe_allow_html=True)

col_in1, col_in2, col_in3, col_in4 = st.columns(4)
with col_in1: ganho_bruto = st.number_input("Ganho Bruto (R$)", min_value=0.0, step=10.0)
with col_in2: km_total = st.number_input("KM Rodados", min_value=1.0, step=1.0)
with col_in3: horas_total = st.number_input("Horas Trabalhadas", min_value=0.1, step=0.5)
with col_in4: combustivel = st.number_input("Gasto Combustível (R$)", min_value=0.0, step=5.0)

# --- CÁLCULOS DIÁRIOS ---
liquido_dia = ganho_bruto - combustivel
km_bruto_v = ganho_bruto / km_total
km_liq_v = liquido_dia / km_total
hora_bruta_v = ganho_bruto / horas_total
hora_liq_v = liquido_dia / horas_total
viagens_est = max(1, round(ganho_bruto / 32)) # Estimativa de viagens

# --- INTERFACE ESTILO APP (RESULTADOS) ---
st.markdown("---")
tab1, tab2 = st.tabs(["📊 Resultados do Dia", "📅 Histórico Acumulado"])

with tab1:
    # Cartões Coloridos Principais
    c_f, c_d, c_s = st.columns(3)
    with c_f:
        st.markdown(f"<div class='status-card' style='background-color: #00C853;'><div class='label-gray' style='color: white;'>Faturamento</div><div style='font-size: 28px; font-weight: bold;'>R$ {ganho_bruto:.2f}</div></div>", unsafe_allow_html=True)
    with c_d:
        st.markdown(f"<div class='status-card' style='background-color: #D50000;'><div class='label-gray' style='color: white;'>Despesas</div><div style='font-size: 28px; font-weight: bold;'>R$ {combustivel:.2f}</div></div>", unsafe_allow_html=True)
    with c_s:
        st.markdown(f"<div class='status-card' style='background-color: #6200EA;'><div class='label-gray' style='color: white;'>Saldo Líquido</div><div style='font-size: 28px; font-weight: bold;'>R$ {liquido_dia:.2f}</div></div>", unsafe_allow_html=True)

    # Grade de Detalhes 3x2
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"<div class='grid-card'><div class='label-gray'>Estimativa Viagens</div><div class='value-bold'>{viagens_est}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grid-card'><div class='label-gray'>KM Bruto</div><div class='value-bold'>R$ {km_bruto_v:.2f}</div></div>", unsafe_allow_html=True)
    with g2:
        h, m = int(horas_total), int((horas_total - int(horas_total)) * 60)
        st.markdown(f"<div class='grid-card'><div class='label-gray'>Tempo</div><div class='value-bold'>{h:02d}:{m:02d}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grid-card'><div class='label-gray'>Hora Bruta</div><div class='value-bold'>R$ {hora_bruta_v:.2f}</div></div>", unsafe_allow_html=True)
    with g3:
        st.markdown(f"<div class='grid-card'><div class='label-gray'>KM Rodado</div><div class='value-bold'>{km_total}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grid-card'><div class='label-gray'>KM Líquido</div><div class='value-bold'>R$ {km_liq_v:.2f}</div></div>", unsafe_allow_html=True)

    # Abate de Contas da Casa
    if total_casa > 0:
        st.markdown("---")
        st.subheader("🏠 Abate das Contas do Mês")
        progresso = min(max(0.0, liquido_dia / total_casa), 1.0)
        st.progress(progresso)
        restante = max(0.0, total_casa - liquido_dia)
        st.write(f"Este ganho abateu *{progresso*100:.1f}%* das suas despesas totais. Faltam *R$ {restante:.2f}*.")

    # Botão Salvar
    if st.button("💾 SALVAR GANHO DIÁRIO", use_container_width=True):
        novo_registro = {
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Bruto": ganho_bruto,
            "Líquido": liquido_dia,
            "KM": km_total,
            "Horas": horas_total,
            "Viagens": viagens_est,
            "KM Liq": km_liq_v,
            "Hora Liq": hora_liq_v
        }
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo_registro])], ignore_index=True)
        st.success("Salvo no histórico semanal!")

with tab2:
    st.subheader("📅 Histórico Acumulado")
    if not st.session_state.historico.empty:
        df = st.session_state.historico
        
        # Resumo do Histórico (Ganhos Totais)
        c_tot1, c_tot2, c_tot3 = st.columns(3)
        c_tot1.metric("Bruto Total", f"R$ {df['Bruto'].sum():.2f}")
        c_tot2.metric("Líquido Total", f"R$ {df['Líquido'].sum():.2f}")
        c_tot3.metric("Média KM Líq", f"R$ {df['KM Liq'].mean():.2f}")
        
        st.dataframe(df, use_container_width=True)
        
        # Botão para limpar
        if st.button("Limpar Histórico"):
            st.session_state.historico = pd.DataFrame(columns=st.session_state.historico.columns)
            st.rerun()
    else:
        st.info("Ainda não há dados salvos.")
