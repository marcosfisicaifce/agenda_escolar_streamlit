import streamlit as st
from db import init_db

# Inicializa o banco de dados e sincroniza com o Airtable
init_db()

# Configuração da página
st.set_page_config(page_title="Agendamentos", layout="wide")

# Barra lateral de navegação
st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para:", ["Agendar (Professores)", "Administração"])

# Navegação entre as páginas
if page == "Agendar (Professores)":
    from pages.teacher import app
    app()
elif page == "Administração":
    from pages.admin import app
    app()
