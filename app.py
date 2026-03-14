import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
# Ajuste na importação para compatibilidade nativa
from streamlit_gsheets import GSheetsConnection

# Configuração de App Mobile
st.set_page_config(
    page_title="UberPro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚗"
)

# --- CSS PARA APP, GRADE 2x3 E BOTÃO VERMELHO (MANTIDO) ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #000000; color: #ffffff; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    label, p, span, h1, h2, h3, .stMarkdown { color: #ffffff !important; }
    [data-testid="column"] { width: 50% !important; flex: 1 1 45% !important; min-width: 45% !important; }
    
    div.stButton > button:first-child:contains("LIMPAR") {
        color: #FF0000 !important;
        border-color: #FF0000 !important;
        background-color: transparent !important;
    }

    .card-faturamento { background-color: #00FF00; color: black !important; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; }
    .card-despesa { background-color: #FF0000; color: white !important; border-radius: 12px; padding: 15px; text-align: center; }
    .card-saldo { background-color: #800080; color: white !important; border-radius: 12px; padding: 15px; text-align: center; }
    .big-val { font-size: 20px; font-weight: bold; }
    .label-card { font-size: 10px; font-weight: 600; text-transform: uppercase; }
    .grid-item { background-color: #1C1C1E; border-radius: 12px; padding: 10px 2px; text-align: center; border: 1px solid #2C2C2E; margin-bottom: 5px; min-height: 85px; display: flex; flex-direction: column; justify-content: center; }
    .grid-label { color: #ffffff !important; font-size: 9px; font-weight: bold; text-transform: uppercase; opacity: 0.8; }
    .grid-value { color: #FFFFFF !important; font-size: 14px; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { background-color: #1C1C1E; border-radius: 8px 8px 0 0; color: #ffffff !important; padding: 8px; font-size: 12px; }
    .stTabs [aria-selected="true"] { background-color: #FF4500 !important; }
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO GOOGLE SHEETS (CORREÇÃO DE ESTABILIDADE) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Erro na conexão com a planilha. Verifique os Secrets.")
    st.stop()

# --- GESTÃO DE USUÁRIO (MANTIDA) ---
if 'usuario' not in st.session_state: st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("🚗 UberPro Login")
    user_input = st.text_input("Seu nome ou apelido:").strip().lower()
    if st.button("ENTRAR", use_container_width=True):
        if user_input:
            st.session_state.usuario = user_input
            st.rerun()
    st.stop()

# --- FUNÇÕES DE DADOS (CORRIGIDAS) ---
def carregar_tudo():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "Usuario"])

def limpar_historico_usuario():
    df_atual = carregar_tudo()
    df_novo = df_atual[df_atual['Usuario'] != st.session_state.usuario]
    conn.update(data=df_novo)
    st.success("Histórico limpo!")
    st.rerun()

# --- LOGICA APP (MANTIDA IGUAL) ---
df_completo = carregar_tudo()
df_user = df_completo[df_completo['Usuario'] == st.session_state.usuario].copy()

# ... (Restante do código das abas RES, TURNO, LANÇAR, HIST e CONTAS permanece 100% idêntico) ...
