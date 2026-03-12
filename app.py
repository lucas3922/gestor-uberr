import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

st.set_page_config(page_title="Gestor Uber PRO", layout="wide")

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

# -------------------------
# CONTAS DA CASA
# -------------------------

st.sidebar.header("🏠 Contas da Casa")

luz = st.sidebar.number_input("Conta de Luz",0.0)
agua = st.sidebar.number_input("Água",0.0)
internet = st.sidebar.number_input("Internet",0.0)
aluguel = st.sidebar.number_input("Aluguel",0.0)
mercado = st.sidebar.number_input("Mercado",0.0)
outros = st.sidebar.number_input("Outros",0.0)

despesa_mensal = luz+agua+internet+aluguel+mercado+outros
meta_diaria = despesa_mensal/30 if despesa_mensal>0 else 0

st.sidebar.write("### 💸 Despesa mensal:", round(despesa_mensal,2))
st.sidebar.write("🎯 Meta diária:", round(meta_diaria,2))

# -------------------------
# TURNO
# -------------------------

st.header("⏱ Controle de Turno")

if "inicio_turno" not in st.session_state:
    st.session_state.inicio_turno = None

if st.button("▶️ Iniciar turno"):
    st.session_state.inicio_turno = datetime.datetime.now()

if st.button("⛔ Encerrar turno"):
    if st.session_state.inicio_turno:
        fim = datetime.datetime.now()
        horas = (fim - st.session_state.inicio_turno).total_seconds()/3600
        st.session_state.horas_trabalhadas = horas

horas = st.session_state.get("horas_trabalhadas",0)

st.write("Horas trabalhadas:",round(horas,2))

# -------------------------
# LANÇAMENTO
# -------------------------

st.header("💰 Lançamento do Dia")

col1,col2,col3 = st.columns(3)

uber = col1.number_input("Ganhos Uber",0.0)
noventa_nove = col2.number_input("Ganhos 99",0.0)
km = col3.number_input("KM rodados",0.0)

col4,col5 = st.columns(2)

consumo = col4.number_input("Consumo do carro (km/L)",0.0)
gasolina = col5.number_input("Preço gasolina",0.0)

litros = km/consumo if consumo>0 else 0
combustivel = litros*gasolina

bruto = uber+noventa_nove
liquido = bruto-combustivel

km_bruto = bruto/km if km>0 else 0
km_liquido = liquido/km if km>0 else 0

hora_bruto = bruto/horas if horas>0 else 0
hora_liquido = liquido/horas if horas>0 else 0

# -------------------------
# RESULTADOS
# -------------------------

st.header("📊 Resultado do Dia")

a,b,c = st.columns(3)

a.metric("💰 Ganho Bruto",round(bruto,2))
b.metric("💵 Ganho Líquido",round(liquido,2))
c.metric("⛽ Combustível",round(combustivel,2))

d,e,f = st.columns(3)

d.metric("🚗 Ganho por KM Bruto",round(km_bruto,2))
e.metric("🚗 Ganho por KM Líquido",round(km_liquido,2))
f.metric("⏱ Ganho por Hora Líquido",round(hora_liquido,2))

# -------------------------
# SALVAR
# -------------------------

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

if len(df)>0:

    st.header("📈 Dashboard")

    df["data"] = pd.to_datetime(df["data"])

    bruto_total = df["bruto"].sum()
    liquido_total = df["liquido"].sum()

    km_total = df["km"].sum()
    horas_total = df["horas"].sum()

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Bruto total",round(bruto_total,2))
    col2.metric("Líquido total",round(liquido_total,2))
    col3.metric("KM rodados",round(km_total,2))
    col4.metric("Horas trabalhadas",round(horas_total,2))

# -------------------------
# MÉDIAS
# -------------------------

    st.header("📊 Médias")

    km_media = bruto_total/km_total if km_total>0 else 0
    hora_media = liquido_total/horas_total if horas_total>0 else 0

    x,y = st.columns(2)

    x.metric("💰 Média por KM",round(km_media,2))
    y.metric("⏱ Média por Hora",round(hora_media,2))

# -------------------------
# GRÁFICO
# -------------------------

    st.header("📉 Evolução de Lucro")

    graf = px.line(df,x="data",y="liquido",markers=True)

    st.plotly_chart(graf,use_container_width=True)

# -------------------------
# RELATÓRIO MENSAL
# -------------------------

    st.header("📅 Relatório mensal")

    df["mes"] = df["data"].dt.to_period("M")

    mensal = df.groupby("mes").sum(numeric_only=True)

    st.dataframe(mensal)

# -------------------------
# META DAS CONTAS
# -------------------------

    st.header("🎯 Progresso para pagar contas do mês")

    progresso = liquido_total/despesa_mensal if despesa_mensal>0 else 0

    st.progress(min(progresso,1.0))

    st.write("Coberto até agora:",round(progresso*100,1),"%")
