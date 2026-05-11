import sqlite3
from pathlib import Path
from datetime import datetime
import os

ORIGEM = Path(r"D:\WebApp Pneus\backend\data\pneus.db")
PASTA_BACKUP = Path(r"D:\WebApp Pneus\Backups")

PASTA_BACKUP.mkdir(parents=True, exist_ok=True)

data = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_db = PASTA_BACKUP / f"pneus_backup_{data}.db"

if not ORIGEM.exists():
    raise FileNotFoundError(f"Banco não encontrado: {ORIGEM}")

# Backup seguro do SQLite mesmo com o sistema rodando
origem_conn = sqlite3.connect(ORIGEM)
backup_conn = sqlite3.connect(backup_db)

with backup_conn:
    origem_conn.backup(backup_conn)

origem_conn.close()
backup_conn.close()

# Mantém somente os 5 backups mais recentes
backups = sorted(
    PASTA_BACKUP.glob("pneus_backup_*.db"),
    key=lambda arquivo: arquivo.stat().st_mtime,
    reverse=True
)

for arquivo_antigo in backups[8:]:
    arquivo_antigo.unlink()

print(f"Backup criado com sucesso: {backup_db}")
print("Mantidos somente os 8 backups mais recentes.")
