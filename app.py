import streamlit as st
import pandas as pd
import datetime
import holidays

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DE TELA E DESIGN PROFISSIONAL
# ---------------------------------------------------------
st.set_page_config(
    page_title="Portal de Férias & Ausências",
    page_icon="🌴",
    layout="wide"
)

# Estilização CSS Avançada (Modo Limpo / Clean UI)
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    
    /* Cartões Modernos */
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .event-card {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    
    .badge-status {
        float: right;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
    }
    .status-aprovado { background-color: #DCFCE7; color: #166534; }
    .status-pendente { background-color: #FEF9C3; color: #854D0E; }
    
    /* Alertas Personalizados */
    .alert-box {
        background-color: #FEF2F2;
        color: #991B1B;
        padding: 14px;
        border-radius: 8px;
        border-left: 4px solid #EF4444;
        margin-top: 10px;
        margin-bottom: 10px;
        font-size: 14px;
    }
    
    /* Botões */
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
# 2. DADOS DA EQUIPE E LOCAIS (Feriados)
# ---------------------------------------------------------
GESTOR = "DANILO DA SILVA VILAS BOAS"
EQUIPE_DETALHES = {
    "ERIKA LIMA DE OLIVEIRA": {"cidade": "São Paulo", "estado": "SP"},
    "JOYCE ADRIELLE DIAS DA SILVA": {"cidade": "Salvador", "estado": "BA"},
    "KELVYN AMARAL CANDIDO": {"cidade": "Belo Horizonte", "estado": "MG"},
    "GABRIELA HELEN SANTOS XAVIER": {"cidade": "Salvador", "estado": "BA"}
}
EQUIPE = list(EQUIPE_DETALHES.keys())

# Banco de dados simulado na sessão
if "agendamentos" not in st.session_state:
    st.session_state["agendamentos"] = [
        {
            "id": 1,
            "colaborador": "JOYCE ADRIELLE DIAS DA SILVA",
            "tipo": "Férias",
            "inicio": datetime.date(2026, 11, 10),
            "fim": datetime.date(2026, 11, 20),
            "status": "Aprovado"
        }
    ]

# ---------------------------------------------------------
# 3. VALIDAÇÕES DE REGRAS (Feriados e Conflitos)
# ---------------------------------------------------------
def checar_regras(nome_colaborador, dt_inicio, dt_fim):
    detalhes = EQUIPE_DETALHES[nome_colaborador]
    feriados_br = holidays.BR(years=2026, subdiv=detalhes["estado"])
    
    erros = []
    avisos = []
    
    if dt_inicio in feriados_br:
        erros.append(f"Feriado detectado em {dt_inicio.strftime('%d/%m/%Y')} ({feriados_br.get(dt_inicio)}). Início de férias não permitido.")
    if dt_inicio.weekday() >= 5:
        erros.append("O início das férias não pode cair em finais de semana (Sábado ou Domingo).")
        
    for reg in st.session_state["agendamentos"]:
        if reg["colaborador"] != nome_colaborador and reg["status"] in ["Aprovado", "Pendente"]:
            if dt_inicio <= reg["fim"] and dt_fim >= reg["inicio"]:
                avisos.append(f"Conflito de agenda: {reg['colaborador']} estará ausente de {reg['inicio'].strftime('%d/%m/%Y')} a {reg['fim'].strftime('%d/%m/%Y')}.")
                
    return erros, avisos

# ---------------------------------------------------------
# 4. INTERFACE VISUAL LIMPA (UI / UX)
# ---------------------------------------------------------
st.title("🌴 Portal de Retenção Nacional — Férias & Ausências")
st.markdown("Gerenciamento inteligente de equipe, sem tabelas pesadas e com validação automática de regras.")
st.markdown("---")

# Abas Limpas
aba_painel, aba_solicitar, aba_gestor = st.tabs(["📊 Visão Geral da Equipe", "➕ Nova Solicitação", f"⚙️ Gestão ({GESTOR.split()[0]})"])

# ---------------------------------------------------------
# ABA 1: VISÃO GERAL (Substituindo a tabela feia por Cards)
# ---------------------------------------------------------
with aba_painel:
    st.subheader("Painel de Ausências Ativas")
    
    # Métricas de topo limpas
    c1, c2, c3 = st.columns(3)
    total_aprovados = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Aprovado")
    total_pendentes = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Pendente")
    
    c1.metric("Ausências Aprovadas", total_aprovados)
    c2.metric("Solicitações Pendentes", total_pendentes)
    c3.metric("Membros na Equipe", len(EQUIPE))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state["agendamentos"]:
        for reg in st.session_state["agendamentos"]:
            dias = (reg["fim"] - reg["inicio"]).days + 1
            status_class = "status-aprovado" if reg["status"] == "Aprovado" else "status-pendente"
            
            # Renderização de card elegante em vez de tabela crua
            st.markdown(f"""
                <div class="event-card">
                    <span class="badge-status {status_class}">{reg['status']}</span>
                    <h4 style="margin: 0; color: #1E293B;">{reg['colaborador']}</h4>
                    <p style="margin: 4px 0 0 0; color: #64748B; font-size: 14px;">
                        📌 <b>{reg['tipo']}</b> | 📅 De <b>{reg['inicio'].strftime('%d/%m/%Y')}</b> até <b>{reg['fim'].strftime('%d/%m/%Y')}</b> ({dias} dias)
                    </p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma ausência registrada no momento.")

# ---------------------------------------------------------
# ABA 2: NOVA SOLICITAÇÃO (Fluida e Intuitiva)
# ---------------------------------------------------------
with aba_solicitar:
    st.subheader("Nova Solicitação de Ausência")
    
    with st.container():
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            solicitante = st.selectbox("Selecione seu Nome", EQUIPE)
        with col_s2:
            tipo = st.radio("Modalidade", ["Férias", "Banco de Horas / Abono"], horizontal=True)
            
        c_d1, c_d2 = st.columns(2)
        with c_d1:
            dt_inicio = st.date_input("Data de Início", datetime.date.today())
        with c_d2:
            if tipo == "Férias":
                qnt = st.number_input("Quantidade de Dias", 1, 30, 10)
                dt_fim = dt_inicio + datetime.timedelta(days=int(qnt) - 1)
            else:
                dt_fim = st.date_input("Data de Término", dt_inicio)
                qnt = (dt_fim - dt_inicio).days + 1

        retorno = dt_fim + datetime.timedelta(days=1)
        st.markdown(f"💡 **Retorno ao trabalho:** {retorno.strftime('%d/%m/%Y')} ({qnt} dias contabilizados)")
        
        # Validações em tempo real
        erros, avisos = checar_regras(solicitante, dt_inicio, dt_fim)
        
        bloqueio = False
        if erros:
            bloqueio = True
            for e in erros:
                st.markdown(f'<div class="alert-box">❌ <b>Restrição de Política:</b> {e}</div>', unsafe_allow_html=True)
                
        if avisos:
            for a in avisos:
                st.warning(f"⚠️ {a}")
                
        if not erros and not avisos:
            st.success("✅ Período livre de conflitos e de acordo com as regras de feriados.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Enviar Solicitação para o Gestor", disabled=bloqueio):
            novo = {
                "id": len(st.session_state["agendamentos"]) + 1,
                "colaborador": solicitante,
                "tipo": tipo,
                "inicio": dt_inicio,
                "fim": dt_fim,
                "status": "Pendente"
            }
            st.session_state["agendamentos"].append(novo)
            st.balloons()
            st.success("Solicitação enviada com sucesso! O gestor foi avisado.")

# ---------------------------------------------------------
# ABA 3: ÁREA DO GESTOR (DANILO)
# ---------------------------------------------------------
with aba_gestor:
    st.subheader(f"Painel de Aprovações de {GESTOR.split()[0]}")
    
    pendentes = [r for r in st.session_state["agendamentos"] if r["status"] == "Pendente"]
    
    if pendentes:
        for p in pendentes:
            st.markdown(f"""
                <div class="event-card" style="border-left-color: #EAB308;">
                    <h4 style="margin: 0; color: #1E293B;">{p['colaborador']}</h4>
                    <p style="margin: 4px 0 8px 0; color: #64748B; font-size: 14px;">
                        📌 <b>{p['tipo']}</b> | 📅 {p['inicio'].strftime('%d/%m/%Y')} até {p['fim'].strftime('%d/%m/%Y')}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"✅ Aprovar", key=f"ok_{p['id']}"):
                    p["status"] = "Aprovado"
                    st.rerun()
            with b2:
                if st.button(f"❌ Rejeitar", key=f"no_{p['id']}"):
                    p["status"] = "Rejeitado"
                    st.rerun()
    else:
        st.success("🎉 Nenhuma solicitação pendente para análise.")
