import sqlite3
import requests
import datetime

# Variáveis da sua configuração
AIRTABLE_BASE_ID = "appy8spIjI876Wzr6"  # Substitua pelo seu base ID do Airtable
TABLE_NAME = "Agendamentos"
PERSONAL_ACCESS_TOKEN = "patvIcYO7t9bazNyf.df657dbe559f752b11c8c7db5e98e46f36df373cbe6219868e5da23ef728dbe0"  # Seu PAT

AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"
HEADERS = {
    "Authorization": f"Bearer {PERSONAL_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def get_connection():
    conn = sqlite3.connect("database.db")
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    # Criação das tabelas se não existirem
    # Ajuste as tabelas conforme suas necessidades
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
    CREATE TABLE IF NOT EXISTS professores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
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

    # Após criar as tabelas, sincronizar com o Airtable
    sync_from_airtable_to_local()


def sync_from_airtable_to_local():
    # Obter todos os registros do Airtable
    records = get_all_records_from_airtable()

    conn = get_connection()
    cur = conn.cursor()

    # Limpa todos os agendamentos locais antes de recarregar
    cur.execute("DELETE FROM agendamentos;")

    for record in records:
        fields = record.get('fields', {})
        data = fields.get('Data', '')
        ambiente = fields.get('Ambiente', '')
        horario = fields.get('Horário', '')
        professor = fields.get('Professor', '')
        disciplina = fields.get('Disciplina', '')
        turma = fields.get('Turma', '')
        objetivo = fields.get('Objetivo', '')
        disciplina_outro = fields.get('Disciplina_outro', '')
        turma_outro = fields.get('Turma_outro', '')
        objetivo_outro = fields.get('Objetivo_outro', '')
        criado_em = fields.get('Criado_em', '')

        cur.execute("""
            INSERT INTO agendamentos(data, ambiente_id, horario, professor, disciplina_id, turma_id, objetivo_id, disciplina_outro, turma_outro, objetivo_outro, criado_em)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data,
            get_option_id("ambientes", ambiente),
            horario,
            professor,
            get_option_id("disciplinas", disciplina),
            get_option_id("turmas", turma),
            get_option_id("objetivos", objetivo),
            disciplina_outro,
            turma_outro,
            objetivo_outro,
            criado_em
        ))

    conn.commit()
    conn.close()

def get_option_id(table_name, nome):
    if not nome:
        return None
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM {table_name} WHERE nome=?", (nome,))
    row = cur.fetchone()
    # Se não existir, opcionalmente crie:
    if not row and nome.strip():
        cur.execute(f"INSERT INTO {table_name}(nome) VALUES(?)", (nome.strip(),))
        conn.commit()
        cur.execute(f"SELECT id FROM {table_name} WHERE nome=?", (nome.strip(),))
        row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None

def get_name_by_id(table_name, id_value):
    if id_value is None:
        return ""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT nome FROM {table_name} WHERE id=?", (id_value,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return ""

def get_all_records_from_airtable():
    response = requests.get(AIRTABLE_URL, headers=HEADERS)
    data = response.json()
    records = data.get('records', [])
    return records

def add_agendamento(data, ambiente_id, horario, professor, disciplina_id, turma_id, objetivo_id, disciplina_outro, turma_outro, objetivo_outro):
    criado_em = datetime.datetime.now().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO agendamentos(data, ambiente_id, horario, professor, disciplina_id, turma_id, objetivo_id, disciplina_outro, turma_outro, objetivo_outro, criado_em)
    VALUES(?,?,?,?,?,?,?,?,?,?,?)
    """, (data, ambiente_id, horario, professor, disciplina_id, turma_id, objetivo_id, disciplina_outro, turma_outro, objetivo_outro, criado_em))
    conn.commit()
    ag_id = cur.lastrowid
    conn.close()

    # Atualizar no Airtable
    ambiente = get_name_by_id("ambientes", ambiente_id)
    disciplina = get_name_by_id("disciplinas", disciplina_id)
    turma = get_name_by_id("turmas", turma_id)
    objetivo = get_name_by_id("objetivos", objetivo_id)

    fields = {
        "Data": data,
        "Ambiente": ambiente,
        "Horário": horario,
        "Professor": professor,
        "Disciplina": disciplina,
        "Turma": turma,
        "Objetivo": objetivo,
        "Disciplina_outro": disciplina_outro,
        "Turma_outro": turma_outro,
        "Objetivo_outro": objetivo_outro,
        "Criado_em": criado_em
    }
    insert_record_into_airtable(fields)

def insert_record_into_airtable(fields):
    payload = {"fields": fields}
    response = requests.post(AIRTABLE_URL, headers=HEADERS, json=payload)
    # Pode verificar response.status_code ou response.json() se quiser
