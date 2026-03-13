import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração para parecer App Mobile
st.set_page_config(
    page_title="Uber Manager Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed", 
    page_icon="📊"
)

# --- ESTILIZAÇÃO CSS PROFISSIONAL ---
st.markdown("""
<style>
    .stApp { background-color: #f1f3f5; }
    
    /* Cartões Principais */
    .status-card {
        border-radius: 16px;
        padding: 20px;
        color: white;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Cartões de Grade (Cinzas) */
    .grid-card {
        background: white;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        border: 1px solid #dee2e6;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .label-gray { font-size: 12px; color: #6c757d; font-weight: 600; text-transform: uppercase; margin-bottom: 4px; }
    .value-bold { font-size: 20px; font-weight: 700; color: #212529; }
    
    /* Botão Principal */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #212529;
        color: white;
        font-weight: bold;
        border: none;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=[
        "Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"
    ])

# --- SIDEBAR (CONTAS DA CASA) ---
with st.sidebar:
    st.header("🏠 Custos da Casa")
    luz = st.number_input("Luz", 0.0)
    agua = st.number_input("Água", 0.0)
    internet = st.number_input("Internet", 0.0)
    aluguel = st.number_input("Aluguel", 0.0)
    mercado = st.number_input("Mercado", 0.0)
    outros = st.number_input("Outros", 0.0)
    total_casa = luz + agua + internet + aluguel + mercado + outros
    st.divider()
    st.metric("Total Mensal", f"R$ {total_casa:.2f}")

# --- ENTRADA DE DADOS ---
st.markdown("<h3 style='text-align: center;'>📝 Lançamento do Dia</h3>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: ganho_bruto = st.number_input("Ganho Bruto (R$)", min_value=0.0, step=5.0)
with c2: km_total = st.number_input("KM Total", min_value=1.0, step=1.0)
with c3: horas_total = st.number_input("Horas On", min_value=0.1, step=0.5)
with c4: custo_comb = st.number_input("Combustível (R$)", min_value=0.0, step=5.0)

# --- CÁLCULOS ---
liquido_dia = ganho_bruto - custo_comb
km_liq_v = liquido_dia / km_total if km_total > 0 else 0
hora_liq_v = liquido_dia / horas_total if horas_total > 0 else 0
viagens_est = max(1, round(ganho_bruto / 30))

# --- DASHBOARD ---
tab_hoje, tab_hist = st.tabs(["📱 Dashboard", "📅 Histórico"])

with tab_hoje:
    # Top Cards
    f, d, s = st.columns(3)
    with f: st.markdown(f"<div class='status-card' style='background: #2ecc71;'><div class='label-gray' style='color: white;'>Faturamento</div><div style='font-size: 26px; font-weight: bold;'>R$ {ganho_bruto:.2f}</div></div>", unsafe_allow_html=True)
    with d: st.markdown(f"<div class='status-card' style='background: #e74c3c;'><div class='label-gray' style='color: white;'>Despesas</div><div style='font-size: 26px; font-weight: bold;'>R$ {custo_comb:.2f}</div></div>", unsafe_allow_html=True)
    with s: st.markdown(f"<div class='status-card' style='background: #3498db;'><div class='label-gray' style='color: white;'>Líquido</div><div style='font-size: 26px; font-weight: bold;'>R$ {liquido_dia:.2f}</div></div>", unsafe_allow_html=True)

    # Grid 3x2
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"<div class='grid-card'><div class='label-gray'>Viagens</div><div class='value-bold'>{viagens_est}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grid-card'><div class='label-gray'>KM Bruto</div><div class='value-bold'>R$ {ganho_bruto/km_total:.2f}</div></div>", unsafe_allow_html=True)
    with g2:
        h, m = int(horas_total), int((horas_total - int(horas_total)) * 60)
        st.markdown(f"<div class='grid-card'><div class='label-gray'>Tempo</div><div class='value-bold'>{h:02d}:{m:02d}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grid-card'><div class='label-gray'>Líquido/Hora</div><div class='value-bold'>R$ {hora_liq_v:.2f}</div></div>", unsafe_allow_html=True)
    with g3:
        st.markdown(f"<div class='grid-card'><div class='label-gray'>KM Rodado</div><div class='value-bold'>{km_total}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='grid-card'><div class='label-gray'>Líquido/KM</div><div class='value-bold'>R$ {km_liq_v:.2f}</div></div>", unsafe_allow_html=True)

    # Abate de Contas
    if total_casa > 0:
        st.divider()
        st.subheader("🏠 Meta Residencial")
        progresso = min(max(0.0, liquido_dia / total_casa), 1.0)
        st.progress(progresso)
        st.write(f"Você abateu *{progresso*100:.1f}%* das contas do mês.")

    if st.button("💾 SALVAR GANHO DIÁRIO"):
        novo = {"Data": datetime.now().strftime("%d/%m/%Y"), "Bruto": ganho_bruto, "Líquido": liquido_dia, 
                "KM": km_total, "Horas": horas_total, "KM_Liq": km_liq_v, "Hora_Liq": hora_liq_v}
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo])], ignore_index=True)
        st.success("Dados salvos!")

with tab_hist:
    if not st.session_state.historico.empty:
        df = st.session_state.historico
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Bruto Total", f"R$ {df['Bruto'].sum():.2f}")
        col_res2.metric("Líquido Total", f"R$ {df['Líquido'].sum():.2f}")
        # A correção principal está aqui:
        media_km = df['KM_Liq'].mean()
        col_res3.metric("Média KM Líq", f"R$ {media_km:.2f}")
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum dado salvo ainda.")
