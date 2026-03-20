import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from supabase import create_client

# 🔐 CONFIG SUPABASE
SUPABASE_URL = "SUA_URL"
SUPABASE_KEY = "SUA_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="UberPro", layout="wide")

# --- LOGIN SIMPLES ---
if "user" not in st.session_state:
    st.session_state.user = None

def login():
    st.title("🚗 UberPro Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": senha
            })
            st.session_state.user = res.user.id
            st.success("Login feito!")
            st.rerun()
        except:
            st.error("Erro no login")

    if st.button("Criar conta"):
        try:
            supabase.auth.sign_up({
                "email": email,
                "password": senha
            })
            st.success("Conta criada!")
        except:
            st.error("Erro ao criar conta")

if not st.session_state.user:
    login()
    st.stop()

user_id = st.session_state.user

# --- FUNÇÕES BANCO ---
def carregar_dados():
    res = supabase.table("registros").select("*").eq("user_id", user_id).execute()
    return pd.DataFrame(res.data)

def salvar_dado(d):
    d["user_id"] = user_id
    supabase.table("registros").insert(d).execute()

def carregar_contas():
    res = supabase.table("contas").select("*").eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]
    return {"aluguel":0,"luz":0,"agua":0,"internet":0,"cartoes":0,"financiamentos":0,"outras":0}

def salvar_contas(c):
    c["user_id"] = user_id
    supabase.table("contas").upsert(c).execute()

# --- ESTADO ---
if "historico" not in st.session_state:
    st.session_state.historico = carregar_dados()

if "contas" not in st.session_state:
    st.session_state.contas = carregar_contas()

if "turno_ativo" not in st.session_state:
    st.session_state.turno_ativo = False

# --- UI ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Resultados","⏱️ Turno","➕ Lançar","📅 Histórico","🏠 Contas"])

# --- RESULTADOS ---
with tab1:
    df = st.session_state.historico

    if not df.empty:
        total = df["liquido"].sum()
        media = df["liquido"].mean()

        st.metric("💰 Total", f"R$ {total:.2f}")
        st.metric("📊 Média", f"R$ {media:.2f}")

        # 📈 previsão
        hoje = date.today()
        ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
        dias_restantes = ultimo_dia - hoje.day

        previsao = media * ultimo_dia
        st.info(f"📈 Previsão mês: R$ {previsao:.2f}")

        st.line_chart(df["liquido"])

# --- TURNO ---
with tab2:
    if not st.session_state.turno_ativo:
        if st.button("🚀 Iniciar"):
            st.session_state.inicio = datetime.now()
            st.session_state.turno_ativo = True
            st.rerun()
    else:
        tempo = (datetime.now() - st.session_state.inicio).total_seconds()/3600
        st.metric("Tempo", f"{tempo:.2f}h")

        if st.button("Encerrar"):
            st.session_state.turno_ativo = "fim"

    if st.session_state.turno_ativo == "fim":
        bruto = st.number_input("Bruto")
        km = st.number_input("KM")
        combustivel = st.number_input("Combustível")

        if st.button("Salvar turno"):
            liquido = bruto - combustivel
            horas = max(tempo, 0.01)

            salvar_dado({
                "data": str(date.today()),
                "bruto": bruto,
                "liquido": liquido,
                "km": km,
                "horas": horas,
                "km_liq": liquido/km if km > 0 else 0,
                "hora_liq": liquido/horas
            })

            st.success("Salvo!")
            st.session_state.turno_ativo = False
            st.session_state.historico = carregar_dados()
            st.rerun()

# --- LANÇAMENTO ---
with tab3:
    bruto = st.number_input("Bruto")
    km = st.number_input("KM")
    horas = st.number_input("Horas")
    comb = st.number_input("Combustível")

    if st.button("Salvar dia"):
        liquido = bruto - comb

        salvar_dado({
            "data": str(date.today()),
            "bruto": bruto,
            "liquido": liquido,
            "km": km,
            "horas": horas,
            "km_liq": liquido/km if km>0 else 0,
            "hora_liq": liquido/horas if horas>0 else 0
        })

        st.success("Salvo!")
        st.session_state.historico = carregar_dados()
        st.rerun()

# --- HISTÓRICO ---
with tab4:
    df = st.session_state.historico

    if not df.empty:
        st.dataframe(df)

# --- CONTAS ---
with tab5:
    c = st.session_state.contas

    for k in c:
        c[k] = st.number_input(k, value=float(c[k]))

    if st.button("Salvar contas"):
        salvar_contas(c)
        st.success("Salvo!")
