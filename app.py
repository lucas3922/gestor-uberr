Import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import os
import time

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
    .stButton>button { border-radius: 12px; height: 3em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- PERSISTÊNCIA ---
FILE_HIST = "dados_uber.csv"
FILE_CONTAS = "contas_uber.csv"

def carregar_dados_todos():
    if os.path.exists(FILE_HIST):
        try: return pd.read_csv(FILE_HIST)
        except: pass
    return pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq", "Usuario"])

def carregar_contas_todas():
    if os.path.exists(FILE_CONTAS):
        try: return pd.read_csv(FILE_CONTAS)
        except: pass
    return pd.DataFrame(columns=["Usuario", "Aluguel", "Luz", "Água", "Internet", "Cartões", "Financiamentos", "Outras"])

# --- SISTEMA DE LOGIN ---
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("<h2 style='text-align: center;'>🚗 UberPro Login</h2>", unsafe_allow_html=True)
    user_input = st.text_input("Digite seu nome para acessar:", placeholder="Ex: Lucas").strip().lower()
    if st.button("ENTRAR NO SISTEMA", use_container_width=True):
        if user_input:
            st.session_state.usuario = user_input
            st.rerun()
    st.stop()

# --- FILTRAGEM DE DADOS POR USUÁRIO ---
df_todos_hist = carregar_dados_todos()
df_user_hist = df_todos_hist[df_todos_hist['Usuario'] == st.session_state.usuario].copy()

df_todas_contas = carregar_contas_todas()
user_contas_df = df_todas_contas[df_todas_contas['Usuario'] == st.session_state.usuario]

if not user_contas_df.empty:
    st.session_state.contas = user_contas_df.iloc[0].to_dict()
else:
    st.session_state.contas = {"Usuario": st.session_state.usuario, "Aluguel": 0.0, "Luz": 0.0, "Água": 0.0, "Internet": 0.0, "Cartões": 0.0, "Financiamentos": 0.0, "Outras": 0.0}

# Inicialização de Turno
if 'turno_ativo' not in st.session_state: st.session_state.turno_ativo = False
if 'inicio_turno' not in st.session_state: st.session_state.inicio_turno = None

# Variáveis Globais de Cálculo
hoje_ref = date.today()
ultimo_dia = calendar.monthrange(hoje_ref.year, hoje_ref.month)[1]
dias_restantes = max(1, (ultimo_dia - hoje_ref.day) + 1)
total_casa = sum(float(v) for k, v in st.session_state.contas.items() if k != "Usuario" and v is not None)

# --- FUNÇÃO DE RENDERIZAR GRADE ---
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
    g3, g4 = st.columns(2)
    with g3: 
        hi, mi = int(h), int((h - int(h)) * 60)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Tempo</div><div class='grid-value'>{hi:02d}:{mi:02d}</div></div>", unsafe_allow_html=True)
    with g4: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/Hora</div><div class='grid-value'>R$ {(l/h if h > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    g5, g6 = st.columns(2)
    with g5: st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Rodado</div><div class='grid-value'>{k:.1f}</div></div>", unsafe_allow_html=True)
    with g6: st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/KM</div><div class='grid-value'>R$ {(l/k if k > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)
    
    if total_meta > 0:
        prog = min(max(0.0, l / total_meta), 1.0)
        restante = total_meta - l
        meta_real = restante / dias_f if dias_f > 0 else restante
        st.write(f"🏠 *Abate das Contas ({st.session_state.usuario.capitalize()}):* {prog*100:.1f}%")
        st.progress(prog)
        st.write(f"📉 *Falta para quitar:* R$ {max(0.0, restante):.2f}")

# --- ABAS ---
tab_res, tab_turno, tab_lan, tab_hist, tab_contas = st.tabs(["📊 RESULTADOS", "⏱️ TURNO", "➕ LANÇAR", "📅 HISTÓRICO", "🏠 CONTAS"])

with tab_res:
    if not df_user_hist.empty:
        u = df_user_hist.iloc[-1]
        renderizar_grade(float(u["Bruto"]), float(u["Líquido"]), float(u["KM"]), float(u["Horas"]), total_casa, dias_restantes, "Dia")
    else: renderizar_grade(0.0, 0.0, 1.0, 1.0, total_casa, dias_restantes, "Dia")

with tab_turno:
    st.subheader(f"Modo Turno: {st.session_state.usuario.capitalize()}")
    if not st.session_state.turno_ativo:
        if st.button("🚀 INICIAR TURNO", use_container_width=True, type="primary"):
            st.session_state.inicio_turno = datetime.now()
            st.session_state.turno_ativo = True
            st.rerun()
    else:
        agora = datetime.now()
        decorrido = agora - st.session_state.inicio_turno
        horas_dec = decorrido.total_seconds() / 3600
        st.metric("Tempo Online", f"{int(horas_dec)}h {int((horas_dec%1)*60)}min")
        if st.button("🏁 ENCERRAR TURNO", use_container_width=True):
            st.session_state.tempo_final = horas_dec
            st.session_state.turno_ativo = "finalizando"
            st.rerun()

    if st.session_state.turno_ativo == "finalizando":
        st.divider()
        b_turno = st.number_input("Ganho Bruto (R$)", value=0.0)
        k_turno = st.number_input("KM Rodados", value=0.0)
        c_turno = st.number_input("Combustível (R$)", value=0.0)
        if st.button("💾 CONFIRMAR E SALVAR", use_container_width=True):
            l_calc = b_turno - c_turno
            h_calc = st.session_state.tempo_final if st.session_state.tempo_final > 0 else 0.1
            k_calc = k_turno if k_turno > 0 else 1.0
            novo = {"Data": date.today().strftime("%d/%m/%Y"), "Bruto": b_turno, "Líquido": l_calc, "KM": k_calc, "Horas": h_calc, "KM_Liq": l_calc/k_calc, "Hora_Liq": l_calc/h_calc, "Usuario": st.session_state.usuario}
            df_final = pd.concat([df_todos_hist, pd.DataFrame([novo])], ignore_index=True)
            df_final.to_csv(FILE_HIST, index=False)
            st.session_state.turno_ativo = False
            st.success("Salvo!")
            st.rerun()

with tab_lan:
    st.subheader("Lançamento Manual")
    data_lan = st.date_input("Data", value=date.today())
    b_in = st.number_input("Ganho Bruto", value=0.0, key="b_man")
    k_in = st.number_input("KM Total", value=0.0, key="k_man")
    h_in = st.number_input("Horas", value=0.0, key="h_man")
    c_in = st.number_input("Combustível", value=0.0, key="c_man")
    if st.button("💾 SALVAR DIA", use_container_width=True):
        l_calc = b_in - c_in
        novo = {"Data": data_lan.strftime("%d/%m/%Y"), "Bruto": b_in, "Líquido": l_calc, "KM": k_in if k_in > 0 else 1, "Horas": h_in if h_in > 0 else 1, "KM_Liq": l_calc/(k_in if k_in > 0 else 1), "Hora_Liq": l_calc/(h_in if h_in > 0 else 1), "Usuario": st.session_state.usuario}
        pd.concat([df_todos_hist, pd.DataFrame([novo])], ignore_index=True).to_csv(FILE_HIST, index=False)
        st.success("Salvo!")
        st.rerun()

with tab_hist:
    if not df_user_hist.empty:
        df_user_hist['Data_dt'] = pd.to_datetime(df_user_hist['Data'], format='%d/%m/%Y')
        periodo = st.radio("Período:", ["Semana", "Mês", "Ano"], horizontal=True)
        # Filtros simplificados para o usuário
        st.dataframe(df_user_hist.sort_values(by='Data_dt', ascending=False).drop(columns=['Data_dt', 'Usuario']), use_container_width=True)
        
        with st.expander("🗑️ Apagar Registro"):
            opcoes = {f"{row['Data']} - R$ {row['Bruto']:.2f}": idx for idx, row in df_user_hist.iterrows()}
            selecionado = st.selectbox("Selecione:", options=list(opcoes.keys()))
            if st.button("CONFIRMAR EXCLUSÃO"):
                df_restante = df_todos_hist.drop(opcoes[selecionado])
                df_restante.to_csv(FILE_HIST, index=False)
                st.rerun()
    else: st.info("Sem dados para este usuário.")

with tab_contas:
    st.subheader(f"🏠 Contas de {st.session_state.usuario.capitalize()}")
    c1, c2 = st.columns(2)
    campos = ["Aluguel", "Luz", "Água", "Internet", "Cartões", "Financiamentos", "Outras"]
    for i, campo in enumerate(campos):
        col = c1 if i < 4 else c2
        st.session_state.contas[campo] = col.number_input(campo, value=float(st.session_state.contas.get(campo, 0)))
    
    col_save, col_logout = st.columns(2)
    if col_save.button("💾 SALVAR CONTAS", use_container_width=True):
        df_sem_user = df_todas_contas[df_todas_contas['Usuario'] != st.session_state.usuario]
        df_novo_contas = pd.concat([df_sem_user, pd.DataFrame([st.session_state.contas])], ignore_index=True)
        df_novo_contas.to_csv(FILE_CONTAS, index=False)
        st.success("Salvo!")
        st.rerun()
    
    if col_logout.button("🚪 SAIR / TROCAR USUÁRIO", use_container_width=True):
        st.session_state.usuario = None
        st.rerun()


