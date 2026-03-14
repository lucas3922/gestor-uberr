import streamlit as st
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

# --- CSS PARA INTERFACE DARK MODE ---
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

# --- ARQUIVOS DE PERSISTÊNCIA ---
FILE_USERS = "usuarios_pro.csv"
FILE_HIST = "dados_uber_v2.csv"
FILE_CONTAS = "contas_uber_v2.csv"

# --- FUNÇÕES DE CARREGAMENTO COM LIMPEZA DE DADOS ---
def carregar_users():
    if os.path.exists(FILE_USERS):
        df = pd.read_csv(FILE_USERS)
        df['email'] = df['email'].astype(str).str.strip().str.lower()
        df['senha'] = df['senha'].astype(str).str.strip()
        return df
    return pd.DataFrame(columns=["email", "senha", "telefone"])

def carregar_dados_v2():
    if os.path.exists(FILE_HIST):
        return pd.read_csv(FILE_HIST)
    return pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq", "Usuario"])

def carregar_contas_v2():
    if os.path.exists(FILE_CONTAS):
        return pd.read_csv(FILE_CONTAS)
    return pd.DataFrame(columns=["Usuario", "Aluguel", "Luz", "Água", "Internet", "Cartões", "Financiamentos", "Outras"])

# --- CONTROLE DE SESSÃO ---
if 'user_logado' not in st.session_state:
    st.session_state.user_logado = None

# --- TELA DE ACESSO (LOGIN / CADASTRO) ---
if st.session_state.user_logado is None:
    st.markdown("<h2 style='text-align: center;'>🚗 UberPro System</h2>", unsafe_allow_html=True)
    t_login, t_cadastro = st.tabs(["🔐 ACESSAR", "📝 CADASTRAR"])

    with t_login:
        email_login = st.text_input("E-mail", key="l_email").strip().lower()
        senha_login = st.text_input("Senha", type="password", key="l_senha").strip()
        if st.button("ENTRAR", use_container_width=True):
            df_u = carregar_users()
            # Validação robusta
            valid_user = df_u[(df_u['email'] == email_login) & (df_u['senha'] == senha_login)]
            if not valid_user.empty:
                st.session_state.user_logado = email_login
                st.success("Acesso concedido!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    with t_cadastro:
        new_email = st.text_input("E-mail para cadastro", key="c_email").strip().lower()
        new_senha = st.text_input("Crie uma senha", type="password", key="c_senha").strip()
        new_tel = st.text_input("Telefone (WhatsApp)", key="c_tel").strip()
        if st.button("CRIAR MINHA CONTA", use_container_width=True):
            df_u = carregar_users()
            if new_email in df_u['email'].values:
                st.warning("Este e-mail já está cadastrado.")
            elif new_email and new_senha:
                novo_u = pd.DataFrame([{"email": new_email, "senha": new_senha, "telefone": new_tel}])
                pd.concat([df_u, novo_u], ignore_index=True).to_csv(FILE_USERS, index=False)
                st.success("Conta criada com sucesso! Mude para a aba ACESSAR.")
            else:
                st.error("Por favor, preencha todos os campos.")
    st.stop()

# --- VARIÁVEIS DO USUÁRIO LOGADO ---
user_atual = st.session_state.user_logado

df_hist_full = carregar_dados_v2()
df_user_hist = df_hist_full[df_hist_full['Usuario'] == user_atual].copy()

df_contas_full = carregar_contas_v2()
user_contas_row = df_contas_full[df_contas_full['Usuario'] == user_atual]

if not user_contas_row.empty:
    minhas_contas = user_contas_row.iloc[0].to_dict()
else:
    minhas_contas = {"Usuario": user_atual, "Aluguel": 0.0, "Luz": 0.0, "Água": 0.0, "Internet": 0.0, "Cartões": 0.0, "Financiamentos": 0.0, "Outras": 0.0}

# Cálculos de Meta
total_meta_casa = sum(float(v) for k, v in minhas_contas.items() if k != "Usuario" and pd.notnull(v))
dias_mes = calendar.monthrange(date.today().year, date.today().month)[1]
dias_restantes = max(1, (dias_mes - date.today().day) + 1)

# --- COMPONENTE DE RESULTADOS ---
def renderizar_grade(b, l, k, h, meta, dias, titulo):
    c = b - l
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento {titulo}</div><div class='big-val'>R$ {b:.2f}</div></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Custos</div><div class='big-val'>R$ {c:.2f}</div></div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo</div><div class='big-val'>R$ {l:.2f}</div></div>", unsafe_allow_html=True)
    st.write("")
    g1, g2 = st.columns(2)
    g1.markdown(f"<div class='grid-item'><div class='grid-label'>R$ / Hora</div><div class='grid-value'>R$ {b/h if h>0 else 0:.2f}</div></div>", unsafe_allow_html=True)
    g2.markdown(f"<div class='grid-item'><div class='grid-label'>R$ / KM</div><div class='grid-value'>R$ {b/k if k>0 else 0:.2f}</div></div>", unsafe_allow_html=True)
    
    if meta > 0:
        prog = min(l / meta, 1.0)
        st.write(f"🏠 *Progresso das Contas:* {prog*100:.1f}%")
        st.progress(prog)
        st.write(f"🎯 *Meta Diária Restante:* R$ {max(0.0, (meta-l)/dias):.2f}")

# --- ABAS PRINCIPAIS ---
tab_res, tab_turno, tab_lan, tab_hist, tab_contas = st.tabs(["📊 RES", "⏱️ TURNO", "➕ LANÇAR", "📅 HIST", "🏠 CONTAS"])

with tab_res:
    if not df_user_hist.empty:
        u = df_user_hist.iloc[-1]
        renderizar_grade(float(u["Bruto"]), float(u["Líquido"]), float(u["KM"]), float(u["Horas"]), total_meta_casa, dias_restantes, "Dia")
    else:
        st.info("Nenhum dado registrado hoje.")

with tab_turno:
    if 't_ativo' not in st.session_state: st.session_state.t_ativo = False
    
    if not st.session_state.t_ativo:
        if st.button("🚀 INICIAR TURNO", use_container_width=True, type="primary"):
            st.session_state.t_inicio = datetime.now()
            st.session_state.t_ativo = True
            st.rerun()
    else:
        decorrido = (datetime.now() - st.session_state.t_inicio).total_seconds() / 3600
        st.metric("Tempo Online", f"{int(decorrido)}h {int((decorrido%1)*60)}min")
        if st.button("🏁 FINALIZAR TURNO", use_container_width=True):
            st.session_state.t_final = decorrido
            st.session_state.t_ativo = "finalizando"
            st.rerun()

    if st.session_state.t_ativo == "finalizando":
        st.divider()
        b_turno = st.number_input("Ganho Bruto (R$)", min_value=0.0)
        k_turno = st.number_input("KM Rodados", min_value=0.0)
        c_turno = st.number_input("Combustível (R$)", min_value=0.0)
        if st.button("💾 SALVAR TURNO", use_container_width=True):
            liq = b_turno - c_turno
            horas = st.session_state.t_final if st.session_state.t_final > 0 else 0.1
            km = k_turno if k_turno > 0 else 1.0
            novo_reg = {"Data": date.today().strftime("%d/%m/%Y"), "Bruto": b_turno, "Líquido": liq, "KM": km, "Horas": horas, "KM_Liq": liq/km, "Hora_Liq": liq/horas, "Usuario": user_atual}
            pd.concat([df_hist_full, pd.DataFrame([novo_reg])], ignore_index=True).to_csv(FILE_HIST, index=False)
            st.session_state.t_ativo = False
            st.success("Salvo!")
            st.rerun()

with tab_lan:
    st.subheader("Lançamento Manual")
    d_lan = st.date_input("Data", value=date.today())
    b_lan = st.number_input("Ganho Bruto", key="ml_b")
    k_lan = st.number_input("KM Total", key="ml_k")
    h_lan = st.number_input("Total Horas", key="ml_h")
    c_lan = st.number_input("Gasto Combustível", key="ml_c")
    if st.button("💾 SALVAR DIA", use_container_width=True):
        liq = b_lan - c_lan
        novo_reg = {"Data": d_lan.strftime("%d/%m/%Y"), "Bruto": b_lan, "Líquido": liq, "KM": k_lan if k_lan>0 else 1, "Horas": h_lan if h_lan>0 else 1, "KM_Liq": liq/(k_lan if k_lan>0 else 1), "Hora_Liq": liq/(h_lan if h_lan>0 else 1), "Usuario": user_atual}
        pd.concat([df_hist_full, pd.DataFrame([novo_reg])], ignore_index=True).to_csv(FILE_HIST, index=False)
        st.success("Lançado!")
        st.rerun()

with tab_hist:
    if not df_user_hist.empty:
        df_display = df_user_hist.copy()
        df_display['Data_dt'] = pd.to_datetime(df_display['Data'], format='%d/%m/%Y')
        st.dataframe(df_display.sort_values('Data_dt', ascending=False).drop(columns=['Data_dt', 'Usuario']), use_container_width=True)
        
        with st.expander("🗑️ Apagar Registro"):
            opcoes = {f"{r['Data']} - R$ {r['Bruto']:.2f}": i for i, r in df_user_hist.iterrows()}
            escolha = st.selectbox("Selecione o registro:", list(opcoes.keys()))
            if st.button("APAGAR AGORA"):
                df_hist_full.drop(opcoes[escolha]).to_csv(FILE_HIST, index=False)
                st.success("Excluído!")
                st.rerun()
    else: st.info("Histórico vazio.")

with tab_contas:
    st.subheader("Configurações")
    for campo in ["Aluguel", "Luz", "Água", "Internet", "Cartões", "Financiamentos", "Outras"]:
        minhas_contas[campo] = st.number_input(campo, value=float(minhas_contas.get(campo, 0)))
    
    if st.button("💾 SALVAR MINHAS CONTAS", use_container_width=True):
        df_outros = df_contas_full[df_contas_full['Usuario'] != user_atual]
        pd.concat([df_outros, pd.DataFrame([minhas_contas])], ignore_index=True).to_csv(FILE_CONTAS, index=False)
        st.success("Contas atualizadas!")
        st.rerun()
    
    st.divider()
    if st.button("🚪 SAIR DO SISTEMA", use_container_width=True):
        st.session_state.user_logado = None
        st.rerun()
