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

# --- CSS PARA INTERFACE DE APP DARK MODE ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    .block-container { padding-top: 0.5rem; padding-bottom: 2rem; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    label, p, span, h1, h2, h3, .stMarkdown { color: #ffffff !important; }
    [data-testid="column"] { width: 50% !important; flex: 1 1 45% !important; min-width: 45% !important; }
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

    /* ALTERAÇÃO PEDIDA: texto dos botões em vermelho */
    button[kind="secondary"] p { color: red !important; }

</style>
""", unsafe_allow_html=True)

FILE_HIST = "dados_uber.csv"
FILE_CONTAS = "contas_uber.csv"

def carregar_dados():
    if os.path.exists(FILE_HIST):
        try:
            return pd.read_csv(FILE_HIST)
        except:
            pass
    return pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"])

def carregar_contas():
    padrao = {"Aluguel": 0.0, "Luz": 0.0, "Água": 0.0, "Internet": 0.0, "Cartões": 0.0, "Financiamentos": 0.0, "Outras": 0.0}
    if os.path.exists(FILE_CONTAS):
        try:
            df = pd.read_csv(FILE_CONTAS)
            if not df.empty:
                return df.iloc[0].to_dict()
        except:
            pass
    return padrao

if 'historico' not in st.session_state:
    st.session_state.historico = carregar_dados()

if 'contas' not in st.session_state:
    st.session_state.contas = carregar_contas()

hoje_ref = date.today()
ultimo_dia = calendar.monthrange(hoje_ref.year, hoje_ref.month)[1]
dias_restantes = max(1, (ultimo_dia - hoje_ref.day) + 1)
total_casa = sum(float(v) for v in st.session_state.contas.values() if v is not None)

tab_res, tab_turno, tab_lan, tab_hist, tab_contas = st.tabs(
["📊 RESULTADOS","🚦 TURNO","➕ LANÇAR","📅 HISTÓRICO","🏠 CONTAS"]
)

def renderizar_grade(b, l, k, h, total_meta, dias_f, titulo_aba=""):
    c = b - l
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento {titulo_aba}</div><div class='big-val'>R$ {b:.2f}</div></div>", unsafe_allow_html=True)
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Despesas</div><div class='big-val'>R$ {c:.2f}</div></div>", unsafe_allow_html=True)
    with c_sub2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo</div><div class='big-val'>R$ {l:.2f}</div></div>", unsafe_allow_html=True)

    st.write("")
    g1, g2 = st.columns(2)
    with g1: st.markdown(f"<div class='grid-item'><div class='grid-label'>Hora Bruta</div><div class='grid-value'>R$ {(b/h if h > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    with g2: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Bruto</div><div class='grid-value'>R$ {(b/k if k > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)

with tab_res:
    if not st.session_state.historico.empty:
        u = st.session_state.historico.iloc[-1]
        renderizar_grade(float(u["Bruto"]), float(u["Líquido"]), float(u["KM"]), float(u["Horas"]), total_casa, dias_restantes, "Dia")
    else:
        renderizar_grade(0.0,0.0,1.0,1.0,total_casa,dias_restantes,"Dia")

with tab_turno:

    st.subheader("🚦 Modo Turno Inteligente")

    if "turno_ativo" not in st.session_state:
        st.session_state.turno_ativo = False

    if "inicio_turno" not in st.session_state:
        st.session_state.inicio_turno = None

    if "ganho_turno" not in st.session_state:
        st.session_state.ganho_turno = 0.0

    if "km_turno" not in st.session_state:
        st.session_state.km_turno = 0.0

    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.turno_ativo:
            if st.button("▶ INICIAR TURNO", use_container_width=True):
                st.session_state.turno_ativo = True
                st.session_state.inicio_turno = datetime.now()
                st.session_state.ganho_turno = 0.0
                st.session_state.km_turno = 0.0
                st.rerun()

    with col2:
        if st.session_state.turno_ativo:
            if st.button("⏹ ENCERRAR TURNO", use_container_width=True):

                tempo = datetime.now() - st.session_state.inicio_turno
                horas = tempo.total_seconds() / 3600

                ganho = st.session_state.ganho_turno
                km = st.session_state.km_turno

                if ganho > 0:

                    k_calc = km if km > 0 else 1.0
                    h_calc = horas if horas > 0 else 1.0

                    novo = {
                        "Data": date.today().strftime("%d/%m/%Y"),
                        "Bruto": ganho,
                        "Líquido": ganho,
                        "KM": k_calc,
                        "Horas": h_calc,
                        "KM_Liq": ganho/k_calc,
                        "Hora_Liq": ganho/h_calc
                    }

                    st.session_state.historico = pd.concat(
                        [st.session_state.historico, pd.DataFrame([novo])],
                        ignore_index=True
                    )

                    st.session_state.historico.to_csv(FILE_HIST, index=False)

                st.session_state.turno_ativo = False
                st.success("Turno salvo no histórico!")
                st.rerun()
