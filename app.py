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

    [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }

    .card-faturamento { background-color: #00FF00; color: black !important; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; width: 100% !important; }
    .card-despesa { background-color: #FF0000; color: white !important; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    .card-saldo { background-color: #800080; color: white !important; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    
    .big-val { font-size: 20px; font-weight: bold; }
    .label-card { font-size: 10px; font-weight: 600; text-transform: uppercase; }

    .grid-item {
        background-color: #1C1C1E;
        border-radius: 12px;
        padding: 10px 2px;
        text-align: center;
        border: 1px solid #2C2C2E;
        margin-bottom: 5px;
        min-height: 85px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .grid-label { color: #ffffff !important; font-size: 9px; font-weight: bold; text-transform: uppercase; opacity: 0.8; }
    .grid-value { color: #FFFFFF !important; font-size: 14px; font-weight: bold; }

    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1C1C1E;
        border-radius: 8px;
        color: #ffffff !important;
        padding: 0 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4500 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- PERSISTÊNCIA ---
FILE_HIST = "dados_uber.csv"
FILE_CONTAS = "contas_uber.csv"

def carregar_dados():
    if os.path.exists(FILE_HIST):
        return pd.read_csv(FILE_HIST)
    return pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"])

def carregar_contas():
    if os.path.exists(FILE_CONTAS):
        df = pd.read_csv(FILE_CONTAS)
        return df.iloc[0].to_dict()
    return {"Aluguel": 0.0, "Luz": 0.0, "Água": 0.0, "Internet": 0.0, "Cartões": 0.0, "Financiamentos": 0.0, "Outras": 0.0}

if 'historico' not in st.session_state:
    st.session_state.historico = carregar_dados()

if 'contas' not in st.session_state:
    st.session_state.contas = carregar_contas()

hoje_ref = date.today()
ultimo_dia = calendar.monthrange(hoje_ref.year, hoje_ref.month)[1]
dias_restantes = (ultimo_dia - hoje_ref.day) + 1
total_casa = sum(v for v in st.session_state.contas.values() if v is not None)

tab_res, tab_lan, tab_hist, tab_contas = st.tabs(["📊 RESULTADOS", "➕ LANÇAR", "📅 HISTÓRICO", "🏠 CONTAS"])

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
        st.write(f"🏠 *Abate das Contas da Casa:* {prog*100:.1f}%")
        st.progress(prog)
        st.write(f"📉 *Falta para quitar o mês:* R$ {max(0.0, restante):.2f}")
        st.write(f"🎯 *Meta diária p/ os {dias_f} dias restantes:* R$ {max(0.0, meta_real):.2f}")

with tab_res:
    if not st.session_state.historico.empty:
        u = st.session_state.historico.iloc[-1]
        renderizar_grade(u["Bruto"], u["Líquido"], u["KM"], u["Horas"], total_casa, dias_restantes, "Dia")
    else:
        renderizar_grade(0.0, 0.0, 1.0, 1.0, total_casa, dias_restantes, "Dia")

with tab_lan:
    st.subheader("Lançar Dia")
    data_lan = st.date_input("Data do Trabalho", value=date.today())
    b_in = st.number_input("Ganho Bruto", value=None, placeholder=" ")
    k_in = st.number_input("KM Total", value=None, placeholder=" ")
    h_in = st.number_input("Horas", value=None, placeholder=" ")
    c_in = st.number_input("Combustível", value=None, placeholder=" ")
    if st.button("💾 SALVAR DIA", use_container_width=True):
        if b_in is not None:
            l_calc = b_in - (c_in or 0.0)
            k_calc = k_in or 1.0
            h_calc = h_in or 1.0
            novo = {"Data": data_lan.strftime("%d/%m/%Y"), "Bruto": b_in, "Líquido": l_calc, "KM": k_calc, "Horas": h_calc, "KM_Liq": l_calc/k_calc, "Hora_Liq": l_calc/h_calc}
            st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo])], ignore_index=True)
            st.session_state.historico.to_csv(FILE_HIST, index=False)
            st.success(f"Dia {data_lan.strftime('%d/%m')} salvo!")
            st.rerun()

with tab_hist:
    if not st.session_state.historico.empty:
        df_h = st.session_state.historico.copy()
        df_h['Data_dt'] = pd.to_datetime(df_h['Data'], format='%d/%m/%Y')
        hoje_agora = datetime.now()
        periodo = st.radio("Período:", ["Semana", "Mês", "Ano"], horizontal=True)
        if periodo == "Semana": mask = df_h['Data_dt'] > (hoje_agora - timedelta(days=7))
        elif periodo == "Mês": mask = df_h['Data_dt'].dt.month == hoje_agora.month
        else: mask = df_h['Data_dt'].dt.year == hoje_agora.year
        df_p = df_h[mask]
        if not df_p.empty:
            renderizar_grade(df_p["Bruto"].sum(), df_p["Líquido"].sum(), df_p["KM"].sum(), df_p["Horas"].sum(), total_casa, dias_restantes, periodo)
        st.divider()
        df_h = df_h.sort_values(by='Data_dt', ascending=False)
        st.dataframe(df_h.drop(columns=['Data_dt']), use_container_width=True)
        if st.button("🗑️ ZERAR TUDO"):
            if os.path.exists(FILE_HIST): os.remove(FILE_HIST)
            st.session_state.historico = pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"])
            st.rerun()
    else:
        st.info("Sem dados no histórico.")

with tab_contas:
    st.subheader("🏠 Contas da Casa")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.contas["Aluguel"] = st.number_input("Aluguel", value=float(st.session_state.contas.get("Aluguel", 0)))
        st.session_state.contas["Luz"] = st.number_input("Luz", value=float(st.session_state.contas.get("Luz", 0)))
        st.session_state.contas["Água"] = st.number_input("Água", value=float(st.session_state.contas.get("Água", 0)))
        st.session_state.contas["Internet"] = st.number_input("Internet", value=float(st.session_state.contas.get("Internet", 0)))
    with c2:
        st.session_state.contas["Cartões"] = st.number_input("Cartões", value=float(st.session_state.contas.get("Cartões", 0)))
        st.session_state.contas["Financiamentos"] = st.number_input("Financiamentos", value=float(st.session_state.contas.get("Financiamentos", 0)))
        st.session_state.contas["Outras"] = st.number_input("Outras", value=float(st.session_state.contas.get("Outras", 0)))
    if st.button("💾 SALVAR CONTAS"):
        pd.DataFrame([st.session_state.contas]).to_csv(FILE_CONTAS, index=False)
        st.success("Contas salvas!")
        st.rerun()
    st.divider()
    st.metric("TOTAL MENSAL", f"R$ {total_casa:.2f}")
