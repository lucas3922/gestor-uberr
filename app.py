import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from streamlit_gsheets import GSheetsConnection

# Configuração de App Mobile
st.set_page_config(
    page_title="UberPro", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="🚗"
)

# --- CSS PARA APP, GRADE 2x3 E BOTÃO VERMELHO ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #000000; color: #ffffff; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    label, p, span, h1, h2, h3, .stMarkdown { color: #ffffff !important; }
    [data-testid="column"] { width: 50% !important; flex: 1 1 45% !important; min-width: 45% !important; }
    
    /* Botão Limpar em Vermelho */
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

# --- CONEXÃO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- GESTÃO DE USUÁRIO ---
if 'usuario' not in st.session_state: st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("🚗 UberPro Login")
    user_input = st.text_input("Seu nome ou apelido:").strip().lower()
    if st.button("ENTRAR", use_container_width=True):
        if user_input:
            st.session_state.usuario = user_input
            st.rerun()
    st.stop()

# --- FUNÇÕES DE DADOS ---
def carregar_tudo():
    try:
        return conn.read(worksheet="dados", ttl=0)
    except:
        return pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "Usuario"])

def limpar_historico_usuario():
    df_atual = carregar_tudo()
    df_novo = df_atual[df_atual['Usuario'] != st.session_state.usuario]
    conn.update(worksheet="dados", data=df_novo)
    st.success("Histórico limpo!")
    st.rerun()

# --- LOGICA APP ---
df_completo = carregar_tudo()
df_user = df_completo[df_completo['Usuario'] == st.session_state.usuario].copy()

if 'contas' not in st.session_state:
    try:
        df_c = conn.read(worksheet="contas", ttl=0)
        user_c = df_c[df_c['Usuario'] == st.session_state.usuario]
        st.session_state.contas = user_c.iloc[0].to_dict() if not user_c.empty else {"Aluguel":0,"Luz":0,"Água":0,"Internet":0,"Cartões":0,"Financiamentos":0,"Outras":0}
    except:
        st.session_state.contas = {"Aluguel":0,"Luz":0,"Água":0,"Internet":0,"Cartões":0,"Financiamentos":0,"Outras":0}

total_casa = sum(float(v) for k, v in st.session_state.contas.items() if k != 'Usuario')
hoje_ref = date.today()
dias_restantes = max(1, (calendar.monthrange(hoje_ref.year, hoje_ref.month)[1] - hoje_ref.day) + 1)

def renderizar_grade(b, l, k, h, titulo=""):
    c = b - l
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento {titulo}</div><div class='big-val'>R$ {b:.2f}</div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Despesas</div><div class='big-val'>R$ {c:.2f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo</div><div class='big-val'>R$ {l:.2f}</div></div>", unsafe_allow_html=True)
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
    with g5: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Rodado</div><div class='grid-value'>{k:.1f}</div></div>", unsafe_allow_html=True)
    with g6: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/KM</div><div class='grid-value'>R$ {(l/k if k > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    if total_casa > 0:
        prog = min(max(0.0, l / total_casa), 1.0)
        st.write(f"🏠 *Abate Contas:* {prog*100:.1f}%")
        st.progress(prog)

# --- ABAS ---
tab_res, tab_turno, tab_lan, tab_hist, tab_contas = st.tabs(["📊 RES", "⏱️ TURNO", "➕ LANÇAR", "📅 HIST", "🏠 CONTAS"])

with tab_res:
    if not df_user.empty:
        u = df_user.iloc[-1]
        renderizar_grade(float(u["Bruto"]), float(u["Líquido"]), float(u["KM"]), float(u["Horas"]), "Dia")
    else: renderizar_grade(0,0,1,1,"Dia")
    st.divider()
    if st.button("🗑️ LIMPAR MEU HISTÓRICO", key="btn_res", use_container_width=True): limpar_historico_usuario()

with tab_turno:
    st.subheader("Modo Turno")
    if 'turno_ativo' not in st.session_state or not st.session_state.turno_ativo:
        if st.button("🚀 INICIAR TURNO", use_container_width=True):
            st.session_state.inicio_turno = datetime.now()
            st.session_state.turno_ativo = True
            st.rerun()
    else:
        decorrido = (datetime.now() - st.session_state.inicio_turno).total_seconds() / 3600
        st.metric("Tempo Online", f"{int(decorrido)}h {int((decorrido%1)*60)}min")
        if st.button("🏁 ENCERRAR TURNO", use_container_width=True):
            st.session_state.tempo_final = decorrido
            st.session_state.turno_ativo = "finalizando"
            st.rerun()
    if st.session_state.get('turno_ativo') == "finalizando":
        b_t = st.number_input("Bruto R$", value=0.0)
        k_t = st.number_input("KM", value=0.0)
        if st.button("💾 SALVAR TURNO", use_container_width=True):
            novo = pd.DataFrame([{"Data":date.today().strftime("%d/%m/%Y"), "Bruto":b_t, "Líquido":b_t, "KM":k_t, "Horas":st.session_state.tempo_final, "Usuario":st.session_state.usuario}])
            conn.update(worksheet="dados", data=pd.concat([df_completo, novo]))
            st.session_state.turno_ativo = False
            st.rerun()
    st.divider()
    if st.button("🗑️ LIMPAR MEU HISTÓRICO", key="btn_turno", use_container_width=True): limpar_historico_usuario()

with tab_lan:
    st.subheader("Lançamento Manual")
    b_man = st.number_input("Ganho Bruto", value=0.0)
    k_man = st.number_input("KM", value=0.0)
    h_man = st.number_input("Horas", value=0.0)
    if st.button("💾 SALVAR DIA", use_container_width=True):
        novo = pd.DataFrame([{"Data":date.today().strftime("%d/%m/%Y"), "Bruto":b_man, "Líquido":b_man, "KM":k_man, "Horas":h_man, "Usuario":st.session_state.usuario}])
        conn.update(worksheet="dados", data=pd.concat([df_completo, novo]))
        st.success("Salvo!")
        st.rerun()
    st.divider()
    if st.button("🗑️ LIMPAR MEU HISTÓRICO", key="btn_lan", use_container_width=True): limpar_historico_usuario()

with tab_hist:
    if not df_user.empty:
        renderizar_grade(df_user["Bruto"].sum(), df_user["Líquido"].sum(), df_user["KM"].sum(), df_user["Horas"].sum(), "Total")
        st.divider()
        st.dataframe(df_user.drop(columns=["Usuario"]), use_container_width=True)
    st.divider()
    if st.button("🗑️ LIMPAR MEU HISTÓRICO", key="btn_hist", use_container_width=True): limpar_historico_usuario()

with tab_contas:
    st.subheader("🏠 Contas")
    if st.button("🚪 SAIR", use_container_width=True):
        st.session_state.usuario = None
        st.rerun()
    st.divider()
    if st.button("🗑️ LIMPAR MEU HISTÓRICO", key="btn_contas", use_container_width=True): limpar_historico_usuario()
