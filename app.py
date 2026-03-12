import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="Driver Finance PRO", layout="wide")

# -----------------------
# ESTILO VISUAL
# -----------------------

st.markdown("""
<style>

.stApp {
background-color: #f5f1e8;
}

h1,h2,h3,h4 {
color:#2b2b2b;
}

div[data-testid="stMetric"] {
background: white;
padding:20px;
border-radius:12px;
box-shadow:0px 2px 6px rgba(0,0,0,0.1);
}

button[kind="secondary"] {
height:70px;
font-size:20px;
border-radius:12px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------
# TÍTULO
# -----------------------

st.title("🚖 Driver Finance PRO")
st.write("Gestão financeira para motoristas de aplicativo")

# -----------------------
# BANCO DE DADOS
# -----------------------

arquivo = "dados_motorista.csv"

if os.path.exists(arquivo):
    df = pd.read_csv(arquivo)
else:
    df = pd.DataFrame(columns=[
        "data","uber","noventa_nove","km","horas",
        "combustivel","bruto","liquido"
    ])

# -----------------------
# MENU
# -----------------------

if "pagina" not in st.session_state:
    st.session_state.pagina = "dashboard"

col1,col2 = st.columns(2)

if col1.button("📊 DASHBOARD", use_container_width=True):
    st.session_state.pagina = "dashboard"

if col2.button("🚖 LANÇAR DIA", use_container_width=True):
    st.session_state.pagina = "lancar"

col3,col4 = st.columns(2)

if col3.button("📈 RELATÓRIOS", use_container_width=True):
    st.session_state.pagina = "relatorios"

if col4.button("🏠 CONTAS DA CASA", use_container_width=True):
    st.session_state.pagina = "contas"

st.divider()

pagina = st.session_state.pagina

# -----------------------
# DASHBOARD
# -----------------------

if pagina == "dashboard":

    st.header("📊 Visão Geral")

    if len(df) > 0:

        df["data"] = pd.to_datetime(df["data"])

        bruto_total = df["bruto"].sum()
        liquido_total = df["liquido"].sum()
        km_total = df["km"].sum()
        horas_total = df["horas"].sum()

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("💰 Ganho Bruto", round(bruto_total,2))
        c2.metric("💵 Ganho Líquido", round(liquido_total,2))
        c3.metric("🚗 KM Rodados", round(km_total,2))
        c4.metric("⏱ Horas Trabalhadas", round(horas_total,2))

        st.divider()

        media_km = liquido_total/km_total if km_total>0 else 0
        media_hora = liquido_total/horas_total if horas_total>0 else 0

        c5,c6 = st.columns(2)

        c5.metric("💰 Média por KM", round(media_km,2))
        c6.metric("⏱ Média por Hora", round(media_hora,2))

    else:
        st.info("Nenhum lançamento registrado ainda.")

# -----------------------
# LANÇAMENTO
# -----------------------

if pagina == "lancar":

    st.header("🚖 Lançamento do dia")

    if "inicio_turno" not in st.session_state:
        st.session_state.inicio_turno = None

    c1,c2 = st.columns(2)

    if c1.button("▶️ Iniciar turno"):
        st.session_state.inicio_turno = datetime.datetime.now()

    if c2.button("⛔ Encerrar turno"):
        if st.session_state.inicio_turno:
            fim = datetime.datetime.now()
            horas = (fim - st.session_state.inicio_turno).total_seconds()/3600
            st.session_state.horas_trabalhadas = horas

    horas_manual = st.number_input("Horas trabalhadas",0.0)

    horas = st.session_state.get("horas_trabalhadas", horas_manual)

    uber = st.number_input("Ganhos Uber",0.0)
    noventa_nove = st.number_input("Ganhos 99",0.0)

    km = st.number_input("KM rodados",0.0)

    consumo = st.number_input("Consumo do carro (km/L)",0.0)
    gasolina = st.number_input("Preço gasolina",0.0)

    litros = km/consumo if consumo>0 else 0
    combustivel = litros*gasolina

    bruto = uber+noventa_nove
    liquido = bruto-combustivel

    km_bruto = bruto/km if km>0 else 0
    km_liquido = liquido/km if km>0 else 0

    hora_liquido = liquido/horas if horas>0 else 0

    st.divider()
    st.subheader("Resultado")

    c1,c2,c3 = st.columns(3)

    c1.metric("💰 Bruto", round(bruto,2))
    c2.metric("💵 Líquido", round(liquido,2))
    c3.metric("⛽ Combustível", round(combustivel,2))

    c4,c5,c6 = st.columns(3)

    c4.metric("🚗 R$/KM Bruto", round(km_bruto,2))
    c5.metric("🚗 R$/KM Líquido", round(km_liquido,2))
    c6.metric("⏱ R$/Hora", round(hora_liquido,2))

    if st.button("💾 Salvar dia"):

        novo = pd.DataFrame({
            "data":[datetime.date.today()],
            "uber":[uber],
            "noventa_nove":[noventa_nove],
            "km":[km],
            "horas":[horas],
            "combustivel":[combustivel],
            "bruto":[bruto],
            "liquido":[liquido]
        })

        df = pd.concat([df,novo],ignore_index=True)
        df.to_csv(arquivo,index=False)

        st.success("Dia salvo!")

# -----------------------
# RELATÓRIOS
# -----------------------

if pagina == "relatorios":

    st.header("📈 Relatórios")

    if len(df) > 0:

        df["data"] = pd.to_datetime(df["data"])

        df["mes"] = df["data"].dt.to_period("M")

        mensal = df.groupby("mes").sum(numeric_only=True)

        st.dataframe(mensal)

    else:
        st.info("Sem dados para relatório.")

# -----------------------
# CONTAS
# -----------------------

if pagina == "contas":

    st.header("🏠 Contas da casa")

    luz = st.number_input("Luz",0.0)
    agua = st.number_input("Água",0.0)
    internet = st.number_input("Internet",0.0)
    aluguel = st.number_input("Aluguel",0.0)
    mercado = st.number_input("Mercado",0.0)
    outros = st.number_input("Outros",0.0)

    despesa = luz+agua+internet+aluguel+mercado+outros

    meta = despesa/30 if despesa>0 else 0

    st.metric("💸 Despesa mensal", round(despesa,2))
    st.metric("🎯 Meta diária", round(meta,2))
