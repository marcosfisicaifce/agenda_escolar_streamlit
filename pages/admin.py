import streamlit as st
from db import get_options, add_option, delete_option, add_feriado, remove_feriado, get_all_agendamentos, remove_agendamento
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")  # Ajuste se necessário

def admin_page():
    # Se a variável de sessão não existir, cria
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False

    # Se não estiver logado, pede senha
    if not st.session_state.admin_logged:
        st.title("Área Administrativa - Login")
        pwd = st.text_input("Senha de Administrador", type="password")
        if st.button("Entrar"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_logged = True
                st.success("Login bem-sucedido!")
                # Não vamos forçar rerun. O usuário pode simplesmente escolher novamente "Administração" no menu,
                # ou atualizar a página, que vai mostrar o painel administrativo agora que está logado.
            else:
                st.error("Senha incorreta!")
        return
    
    # Se chegou aqui, está logado
    st.title("Área Administrativa")

    # Gerenciar Opções (Ambientes, Disciplinas, Turmas, Objetivos)
    st.subheader("Gerenciar Opções")
    tabela = st.selectbox("Selecionar tabela", ["ambientes", "disciplinas", "turmas", "objetivos"])
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
