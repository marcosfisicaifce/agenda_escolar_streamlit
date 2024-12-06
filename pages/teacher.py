import streamlit as st
from db import get_options, add_agendamento, is_available, is_feriado, get_all_agendamentos
from datetime import date, timedelta

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
    st.title("Agendamento de Ambientes (Professores)")

    modo = st.radio("Selecione a ação:", ["Agendar Ambiente", "Visualizar Agendamentos"])

    if modo == "Agendar Ambiente":
        st.subheader("Agendar Ambiente")
        datas = dias_disponiveis()
        if not datas:
            st.warning("Não há datas disponíveis nos próximos 7 dias letivos.")
            st.stop()

        data_selecionada = st.date_input("Data", value=datas[0], min_value=date.today())
        if data_selecionada not in datas:
            st.error("Data selecionada não está dentro do intervalo permitido (próximos 7 dias letivos).")
            st.stop()

        # Ambiente
        ambientes = get_options("ambientes")
        if not ambientes:
            st.error("Nenhum ambiente cadastrado. Contate o administrador.")
            st.stop()
        ambiente_nomes = [a[1] for a in ambientes]
        ambiente_escolhido = st.selectbox("Ambiente", ambiente_nomes)
        ambiente_id = [a[0] for a in ambientes if a[1] == ambiente_escolhido][0]

        # Horários
        horarios = ["1ª aula", "2ª aula", "3ª aula", "4ª aula", "5ª aula"]
        horario_escolhido = st.selectbox("Horário", horarios)

        # Professor
        professor = st.text_input("Nome do Professor")

        # Disciplinas
        disciplinas = get_options("disciplinas")
        disc_opcoes = [d[1] for d in disciplinas] + ["Outro"]
        disciplina_escolhida = st.selectbox("Disciplina", disc_opcoes)
        disciplina_outro = ""
        disciplina_id = None
        if disciplina_escolhida == "Outro":
            disciplina_outro = st.text_input("Informe a disciplina")
        else:
            disciplina_id = [d[0] for d in disciplinas if d[1] == disciplina_escolhida][0] if disciplinas else None

        # Turmas
        turmas = get_options("turmas")
        turma_opcoes = [t[1] for t in turmas] + ["Outro"]
        turma_escolhida = st.selectbox("Turma", turma_opcoes)
        turma_outro = ""
        turma_id = None
        if turma_escolhida == "Outro":
            turma_outro = st.text_input("Informe a turma")
        else:
            turma_id = [t[0] for t in turmas if t[1] == turma_escolhida][0] if turmas else None

        # Objetivos
        objetivos = get_options("objetivos")
        objetivo_opcoes = [o[1] for o in objetivos] + ["Outro"]
        objetivo_escolhido = st.selectbox("Objetivo", objetivo_opcoes)
        objetivo_outro = ""
        objetivo_id = None
        if objetivo_escolhido == "Outro":
            objetivo_outro = st.text_input("Informe o objetivo")
        else:
            objetivo_id = [o[0] for o in objetivos if o[1] == objetivo_escolhido][0] if objetivos else None

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

    else:
        # Modo Visualização de Agendamentos
        st.subheader("Visualizar Agendamentos")
        # Filtro por data e ambiente
        # Primeiro pegamos todos agendamentos
        ags = get_all_agendamentos()

        # Lista de datas únicas
        datas_unicas = sorted(list(set([a[1] for a in ags]))) # a[1] é a data no get_all_agendamentos
        datas_opcoes = ["Todas"] + datas_unicas
        data_filtrar = st.selectbox("Filtrar por data", datas_opcoes)

        # Lista de ambientes únicos
        ambientes_unicos = sorted(list(set([a[2] for a in ags]))) # a[2] é o nome do ambiente
        ambientes_opcoes = ["Todos"] + ambientes_unicos
        ambiente_filtrar = st.selectbox("Filtrar por ambiente", ambientes_opcoes)

        # Aplicar filtros
        ags_filtrados = []
        for ag in ags:
            (ag_id, ag_data, ag_ambiente, ag_horario, ag_prof, ag_disc, ag_tur, ag_obj, ag_disc_outro, ag_tur_outro, ag_obj_outro, ag_criado) = ag
            if (data_filtrar == "Todas" or ag_data == data_filtrar) and (ambiente_filtrar == "Todos" or ag_ambiente == ambiente_filtrar):
                ags_filtrados.append(ag)

        if ags_filtrados:
            for ag in ags_filtrados:
                (ag_id, ag_data, ag_ambiente, ag_horario, ag_prof, ag_disc, ag_tur, ag_obj, ag_disc_outro, ag_tur_outro, ag_obj_outro, ag_criado) = ag
                st.write(f"**Data:** {ag_data} | **Ambiente:** {ag_ambiente} | **Horário:** {ag_horario}")
                st.write(f"**Professor:** {ag_prof}")
                disc_str = ag_disc if ag_disc else ag_disc_outro
                tur_str = ag_tur if ag_tur else ag_tur_outro
                obj_str = ag_obj if ag_obj else ag_obj_outro
                st.write(f"**Disciplina:** {disc_str}")
                st.write(f"**Turma:** {tur_str}")
                st.write(f"**Objetivo:** {obj_str}")
                st.write("---")
        else:
            st.write("Nenhum agendamento encontrado com os filtros selecionados.")
