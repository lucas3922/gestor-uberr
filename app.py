import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

st.set_page_config(page_title="Gestor Uber PRO", layout="wide")

# CSS para interface escura
st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: white;
}

[data-testid="stMetricValue"] {
    font-size: 28px;
}

</style>
""", unsafe_allow_html=True)

st.title("🚖 Gestor Uber PRO")

arquivo = "dados_motorista.csv"

if os.path.exists(arquivo):
    df = pd.read_csv(arquivo)
else:
    df = pd.DataFrame(columns=[
        "data","uber","noventa_nove","km","horas",
        "combustivel","bruto","liquido"
    ])

# ABAS
dashboard, lancamento, relatorios, contas = st.tabs([
    "📊 Dashboard",
    "🚖 Lançar Dia",
    "📈 Relatórios",
    "🏠 Contas da Casa"
])

# -------------------------
# DASHBOARD
# -------------------------

with dashboard:

    st.header("📊 Painel Geral")

    if len(df) > 0:

        df["data"] = pd.to_datetime(df["data"])

        bruto_total = df["bruto"].sum()
        liquido_total = df["liquido"].sum()
        km_total = df["km"].sum()
        horas_total = df["horas"].sum()

        c1,c2,c3,c4 = st.columns(4)

        c1.metric("💰 Bruto total", round(bruto_total,2))
        c2.metric("💵 Líquido total", round(liquido_total,2))
        c3.metric("🚗 KM rodados", round(km_total,2))
        c4.metric("⏱ Horas", round(horas_total,2))

        graf = px.line(
            df,
            x="data",
            y="liquido",
            markers=True,
            template="plotly_dark",
            title="Lucro diário"
        )

        st.plotly_chart(graf, use_container_width=True)

    else:
        st.write("Nenhum dado ainda.")

# -------------------------
# LANÇAMENTO
# -------------------------

with lancamento:

    st.header("🚖 Lançamento do Dia")

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

    hora_bruto = bruto/horas if horas>0 else 0
    hora_liquido = liquido/horas if horas>0 else 0

    st.subheader("Resultado")

    c1,c2,c3 = st.columns(3)

    c1.metric("💰 Bruto", round(bruto,2))
    c2.metric("💵 Líquido", round(liquido,2))
    c3.metric("⛽ Combustível", round(combustivel,2))

    c4,c5,c6 = st.columns(3)

    c4.metric("🚗 KM bruto", round(km_bruto,2))
    c5.metric("🚗 KM líquido", round(km_liquido,2))
    c6.metric("⏱ Hora líquida", round(hora_liquido,2))

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

        st.success("Dia salvo!")

# -------------------------
# RELATÓRIOS
# -------------------------

with relatorios:

    st.header("📈 Relatórios")

    if len(df) > 0:

        df["data"] = pd.to_datetime(df["data"])

        df["mes"] = df["data"].dt.to_period("M")

        mensal = df.groupby("mes").sum(numeric_only=True)

        st.dataframe(mensal)

# -------------------------
# CONTAS
# -------------------------

with contas:

    st.header("🏠 Contas da Casa")

    luz = st.number_input("Luz",0.0)
    agua = st.number_input("Água",0.0)
    internet = st.number_input("Internet",0.0)
    aluguel = st.number_input("Aluguel",0.0)
    mercado = st.number_input("Mercado",0.0)
    outros = st.number_input("Outros",0.0)

    despesa = luz+agua+internet+aluguel+mercado+outros

    meta = despesa/30 if despesa>0 else 0

    st.metric("Despesa mensal", round(despesa,2))
    st.metric("Meta diária", round(meta,2))
