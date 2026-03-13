import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página e ícone
st.set_page_config(page_title="Gestor Uber + Casa", layout="wide", page_icon="🚗")

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 30px !important;
        font-weight: bold;
    }
    .main-metric {
        border-radius: 10px;
        padding: 20px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .secondary-metric {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 15px;
        color: #31333F;
        margin-bottom: 10px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .metric-label-custom {
        font-size: 14px;
        color: #6c757d;
        margin-bottom: 5px;
    }
    .metric-value-custom {
        font-size: 24px;
        font-weight: bold;
        color: #31333F;
    }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("<div style='background-color: #ff4b4b; padding: 20px; border-radius: 50%; text-align: center; color: white; font-weight: bold;'>UB</div>", unsafe_allow_html=True)
with col_title:
    st.title("Gestor Financeiro: Uber & Residencial")
st.markdown("---")

# --- SIDEBAR: GESTÃO DE CONTAS DA CASA ---
st.sidebar.header("🏠 Contas da Casa (Mensal)")
luz = st.sidebar.number_input("Luz (R$)", min_value=0.0, value=0.0, step=10.0)
agua = st.sidebar.number_input("Água (R$)", min_value=0.0, value=0.0, step=10.0)
internet = st.sidebar.number_input("Internet (R$)", min_value=0.0, value=0.0, step=10.0)
aluguel = st.sidebar.number_input("Aluguel (R$)", min_value=0.0, value=0.0, step=10.0)
mercado = st.sidebar.number_input("Mercado (R$)", min_value=0.0, value=0.0, step=50.0)
outros = st.sidebar.number_input("Outros (R$)", min_value=0.0, value=0.0, step=10.0)

total_despesas = luz + agua + internet + aluguel + mercado + outros
meta_diaria = total_despesas / 22 if total_despesas > 0 else 0 

st.sidebar.metric("Total Despesas", f"R$ {total_despesas:.2f}")
st.sidebar.info(f"🎯 Meta Diária Sugerida (22 dias): R$ {meta_diaria:.2f}")

# --- ENTRADA DE DADOS ---
st.header("🚗 Entrada do Dia")
col1, col2, col3, col4 = st.columns(4)

with col1:
    ganho_bruto = st.number_input("Ganho Bruto Total (R$)", min_value=0.0, value=0.0, step=10.0)
with col2:
    km_rodados = st.number_input("KM Rodados", min_value=1.0, value=1.0, step=1.0)
with col3:
    horas_trab = st.number_input("Horas Trabalhadas", min_value=0.1, value=1.0, step=0.5)
with col4:
    custo_combustivel = st.number_input("Custo Combustível/Geral (R$)", min_value=0.0, value=0.0, step=5.0)

# Cálculos
ganho_liquido = ganho_bruto - custo_combustivel
km_bruto = ganho_bruto / km_rodados
km_liquido = ganho_liquido / km_rodados
hora_bruto = ganho_bruto / horas_trab
hora_liquido = ganho_liquido / horas_trab
viagens_estimadas = max(1, round(ganho_bruto / 35))

# --- DASHBOARD ---
st.markdown("---")
tabs = st.tabs(["Diário", "Semanal", "Mensal", "Anual"])

with tabs[0]:
    col_fat, col_desp, col_saldo = st.columns(3)

    with col_fat:
        st.markdown(f"<div class='main-metric' style='background-color: #2e7d32; text-align: center;'><p style='color: #e0e0e0; font-size: 14px;'>Faturamento Dia</p><p style='font-size: 32px; font-weight: bold;'>R$ {ganho_bruto:.2f}</p></div>", unsafe_allow_html=True)

    with col_desp:
        st.markdown(f"<div class='main-metric' style='background-color: #c62828; text-align: center;'><p style='color: #e0e0e0; font-size: 14px;'>Despesas</p><p style='font-size: 32px; font-weight: bold;'>R$ {custo_combustivel:.2f}</p></div>", unsafe_allow_html=True)

    with col_saldo:
        st.markdown(f"<div class='main-metric' style='background-color: #1976d2; text-align: center;'><p style='color: #e0e0e0; font-size: 14px;'>Saldo</p><p style='font-size: 32px; font-weight: bold;'>R$ {ganho_liquido:.2f}</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    col_via, col_hor, col_km = st.columns(3)
    with col_via:
        st.markdown(f"<div class='secondary-metric'><p class='metric-label-custom'>Total de Viagens</p><p class='metric-value-custom'>{viagens_estimadas}</p></div>", unsafe_allow_html=True)
    with col_hor:
        h = int(horas_trab)
        m = int((horas_trab - h) * 60)
        st.markdown(f"<div class='secondary-metric'><p class='metric-label-custom'>Horas Trabalhadas</p><p class='metric-value-custom'>{h:02d}:{m:02d}</p></div>", unsafe_allow_html=True)
    with col_km:
        st.markdown(f"<div class='secondary-metric'><p class='metric-label-custom'>KMs Rodados</p><p class='metric-value-custom'>{km_rodados:.2f}</p></div>", unsafe_allow_html=True)

    col_fv, col_fh, col_fk = st.columns(3)
    with col_fv:
        st.markdown(f"<div class='secondary-metric'><p class='metric-label-custom'>Fat. por viagens</p><p class='metric-value-custom'>R$ {ganho_bruto/viagens_estimadas:.2f}</p></div>", unsafe_allow_html=True)
    with col_fh:
        st.markdown(f"<div class='secondary-metric'><p class='metric-label-custom'>Fat. médio por hora</p><p class='metric-value-custom'>R$ {hora_bruto:.2f}</p></div>", unsafe_allow_html=True)
    with col_fk:
        st.markdown(f"<div class='secondary-metric'><p class='metric-label-custom'>Fat. médio por KM</p><p class='metric-value-custom'>R$ {km_bruto:.2f}</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    if total_despesas > 0:
        progresso = min(max(0.0, ganho_liquido / total_despesas), 1.0)
        restante = max(0.0, total_despesas - ganho_liquido)
        st.write(f"*Abate Mensal:* Faltam R$ {restante:.2f} para cobrir as contas da casa.")
        st.progress(progresso)

# --- SALVAMENTO ---
st.markdown("---")
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas"])

if st.button("💾 Salvar Lançamento Diário"):
    novo_dado = {
        "Data": datetime.now().strftime("%d/%m/%Y"),
        "Bruto": ganho_bruto,
        "Líquido": ganho_liquido,
        "KM": km_rodados,
        "Horas": horas_trab
    }
    st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo_dado])], ignore_index=True)
    st.success("Dados salvos com sucesso!")

st.header("📅 Resumo Acumulado")
st.dataframe(st.session_state.historico, use_container_width=True)
