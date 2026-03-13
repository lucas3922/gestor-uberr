import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração para Mobile (App Mode)
st.set_page_config(
    page_title="UberPro", 
    layout="wide", 
    initial_sidebar_state="collapsed", 
    page_icon="🚗"
)

# --- CSS PARA ELIMINAR SCROLL E FIXAR INTERFACE ---
st.markdown("""
<style>
    /* Remove espaços inúteis no topo */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    
    /* Cores e Cartões */
    .stApp { background-color: #f2f2f7; }
    
    .app-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    /* Estilo das métricas compactas */
    .metric-box {
        text-align: center;
        padding: 10px;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e5e5ea;
    }
    
    .label { font-size: 11px; color: #8e8e93; font-weight: 600; text-transform: uppercase; }
    .value { font-size: 18px; font-weight: 700; color: #1c1c1e; }

    /* Botão Salvar Estilo iOS */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: #007aff;
        color: white;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"])

# --- SIDEBAR (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("🏠 Contas Fixas")
    luz = st.number_input("Luz", 0.0)
    agua = st.number_input("Água", 0.0)
    internet = st.number_input("Internet", 0.0)
    aluguel = st.number_input("Aluguel", 0.0)
    mercado = st.number_input("Mercado", 0.0)
    outros = st.number_input("Outros", 0.0)
    total_casa = luz + agua + internet + aluguel + mercado + outros

# --- NAVEGAÇÃO POR TABS (Cara de App) ---
tab_home, tab_stats, tab_history = st.tabs(["➕ LANÇAR", "📈 DASHBOARD", "📅 HISTÓRICO"])

with tab_home:
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        ganho_bruto = st.number_input("Ganho Bruto (R$)", min_value=0.0, step=10.0)
        km_total = st.number_input("KM Total", min_value=1.0, step=1.0)
    with c2:
        horas_total = st.number_input("Horas On", min_value=0.1, step=0.5)
        custo_comb = st.number_input("Combustível (R$)", min_value=0.0, step=5.0)
    st.markdown("</div>", unsafe_allow_html=True)

    # Cálculos rápidos
    liquido_dia = ganho_bruto - custo_comb
    km_liq = liquido_dia / km_total if km_total > 0 else 0
    hr_liq = liquido_dia / horas_total if horas_total > 0 else 0
    
    # Barra de Meta (Abate)
    if total_casa > 0:
        prog = min(max(0.0, liquido_dia / total_casa), 1.0)
        st.write(f"*Abate Mensal:* {prog*100:.1f}%")
        st.progress(prog)

    if st.button("💾 SALVAR DIA"):
        novo = {"Data": datetime.now().strftime("%d/%m/%Y"), "Bruto": ganho_bruto, "Líquido": liquido_dia, 
                "KM": km_total, "Horas": horas_total, "KM_Liq": km_liq, "Hora_Liq": hr_liq}
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo])], ignore_index=True)
        st.toast("Dados salvos com sucesso!", icon="✅")

with tab_stats:
    # Resumo Colorido Compacto
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-bottom: 15px;">
        <div class='status-card' style="flex:1; background:#34c759; border-radius:12px; padding:10px; color:white; text-align:center;">
            <small>BRUTO</small><br><b>R$ {ganho_bruto:.2f}</b>
        </div>
        <div class='status-card' style="flex:1; background:#ff3b30; border-radius:12px; padding:10px; color:white; text-align:center;">
            <small>CUSTO</small><br><b>R$ {custo_comb:.2f}</b>
        </div>
        <div class='status-card' style="flex:1; background:#007aff; border-radius:12px; padding:10px; color:white; text-align:center;">
            <small>LÍQUIDO</small><br><b>R$ {liquido_dia:.2f}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Grade de Métricas 3x2 (compacta)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"<div class='metric-box'><div class='label'>KM Líq</div><div class='value'>R$ {km_liq:.2f}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-box'><div class='label'>KM Bruto</div><div class='value'>R$ {ganho_bruto/km_total:.2f}</div></div>", unsafe_allow_html=True)
    with g2:
        st.markdown(f"<div class='metric-box'><div class='label'>Hr Líq</div><div class='value'>R$ {hr_liq:.2f}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-box'><div class='label'>Hr Bruta</div><div class='value'>R$ {ganho_bruto/horas_total:.2f}</div></div>", unsafe_allow_html=True)
    with g3:
        st.markdown(f"<div class='metric-box'><div class='label'>Viagens</div><div class='value'>{max(1, round(ganho_bruto/30))}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-box'><div class='label'>Eficiência</div><div class='value'>{(liquido_dia/ganho_bruto*100) if ganho_bruto>0 else 0:.0f}%</div></div>", unsafe_allow_html=True)

with tab_history:
    if not st.session_state.historico.empty:
        df = st.session_state.historico
        st.metric("Total Acumulado (Líquido)", f"R$ {df['Líquido'].sum():.2f}")
        # Container com altura fixa para evitar rolar a página inteira
        st.dataframe(df, use_container_width=True, height=300)
    else:
        st.info("Lance seu primeiro dia para ver o histórico.")
