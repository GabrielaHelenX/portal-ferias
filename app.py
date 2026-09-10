import streamlit as st
import pandas as pd
import datetime
import holidays

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA (Layout Profissional)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Portal de Férias & Ausências | Ânima",
    page_icon="🌴",
    layout="wide"
)

# Estilização Clean & Modern UI (Padrão Ânima)
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    h1 { color: #F3E8FF !important; font-weight: 800; font-size: 1.8rem !important; }
    h2, h3 { color: #E9D5FF !important; font-weight: 700; }
    
    .anima-card {
        background-color: #1E1B4B;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #4C1D95;
        box-shadow: 0 4px 12px rgba(76, 29, 149, 0.1);
        margin-bottom: 12px;
    }
    
    .holiday-badge {
        background-color: #831843;
        color: #F43F5E;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        border: 1px solid #9F1239;
    }
    
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
# 2. DADOS DA EQUIPE E LOCALIDADES
# ---------------------------------------------------------
GESTOR_OFICIAL = "DANILO DA SILVA VILAS BOAS"
SENHA_GESTOR = "anima2026"

EQUIPE_DETALHES = {
    "DANILO DA SILVA VILAS BOAS": {"estado": "SP", "local": "São Paulo - SP", "cargo": "Gestor", "inic": "DV"},
    "ERIKA LIMA DE OLIVEIRA": {"estado": "MG", "local": "Belo Horizonte - MG", "cargo": "Analista", "inic": "EO"},
    "JOYCE ADRIELLE DIAS DA SILVA": {"estado": "BA", "local": "Bahia (Salvador / Feira)", "cargo": "Analista", "inic": "JD"},
    "KELVYN AMARAL CANDIDO": {"estado": "MG", "local": "Belo Horizonte - MG", "cargo": "Analista", "inic": "KC"},
    "GABRIELA HELEN SANTOS XAVIER": {"estado": "BA", "local": "Bahia (Salvador / Feira)", "cargo": "Analista de Dados", "inic": "GX"}
}
EQUIPE = list(EQUIPE_DETALHES.keys())

# Inicialização com tratamento de segurança para evitar qualquer KeyError
if "agendamentos" not in st.session_state:
    st.session_state["agendamentos"] = [
        {
            "id": 1,
            "colaborador": "JOYCE ADRIELLE DIAS DA SILVA",
            "tipo": "Férias",
            "modo": "Dias Inteiros",
            "inicio": datetime.date(2024, 12, 10),
            "fim": datetime.date(2025, 12, 9),
            "detalhe_tempo": "20 dias",
            "justificativa": "Férias anuais programadas",
            "status": "Aprovado"
        },
        {
            "id": 2,
            "colaborador": "KELVYN AMARAL CANDIDO",
            "tipo": "Férias",
            "modo": "Dias Inteiros",
            "inicio": datetime.date(2026, 11, 13),
            "fim": datetime.date(2026, 11, 27),
            "detalhe_tempo": "15 dias",
            "justificativa": "Férias programadas de novembro",
            "status": "Aprovado"
        }
    ]

def checar_regras(nome_colaborador, dt_inicio, dt_fim):
    detalhes = EQUIPE_DETALHES[nome_colaborador]
    feriados_br = holidays.BR(years=dt_inicio.year, subdiv=detalhes["estado"])
    erros, avisos = [], []
    
    if dt_inicio in feriados_br:
        erros.append(f"A data de início cai no feriado nacional/estadual: '{feriados_br.get(dt_inicio)}'. Não é permitido iniciar ausências em feriados.")
    if dt_inicio.weekday() >= 5:
        erros.append("O início das ausências não pode cair em finais de semana.")
        
    feriados_no_periodo = []
    atual = dt_inicio
    while atual <= dt_fim:
        if atual in feriados_br:
            feriados_no_periodo.append(f"{atual.strftime('%d/%m/%Y')} ({feriados_br.get(atual)})")
        atual += datetime.timedelta(days=1)
        
    if feriados_no_periodo:
        avisos.append(f"Feriado(s) identificado(s) no meio do período: {', '.join(feriados_no_periodo)}.")

    for reg in st.session_state["agendamentos"]:
        if reg["colaborador"] != nome_colaborador and reg["status"] == "Aprovado":
            if dt_inicio <= reg["fim"] and dt_fim >= reg["inicio"]:
                avisos.append(f"Atenção: {reg['colaborador'].split()[0]} já estará ausente neste mesmo período.")
    return erros, avisos

# ---------------------------------------------------------
# 3. INTERFACE PRINCIPAL
# ---------------------------------------------------------
st.title("🌴 Portal de Férias & Ausências")
st.caption(f"Ecossistema de Controle e Retenção Nacional — Ânima Educação")
st.divider()

with st.sidebar:
    st.markdown("### 👤 Identificação")
    perfil_usuario = st.selectbox(
        "Quem está acessando?", 
        EQUIPE
    )
    local_atual = EQUIPE_DETALHES[perfil_usuario]["local"]
    st.info(f"Logado como: **{perfil_usuario.split()[0]}**\n📍 Base: {local_atual}")
    st.markdown("---")
    st.markdown("📌 **Regras & Feriados por Estado:**\n- Danilo: SP\n- Erika & Kelvyn: MG\n- Gabriela & Joyce: BA\n- Bloqueio automático de início em feriados e fins de semana.")

aba_painel, aba_solicitar, aba_gestor = st.tabs([
    "📊 Calendário & Feriados", 
    "➕ Nova Solicitação", 
    f"⚙️ Painel do Gestor 🔒"
])

# ---------------------------------------------------------
# ABA 1: CALENDÁRIO, EQUIPE E FERIADOS DESTACADOS
# ---------------------------------------------------------
with aba_painel:
    st.subheader("Painel de Controle & Calendário da Equipe")
    
    col1, col2, col3 = st.columns(3)
    total_aprovados = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Aprovado")
    total_pendentes = sum(1 for r in st.session_state["agendamentos"] if r["status"] == "Pendente")
    
    col1.metric("Ausências Aprovadas", total_aprovados)
    col2.metric("Pendentes de Aprovação", total_pendentes)
    col3.metric("Membros Monitorados", len(EQUIPE))
    
    st.write("")
    
    with st.expander(f"📅 Ver Feriados Nacionais e Estaduais para {local_atual} (Ano 2026)", expanded=False):
        feriados_usuario = holidays.BR(years=2026, subdiv=EQUIPE_DETALHES[perfil_usuario]["estado"])
        feriados_futuros = {d: n for d, n in sorted(feriados_usuario.items()) if d >= datetime.date.today()}
        
        cols_f = st.columns(2)
        idx = 0
        for data_f, nome_f in list(feriados_futuros.items())[:10]:
            with cols_f[idx % 2]:
                st.markdown(f"🔴 **{data_f.strftime('%d/%m/%Y')}** — <span class='holiday-badge'>{nome_f}</span>", unsafe_allow_html=True)
            idx += 1

    st.markdown("### 📅 Linha do Tempo e Ausências da Equipe")
    st.caption("Consulte abaixo quem estará ausente para evitar conflitos de cobertura.")
    
    agendamentos_ativos = [r for r in st.session_state["agendamentos"] if r["status"] == "Aprovado"]
    
    if agendamentos_ativos:
        for reg in agendamentos_ativos:
            inic = EQUIPE_DETALHES.get(reg['colaborador'], {}).get('inic', 'COL')
            modo_reg = reg.get("modo", "Dias Inteiros")
            detalhe_reg = reg.get("detalhe_tempo", f"{(reg['fim'] - reg['inicio']).days + 1} dias")
            
            if modo_reg == "Horas Parciais":
                info_tempo = f"⏰ Horário: {detalhe_reg} em {reg['inicio'].strftime('%d/%m/%Y')}"
            else:
                info_tempo = f"📅 De {reg['inicio'].strftime('%d/%m/%Y')} até {reg['fim'].strftime('%d/%m/%Y')} ({detalhe_reg})"

            st.markdown(f"""
                <div class="anima-card">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div>
                            <span style="background-color: #7C3AED; color: white; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold;">{inic}</span>
                            <b style="font-size: 15px; color: #F8FAFC; margin-left: 8px;">{reg['colaborador']}</b>
                            <p style="margin: 6px 0 0 0; color: #CBD5E1; font-size: 13px;">
                                📌 <b>{reg['tipo']}</b> | {info_tempo}
                            </p>
                            <p style="margin: 4px 0 0 0; color: #C084FC; font-size: 12px; font-style: italic;">
                                💬 Justificativa: "{reg.get('justificativa', 'Sem justificativa')}"
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
# ABA 2: NOVA SOLICITAÇÃO
# ---------------------------------------------------------
with aba_solicitar:
    st.subheader("Registrar Nova Solicitação de Ausência")
    st.caption(f"Base operacional do solicitante: **{local_atual}** (Validação de feriados estaduais ativa).")
    
    with st.form("form_solicitacao_limpo"):
        solicitante = perfil_usuario
        st.write(f"✍️ Solicitante: **{solicitante}**")

        tipo = st.radio("Modalidade", ["Férias", "Banco de Horas / Abono", "Folga de Aniversário"], horizontal=True)
        modo_tempo = st.radio("Duração da Ausência", ["Dias Inteiros", "Horário Específico (Parcial)"], horizontal=True)
        
        if modo_tempo == "Dias Inteiros":
            c1, c2 = st.columns(2)
            with c1:
                dt_inicio = st.date_input("Data de Início", datetime.date.today())
            with c2:
                if tipo == "Férias":
                    qnt_dias = st.number_input("Quantidade de Dias", min_value=1, max_value=30, value=10, step=1)
                    dt_fim = dt_inicio + datetime.timedelta(days=int(qnt_dias) - 1)
                else:
                    dt_fim = st.date_input("Data de Término", dt_inicio)
                    qnt_dias = max(1, (dt_fim - dt_inicio).days + 1)

            retorno = dt_fim + datetime.timedelta(days=1)
            detalhe_str = f"{int(qnt_dias)} dias"
            st.markdown(f"💡 **Previsão de Retorno:** {retorno.strftime('%d/%m/%Y')} ({int(qnt_dias)} dias ausente)")
        else:
            dt_inicio = st.date_input("Data da Ausência", datetime.date.today())
            dt_fim = dt_inicio
            
            c_h1, c_h2 = st.columns(2)
            with c_h1:
                hora_inicio = st.time_input("Horário de Início", datetime.time(9, 0))
            with c_h2:
                hora_fim = st.time_input("Horário de Retorno", datetime.time(12, 0))
            
            detalhe_str = f"Das {hora_inicio.strftime('%H:%M')} às {hora_fim.strftime('%H:%M')}"
            st.markdown(f"💡 **Resumo do Horário:** Ausente no dia {dt_inicio.strftime('%d/%m/%Y')} ({detalhe_str})")

        justificativa = st.text_area("Justificativa / Motivo", placeholder="Ex: Consulta médica, compromisso pessoal...")
        
        erros, avisos = checar_regras(solicitante, dt_inicio, dt_fim)
        bloqueio = False
        
        if erros:
            bloqueio = True
            for e in erros:
                st.error(f"❌ {e}")
        if avisos:
            for a in avisos:
                st.warning(f"⚠️ {a}")
                
        enviar = st.form_submit_button("🚀 Enviar Solicitação para Aprovação", use_container_width=True)
        
        if enviar:
            if bloqueio:
                st.error("Envio bloqueado por regras de feriados ou fins de semana.")
            elif not justificativa.strip():
                st.error("A justificativa é obrigatória.")
            else:
                novo_pedido = {
                    "id": len(st.session_state["agendamentos"]) + 1,
                    "colaborador": solicitante,
                    "tipo": tipo,
                    "modo": modo_tempo,
                    "inicio": dt_inicio,
                    "fim": dt_fim,
                    "detalhe_tempo": detalhe_str,
                    "justificativa": justificativa,
                    "status": "Pendente"
                }
                st.session_state["agendamentos"].append(novo_pedido)
                st.balloons()
                st.success("Solicitação enviada com sucesso! O gestor foi notificado.")

# ---------------------------------------------------------
# ABA 3: PAINEL DO GESTOR COM SENHA
# ---------------------------------------------------------
with aba_gestor:
    st.subheader("Área Restrita do Gestor")
    st.caption("Insira a senha de acesso para gerenciar as aprovações da equipe.")
    
    senha_digitada = st.text_input("Senha de Acesso do Gestor", type="password", placeholder="Digite a senha...")
    
    if senha_digitada == SENHA_GESTOR:
        st.success("✅ Acesso autorizado!")
        st.markdown(f"### Painel Gerencial de {GESTOR_OFICIAL}")
        
        sub_pendentes, sub_historico = st.tabs(["⏳ Pendentes de Aprovação", "📋 Histórico Completo"])
        
        with sub_pendentes:
            pendentes = [r for r in st.session_state["agendamentos"] if r["status"] == "Pendente"]
            
            if pendentes:
                for p in pendentes:
                    p_modo = p.get("modo", "Dias Inteiros")
                    p_detalhe = p.get("detalhe_tempo", "")
                    
                    with st.container(border=True):
                        if p_modo == "Horas Parciais":
                            info_p = f"⏰ Horário Parcial: {p_detalhe} em {p['inicio'].strftime('%d/%m/%Y')}"
                        else:
                            info_p = f"📅 Período: De {p['inicio'].strftime('%d/%m/%Y')} até {p['fim'].strftime('%d/%m/%Y')} ({p_detalhe})"

                        st.markdown(f"**{p['colaborador']}** — 📌 *{p['tipo']}*")
                        st.caption(info_p)
                        st.text(f"Justificativa: {p.get('justificativa', 'Sem justificativa')}")
                        
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button(f"✅ Aprovar #{p['id']}", key=f"ok_{p['id']}", use_container_width=True):
                                p["status"] = "Aprovado"
                                st.success(f"Solicitação de {p['colaborador'].split()[0]} aprovada!")
                                st.rerun()
                        with b2:
                            if st.button(f"❌ Rejeitar #{p['id']}", key=f"no_{p['id']}", use_container_width=True):
                                p["status"] = "Rejeitado"
                                st.warning("Solicitação rejeitada.")
                                st.rerun()
            else:
                st.success("🎉 Nenhuma solicitação pendente no momento. Tudo em dia!")
                
        with sub_historico:
            st.markdown("### Registro Geral de Solicitações")
            df_hist = pd.DataFrame(st.session_state["agendamentos"])
            if not df_hist.empty:
                st.dataframe(df_hist, use_container_width=True)
            else:
                st.info("Nenhum registro encontrado.")
                
    elif senha_digitada != "":
        st.error("❌ Senha incorreta. Apenas o gestor autorizado possui a senha de acesso.")
    else:
        st.info("🔒 Por favor, digite a senha para visualizar o painel gerencial.")
