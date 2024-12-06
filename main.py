import streamlit as st
from db import init_db

init_db()

st.set_page_config(page_title="Agendamentos", layout="wide")

# Navegação principal
st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para:", ["Agendar (Professores)", "Administração"])

if page == "Agendar (Professores)":
    from pages.teacher import app
    app()
elif page == "Administração":
    from pages.admin import app
    app()
