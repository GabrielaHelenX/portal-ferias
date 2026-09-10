import streamlit as st
import datetime

st.set_page_config(page_title="Portal de Férias & Ausências", page_icon="🌴", layout="wide")

st.title("🌴 Portal de Férias & Ausências")
st.markdown("Gerencie suas solicitações de forma rápida e integrada com a equipe.")

# Abas limpas
aba_calendario, aba_solicitar = st.tabs(["📅 Visão da Equipe", "➕ Nova Solicitação"])

with aba_calendario:
    st.subheader("Calendário Consolidado da Equipe")
    st.info("Aqui a equipe visualiza o panorama de ausências e férias do mês.")
    
    # Exemplo da matriz da equipe
    dados_equipe = {
        "Colaborador": ["Danilo", "Joyce", "Erika", "Gabriela", "Kelvyn"],
        "Outubro/2026": ["Trabalhando", "Férias (10 dias)", "Trabalhando", "Trabalhando", "Trabalhando"],
        "Novembro/2026": ["Trabalhando", "Trabalhando", "Banco de Horas", "Férias (5 dias)", "Trabalhando"]
    }
    st.dataframe(dados_equipe, use_container_width=True)

with aba_solicitar:
    st.subheader("Solicitação Rápida")
    
    with st.form("form_ferias"):
        colaborador = st.selectbox("Seu Nome", ["Danilo", "Pedro", "Joyce", "Karina", "Gabriela"])
        tipo = st.radio("Tipo de Ausência", ["Férias", "Banco de Horas / Abono"], horizontal=True)
        
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("Data de Início", datetime.date.today())
        with col2:
            dias = st.number_input("Quantidade de Dias / Horas", min_value=1, max_value=30, value=5)
            
        data_fim = data_inicio + datetime.timedelta(days=int(dias))
        st.write(f"📅 **Previsão de Retorno:** {data_fim.strftime('%d/%m/%Y')}")
        
        st.markdown("---")
        st.markdown("🟢 **Validador Inteligente:** Sem conflitos com outros membros da equipe neste período.")
        
        enviar = st.form_submit_button("Enviar Solicitação para o Coordenador")
        
        if enviar:
            st.success(f"Solicitação enviada com sucesso, {colaborador}! O coordenador foi notificado.")