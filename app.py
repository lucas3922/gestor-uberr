import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
import os
import time

# Configuração de App
st.set_page_config(page_title="UberPro", layout="wide", initial_sidebar_state="collapsed", page_icon="🚗")

# --- CSS DARK MODE ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    header, footer {visibility: hidden;}
    [data-testid="column"] { width: 50% !important; flex: 1 1 45% !important; min-width: 45% !important; }
    .card-faturamento { background-color: #00FF00; color: black !important; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; }
    .card-despesa { background-color: #FF0000; color: white !important; border-radius: 12px; padding: 15px; text-align: center; }
    .card-saldo { background-color: #800080; color: white !important; border-radius: 12px; padding: 15px; text-align: center; }
    .grid-item { background-color: #1C1C1E; border-radius: 12px; padding: 10px 2px; text-align: center; border: 1px solid #2C2C2E; margin-bottom: 5px; min-height: 85px; display: flex; flex-direction: column; justify-content: center; }
    .grid-label { font-size: 9px; font-weight: bold; text-transform: uppercase; opacity: 0.8; }
    .grid-value { font-size: 14px; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #FF4500 !important; }
</style>
""", unsafe_allow_html=True)

# --- ARQUIVOS ---
FILE_USERS = "usuarios_pro.csv"
FILE_HIST = "dados_uber_v2.csv"
FILE_CONTAS = "contas_uber_v2.csv"

# --- FUNÇÕES DE CARREGAMENTO ---
def carregar_users():
    if os.path.exists(FILE_USERS): return pd.read_csv(FILE_USERS)
    return pd.DataFrame(columns=["email", "senha", "telefone"])

def carregar_dados_v2():
    if os.path.exists(FILE_HIST): return pd.read_csv(FILE_HIST)
    return pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq", "Usuario"])

def carregar_contas_v2():
    if os.path.exists(FILE_CONTAS): return pd.read_csv(FILE_CONTAS)
    return pd.DataFrame(columns=["Usuario", "Aluguel", "Luz", "Água", "Internet", "Cartões", "Financiamentos", "Outras"])

# --- ESTADO DO LOGIN ---
if 'user_logado' not in st.session_state: st.session_state.user_logado = None

# --- TELA DE LOGIN / CADASTRO ---
if st.session_state.user_logado is None:
    tab_log, tab_cad = st.tabs(["🔐 LOGIN", "📝 CADASTRO"])
    
    with tab_log:
        st.subheader("Entrar")
        email_l = st.text_input("E-mail").strip().lower()
        senha_l = st.text_input("Senha", type="password")
        if st.button("ACESSAR", use_container_width=True):
            df_u = carregar_users()
            user = df_u[(df_u['email'] == email_l) & (df_u['senha'] == senha_l)]
            if not user.empty:
                st.session_state.user_logado = email_l
                st.rerun()
            else: st.error("E-mail ou Senha incorretos")
            
    with tab_cad:
        st.subheader("Criar Conta")
        email_c = st.text_input("Novo E-mail").strip().lower()
        senha_c = st.text_input("Nova Senha", type="password")
        tel_c = st.text_input("Telefone")
        if st.button("CRIAR CADASTRO", use_container_width=True):
            df_u = carregar_users()
            if email_c in df_u['email'].values: st.warning("E-mail já cadastrado!")
            elif email_c and senha_c:
                novo_u = pd.DataFrame([{"email": email_c, "senha": senha_c, "telefone": tel_c}])
                pd.concat([df_u, novo_u], ignore_index=True).to_csv(FILE_USERS, index=False)
                st.success("Cadastro realizado! Faça login.")
            else: st.error("Preencha e-mail e senha.")
    st.stop()

# --- LOGICA DO APP (PÓS-LOGIN) ---
usuario_atual = st.session_state.user_logado

# Carregar dados filtrados
df_hist_all = carregar_dados_v2()
df_user_hist = df_hist_all[df_hist_all['Usuario'] == usuario_atual].copy()

df_contas_all = carregar_contas_v2()
user_contas_row = df_contas_all[df_contas_all['Usuario'] == usuario_atual]

if not user_contas_row.empty:
    minhas_contas = user_contas_row.iloc[0].to_dict()
else:
    minhas_contas = {"Usuario": usuario_atual, "Aluguel": 0.0, "Luz": 0.0, "Água": 0.0, "Internet": 0.0, "Cartões": 0.0, "Financiamentos": 0.0, "Outras": 0.0}

total_casa = sum(float(v) for k, v in minhas_contas.items() if k != "Usuario" and pd.notnull(v))
dias_restantes = max(1, calendar.monthrange(date.today().year, date.today().month)[1] - date.today().day + 1)

# --- FUNÇÃO GRADE ---
def renderizar_grade(b, l, k, h, meta, dias, tit):
    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento {tit}</div><div class='big-val'>R$ {b:.2f}</div></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Custos</div><div class='big-val'>R$ {b-l:.2f}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Líquido</div><div class='big-val'>R$ {l:.2f}</div></div>", unsafe_allow_html=True)
    st.write("")
    g1, g2 = st.columns(2); g1.markdown(f"<div class='grid-item'><div class='grid-label'>Hora Bruta</div><div class='grid-value'>R$ {b/h if h>0 else 0:.2f}</div></div>", unsafe_allow_html=True); g2.markdown(f"<div class='grid-item'><div class='grid-label'>KM Bruto</div><div class='grid-value'>R$ {b/k if k>0 else 0:.2f}</div></div>", unsafe_allow_html=True)
    g3, g4 = st.columns(2); hi, mi = int(h), int((h-int(h))*60); g3.markdown(f"<div class='grid-item'><div class='grid-label'>Tempo</div><div class='grid-value'>{hi:02d}:{mi:02d}</div></div>", unsafe_allow_html=True); g4.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/Hora</div><div class='grid-value'>R$ {l/h if h>0 else 0:.2f}</div></div>", unsafe_allow_html=True)
    if meta > 0:
        p = min(l/meta, 1.0)
        st.write(f"🏠 Meta: R$ {meta:.2f} | {p*100:.1f}%")
        st.progress(p)

# --- INTERFACE ---
tab_res, tab_turno, tab_lan, tab_hist, tab_contas = st.tabs(["📊 RES", "⏱️ TURNO", "➕ LANÇAR", "📅 HIST", "🏠 CONTAS"])

with tab_res:
    if not df_user_hist.empty:
        u = df_user_hist.iloc[-1]
        renderizar_grade(float(u["Bruto"]), float(u["Líquido"]), float(u["KM"]), float(u["Horas"]), total_casa, dias_restantes, "Dia")
    else: st.info("Sem dados.")

with tab_turno:
    if 't_ativo' not in st.session_state: st.session_state.t_ativo = False
    if not st.session_state.t_ativo:
        if st.button("🚀 INICIAR", use_container_width=True):
            st.session_state.t_inicio = datetime.now(); st.session_state.t_ativo = True; st.rerun()
    else:
        dec = (datetime.now() - st.session_state.t_inicio).total_seconds()/3600
        st.metric("Tempo Online", f"{int(dec)}h {int((dec%1)*60)}m")
        if st.button("🏁 FINALIZAR"):
            st.session_state.t_final = dec; st.session_state.t_ativo = "fim"; st.rerun()
    if st.session_state.t_ativo == "fim":
        br = st.number_input("Bruto")
        km = st.number_input("KM")
        co = st.number_input("Combustível")
        if st.button("SALVAR"):
            liq = br - co
            nv = {"Data": date.today().strftime("%d/%m/%Y"), "Bruto": br, "Líquido": liq, "KM": km if km>0 else 1, "Horas": st.session_state.t_final, "KM_Liq": liq/(km if km>0 else 1), "Hora_Liq": liq/st.session_state.t_final, "Usuario": usuario_atual}
            pd.concat([df_hist_all, pd.DataFrame([nv])], ignore_index=True).to_csv(FILE_HIST, index=False)
            st.session_state.t_ativo = False; st.rerun()

with tab_hist:
    if not df_user_hist.empty:
        st.dataframe(df_user_hist.sort_index(ascending=False).drop(columns=['Usuario']), use_container_width=True)
        if st.button("🗑️ APAGAR ÚLTIMO"):
            df_hist_all.drop(df_user_hist.index[-1]).to_csv(FILE_HIST, index=False); st.rerun()

with tab_contas:
    for c in ["Aluguel", "Luz", "Água", "Internet", "Cartões", "Financiamentos", "Outras"]:
        minhas_contas[c] = st.number_input(c, value=float(minhas_contas.get(c, 0)))
    if st.button("SALVAR CONTAS"):
        df_sem_mim = df_contas_all[df_contas_all['Usuario'] != usuario_atual]
        pd.concat([df_sem_mim, pd.DataFrame([minhas_contas])], ignore_index=True).to_csv(FILE_CONTAS, index=False)
        st.success("Salvo!"); st.rerun()
    if st.button("SAIR"): st.session_state.user_logado = None; st.rerun()
