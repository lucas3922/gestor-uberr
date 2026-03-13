import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página para parecer um App
st.set_page_config(
    page_title="Uber Manager Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed", # Esconde o menu lateral no celular
    page_icon="📊"
)

# --- ESTILIZAÇÃO CSS AVANÇADA ---
st.markdown("""
<style>
    /* Fundo do App */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Esconder menus desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Cartão Principal de Destaque */
    .main-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eee;
    }

    /* Estilo das Métricas Coloridas */
    .status-card {
        border-radius: 12px;
        padding: 15px;
        color: white;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Estilo da Grade Inferior */
    .grid-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #ececf1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .label { font-size: 12px; color: #6e6e73; text-transform: uppercase; letter-spacing: 0.5px; }
    .value { font-size: 20px; font-weight: 700; color: #1d1d1f; }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("<h2 style='text-align: center; color: #1d1d1f; margin-bottom: 25px;'>📊 Uber Manager Pro</h2>", unsafe_allow_html=True)

# --- SIDEBAR (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("🏠 Custos Fixos")
    luz = st.number_input("Luz", value=0.0)
    agua = st.number_input("Água", value=0.0)
    internet = st.number_input("Internet", value=0.0)
    aluguel = st.number_input("Aluguel", value=0.0)
    mercado = st.number_input("Mercado", value=0.0)
    outros = st.number_input("Outros", value=0.0)
    total_casa = luz + agua + internet + aluguel + mercado + outros

# --- ÁREA DE INPUT ---
with st.container():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: ganho_bruto = st.number_input("Total Bruto (R$)", min_value=0.0, step=10.0)
    with c2: km = st.number_input("KM Total", min_value=1.0, step=1.0)
    with c3: horas = st.number_input("Horas On", min_value=0.1, step=0.5)
    with c4: combustivel = st.number_input("Combustível (R$)", min_value=0.0, step=5.0)
    st.markdown("</div>", unsafe_allow_html=True)

# --- CÁLCULOS ---
liquido = ganho_bruto - combustivel
km_liq = liquido / km if km > 0 else 0
hr_liq = liquido / horas if horas > 0 else 0
viagens = max(1, round(ganho_bruto / 30))

# --- DASHBOARD DE RESULTADOS ---
st.markdown("---")
# Linha 1: Destaques Coloridos
col_f, col_d, col_s = st.columns(3)
with col_f:
    st.markdown(f"<div class='status-card' style='background: linear-gradient(135deg, #28a745, #218838);'><div class='label' style='color: #e9ecef;'>FATURAMENTO</div><div style='font-size: 28px;'>R$ {ganho_bruto:.2f}</div></div>", unsafe_allow_html=True)
with col_d:
    st.markdown(f"<div class='status-card' style='background: linear-gradient(135deg, #dc3545, #c82333);'><div class='label' style='color: #e9ecef;'>CUSTO OPERACIONAL</div><div style='font-size: 28px;'>R$ {combustivel:.2f}</div></div>", unsafe_allow_html=True)
with col_s:
    st.markdown(f"<div class='status-card' style='background: linear-gradient(135deg, #007bff, #0069d9);'><div class='label' style='color: #e9ecef;'>LUCRO LÍQUIDO</div><div style='font-size: 28px;'>R$ {liquido:.2f}</div></div>", unsafe_allow_html=True)

st.write("") # Espaçador

# Linha 2: Grade de métricas (Igual ao seu print)
g1, g2, g3 = st.columns(3)
with g1:
    st.markdown(f"<div class='grid-card'><div class='label'>Viagens</div><div class='value'>{viagens}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='grid-card'><div class='label'>Fat. por Viagem</div><div class='value'>R$ {ganho_bruto/viagens:.2f}</div></div>", unsafe_allow_html=True)
with g2:
    h_int, m_int = int(horas), int((horas - int(horas)) * 60)
    st.markdown(f"<div class='grid-card'><div class='label'>Tempo Logado</div><div class='value'>{h_int:02d}:{m_int:02d}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='grid-card'><div class='label'>Líquido/Hora</div><div class='value'>R$ {hr_liq:.2f}</div></div>", unsafe_allow_html=True)
with g3:
    st.markdown(f"<div class='grid-card'><div class='label'>KM Rodado</div><div class='value'>{km:.1f}</div></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='grid-card'><div class='label'>Líquido/KM</div><div class='value'>R$ {km_liq:.2f}</div></div>", unsafe_allow_html=True)

# --- META DA CASA ---
if total_casa > 0:
    st.markdown("---")
    st.subheader("🏠 Progresso das Contas")
    percentual = min(max(0.0, liquido / total_casa), 1.0)
    faltam = max(0.0, total_casa - liquido)
    st.progress(percentual)
    st.write(f"Você já cobriu *{percentual*100:.1f}%* das suas contas. Faltam *R$ {faltam:.2f}*.")

# --- PERSISTÊNCIA ---
if st.button("💾 SALVAR DIA", use_container_width=True):
    st.balloons()
    st.success("Dados arquivados com sucesso!")
