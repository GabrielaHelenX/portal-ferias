import streamlit as st
import datetime
import holidays

# Configuração da página
st.set_page_config(
    page_title="Portal de Férias & Ausências | Ânima",
    page_icon="🌴",
    layout="wide"
)

# Dados da Equipe
GESTOR = "DANILO DA SILVA VILAS BOAS"
EQUIPE_DETALHES = {
    "ERIKA LIMA DE OLIVEIRA": {"estado": "SP", "saldo": 30, "inic": "EO", "nasc": datetime.date(1995, 5, 12)},
    "JOYCE ADRIELLE DIAS DA SILVA": {"estado": "BA", "saldo": 25, "inic": "JD", "nasc": datetime.date(1998, 10, 4)},
    "KELVYN AMARAL CANDIDO": {"estado": "MG", "saldo": 30, "inic": "KC", "nasc": datetime.date(1996, 2, 18)},
    "GABRIELA HELEN SANTOS XAVIER": {"estado": "BA", "saldo": 22, "inic": "GX", "nasc": datetime.date(1997, 8, 20)}
}
EQUIPE = list(EQUIPE_DETALHES.keys())

# Memória de agendamentos
if "agendamentos" not in st.session_state:
    st.session_state["agendamentos"] = [
        {
            "id": 1,
            "colaborador": "JOYCE ADRIELLE DIAS DA SILVA",
            "tipo": "Férias",
            "inicio": datetime.date(2026, 11, 10),
            "fim": datetime.date(2026, 11, 20),
            "dias": 11,
            "justificativa": "Descanso anual",
            "status": "Aprovado"
        }
    ]

# Título principal
st.title("🌴 Portal de Férias & Ausências — Ânima")
st.markdown("Gestão integrada de ausências, saldos e escalas da equipe.")

# Aniversariante do dia
hoje = datetime.date.today()
aniversariantes = [n for n, info in EQUIPE_DETALHES.items() if info["nasc"].month == hoje.month and info["nasc"].day == hoje.day]
if aniversariantes:
    st.success(f"🎂 **Parabéns!** Hoje é aniversário de **{' e '.join(aniversariantes)}**! Muita felicidade!")

st.divider()

# Abas do Sistema
aba1, aba2, aba3 = st.tabs(["📊 Visão Geral & Equipe", "➕ Nova Solicitação", "⚙️ Painel do Gestor"])

# ABA 1: Visão Geral
with aba1:
    st.subheader("Panorama da Equipe")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Aprovados", sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Aprovado"))
    col2.metric("Pendentes", sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Pendente"))
    col3.metric("Membros", len(EQUIPE))
    
    st.markdown("### 👥 Saldos Atuais")
    cols = st.columns(len(EQUIPE))
    for i, (colab, info) in enumerate(EQUIPE_DETALHES.items()):
        usados = sum(r['dias'] for r in st.session_state["agendamentos"] if r['colaborador'] == colab and r['tipo'] == 'Férias' and r['status'] == 'Aprovado')
        restante = info['saldo'] - usados
        with cols[i]:
            with st.container(border=True):
                st.write(f"**{info['inic']} - {colab.split()[0]}**")
                st.caption(f"Restam: {restante} dias\nAniv: {info['nasc'].strftime('%d/%m')}")

    st.markdown("### 📅 Ausências Registradas")
    for reg in st.session_state["agendamentos"]:
        with st.container(border=True):
            st.write(f"**{reg['colaborador']}** — 📌 {reg['tipo']} ({reg['dias']} dias)")
            st.caption(f"De {reg['inicio'].strftime('%d/%m/%Y')} até {reg['fim'].strftime('%d/%m/%Y')} | Status: {reg['status']}")
            st.text(f"Justificativa: {reg['justificativa']}")

# ABA 2: Solicitação
with aba2:
    st.subheader("Solicitar Nova Ausência")
    
    with st.form("form_solicitacao"):
        solicitante = st.selectbox("Seu Nome", EQUIPE)
        tipo = st.radio("Tipo", ["Férias", "Banco de Horas / Abono", "Folga de Aniversário"], horizontal=True)
        
        c1, c2 = st.columns(2)
        with c1:
            dt_inicio = st.date_input("Data de Início", datetime.date.today())
        with c2:
            if tipo == "Férias":
                qnt = st.number_input("Quantidade de Dias", 1, 30, 10)
                dt_fim = dt_inicio + datetime.timedelta(days=int(qnt) - 1)
            else:
                dt_fim = st.date_input("Data de Término", dt_inicio)
                qnt = (dt_fim - dt_inicio).days + 1

        justificativa = st.text_area("Justificativa", placeholder="Informe o motivo...")
        
        enviar = st.form_submit_button("Enviar para o Gestor", use_container_width=True)
        
        if enviar:
            if not justificativa.strip():
                st.error("Preencha a justificativa.")
            else:
                novo = {
                    "id": len(st.session_state["agendamentos"]) + 1,
                    "colaborador": solicitante,
                    "tipo": tipo,
                    "inicio": dt_inicio,
                    "fim": dt_fim,
                    "dias": qnt,
                    "justificativa": justificativa,
                    "status": "Pendente"
                }
                st.session_state["agendamentos"].append(novo)
                st.success("Solicitação enviada com sucesso!")

# ABA 3: Gestor
with aba3:
    st.subheader(f"Painel do Gestor ({GESTOR})")
    pendentes = [r for r in st.session_state["agendamentos"] if r["status"] == "Pendente"]
    
    if pendentes:
        for p in pendentes:
            with st.container(border=True):
                st.write(f"**{p['colaborador']}** — {p['tipo']} ({p['dias']} dias)")
                st.caption(f"Período: {p['inicio'].strftime('%d/%m/%Y')} a {p['fim'].strftime('%d/%m/%Y')}")
                st.text(f"Justificativa: {p['justificativa']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Aprovar", key=f"ok_{p['id']}", use_container_width=True):
                        p["status"] = "Aprovado"
                        st.success("Aprovado!")
                        st.rerun()
                with c2:
                    if st.button("Rejeitar", key=f"no_{p['id']}", use_container_width=True):
                        p["status"] = "Rejeitado"
                        st.warning("Rejeitado.")
                        st.rerun()
    else:
        st.success("Nenhuma solicitação pendente.")

