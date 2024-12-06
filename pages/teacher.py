import streamlit as st
from db import get_options, add_agendamento, is_available, is_feriado
from datetime import date, timedelta
import sqlite3

def dias_disponiveis():
    hoje = date.today()
    dias = []
    for i in range(1,8): # Próximos 7 dias
        d = hoje + timedelta(days=i)
        # Verificar se não é sábado(5), domingo(6) e nem feriado
        if d.weekday() < 5 and not is_feriado(d.isoformat()):
            dias.append(d)
    return dias

def app():
    st.title("Agendamento de Ambientes")

    st.write("Selecione as informações para agendar.")
    # Selecionar data
    datas = dias_disponiveis()
    data_selecionada = st.date_input("Data", value=datas[0] if datas else None, min_value=date.today())
    # Caso não haja datas (exemplo, se todos os próximos 7 dias forem fds/feriado), avisar
    if not datas:
        st.warning("Não há datas disponíveis para agendamento nos próximos 7 dias.")
        st.stop()

    if data_selecionada not in datas:
        st.error("Data selecionada não está dentro do range permitido (próximos 7 dias letivos).")
        st.stop()

    # Ambiente
    ambientes = get_options("ambientes")
    ambiente_nomes = [a[1] for a in ambientes]
    ambiente_escolhido = st.selectbox("Ambiente", ambiente_nomes)
    ambiente_id = [a[0] for a in ambientes if a[1] == ambiente_escolhido][0]

    # Horários (fixos para exemplo)
    horarios = ["1ª aula", "2ª aula", "3ª aula", "4ª aula", "5ª aula"]
    horario_escolhido = st.selectbox("Horário", horarios)

    # Professor
    professor = st.text_input("Nome do Professor")
    if not professor.strip():
        st.warning("Favor inserir o nome do professor.")
    
    # Disciplinas
    disciplinas = get_options("disciplinas")
    disc_opcoes = [d[1] for d in disciplinas] + ["Outro"]
    disciplina_escolhida = st.selectbox("Disciplina", disc_opcoes)
    disciplina_outro = ""
    disciplina_id = None
    if disciplina_escolhida == "Outro":
        disciplina_outro = st.text_input("Informe a disciplina")
    else:
        disciplina_id = [d[0] for d in disciplinas if d[1] == disciplina_escolhida][0]

    # Turmas
    turmas = get_options("turmas")
    turma_opcoes = [t[1] for t in turmas] + ["Outro"]
    turma_escolhida = st.selectbox("Turma", turma_opcoes)
    turma_outro = ""
    turma_id = None
    if turma_escolhida == "Outro":
        turma_outro = st.text_input("Informe a turma")
    else:
        turma_id = [t[0] for t in turmas if t[1] == turma_escolhida][0]

    # Objetivos
    objetivos = get_options("objetivos")
    objetivo_opcoes = [o[1] for o in objetivos] + ["Outro"]
    objetivo_escolhido = st.selectbox("Objetivo", objetivo_opcoes)
    objetivo_outro = ""
    objetivo_id = None
    if objetivo_escolhido == "Outro":
        objetivo_outro = st.text_input("Informe o objetivo")
    else:
        objetivo_id = [o[0] for o in objetivos if o[1] == objetivo_escolhido][0]

    if st.button("Agendar"):
        if not professor.strip():
            st.error("É necessário inserir o nome do professor.")
            st.stop()

        data_str = data_selecionada.isoformat()
        # Verificar disponibilidade
        if is_available(data_str, ambiente_id, horario_escolhido):
            add_agendamento(data_str, ambiente_id, horario_escolhido, professor.strip(), 
                            disciplina_id, turma_id, objetivo_id, 
                            disciplina_outro.strip(), turma_outro.strip(), objetivo_outro.strip())
            st.success("Agendamento realizado com sucesso!")
        else:
            st.error("Este horário já está agendado para o ambiente escolhido.")


