import sqlite3
import hashlib
from database import get_conn


def gerar_hash(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


conn = get_conn()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    perfil TEXT NOT NULL,
    ativo INTEGER DEFAULT 1
)
""")

usuarios = [
    ("renan.ramos", "bjnubin8", "ADM"),
    ("jairo.arcanjo", "123456", "UTILIZADOR"),
    ("clayton.oliveira", "123456", "ANALISTA"),
]

for usuario, senha, perfil in usuarios:
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios
        (usuario, senha_hash, perfil, ativo)
        VALUES (?, ?, ?, 1)
    """, (
        usuario,
        gerar_hash(senha),
        perfil
    ))

conn.commit()
conn.close()

print("Usuários criados com sucesso.")