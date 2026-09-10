import streamlit as st
import pandas as pd
import datetime
import holidays

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Portal de Férias & Ausências",
    page_icon="🌴",
    layout="wide"
)

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
# 4. INTERFACE VISUAL LIMPA E NATIVA
# ---------------------------------------------------------
st.title("🌴 Portal de Retenção Nacional")
st.caption("Gerenciamento integrado de férias e ausências da equipe.")
st.divider()

# Abas Limpas
aba_painel, aba_solicitar, aba_gestor = st.tabs(["📊 Visão Geral da Equipe", "➕ Nova Solicitação", f"⚙️ Gestão ({GESTOR.split()[0]})"])

# ---------------------------------------------------------
# ABA 1: VISÃO GERAL
# ---------------------------------------------------------
with aba_painel:
    st.subheader("Painel de Ausências Ativas")
    
    c1, c2, c3 = st.columns(3)
    total_aprovados = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Aprovado")
    total_pendentes = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Pendente")
    
    c1.metric("Ausências Aprovadas", total_aprovados)
    c2.metric("Solicitações Pendentes", total_pendentes)
    c3.metric("Membros na Equipe", len(EQUIPE))
    
    st.write("")
    st.markdown("### Histórico de Registros")
    
    if st.session_state["agendamentos"]:
        for reg in st.session_state["agendamentos"]:
            dias = (reg["fim"] - reg["inicio"]).days + 1
            
            # Usando containers nativos do Streamlit para um visual limpo e sem falhas de cor
            with st.container(border=True):
                col_info1, col_info2 = st.columns([3, 1])
                with col_info1:
                    st.markdown(f"**{reg['colaborador']}**")
                    st.caption(f"📌 **{reg['tipo']}** | 📅 De **{reg['inicio'].strftime('%d/%m/%Y')}** até **{reg['fim'].strftime('%d/%m/%Y')}** ({dias} dias)")
                with col_info2:
                    if reg["status"] == "Aprovado":
                        st.success("Aprovado")
                    else:
                        st.warning("Pendente")
    else:
        st.info("Nenhuma ausência registrada no momento.")

# ---------------------------------------------------------
# ABA 2: NOVA SOLICITAÇÃO
# ---------------------------------------------------------
with aba_solicitar:
    st.subheader("Nova Solicitação de Ausência")
    
    with st.form("form_solicitacao"):
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
        st.info(f"💡 **Retorno ao trabalho:** {retorno.strftime('%d/%m/%Y')} ({qnt} dias contabilizados)")
        
        # Validações em tempo real
        erros, avisos = checar_regras(solicitante, dt_inicio, dt_fim)
        
        bloqueio = False
        if erros:
            bloqueio = True
            for e in erros:
                st.error(f"❌ **Restrição de Política:** {e}")
                
        if avisos:
            for a in avisos:
                st.warning(f"⚠️ {a}")
                
        if not erros and not avisos:
            st.success("✅ Período livre de conflitos e de acordo com as regras de feriados.")
            
        enviar = st.form_submit_button("🚀 Enviar Solicitação para o Gestor", use_container_width=True)
        
        if enviar:
            if bloqueio:
                st.error("Não é possível enviar a solicitação devido às restrições acima.")
            else:
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
            with st.container(border=True):
                st.markdown(f"**{p['colaborador']}**")
                st.caption(f"📌 **{p['tipo']}** | 📅 {p['inicio'].strftime('%d/%m/%Y')} até {p['fim'].strftime('%d/%m/%Y')}")
                
                b1, b2 = st.columns(2)
                with b1:
                    if st.button(f"✅ Aprovar ID {p['id']}", key=f"ok_{p['id']}", use_container_width=True):
                        p["status"] = "Aprovado"
                        st.rerun()
                with b2:
                    if st.button(f"❌ Rejeitar ID {p['id']}", key=f"no_{p['id']}", use_container_width=True):
                        p["status"] = "Rejeitado"
                        st.rerun()
    else:
        st.success("🎉 Nenhuma solicitação pendente para análise.")
