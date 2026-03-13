import streamlit as st
import pandas as pd
from datetime import datetime

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

    /* Forçar colunas lado a lado no celular (Necessário para a grade 2x3) */
    [data-testid="column"] {
        width: 50% !important;
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }

    /* Cartões Coloridos Estilo Print */
    .card-faturamento { background-color: #00FF00; color: black !important; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px; width: 100% !important; }
    .card-despesa { background-color: #FF0000; color: white !important; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    .card-saldo { background-color: #800080; color: white !important; border-radius: 12px; padding: 15px; text-align: center; width: 100% !important; }
    
    .big-val { font-size: 20px; font-weight: bold; }
    .label-card { font-size: 10px; font-weight: 600; text-transform: uppercase; }

    /* Grade de métricas em quadrados (2 Colunas) */
    .grid-item {
        background-color: #1C1C1E;
        border-radius: 12px;
        padding: 10px 5px;
        text-align: center;
        border: 1px solid #2C2C2E;
        margin-bottom: 8px;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    /* Letras brancas e mais visíveis nos quadrados */
    .grid-label { color: #ffffff !important; font-size: 9px; font-weight: bold; text-transform: uppercase; opacity: 0.8; }
    .grid-value { color: #FFFFFF !important; font-size: 14px; font-weight: bold; }

    /* Estilo das Tabs */
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

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'historico' not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=["Data", "Bruto", "Líquido", "KM", "Horas", "KM_Liq", "Hora_Liq"])

if 'contas' not in st.session_state:
    st.session_state.contas = {
        "Aluguel": None, "Luz": None, "Água": None, "Internet": None, 
        "Cartões": None, "Financiamentos": None, "Outras": None
    }

# --- CÁLCULOS TÉCNICOS ---
# Cálculo seguro das contas (ignora None)
total_casa = sum(v if v is not None else 0.0 for v in st.session_state.contas.values())

# --- ABAS ---
tab_res, tab_lan, tab_hist, tab_contas = st.tabs(["📊 RESULTADOS", "➕ LANÇAR", "📅 HISTÓRICO", "🏠 CONTAS"])

# --- ABA 1: RESULTADOS (DIÁRIO) ---
with tab_res:
    # Pega o último faturamento bruto salvo no histórico para exibir nos resultados
    if not st.session_state.historico.empty:
        ultimo = st.session_state.historico.iloc[-1]
        res_b, res_l, res_c, res_k, res_h = ultimo["Bruto"], ultimo["Líquido"], ultimo["Bruto"]-ultimo["Líquido"], ultimo["KM"], ultimo["Horas"]
    else:
        res_b, res_l, res_c, res_k, res_h = 0.0, 0.0, 0.0, 0.0, 0.0

    st.markdown(f"<div class='card-faturamento'><div class='label-card'>Faturamento Dia</div><div class='big-val'>R$ {res_b:.2f}</div></div>", unsafe_allow_html=True)
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1: st.markdown(f"<div class='card-despesa'><div class='label-card'>Despesas</div><div class='big-val'>R$ {res_c:.2f}</div></div>", unsafe_allow_html=True)
    with c_sub2: st.markdown(f"<div class='card-saldo'><div class='label-card'>Saldo</div><div class='big-val'>R$ {res_l:.2f}</div></div>", unsafe_allow_html=True)
    
    st.write("")
    # --- GRADE DE QUADRADOS (2 COLUNAS X 3 LINHAS) ---
    # Linha 1 da Grade
    g1, g2 = st.columns(2)
    with g1: 
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Viagens</div><div class='grid-value'>{max(0, round(res_b / 35)) if res_b > 0 else 0}</div></div>", unsafe_allow_html=True)
    with g2: 
        st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Bruto</div><div class='grid-value'>R$ {(res_b/res_k if res_k > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)

    # Linha 2 da Grade
    g3, g4 = st.columns(2)
    with g3: 
        hr_int, min_int = int(res_h), int((res_h - int(res_h)) * 60)
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Tempo</div><div class='grid-value'>{hr_int:02d}:{min_int:02d}</div></div>", unsafe_allow_html=True)
    with g4: 
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/Hora</div><div class='grid-value'>R$ {(res_l/res_h if res_h > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)

    # Linha 3 da Grade
    g5, g6 = st.columns(2)
    with g5: 
        st.markdown(f"<div class='grid-item'><div class='grid-label'>KM Rodado</div><div class='grid-value'>{res_k}</div></div>", unsafe_allow_html=True)
    with g6: 
        st.markdown(f"<div class='grid-item'><div class='grid-label'>Líq/KM</div><div class='grid-value'>R$ {(res_l/res_k if res_k > 0 else 0):.2f}</div></div>", unsafe_allow_html=True)

    # --- BARRA DE PROGRESSO COM VALORES REAIS (ATUALIZADA) ---
    if total_casa > 0:
        st.write("")
        st.divider()
        # Calcula o progresso com base no líquido do dia
        prog = min(max(0.0, res_l / total_casa), 1.0)
        
        # Calcula o restante da dívida e a meta diária (considerando 20 dias úteis)
        restante_divida = total_casa - res_l
        if restante_divida < 0: restante_divida = 0 # Evita valor negativo se faturar mais que a divida
        meta_diaria = restante_divida / 20

        st.write(f"🏠 *Visão de Abate das Contas Mensais:* {prog*100:.1f}%")
        st.progress(prog)
        
        # Exibe os valores reais pedidos
        st.info(f"*Restante da dívida do mês:* R$ {restante_divida:.2f}")
        st.info(f"*Meta diária p/ bater contas (20 dias):* R$ {meta_diaria:.2f}")

# --- ABA 2: LANÇAR GANHO DIÁRIO ---
with tab_lan:
    st.subheader("Lançar Dia")
    # value=None deixa o campo vazio para digitação imediata
    bruto_input = st.number_input("Ganho Bruto", value=None, placeholder=" ")
    km_input = st.number_input("KM Total", value=None, placeholder=" ")
    horas_input = st.number_input("Tempo Total (ex: 8.5)", value=None, placeholder=" ")
    comb_input = st.number_input("Gasto Combustível", value=None, placeholder=" ")
    
    if st.button("💾 SALVAR GANHO DIÁRIO", use_container_width=True):
        if bruto_input is not None:
            # Pega o histórico para cálculo técnico seguro
            novo = {
                "Data": datetime.now().strftime("%d/%m/%Y"), 
                "Bruto": bruto_input, 
                "Líquido": bruto_input - (comb_input if comb_input else 0.0), 
                "KM": km_input if km_input and km_input > 0 else 1.0, 
                "Horas": horas_input if horas_input and horas_input > 0 else 1.0
            }
            # Adiciona os cálculos de KM_Liq e Hora_Liq que são usados no histórico
            novo["KM_Liq"] = novo["Líquido"] / novo["KM"]
            novo["Hora_Liq"] = novo["Líquido"] / novo["Horas"]
            
            st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([novo])], ignore_index=True)
            st.success("Dados salvos! Confira na aba Resultados.")
            st.rerun() # Atualiza para os resultados aparecerem
        else:
            st.warning("Preencha o Ganho Bruto.")

# --- ABA 3: HISTÓRICO ---
with tab_hist:
    if not st.session_state.historico.empty:
        st.dataframe(st.session_state.historico, use_container_width=True)
        if st.button("Zerar Histórico"):
            st.session_state.historico = pd.DataFrame(columns=st.session_state.historico.columns)
            st.rerun()
    else:
        st.info("Sem dados no histórico.")

# --- ABA 4: CONTAS DA CASA ---
with tab_contas:
    st.subheader("🏠 Gestão Financeira da Casa")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.contas["Aluguel"] = st.number_input("Aluguel", value=st.session_state.contas["Aluguel"], placeholder=" ")
        st.session_state.contas["Luz"] = st.number_input("Conta luz", value=st.session_state.contas["Luz"], placeholder=" ")
        st.session_state.contas["Água"] = st.number_input("Água", value=st.session_state.contas["Água"], placeholder=" ")
        st.session_state.contas["Internet"] = st.number_input("Internet", value=st.session_state.contas["Internet"], placeholder=" ")
    with col2:
        st.session_state.contas["Cartões"] = st.number_input("Cartões", value=st.session_state.contas["Cartões"], placeholder=" ")
        st.session_state.contas["Financiamentos"] = st.number_input("Financiamentos", value=st.session_state.contas["Financiamentos"], placeholder=" ")
        st.session_state.contas["Outras"] = st.number_input("Outras contas", value=st.session_state.contas["Outras"], placeholder=" ")
    
    st.divider()
    # Recalcula o total das contas com base nos novos inputs
    total_casa_lan = sum(v if v is not None else 0.0 for v in st.session_state.contas.values())
    st.metric("TOTAL MENSAL", f"R$ {total_casa_lan:.2f}")
