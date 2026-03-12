import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

st.set_page_config(page_title="Gestor Uber PRO", layout="centered")

st.title("🚖 Gestor Financeiro do Motorista")

arquivo = "dados_motorista.csv"

# carregar histórico
if os.path.exists(arquivo):
    df = pd.read_csv(arquivo)
else:
    df = pd.DataFrame(columns=[
        "data","uber","noventa_nove","km","horas",
        "combustivel","bruto","liquido"
    ])

# MENU
pagina = st.sidebar.selectbox(
    "Menu",
    ["Dashboard","Lançar Dia","Relatórios","Contas da Casa"]
)

# -------------------------
# CONTAS DA CASA
# -------------------------

if pagina == "Contas da Casa":

    st.header("🏠 Contas da Casa")

    luz = st.number_input("Conta de Luz",0.0)
    agua = st.number_input("Água",0.0)
    internet = st.number_input("Internet",0.0)
    aluguel = st.number_input("Aluguel",0.0)
    mercado = st.number_input("Mercado",0.0)
    outros = st.number_input("Outros",0.0)

    despesa_mensal = luz+agua+internet+aluguel+mercado+outros
    meta_diaria = despesa_mensal/30 if despesa_mensal>0 else 0

    st.metric("💸 Despesa mensal",round(despesa_mensal,2))
    st.metric("🎯 Meta diária",round(meta_diaria,2))

# -------------------------
# LANÇAMENTO
# -------------------------

if pagina == "Lançar Dia":

    st.header("🚖 Lançamento do Dia")

    # iniciar turno
    if "inicio_turno" not in st.session_state:
        st.session_state.inicio_turno = None

    if st.button("▶️ Iniciar turno"):
        st.session_state.inicio_turno = datetime.datetime.now()

    if st.button("⛔ Encerrar turno"):
        if st.session_state.inicio_turno:
            fim = datetime.datetime.now()
            horas_calc = (fim - st.session_state.inicio_turno).total_seconds()/3600
            st.session_state.horas_trabalhadas = horas_calc

    # horas manual
    horas_manual = st.number_input("Horas trabalhadas (manual)",0.0)

    horas_turno = st.session_state.get("horas_trabalhadas",0)

    if horas_turno > 0:
        horas = horas_turno
        st.write("Horas calculadas pelo turno:",round(horas,2))
    else:
        horas = horas_manual

    # ganhos
    uber = st.number_input("Ganhos Uber",0.0)
    noventa_nove = st.number_input("Ganhos 99",0.0)

    # km
    km = st.number_input("KM rodados",0.0)

    # combustível
    consumo = st.number_input("Consumo do carro (km/L)",0.0)
    gasolina = st.number_input("Preço gasolina",0.0)

    litros = km/consumo if consumo>0 else 0
    combustivel = litros*gasolina

    bruto = uber+noventa_nove
    liquido = bruto-combustivel

    km_bruto = bruto/km if km>0 else 0
    km_liquido = liquido/km if km>0 else 0

    hora_bruto = bruto/horas if horas>0 else 0
    hora_liquido = liquido/horas if horas>0 else 0

    st.subheader("📊 Resultado")

    st.metric("💰 Ganho bruto",round(bruto,2))
    st.metric("💵 Ganho líquido",round(liquido,2))
    st.metric("🚗 KM bruto",round(km_bruto,2))
    st.metric("🚗 KM líquido",round(km_liquido,2))
    st.metric("⏱ Hora bruto",round(hora_bruto,2))
    st.metric("⏱ Hora líquido",round(hora_liquido,2))

    if st.button("💾 Salvar Dia"):

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

        st.success("Dia salvo com sucesso!")

# -------------------------
# DASHBOARD
# -------------------------

if pagina == "Dashboard":

    st.header("📊 Dashboard")

    if len(df) == 0:
        st.write("Nenhum dado ainda.")
    else:

        df["data"] = pd.to_datetime(df["data"])

        bruto_total = df["bruto"].sum()
        liquido_total = df["liquido"].sum()
        km_total = df["km"].sum()
        horas_total = df["horas"].sum()

        st.metric("💰 Total bruto",round(bruto_total,2))
        st.metric("💵 Total líquido",round(liquido_total,2))
        st.metric("🚗 KM rodados",round(km_total,2))
        st.metric("⏱ Horas trabalhadas",round(horas_total,2))

        graf = px.line(df,x="data",y="liquido",markers=True,title="Lucro diário")

        st.plotly_chart(graf,use_container_width=True)

# -------------------------
# RELATÓRIOS
# -------------------------

if pagina == "Relatórios":

    st.header("📅 Relatórios")

    if len(df) == 0:
        st.write("Nenhum dado ainda.")
    else:

        df["data"] = pd.to_datetime(df["data"])

        df["mes"] = df["data"].dt.to_period("M")

        mensal = df.groupby("mes").sum(numeric_only=True)

        st.subheader("Relatório mensal")

        st.dataframe(mensal)

        km_total = df["km"].sum()
        bruto_total = df["bruto"].sum()

        media_km = bruto_total/km_total if km_total>0 else 0

        st.metric("🚗 Média ganho por KM",round(media_km,2))
