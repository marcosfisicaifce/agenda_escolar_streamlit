import streamlit as st
from db import init_db, add_agendamento

init_db()

st.title("Exemplo de Agendamento com Airtable")

if st.button("Criar Agendamento de Teste"):
    # Exemplo fixo
    add_agendamento(
        data="2024-12-10",
        ambiente_id=None, # Suponha que aqui não há ID ainda, o código cria um
        horario="1ª aula",
        professor="Fulano",
        disciplina_id=None,
        turma_id=None,
        objetivo_id=None,
        disciplina_outro="",
        turma_outro="",
        objetivo_outro=""
    )
    st.success("Agendamento criado e sincronizado com Airtable!")
