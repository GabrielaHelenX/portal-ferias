import streamlit as st
import pandas as pd
import datetime

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO E DESIGN PROFISSIONAL (CSS)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Portal de Ausências & Férias",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .card-box {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0px 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
    }
    .badge-alerta {
        background-color: #FEF2F2;
        color: #991B1B;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #EF4444;
        font-weight: 500;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        width: 100%;
        padding: 10px;
    }
    .stButton>button:hover { background-color: #1D4ED8; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. EQUIPE E BANCO DE DADOS INICIAL
# ---------------------------------------------------------
GESTOR = "DANILO DA SILVA VILAS BOAS"
EQUIPE = [
    "ERIKA LIMA DE OLIVEIRA",
    "JOYCE ADRIELLE DIAS DA SILVA",
    "KELVYN AMARAL CANDIDO",
    "GABRIELA HELEN SANTOS XAVIER"
]
TODOS_USUARIOS = [GESTOR] + EQUIPE

# Simulador de banco de dados na sessão (em breve ligado ao Excel/Google Sheets)
if "agendamentos" not in st.session_state:
    st.session_state["agendamentos"] = [
        {
            "id": 1,
            "colaborador": "JOYCE ADRIELLE DIAS DA SILVA",
            "tipo": "Férias",
            "inicio": datetime.date(2026, 11, 10),
            "fim": datetime.date(2026, 11, 20),
            "status": "Aprovado"
        },
        {
            "id": 2,
            "colaborador": "KELVYN AMARAL CANDIDO",
            "tipo": "Banco de Horas / Abono",
            "inicio": datetime.date(2026, 11, 15),
            "fim": datetime.date(2026, 11, 15),
            "status": "Aprovado"
        }
    ]

# ---------------------------------------------------------
# 3. FUNÇÃO DE CONFLITO DE DATAS
# ---------------------------------------------------------
def checar_conflitos(nome_solicitante, dt_inicio, dt_fim):
    conflitos = []
    for reg in st.session_state["agendamentos"]:
        if reg["colaborador"] != nome_solicitante and reg["status"] in ["Aprovado", "Pendente de Aprovação"]:
            if dt_inicio <= reg["fim"] and dt_fim >= reg["inicio"]:
                conflitos.append(reg)
    return conflitos

# ---------------------------------------------------------
# 4. INTERFACE DO APLICATIVO
# ---------------------------------------------------------
st.title("🌴 Portal de Férias & Ausências — Retenção Nacional")
st.caption("Substituindo o controle manual por um fluxo inteligente, integrado e sem conflitos.")

st.markdown("---")

# Abas de navegação (Aba do Gestor liberada se for o Danilo)
aba1, aba2, aba3 = st.tabs(["📅 Painel da Equipe", "➕ Nova Solicitação", "⚙️ Área do Gestor (Danilo)"])

# ---------------------------------------------------------
# ABA 1: PAINEL DA EQUIPE
# ---------------------------------------------------------
with aba1:
    st.subheader("Panorama de Ausências e Férias")
    
    col1, col2, col3 = st.columns(3)
    total_ferias = sum(1 for r in st.session_state["agendamentos"] if r["tipo"] == "Férias" and r["status"] == "Aprovado")
    total_banco = sum(1 for r in st.session_state["agendamentos"] if r["tipo"] != "Férias" and r["status"] == "Aprovado")
    
    col1.metric("Férias Ativas / Aprovadas", f"{total_ferias}")
    col2.metric("Banco de Horas Aprovados", f"{total_banco}")
    col3.metric("Total da Equipe", f"{len(EQUIPE)} membros")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state["agendamentos"]:
        df_display = []
        for reg in st.session_state["agendamentos"]:
            dias_totais = (reg["fim"] - reg["inicio"]).days + 1
            df_display.append({
                "Colaborador": reg["colaborador"],
                "Tipo": reg["tipo"],
                "Início": reg["inicio"].strftime("%d/%m/%Y"),
                "Término": reg["fim"].strftime("%d/%m/%Y"),
                "Duração": f"{dias_totais} dia(s)",
                "Status": reg["status"]
            })
        st.dataframe(pd.DataFrame(df_display), use_container_width=True)
    else:
        st.info("Nenhuma ausência registrada no momento.")

# ---------------------------------------------------------
# ABA 2: NOVA SOLICITAÇÃO
# ---------------------------------------------------------
with aba2:
    st.subheader("Solicitar Férias ou Banco de Horas")
    
    with st.container():
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        
        solicitante = st.selectbox("Selecione seu Nome", EQUIPE)
        tipo_solicitacao = st.radio("Tipo de Solicitação", ["Férias", "Banco de Horas / Abono"], horizontal=True)
        
        col_dt1, col_dt2 = st.columns(2)
        with col_dt1:
            dt_inicio = st.date_input("Data de Início", datetime.date.today())
        
        if tipo_solicitacao == "Férias":
            with col_dt2:
                qnt_dias = st.number_input("Quantidade de Dias", min_value=1, max_value=30, value=10)
            dt_fim = dt_inicio + datetime.timedelta(days=int(qnt_dias) - 1)
        else:
            with col_dt2:
                dt_fim = st.date_input("Data de Término", dt_inicio)
            qnt_dias = (dt_fim - dt_inicio).days + 1

        dt_retorno = dt_fim + datetime.timedelta(days=1)
        
        st.markdown("---")
        st.write(f"📊 **Resumo:** {qnt_dias} dia(s). Retorno previsto ao trabalho em: **{dt_retorno.strftime('%d/%m/%Y')}**")
        
        # VALIDAÇÃO DE CONFLITO EM TEMPO REAL
        conflitos = checar_conflitos(solicitante, dt_inicio, dt_fim)
        
        if conflitos:
            st.markdown('<div class="badge-alerta">', unsafe_allow_html=True)
            st.warning("⚠️ **ALERTA DE CHOQUE DE DATAS NA EQUIPE:**")
            for c in conflitos:
                st.write(f"• **{c['colaborador']}** já estará ausente ({c['tipo']}) entre {c['inicio'].strftime('%d/%m/%Y')} e {c['fim'].strftime('%d/%m/%Y')}.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("✅ **Agenda Livre:** Nenhum outro membro da equipe está ausente nesta mesma janela.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Enviar Solicitação para o Gestor (Danilo)"):
            novo_registro = {
                "id": len(st.session_state["agendamentos"]) + 1,
                "colaborador": solicitante,
                "tipo": tipo_solicitacao,
                "inicio": dt_inicio,
                "fim": dt_fim,
                "status": "Pendente de Aprovação"
            }
            st.session_state["agendamentos"].append(novo_registro)
            st.balloons()
            st.success("Solicitação enviada com sucesso! O gestor foi notificado.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# ABA 3: ÁREA DO GESTOR (DANILO)
# ---------------------------------------------------------
with aba3:
    st.subheader(f"Painel de Aprovação do Gestor ({GESTOR})")
    st.info("Aqui o Danilo gerencia e aprova as solicitações pendentes da equipe.")
    
    pendentes = [r for r in st.session_state["agendamentos"] if r["status"] == "Pendente de Aprovação"]
    
    if pendentes:
        for p in pendentes:
            with st.container():
                st.markdown('<div class="card-box">', unsafe_allow_html=True)
                st.write(f"👤 **Colaborador:** {p['colaborador']}")
                st.write(f"📌 **Tipo:** {p['tipo']} | **Período:** {p['inicio'].strftime('%d/%m/%Y')} até {p['fim'].strftime('%d/%m/%Y')}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"✅ Aprovar ID {p['id']}", key=f"aprov_{p['id']}"):
                        p["status"] = "Aprovado"
                        st.success(f"Solicitação de {p['colaborador']} aprovada!")
                        st.rerun()
                with col_btn2:
                    if st.button(f"❌ Rejeitar ID {p['id']}", key=f"rejeit_{p['id']}"):
                        p["status"] = "Rejeitado"
                        st.warning(f"Solicitação rejeitada.")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.success("🎉 Não há solicitações pendentes de aprovação no momento.")
