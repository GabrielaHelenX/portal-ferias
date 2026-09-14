import streamlit as st
import pandas as pd
import datetime
import holidays
import sqlite3

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA & BANCO DE DADOS LIMPO
# ---------------------------------------------------------
st.set_page_config(
    page_title="Portal de Férias & Ausências | Ânima",
    page_icon="🌴",
    layout="wide"
)

def obter_conexao():
    # Usando um novo nome de arquivo para limpar todos os dados de teste antigos
    conn = sqlite3.connect("banco_ferias_v2.db", check_same_thread=False)
    conn.text_factory = str
    return conn

def inicializar_banco():
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador TEXT,
            tipo TEXT,
            modo TEXT,
            inicio TEXT,
            fim TEXT,
            detalhe_tempo TEXT,
            justificativa TEXT,
            status TEXT
        );
    """)
    conn.commit()
    conn.close()

inicializar_banco()

def carregar_dados():
    conn = obter_conexao()
    df = pd.read_sql_query("SELECT * FROM agendamentos", conn)
    conn.close()
    
    if df.empty:
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agendamentos (colaborador, tipo, modo, inicio, fim, detalhe_tempo, justificativa, status)
            VALUES ('KELVYN AMARAL CANDIDO', 'Férias', 'Dias Inteiros', '2026-11-13', '2026-11-27', '15 dias', 'Férias programadas de novembro', 'Aprovado');
        """)
        conn.commit()
        conn.close()
        
        conn = obter_conexao()
        df = pd.read_sql_query("SELECT * FROM agendamentos", conn)
        conn.close()
        
    if not df.empty:
        df["inicio"] = pd.to_datetime(df["inicio"]).dt.date
        df["fim"] = pd.to_datetime(df["fim"]).dt.date
        df["id"] = pd.to_numeric(df["id"], errors="coerce")
    return df.to_dict(orient="records")

def salvar_novo_pedido(pedido):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO agendamentos (colaborador, tipo, modo, inicio, fim, detalhe_tempo, justificativa, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        pedido["colaborador"],
        pedido["tipo"],
        pedido["modo"],
        pedido["inicio"],
        pedido["fim"],
        pedido["detalhe_tempo"],
        pedido["justificativa"],
        pedido["status"]
    ))
    conn.commit()
    conn.close()

def atualizar_status_pedido(id_pedido, novo_status):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE agendamentos SET status = ? WHERE id = ?;
    """, (novo_status, id_pedido))
    conn.commit()
    conn.close()

def excluir_pedido(id_pedido):
    conn = obter_conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos WHERE id = ?;", (id_pedido,))
    conn.commit()
    conn.close()

# Carrega os dados para a sessão
st.session_state["agendamentos"] = carregar_dados()

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
    
    .alert-pendente {
        background-color: #7F1D1D;
        color: #FEE2E2;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #B91C1C;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
        font-size: 16px;
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

if "senha_gestor" not in st.session_state:
    st.session_state["senha_gestor"] = "1234"

EQUIPE_DETALHES = {
    "DANILO DA SILVA VILAS BOAS": {"estado": "SP", "local": "São Paulo - SP", "cargo": "Gestor", "inic": "DV"},
    "ERIKA LIMA DE OLIVEIRA": {"estado": "MG", "local": "Belo Horizonte - MG", "cargo": "Analista", "inic": "EO"},
    "JOYCE ADRIELLE DIAS DA SILVA": {"estado": "BA", "local": "Bahia (Salvador / Feira)", "cargo": "Analista", "inic": "JD"},
    "KELVYN AMARAL CANDIDO": {"estado": "MG", "local": "Belo Horizonte - MG", "cargo": "Analista", "inic": "KC"},
    "GABRIELA HELEN SANTOS XAVIER": {"estado": "BA", "local": "Bahia (Salvador / Feira)", "cargo": "Analista de Dados", "inic": "GX"}
}
EQUIPE = list(EQUIPE_DETALHES.keys())

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

    return erros, avisos

# ---------------------------------------------------------
# 3. INTERFACE PRINCIPAL
# ---------------------------------------------------------
st.title("🌴 Portal de Férias & Ausências")
st.caption(f"Ecossistema de Controle e Retenção Nacional — Ânima Educação")
st.divider()

with st.sidebar:
    st.markdown("### 👤 Identificação")
    perfil_usuario = st.selectbox("Quem está acessando?", EQUIPE)
    local_atual = EQUIPE_DETALHES[perfil_usuario]["local"]
    st.info(f"Logado como: **{perfil_usuario.split()[0]}**\n📍 Base: {local_atual}")
    st.markdown("---")
    st.markdown("📌 **Regras & Feriados por Estado:**\n- Danilo: SP\n- Erika & Kelvyn: MG\n- Gabriela & Joyce: BA\n- Bloqueio automático de início em feriados e fins de semana.")

if perfil_usuario == GESTOR_OFICIAL:
    aba_painel, aba_solicitar, aba_gestor = st.tabs([
        "📊 Calendário & Feriados", 
        "➕ Nova Solicitação", 
        f"⚙️ Painel do Gestor 🔒"
    ])
else:
    aba_painel, aba_solicitar = st.tabs([
        "📊 Calendário & Feriados", 
        "➕ Nova Solicitação"
    ])
    aba_gestor = None

# ---------------------------------------------------------
# ABA 1: CALENDÁRIO
# ---------------------------------------------------------
with aba_painel:
    st.subheader("Painel de Controle & Calendário da Equipe")
    
    col1, col2, col3 = st.columns(3)
    total_aprovados = sum(1 for r in st.session_state["agendamentos"] if str(r["status"]).strip().lower() == "aprovado")
    total_pendentes = sum(1 for r in st.session_state["agendamentos"] if str(r["status"]).strip().lower() == "pendente")
    
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
    
    agendamentos_ativos = [r for r in st.session_state["agendamentos"] if str(r["status"]).strip().lower() == "aprovado"]
    
    if agendamentos_ativos:
        for reg in agendamentos_ativos:
            inic = EQUIPE_DETALHES.get(reg['colaborador'], {}).get('inic', 'COL')
            modo_reg = reg.get("modo", "Dias Inteiros")
            detalhe_reg = reg.get("detalhe_tempo", f"{(reg['fim'] - reg['inicio']).days + 1} dias")
            
            if modo_reg == "Horas Parciais":
                info_tempo = f"⏰ Horário Parcial: {detalhe_reg} em {reg['inicio'].strftime('%d/%m/%Y')}"
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
    
    solicitante = perfil_usuario
    st.write(f"✍️ Solicitante: **{solicitante}**")

    tipo = st.radio("Modalidade", ["Férias", "Banco de Horas / Abono"], horizontal=True)
    modo_tempo = st.radio("Duração da Ausência", ["Dias Inteiros (Início e Fim)", "Horário Específico (Parcial)"], horizontal=True)
    
    dt_inicio = datetime.date.today()
    dt_fim = datetime.date.today()
    detalhe_str = ""
    
    if modo_tempo == "Dias Inteiros (Início e Fim)":
        c1, c2 = st.columns(2)
        with c1:
            dt_inicio = st.date_input("Data de Início", datetime.date.today())
        with c2:
            dt_fim = st.date_input("Data de Término", datetime.date.today() + datetime.timedelta(days=5))
        
        if dt_fim >= dt_inicio:
            qnt_dias = (dt_fim - dt_inicio).days + 1
        else:
            qnt_dias = 0
            
        retorno = dt_fim + datetime.timedelta(days=1)
        detalhe_str = f"{qnt_dias} dias"
        
        if qnt_dias > 0:
            st.markdown(f"💡 **Resumo Dinâmico:** De **{dt_inicio.strftime('%d/%m/%Y')}** até **{dt_fim.strftime('%d/%m/%Y')}** (**{qnt_dias} dias** no total). Retorno em: {retorno.strftime('%d/%m/%Y')}")
        else:
            st.error("❌ A data de término deve ser igual ou posterior à data de início.")
    else:
        st.markdown("---")
        st.markdown("🕒 **Defina o período da ausência parcial neste dia:**")
        
        dt_inicio = st.date_input("Data da Ausência Parcial", datetime.date.today())
        dt_fim = dt_inicio
        
        c_h1, c_h2 = st.columns(2)
        with c_h1:
            hora_inicio = st.time_input("Horário de Saída / Início", datetime.time(9, 0))
        with c_h2:
            hora_fim = st.time_input("Horário de Retorno / Término", datetime.time(12, 0))
        
        detalhe_str = f"Das {hora_inicio.strftime('%H:%M')} às {hora_fim.strftime('%H:%M')}"
        st.markdown(f"💡 **Resumo do Horário:** Ausente no dia **{dt_inicio.strftime('%d/%m/%Y')}** ({detalhe_str})")
        st.markdown("---")

    justificativa = st.text_area("Justificativa / Motivo", placeholder="Ex: Consulta médica, compromisso pessoal, descanso...")
    
    erros, avisos = checar_regras(solicitante, dt_inicio, dt_fim)
    bloqueio = False
    
    if modo_tempo == "Dias Inteiros (Início e Fim)" and dt_fim < dt_inicio:
        bloqueio = True
        erros.append("A data de término não pode ser anterior à data de início.")

    if erros:
        bloqueio = True
        for e in erros:
            st.error(f"❌ {e}")
    if avisos:
        for a in avisos:
            st.warning(f"⚠️ {a}")
            
    enviar = st.button("🚀 Enviar Solicitação para Aprovação", width='stretch')
    
    if enviar:
        if bloqueio:
            st.error("Envio bloqueado devido a inconsistências nas datas.")
        elif not justificativa.strip():
            st.error("A justificativa é obrigatória.")
        else:
            novo_pedido = {
                "colaborador": solicitante,
                "tipo": tipo,
                "modo": "Horas Parciais" if "Parcial" in modo_tempo else "Dias Inteiros",
                "inicio": str(dt_inicio),
                "fim": str(dt_fim),
                "detalhe_tempo": detalhe_str,
                "justificativa": justificativa,
                "status": "Pendente"
            }
            salvar_novo_pedido(novo_pedido)
            st.success("✅ Solicitação enviada com sucesso! Redirecionando para o calendário...")
            st.balloons()
            
            st.session_state["agendamentos"] = carregar_dados()
            st.rerun()

# ---------------------------------------------------------
# ABA 3: PAINEL DO GESTOR
# ---------------------------------------------------------
if aba_gestor is not None:
    with aba_gestor:
        st.subheader("Área Restrita do Gestor")
        st.caption("Insira a senha de acesso para gerenciar as aprovações da equipe.")
        
        with st.expander("🔑 Configurar ou Alterar Senha de Acesso (Gestor)", expanded=False):
            nova_senha_input = st.text_input("Definir Nova Senha para o Painel", type="password", placeholder="Digite a nova senha...")
            if st.button("Salvar Nova Senha", width='stretch'):
                if nova_senha_input.strip() != "":
                    st.session_state["senha_gestor"] = nova_senha_input.strip()
                    st.success("✅ Senha atualizada com sucesso!")
                else:
                    st.error("A senha não pode estar em branco.")

        st.markdown("---")
        senha_digitada = st.text_input("Digite a Senha de Acesso", type="password", placeholder="Insira a senha do gestor...")
        
        if senha_digitada == st.session_state["senha_gestor"]:
            st.success("✅ Acesso autorizado!")
            st.markdown(f"### Painel Gerencial de {GESTOR_OFICIAL}")
            
            total_pendentes_gestor = sum(1 for r in st.session_state["agendamentos"] if str(r["status"]).strip().lower() == "pendente")
            
            if total_pendentes_gestor > 0:
                st.markdown(f"""
                    <div class="alert-pendente">
                        🚨 ATENÇÃO: Existem <b>{total_pendentes_gestor}</b> solicitação(ões) aguardando sua análise e aprovação abaixo!
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.success("🎉 Tudo em dia! Nenhuma solicitação pendente no momento.")

            sub_pendentes, sub_historico = st.tabs(["⏳ Pendentes de Aprovação", "📋 Histórico Completo & Limpeza"])
            
            with sub_pendentes:
                pendentes = [r for r in st.session_state["agendamentos"] if str(r["status"]).strip().lower() == "pendente"]
                
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
                            
                            b1, b2, b3 = st.columns(3)
                            with b1:
                                if st.button(f"✅ Aprovar #{p['id']}", key=f"ok_{p['id']}", width='stretch'):
                                    atualizar_status_pedido(p['id'], "Aprovado")
                                    st.success(f"Solicitação de {p['colaborador'].split()[0]} aprovada com sucesso!")
                                    st.session_state["agendamentos"] = carregar_dados()
                                    st.rerun()
                            with b2:
                                if st.button(f"❌ Rejeitar #{p['id']}", key=f"no_{p['id']}", width='stretch'):
                                    atualizar_status_pedido(p['id'], "Rejeitado")
                                    st.warning("Solicitação rejeitada.")
                                    st.session_state["agendamentos"] = carregar_dados()
                                    st.rerun()
                            with b3:
                                if st.button(f"🗑️ Excluir #{p['id']}", key=f"del_{p['id']}", width='stretch'):
                                    excluir_pedido(p['id'])
                                    st.error(f"Solicitação #{p['id']} excluída permanentemente.")
                                    st.session_state["agendamentos"] = carregar_dados()
                                    st.rerun()
                else:
                    st.info("Nenhum pedido pendente na aba de análises.")
                    
            with sub_historico:
                st.markdown("### Registro Geral de Solicitações & Exclusão de Testes")
                st.caption("Você pode visualizar o histórico ou excluir registros indesejados/testes da base.")
                
                todos_regs = st.session_state["agendamentos"]
                if todos_regs:
                    for reg in todos_regs:
                        col_h1, col_h2 = st.columns([4, 1])
                        with col_h1:
                            st.text(f"ID #{reg['id']} | {reg['colaborador']} | {reg['tipo']} | De {reg['inicio']} até {reg['fim']} [{reg['status']}]")
                        with col_h2:
                            if st.button(f"🗑️ Apagar", key=f"del_hist_{reg['id']}", width='stretch'):
                                excluir_pedido(reg['id'])
                                st.warning(f"Registro #{reg['id']} apagado!")
                                st.session_state["agendamentos"] = carregar_dados()
                                st.rerun()
                    
                    st.divider()
                    df_hist = pd.DataFrame(todos_regs)
                    st.dataframe(df_hist, width='stretch')
                    
                    csv_data = df_hist.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 Baixar Histórico Completo (Planilha CSV / Excel)",
                        data=csv_data,
                        file_name="historico_ferias_anima.csv",
                        mime="text/csv",
                        width='stretch'
                    )
                else:
                    st.info("Nenhum registro encontrado.")
                    
        elif senha_digitada != "":
            st.error("❌ Senha incorreta. Apenas o gestor autorizado possui a senha de acesso.")
        else:
            st.info("🔒 Por favor, digite a senha para visualizar o painel gerencial.")
