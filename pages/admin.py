import streamlit as st
from db import get_options, add_option, delete_option, add_feriado, remove_feriado, get_all_agendamentos, remove_agendamento, add_agendamento, is_available
import os
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")

def admin_page():
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False

    if not st.session_state.admin_logged:
        st.title("Área Administrativa - Login")
        pwd = st.text_input("Senha de Administrador", type="password")
        if st.button("Entrar"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_logged = True
                st.success("Login bem-sucedido!")
            else:
                st.error("Senha incorreta!")
        return
    
    st.title("Área Administrativa")

    # Gerenciar Opções (Agora incluindo professores)
    st.subheader("Gerenciar Opções")
    tabela = st.selectbox("Selecionar tabela", ["ambientes", "disciplinas", "turmas", "objetivos", "professores"])
    options = get_options(tabela)
    st.write("Opções cadastradas:")
    for oid, nome in options:
        col1, col2 = st.columns([4,1])
        with col1:
            st.write(nome)
        with col2:
            if st.button("Remover", key=f"remover_{tabela}_{oid}"):
                delete_option(tabela, oid)
                st.experimental_rerun()

    novo = st.text_input(f"Novo {tabela[:-1]}:")
    if st.button(f"Adicionar {tabela[:-1]}"):
        if novo.strip():
            try:
                add_option(tabela, novo.strip())
                st.success("Adicionado com sucesso.")
                st.experimental_rerun()
            except:
                st.error("Erro ao adicionar. Verifique se já existe.")
        else:
            st.error("Nome inválido.")

    # Gerenciar Feriados
    st.subheader("Gerenciar Feriados")
    feriado_data = st.date_input("Data do feriado")
    if st.button("Adicionar Feriado"):
        add_feriado(feriado_data.isoformat())
        st.success("Feriado adicionado!")
        st.experimental_rerun()

    from db import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT data FROM feriados ORDER BY data;")
    feriados = cur.fetchall()
    conn.close()
    if feriados:
        st.write("Feriados cadastrados:")
        for (fdata,) in feriados:
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(fdata)
            with col2:
                if st.button("Remover", key=f"remover_feriado_{fdata}"):
                    remove_feriado(fdata)
                    st.experimental_rerun()

    # Administrador pode agendar além dos 7 dias
    st.subheader("Agendar (Administrador, sem limite de data)")

    # Opções para agendamento:
    # Data livre
    data_livre = st.date_input("Data para agendar (administrador pode escolher qualquer data)")

    # Selecionar ambiente
    ambientes = get_options("ambientes")
    if ambientes:
        ambiente_nomes = [a[1] for a in ambientes]
        ambiente_escolhido = st.selectbox("Ambiente", ambiente_nomes)
        ambiente_id = [a[0] for a in ambientes if a[1] == ambiente_escolhido][0]
    else:
        st.warning("Nenhum ambiente cadastrado.")
        ambiente_id = None

    # Selecionar professor
    profs = get_options("professores")
    if profs:
        prof_nomes = [p[1] for p in profs]
        prof_escolhido = st.selectbox("Professor", prof_nomes)
        professor = prof_escolhido
    else:
        st.warning("Nenhum professor cadastrado.")
        professor = st.text_input("Professor (nome livre)")

    # Aulas disponíveis (múltipla seleção)
    aulas_opcoes = ["1ª aula", "2ª aula", "3ª aula", "4ª aula", "5ª aula", "6ª aula", "7ª aula", "8ª aula", "9ª aula", "Intervalo do almoço"]
    aulas_escolhidas = st.multiselect("Aulas", aulas_opcoes)

    # Disciplinas
    disciplinas = get_options("disciplinas")
    disc_opcoes = [d[1] for d in disciplinas] + ["Outro"]
    disciplina_escolhida = st.selectbox("Disciplina", disc_opcoes)
    disciplina_outro = ""
    disciplina_id = None
    if disciplina_escolhida == "Outro":
        disciplina_outro = st.text_input("Informe a disciplina")
    else:
        if disciplinas:
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
        if turmas:
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
        if objetivos:
            objetivo_id = [o[0] for o in objetivos if o[1] == objetivo_escolhido][0]

    if st.button("Agendar (Admin)"):
        if not professor.strip():
            st.error("É necessário inserir o nome do professor.")
        elif not aulas_escolhidas:
            st.error("É necessário escolher pelo menos uma aula.")
        else:
            data_str = data_livre.isoformat()
            # Verificar disponibilidade de todas as aulas escolhidas
            aulas_indisponiveis = []
            for aula in aulas_escolhidas:
                if not is_available(data_str, ambiente_id, aula):
                    aulas_indisponiveis.append(aula)
            if aulas_indisponiveis:
                st.error(f"As seguintes aulas já estão agendadas: {', '.join(aulas_indisponiveis)}")
            else:
                # Todas disponíveis, inserir um agendamento para cada aula
                for aula in aulas_escolhidas:
                    add_agendamento(data_str, ambiente_id, aula, professor.strip(), 
                                    disciplina_id, turma_id, objetivo_id, 
                                    disciplina_outro.strip(), turma_outro.strip(), objetivo_outro.strip())
                st.success("Agendamento realizado com sucesso!")

    st.subheader("Agendamentos")
    ags = get_all_agendamentos()
    if ags:
        for ag in ags:
            (ag_id, ag_data, ag_ambiente, ag_horario, ag_prof, ag_disc, ag_tur, ag_obj, ag_disc_outro, ag_tur_outro, ag_obj_outro, ag_criado) = ag
            st.write(f"**ID:** {ag_id} | **Data:** {ag_data} | **Ambiente:** {ag_ambiente} | **Horário:** {ag_horario}")
            st.write(f"**Professor:** {ag_prof}")
            disc_str = ag_disc if ag_disc else ag_disc_outro
            tur_str = ag_tur if ag_tur else ag_tur_outro
            obj_str = ag_obj if ag_obj else ag_obj_outro
            st.write(f"**Disciplina:** {disc_str}")
            st.write(f"**Turma:** {tur_str}")
            st.write(f"**Objetivo:** {obj_str}")
            st.write(f"Criado em: {ag_criado}")
            if st.button("Remover agendamento", key=f"rem_ag_{ag_id}"):
                remove_agendamento(ag_id)
                st.experimental_rerun()
            st.markdown("---")
    else:
        st.write("Nenhum agendamento encontrado.")

def app():
    admin_page()
