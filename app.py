import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import os

# Configuração de App Mobile
st.set_page_config(
    page_title="UberPro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚗"
)

# --- CSS PARA INTERFACE DARK MODE E GRADE 2x3 ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    label, p, span, h1, h2, h3, .stMarkdown { color: #ffffff !important; }
    [data-testid="column"] { width: 50% !important; flex: 1 1 45% !important; min-width: 45% !important; }
    
    /* Estilo dos Cards Principais */
    .card-faturamento { background-color: #00FF00; color: black !important; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; }
    .card-despesa { background-color: #FF0000; color: white !important; border-radius: 12px; padding: 15px; text-align: center; }
    .card-saldo { background-color: #800080; color: white !important; border-radius: 12px; padding: 15px; text-align: center; }
    
    .big-val { font-size: 22px; font-weight: bold; }
    .label-card { font-size: 11px; font-weight: 600; text-transform: uppercase; }

    /* Grade de Métricas 2x3 */
    .grid-item { 
        background-color: #1C1C1E; 
        border-radius: 12px; 
        padding: 12px 5px; 
        text-align: center; 
        border: 1px solid #2C2C2E; 
        margin-bottom: 8px;
        min-height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .grid-label { color: #ffffff !important; font-size: 10px; font-weight: bold; text-transform: uppercase; opacity: 0.8; }
    .grid-value { color: #FFFFFF !important; font-size: 16px; font-weight: bold; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1C1C1E;
        border-radius: 8px 8px 0 0;
        color: #ffffff !important;
        padding: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #FF4500 !important; }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DADOS (CSV LOCAL) ---
DB_FILE = "dados_uber.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas"])

if 'historico' not in st.session_state:
    st.session_state.historico = carregar_dados()

def salvar_dados(df):
    df.to_csv(DB_FILE, index=False)
    st.session_state.historico = df

# --- CÁLCULOS DE METAS ---
hoje_ref = date.today()
ultimo_dia = calendar.monthrange(hoje_ref.year, hoje_ref.month)[1]
dias_restantes = max(1, (ultimo_dia - hoje_ref.day) + 1)

# --- FUNÇÃO DE RENDERIZAR GRADE 2x3 ---
def renderizar_grade(bruto, liquido, km, horas, titulo_principal=""):
    custo = bruto - liquido
    
    # Cards de Topo
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento {titulo_principal}</div><div class='big-val'>R$ {bruto:.2f}</div></div>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a: st.markdown(f"<div class='card-despesa'><div class='label-card'>Despesas</div><div class='big-val'>R$ {custo:.2f}</div></div>", unsafe_allow_html=True)
    with col_b: st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo Líquido</div><div class='big-val'>R$ {liquido:.2f}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    
    # Grade 2x3
    g1, g2 = st.columns(2)
    with g1: st.markdown(f"<div class='grid-item'><div class='grid-label'>Hora Bruta</div><div class='grid-value'>R$ {(bruto/horas if horas > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    with g2: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Bruto</div><div class='grid-value'>R$ {(bruto/km if km > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    
    g3, g4 = st.columns(2)
    with g3: 
        h_int = int(horas)
        m_int = int((horas - h_int) * 60)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Tempo Total</div><div class='grid-value'>{h_int:02d}:{m_int:02d}h</div></div>", unsafe_allow_html=True)
    with g4: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/Hora</div><div class='grid-value'>R$ {(liquido/horas if horas > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    
    g5, g6 = st.columns(2)
    with g5: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Rodado</div><div class='grid-value'>{km:.1f} km</div></div>", unsafe_allow_html=True)
    with g6: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/KM</div><div class='grid-value'>R$ {(liquido/km if km > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)

# --- INTERFACE POR ABAS ---
tab_res, tab_turno, tab_lan, tab_hist = st.tabs(["📊 RES", "⏱️ TURNO", "➕ LANÇAR", "📅 HIST"])

with tab_res:
    if not st.session_state.historico.empty:
        u = st.session_state.historico.iloc[-1]
        renderizar_grade(u['Bruto'], u['Líquido'], u['KM'], u['Horas'], "do Dia")
    else:
        st.info("Nenhum dado lançado ainda.")

with tab_turno:
    st.subheader("Controle de Turno")
    if 'turno_ativo' not in st.session_state: st.session_state.turno_ativo = False

    if not st.session_state.turno_ativo:
        if st.button("🚀 INICIAR TURNO", use_container_width=True):
            st.session_state.inicio_turno = datetime.now()
            st.session_state.turno_ativo = True
            st.rerun()
    else:
        agora = datetime.now()
        decorrido = (agora - st.session_state.inicio_turno).total_seconds() / 3600
        st.metric("Tempo Online", f"{int(decorrido)}h {int((decorrido%1)*60)}min")
        
        if st.button("🏁 ENCERRAR TURNO", use_container_width=True):
            st.session_state.tempo_final = decorrido
            st.session_state.turno_ativo = "finalizando"
            st.rerun()

    if st.session_state.get('turno_ativo') == "finalizando":
        bruto_t = st.number_input("Total Bruto (R$)", min_value=0.0)
        km_t = st.number_input("KM Percorrido", min_value=0.0)
        if st.button("💾 SALVAR TURNO"):
            novo_dia = pd.DataFrame([{
                "Data": hoje_ref.strftime("%d/%m/%Y"),
                "Bruto": bruto_t,
                "Líquido": bruto_t * 0.75, # Exemplo de cálculo de líquido
                "KM": km_t,
                "Horas": st.session_state.tempo_final
            }])
            salvar_dados(pd.concat([st.session_state.historico, novo_dia], ignore_index=True))
            st.session_state.turno_ativo = False
            st.success("Turno salvo!")
            st.rerun()

with tab_lan:
    st.subheader("Lançamento Manual")
    with st.form("manual"):
        f_bruto = st.number_input("Valor Bruto (R$)", min_value=0.0)
        f_km = st.number_input("KM Total", min_value=0.0)
        f_horas = st.number_input("Horas Trabalhadas", min_value=0.1)
        if st.form_submit_button("SALVAR DIA"):
            novo_dia = pd.DataFrame([{
                "Data": hoje_ref.strftime("%d/%m/%Y"),
                "Bruto": f_bruto,
                "Líquido": f_bruto * 0.75,
                "KM": f_km,
                "Horas": f_horas
            }])
            salvar_dados(pd.concat([st.session_state.historico, novo_dia], ignore_index=True))
            st.success("Dados salvos!")

with tab_hist:
    st.subheader("Histórico de Ganhos")
    if not st.session_state.historico.empty:
        st.dataframe(st.session_state.historico, use_container_width=True)
    else:
        st.write("Histórico vazio.")
