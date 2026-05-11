import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "pneus.db"


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def criar_banco():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pneus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fogo TEXT UNIQUE NOT NULL,
        medida TEXT,
        marca TEXT,
        modelo TEXT,
        status TEXT DEFAULT 'ESTOQUE',
        valor_compra REAL DEFAULT 0,
        custos_adicionais REAL DEFAULT 0,
        observacao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS veiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        placa TEXT UNIQUE NOT NULL,
        modelo TEXT,
        tipo TEXT,
        km_atual INTEGER DEFAULT 0,
        status TEXT DEFAULT 'ATIVO'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pneu_id INTEGER NOT NULL,
        veiculo_id INTEGER,
        posicao TEXT,
        data_entrada TEXT NOT NULL,
        km_entrada INTEGER NOT NULL,
        data_saida TEXT,
        km_saida INTEGER,
        km_rodado INTEGER,
        motivo_saida TEXT,
        destino TEXT,
        status_movimento TEXT DEFAULT 'ABERTO',
        observacao TEXT,
        FOREIGN KEY (pneu_id) REFERENCES pneus(id),
        FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
    )
    """)

    conn.commit()
    conn.close()