import streamlit as st
import pandas as pd
import datetime
import holidays

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA (Layout Profissional)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Portal de Férias & Ausências | Planejamento",
    page_icon="🌴",
    layout="wide"
)

# Estilização Clean & Modern UI (Padrão corporativo moderno com tons Ânima)
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    h1 { color: #F3E8FF !important; font-weight: 800; font-size: 1.8rem !important; }
    h2, h3 { color: #E9D5FF !important; font-weight: 700; }
    
    /* Cartões Modernos */
    .anima-card {
        background-color: #1E1B4B;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #4C1D95;
        box-shadow: 0 4px 12px rgba(76, 29, 149, 0.1);
        margin-bottom: 12px;
    }
    
    /* Botões */
    .stButton>button {
        background-color: #7C3AED;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        width: 100%;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #6D28D9;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DADOS DA EQUIPE E CONFIGURAÇÕES
# ---------------------------------------------------------
GESTOR_OFICIAL = "DANILO DA SILVA VILAS BOAS"

EQUIPE_DETALHES = {
    "ERIKA LIMA DE OLIVEIRA": {"estado": "SP", "cargo": "Analista", "inic": "EO"},
    "JOYCE ADRIELLE DIAS DA SILVA": {"estado": "BA", "cargo": "Analista", "inic": "JD"},
    "KELVYN AMARAL CANDIDO": {"estado": "MG", "cargo": "Analista", "inic": "KC"},
    "GABRIELA HELEN SANTOS XAVIER": {"estado": "BA", "cargo": "Analista de Dados", "inic": "GX"}
}
EQUIPE = list(EQUIPE_DETALHES.keys())

# Banco de dados na sessão (Garante persistência durante o uso)
if "agendamentos" not in st.session_state:
    st.session_state["agendamentos"] = [
        {
            "id": 1,
            "colaborador": "JOYCE ADRIELLE DIAS DA SILVA",
            "tipo": "Férias",
            "inicio": datetime.date(2026, 11, 10),
            "fim": datetime.date(2026, 11, 20),
            "dias": 11,
            "justificativa": "Descanso anual programado",
            "status": "Aprovado"
        }
    ]

# Função para validar feriados e conflitos
def checar_regras(nome_colaborador, dt_inicio, dt_fim):
    detalhes = EQUIPE_DETALHES[nome_colaborador]
    feriados_br = holidays.BR(years=dt_inicio.year, subdiv=detalhes["estado"])
    erros, avisos = [], []
    
    if dt_inicio in feriados_br:
        erros.append(f"A data de início cai no feriado: {feriados_br.get(dt_inicio)}. Escolha um dia útil.")
    if dt_inicio.weekday() >= 5:
        erros.append("O início das férias não pode cair em finais de semana.")
        
    for reg in st.session_state["agendamentos"]:
        if reg["colaborador"] != nome_colaborador and reg["status"] == "Aprovado":
            if dt_inicio <= reg["fim"] and dt_fim >= reg["inicio"]:
                avisos.append(f"Atenção: {reg['colaborador'].split()[0]} já estará ausente neste mesmo período.")
    return erros, avisos

# ---------------------------------------------------------
# 3. INTERFACE PRINCIPAL
# ---------------------------------------------------------
st.title("🌴 Portal de Férias & Ausências")
st.caption(f"Ecossistema de Controle e Retenção Nacional — Equipe & Gestão ({GESTOR_OFICIAL.split()[0]})")
st.divider()

# Barra lateral para identificação de quem está acessando (Simulação de Perfil)
with st.sidebar:
    st.markdown("### 👤 Sessão Atual")
    perfil_usuario = st.selectbox(
        "Você é:", 
        [GESTOR_OFICIAL] + EQUIPE
    )
    st.info(f"Logado como: **{perfil_usuario.split()[0]}**")
    st.markdown("---")
    st.markdown("📌 **Regras Rápidas:**\n- Sem início em feriados/fins de semana.\n- Verificação automática de conflitos na equipe.")

# Abas Limpas e Organizadas
aba_painel, aba_solicitar, aba_gestor = st.tabs([
    "📊 Calendário & Equipe", 
    "➕ Nova Solicitação", 
    f"⚙️ Painel do Gestor {'🔒' if perfil_usuario != GESTOR_OFICIAL else ''}"
])

# ---------------------------------------------------------
# ABA 1: CALENDÁRIO & VISÃO GERAL DA EQUIPE
# ---------------------------------------------------------
with aba_painel:
    st.subheader("Painel de Controle da Equipe")
    
    col1, col2, col3 = st.columns(3)
    total_aprovados = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Aprovado")
    total_pendentes = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Pendente")
    
    col1.metric("Ausências Aprovadas", total_aprovados)
    col2.metric("Pendentes de Aprovação", total_pendentes)
    col3.metric("Membros Monitorados", len(EQUIPE))
    
    st.write("")
    st.markdown("### 📅 Linha do Tempo e Ausências da Equipe")
    st.caption("Consulte abaixo quem estará ausente para evitar conflitos de cobertura.")
    
    agendamentos_ativos = [r for r in st.session_state["agendamentos"] if r["status"] == "Aprovado"]
    
    if agendamentos_ativos:
        for reg in agendamentos_ativos:
            inic = EQUIPE_DETALHES.get(reg['colaborador'], {}).get('inic', 'COL')
            st.markdown(f"""
                <div class="anima-card">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <span style="background-color: #7C3AED; color: white; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold;">{inic}</span>
                            <b style="font-size: 15px; color: #F8FAFC; margin-left: 8px;">{reg['colaborador']}</b>
                            <p style="margin: 6px 0 0 0; color: #CBD5E1; font-size: 13px;">
                                📌 <b>{reg['tipo']}</b> ({reg['dias']} dias) | 📅 De <b>{reg['inicio'].strftime('%d/%m/%Y')}</b> até <b>{reg['fim'].strftime('%d/%m/%Y')}</b>
                            </p>
                            <p style="margin: 4px 0 0 0; color: #C084FC; font-size: 12px; font-style: italic;">
                                💬 Justificativa: "{reg['justificativa']}"
                            </p>
                        </div>
                        <div>
                            <span style="background-color: #065F46; color: #A7F3D0; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">Confirmado</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma ausência confirmada no momento.")

# ---------------------------------------------------------
# ABA 2: NOVA SOLICITAÇÃO (Simples, Didática e Sem Fricção)
# ---------------------------------------------------------
with aba_solicitar:
    st.subheader("Registrar Nova Solicitação de Ausência")
    st.caption("Preencha os campos abaixo. O sistema valida automaticamente feriados e choques na equipe.")
    
    with st.form("form_solicitacao_limpo"):
        # Se estiver logado como gestor na barra lateral, permite escolher; se for colaborador, assume o nome dele
        if perfil_usuario == GESTOR_OFICIAL:
            solicitante = st.selectbox("Colaborador Solicitante", EQUIPE)
        else:
            solicitante = perfil_usuario
            st.write(f"✍️ Solicitante: **{solicitante}**")

        tipo = st.radio("Modalidade", ["Férias", "Banco de Horas / Abono", "Folga de Aniversário"], horizontal=True)
        
        c1, c2 = st.columns(2)
        with c1:
            dt_inicio = st.date_input("Data de Início", datetime.date.today())
        with c2:
            if tipo == "Férias":
                qnt_dias = st.number_input("Quantidade de Dias", 1, 30, 10)
                dt_fim = dt_inicio + datetime.timedelta(days=int(qnt_dias) - 1)
            else:
                dt_fim = st.date_input("Data de Término", dt_inicio)
                qnt_dias = (dt_fim - dt_inicio).days + 1

        retorno = dt_fim + datetime.timedelta(days=1)
        st.markdown(f"💡 **Previsão de Retorno:** {retorno.strftime('%d/%m/%Y')} ({qnt_dias} dias ausente)")
        
        justificativa = st.text_area("Justificativa / Motivo", placeholder="Ex: Descanso anual, compensação de horas extras...")
        
        # Validações em tempo real
        erros, avisos = checar_regras(solicitante, dt_inicio, dt_fim)
        bloqueio = False
        
        if erros:
            bloqueio = True
            for e in erros:
                st.error(f"❌ {e}")
        if avisos:
            for a in avisos:
                st.warning(f"⚠️ {a}")
                
        enviar = st.form_submit_button("🚀 Enviar para Aprovação do Gestor", use_container_width=True)
        
        if enviar:
            if bloqueio:
                st.error("Envio bloqueado por regras de política da empresa.")
            elif not justificativa.strip():
                st.error("A justificativa é obrigatória para o controle do gestor.")
            else:
                novo_pedido = {
                    "id": len(st.session_state["agendamentos"]) + 1,
                    "colaborador": solicitante,
                    "tipo": tipo,
                    "inicio": dt_inicio,
                    "fim": dt_fim,
                    "dias": qnt_dias,
                    "justificativa": justificativa,
                    "status": "Pendente"
                }
                st.session_state["agendamentos"].append(novo_pedido)
                st.balloons()
                st.success(f"Solicitação enviada com sucesso! Um aviso foi disparado para {GESTOR_OFICIAL.split()[0]}.")

# ---------------------------------------------------------
# ABA 3: PAINEL DO GESTOR (Exclusivo para Danilo)
# ---------------------------------------------------------
with aba_gestor:
    if perfil_usuario != GESTOR_OFICIAL:
        st.warning(f"🔒 **Área Restrita:** Este painel de aprovação é exclusivo para o gestor ({GESTOR_OFICIAL}). Alterne sua sessão na barra lateral para testar como gestor.")
    else:
        st.subheader(f"Painel Gerencial de {GESTOR_OFICIAL}")
        st.caption("Aprove ou rejeite solicitações pendentes da equipe com um clique.")
        
        sub_pendentes, sub_historico = st.tabs(["⏳ Pendentes de Aprovação", "📋 Histórico Completo"])
        
        with sub_pendentes:
            pendentes = [r for r in st.session_state["agendamentos"] if r["status"] == "Pendente"]
            
            if pendentes:
                for p in pendentes:
                    with st.container(border=True):
                        st.markdown(f"**{p['colaborador']}** — 📌 *{p['tipo']}* ({p['dias']} dias)")
                        st.caption(f"📅 Período: De {p['inicio'].strftime('%d/%m/%Y')} até {p['fim'].strftime('%d/%m/%Y')}")
                        st.text(f"Justificativa: {p['justificativa']}")
                        
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button(f"✅ Aprovar #{p['id']}", key=f"ok_{p['id']}", use_container_width=True):
                                p["status"] = "Aprovado"
                                st.success(f"Solicitação de {p['colaborador'].split()[0]} aprovada! O calendário foi atualizado.")
                                st.rerun()
                        with b2:
                            if st.button(f"❌ Rejeitar #{p['id']}", key=f"no_{p['id']}", use_container_width=True):
                                p["status"] = "Rejeitado"
                                st.warning("Solicitação rejeitada.")
                                st.rerun()
            else:
                st.success("🎉 Nenhuma solicitação pendente no momento. Tudo em dia com a equipe!")
                
        with sub_historico:
            st.markdown("### Registro Geral de Solicitações")
            df_hist = pd.DataFrame(st.session_state["agendamentos"])
            if not df_hist.empty:
                st.dataframe(df_hist, use_container_width=True)
            else:
                st.info("Nenhum registro encontrado.")
