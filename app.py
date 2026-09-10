import streamlit as st
import pandas as pd
import datetime
import holidays

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Portal de Férias & Ausências | Planejamento",
    page_icon="🌴",
    layout="wide"
)

# Estilização limpa e profissional com detalhes em Roxo Ânima
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    h1 { color: #2E1065 !important; font-weight: 800; font-size: 2rem !important; }
    h2, h3 { color: #4C1D95 !important; font-weight: 700; }
    
    /* Banner de Aniversário Elegante */
    .bday-banner {
        background: linear-gradient(135deg, #7C3AED 0%, #C084FC 100%);
        padding: 16px 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.2);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* Botões personalizados com o Roxo Ânima */
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
# 2. DADOS DA EQUIPE E SALDOS
# ---------------------------------------------------------
GESTOR = "DANILO DA SILVA VILAS BOAS"

EQUIPE_DETALHES = {
    "ERIKA LIMA DE OLIVEIRA": {
        "cidade": "São Paulo", "estado": "SP", 
        "saldo_ferias": 30, "iniciais": "EO", 
        "nascimento": datetime.date(1995, 5, 12)
    },
    "JOYCE ADRIELLE DIAS DA SILVA": {
        "cidade": "Salvador", "estado": "BA", 
        "saldo_ferias": 25, "iniciais": "JD", 
        "nascimento": datetime.date(1998, 10, 4)
    },
    "KELVYN AMARAL CANDIDO": {
        "cidade": "Belo Horizonte", "estado": "MG", 
        "saldo_ferias": 30, "iniciais": "KC", 
        "nascimento": datetime.date(1996, 2, 18)
    },
    "GABRIELA HELEN SANTOS XAVIER": {
        "cidade": "Salvador", "estado": "BA", 
        "saldo_ferias": 22, "iniciais": "GX", 
        "nascimento": datetime.date(1997, 8, 20)
    }
}
EQUIPE = list(EQUIPE_DETALHES.keys())

# Banco de dados temporário na memória (sem arquivos físicos)
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

# ---------------------------------------------------------
# 3. VALIDAÇÕES DE REGRAS (Feriados Multi-Ano e Conflitos)
# ---------------------------------------------------------
def checar_regras(nome_colaborador, dt_inicio, dt_fim):
    detalhes = EQUIPE_DETALHES[nome_colaborador]
    ano_solicitacao = dt_inicio.year
    feriados_br = holidays.BR(years=ano_solicitacao, subdiv=detalhes["estado"])
    
    erros = []
    avisos = []
    
    if dt_inicio in feriados_br:
        erros.append(f"A data de início cai no feriado: {feriados_br.get(dt_inicio)}.")
    if dt_inicio.weekday() >= 5:
        erros.append("O início das férias não pode cair em finais de semana.")
        
    for reg in st.session_state["agendamentos"]:
        if reg["colaborador"] != nome_colaborador and reg["status"] == "Aprovado":
            if dt_inicio <= reg["fim"] and dt_fim >= reg["inicio"]:
                avisos.append(f"Choque de agenda: {reg['colaborador']} estará ausente neste período.")
                
    return erros, avisos

# ---------------------------------------------------------
# 4. INTERFACE DO APLICATIVO
# ---------------------------------------------------------
st.title("🌴 Portal de Férias & Ausências")
st.caption("Retenção Nacional — Gestão Dinâmica & Multi-Anual")

# Alerta de Aniversário Dinâmico
hoje = datetime.date.today()
aniversariantes_hoje = [
    nome for nome, info in EQUIPE_DETALHES.items() 
    if info["nascimento"].month == hoje.month and info["nascimento"].day == hoje.day
]

if aniversariantes_hoje:
    nomes_str = " e ".join([n.title() for n in aniversariantes_hoje])
    st.markdown(f"""
        <div class="bday-banner">
            <div>
                <b style="font-size: 16px;">🎂 Aniversário da Equipe Hoje!</b>
                <p style="margin: 2px 0 0 0; font-size: 14px; opacity: 0.95;">Parabéns a <b>{nomes_str}</b> pelo seu dia!</p>
            </div>
            <div style="font-size: 28px;">🎉</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

aba_painel, aba_solicitar, aba_gestor = st.tabs(["📊 Visão Geral & Equipe", "➕ Nova Solicitação", f"⚙️ Gestão & Histórico ({GESTOR.split()[0]})"])

# ---------------------------------------------------------
# ABA 1: VISÃO GERAL
# ---------------------------------------------------------
with aba_painel:
    st.subheader("Painel de Controle da Equipe")
    
    c1, c2, c3 = st.columns(3)
    aprovados_total = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Aprovado")
    pendentes_total = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Pendente")
    
    c1.metric("Ausências Aprovadas", aprovados_total)
    c2.metric("Pendentes de Análise", pendentes_total)
    c3.metric("Membros Ativos", len(EQUIPE))
    
    st.write("")
    st.markdown("### 👥 Saldo Atual de Férias da Equipe")
    
    cols_saldo = st.columns(len(EQUIPE))
    for i, (colab, info) in enumerate(EQUIPE_DETALHES.items()):
        dias_usados = sum(int(r.get('dias', (r['fim'] - r['inicio']).days + 1)) for r in st.session_state["agendamentos"] if r['colaborador'] == colab and r['tipo'] == 'Férias' and r['status'] == 'Aprovado')
        saldo_restante = info['saldo_ferias'] - dias_usados
        aniver_fmt = info['nascimento'].strftime('%d/%m')
        
        with cols_saldo[i]:
            with st.container(border=True):
                st.markdown(f"**{info['iniciais']}** - {colab.split()[0]}")
                st.caption(f"Restam: **{saldo_restante} dias**\n🎂 Aniv: {aniver_fmt}")
                
    st.write("")
    st.markdown("### 📅 Linha do Tempo de Ausências Aprovadas")
    
    aprovados = [r for r in st.session_state["agendamentos"] if r["status"] == "Aprovado"]
    if aprovados:
        for reg in aprovados:
            iniciais = EQUIPE_DETALHES.get(reg['colaborador'], {}).get('iniciais', 'COL')
            dias_reg = reg.get('dias', (reg['fim'] - reg['inicio']).days + 1)
            just_reg = reg.get('justificativa', 'Sem justificativa')
            
            with st.container(border=True):
                col_i1, col_i2 = st.columns([4, 1])
                with col_i1:
                    st.markdown(f"**{reg['colaborador']}**")
                    st.caption(f"📌 **{reg['tipo']}** ({dias_reg} dias) | 📅 De **{reg['inicio'].strftime('%d/%m/%Y')}** até **{reg['fim'].strftime('%d/%m/%Y')}**")
                    st.text(f"Justificativa: {just_reg}")
                with col_i2:
                    st.success("Aprovado")
    else:
        st.info("Nenhuma ausência aprovada no momento.")

# ---------------------------------------------------------
# ABA 2: NOVA SOLICITAÇÃO
# ---------------------------------------------------------
with aba_solicitar:
    st.subheader("Cadastrar Nova Solicitação")
    
    with st.form("form_limpo"):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            solicitante = st.selectbox("Selecione seu Nome", EQUIPE)
        with col_s2:
            tipo = st.radio("Modalidade da Ausência", ["Férias", "Banco de Horas / Abono", "Folga de Aniversário"], horizontal=True)
            
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
        
        justificativa = st.text_area("Justificativa / Observação", placeholder="Explique brevemente o motivo...")
        
        erros, avisos = checar_regras(solicitante, dt_inicio, dt_fim)
        
        bloqueio = False
        if erros:
            bloqueio = True
            for e in erros:
                st.error(f"❌ {e}")
                
        if avisos:
            for a in avisos:
                st.warning(f"⚠️ {a}")
                
        enviar = st.form_submit_button("🚀 Enviar Solicitação para o Gestor", use_container_width=True)
        
        if enviar:
            if bloqueio:
                st.error("Envio bloqueado devido às regras de feriados ou fins de semana.")
            elif not justificativa.strip():
                st.error("Por favor, preencha a justificativa.")
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
                st.balloons()
                st.success("Solicitação enviada com sucesso! O gestor foi notificado.")

# ---------------------------------------------------------
# ABA 3: GESTOR
# ---------------------------------------------------------
with aba_gestor:
    st.subheader(f"Painel Gerencial de {GESTOR}")
    
    sub_aba1, sub_aba2 = st.tabs(["⏳ Pendentes de Aprovação", "📋 Histórico Geral da Equipe"])
    
    with sub_aba1:
        pendentes = [r for r in st.session_state["agendamentos"] if r["status"] == "Pendente"]
        
        if pendentes:
            for p in pendentes:
                p_dias = p.get('dias', (p['fim'] - p['inicio']).days + 1)
                p_just = p.get('justificativa', 'Sem justificativa')
                
                with st.container(border=True):
                    st.markdown(f"**{p['colaborador']}**")
                    st.caption(f"📌 **{p['tipo']}** ({p_dias} dias) | 📅 De {p['inicio'].strftime('%d/%m/%Y')} até {p['fim'].strftime('%d/%m/%Y')}")
                    st.text(f"Justificativa: {p_just}")
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button(f"✅ Aprovar #{p['id']}", key=f"ok_{p['id']}", use_container_width=True):
                            p["status"] = "Aprovado"
                            st.success("Aprovado com sucesso!")
                            st.rerun()
                    with b2:
                        if st.button(f"❌ Rejeitar #{p['id']}", key=f"no_{p['id']}", use_container_width=True):
                            p["status"] = "Rejeitado"
                            st.warning("Solicitação rejeitada.")
                            st.rerun()
        else:
            st.success("🎉 Nenhuma solicitação pendente no momento.")
            
    with sub_aba2:
        st.markdown("### Histórico Completo de Solicitações")
        df_historico = pd.DataFrame(st.session_state["agendamentos"])
        if not df_historico.empty:
            st.dataframe(df_historico, width='stretch')
        else:
            st.info("Nenhum registro no histórico.")
