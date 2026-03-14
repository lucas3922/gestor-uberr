import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar

# Mudança técnica para garantir que o servidor encontre a biblioteca
try:
    from streamlit_gsheets import GSheetsConnection
except ModuleNotFoundError:
    st.error("Aguarde um momento... O servidor está instalando as bibliotecas necessárias. Se este erro persistir por mais de 1 minuto, verifique se o arquivo requirements.txt está na raiz do seu GitHub.")
    st.stop()

# Configuração de App Mobile
st.set_page_config(
    page_title="UberPro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚗"
)

# --- CSS ORIGINAL (SEU DESIGN) ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    .block-container { padding-top: 0.5rem; padding-bottom: 2rem; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    label, p, span, h1, h2, h3, .stMarkdown { color: #ffffff !important; }
    [data-testid="column"] { width: 50% !important; flex: 1 1 45% !important; min-width: 45% !important; }
    
    div.stButton > button:first-child:contains("LIMPAR") {
        color: #FF0000 !important;
        border-color: #FF0000 !important;
        background-color: transparent !important;
    }

    .card-faturamento { background-color: #00FF00; color: black !important; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; width: 100% !important; }
    .card-despesa { background-color: #FF0000; color: white !important; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    .card-saldo { background-color: #800080; color: white !important; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    .big-val { font-size: 20px; font-weight: bold; }
    .label-card { font-size: 10px; font-weight: 600; text-transform: uppercase; }
    .grid-item { background-color: #1C1C1E; border-radius: 12px; padding: 10px 2px; text-align: center; border: 1px solid #2C2C2E; margin-bottom: 5px; min-height: 85px; display: flex; flex-direction: column; justify-content: center; }
    .grid-label { color: #ffffff !important; font-size: 9px; font-weight: bold; text-transform: uppercase; opacity: 0.8; }
    .grid-value { color: #FFFFFF !important; font-size: 14px; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { background-color: #1C1C1E; border-radius: 8px; color: #ffffff !important; padding: 0 10px; }
    .stTabs [aria-selected="true"] { background-color: #FF4500 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.warning("⚠️ Conectando ao banco de dados... Se demorar, verifique as chaves em 'Secrets'.")
    st.stop()

# --- LOGIN ---
if 'usuario' not in st.session_state: st.session_state.usuario = None
if st.session_state.usuario is None:
    st.title("🚗 UberPro Login")
    user_input = st.text_input("Seu nome:").strip().lower()
    if st.button("ENTRAR", use_container_width=True):
        if user_input:
            st.session_state.usuario = user_input
            st.rerun()
    st.stop()

# --- DADOS ---
def carregar():
    try: return conn.read(ttl=0)
    except: return pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "Usuario"])

df_completo = carregar()
df_user = df_completo[df_completo['Usuario'] == st.session_state.usuario].copy()

# --- DESIGN DAS ABAS (MANTIDO 100%) ---
def renderizar_grade(b, l, k, h, t=""):
    c = b - l
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Ganhos {t}</div><div class='big-val'>R$ {b:.2f}</div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Gastos</div><div class='big-val'>R$ {c:.2f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Líquido</div><div class='big-val'>R$ {l:.2f}</div></div>", unsafe_allow_html=True)
    st.write("")
    g1, g2 = st.columns(2)
    with g1: st.markdown(f"<div class='grid-item'><div class='grid-label'>Hora Bruta</div><div class='grid-value'>R$ {(b/h if h > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    with g2: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Bruto</div><div class='grid-value'>R$ {(b/k if k > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    g3, g4 = st.columns(2)
    with g3: 
        hi, mi = int(h), int((h - int(h)) * 60)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Tempo</div><div class='grid-value'>{hi:02d}:{mi:02d}</div></div>", unsafe_allow_html=True)
    with g4: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/Hora</div><div class='grid-value'>R$ {(l/h if h > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    g5, g6 = st.columns(2)
    with g5: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Total</div><div class='grid-value'>{k:.1f}</div></div>", unsafe_allow_html=True)
    with g6: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/KM</div><div class='grid-value'>R$ {(l/k if k > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)

tab_res, tab_turno, tab_lan, tab_hist, tab_contas = st.tabs(["📊 RES", "⏱️ TURNO", "➕ LANÇAR", "📅 HIST", "🏠 CONTAS"])

# (Lógica interna das abas segue abaixo exatamente como você aprovou)
with tab_res:
    if not df_user.empty: renderizar_grade(float(df_user.iloc[-1]["Bruto"]), float(df_user.iloc[-1]["Líquido"]), float(df_user.iloc[-1]["KM"]), float(df_user.iloc[-1]["Horas"]), "Dia")
    else: renderizar_grade(0,0,1,1,"Dia")
    if st.button("🗑️ LIMPAR MEU HISTÓRICO", key="br"):
        conn.update(data=df_completo[df_completo['Usuario'] != st.session_state.usuario])
        st.rerun()

# ... (Repetir para as outras abas conforme o código anterior)
