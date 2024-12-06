import sqlite3

def get_connection():
    conn = sqlite3.connect("database.db")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Cria tabelas se não existirem
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ambientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS disciplinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS turmas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS objetivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS feriados (
        data TEXT UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        ambiente_id INTEGER,
        horario TEXT,
        professor TEXT,
        disciplina_id INTEGER,
        turma_id INTEGER,
        objetivo_id INTEGER,
        disciplina_outro TEXT,
        turma_outro TEXT,
        objetivo_outro TEXT,
        criado_em TEXT,
        FOREIGN KEY(ambiente_id) REFERENCES ambientes(id),
        FOREIGN KEY(disciplina_id) REFERENCES disciplinas(id),
        FOREIGN KEY(turma_id) REFERENCES turmas(id),
        FOREIGN KEY(objetivo_id) REFERENCES objetivos(id)
    );
    """)

    conn.commit()
    conn.close()

def get_options(table_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id, nome FROM {table_name} ORDER BY nome;")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_option(table_name, nome):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {table_name}(nome) VALUES(?)", (nome,))
    conn.commit()
    conn.close()

def delete_option(table_name, option_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table_name} WHERE id=?", (option_id,))
    conn.commit()
    conn.close()

def is_feriado(data_str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT data FROM feriados WHERE data=?", (data_str,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def add_feriado(data_str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO feriados(data) VALUES(?)", (data_str,))
    conn.commit()
    conn.close()

def remove_feriado(data_str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM feriados WHERE data=?", (data_str,))
    conn.commit()
    conn.close()

def add_agendamento(data, ambiente_id, horario, professor, disciplina_id, turma_id, objetivo_id, disciplina_outro, turma_outro, objetivo_outro):
    import datetime
    criado_em = datetime.datetime.now().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO agendamentos(data, ambiente_id, horario, professor, disciplina_id, turma_id, objetivo_id, disciplina_outro, turma_outro, objetivo_outro, criado_em)
    VALUES(?,?,?,?,?,?,?,?,?,?,?)
    """, (data, ambiente_id, horario, professor, disciplina_id, turma_id, objetivo_id, disciplina_outro, turma_outro, objetivo_outro, criado_em))
    conn.commit()
    conn.close()

def is_available(data, ambiente_id, horario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT id FROM agendamentos
    WHERE data=? AND ambiente_id=? AND horario=?
    """, (data, ambiente_id, horario))
    row = cur.fetchone()
    conn.close()
    return row is None

def get_all_agendamentos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT a.id, a.data, amb.nome as ambiente, a.horario, a.professor, 
           d.nome as disciplina, t.nome as turma, o.nome as objetivo, 
           a.disciplina_outro, a.turma_outro, a.objetivo_outro, a.criado_em
    FROM agendamentos a
    LEFT JOIN ambientes amb ON a.ambiente_id = amb.id
    LEFT JOIN disciplinas d ON a.disciplina_id = d.id
    LEFT JOIN turmas t ON a.turma_id = t.id
    LEFT JOIN objetivos o ON a.objetivo_id = o.id
    ORDER BY a.data, a.horario;
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def remove_agendamento(ag_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM agendamentos WHERE id=?", (ag_id,))
    conn.commit()
    conn.close()
