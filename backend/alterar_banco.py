from database import get_conn, DB_PATH

print("Banco usado:", DB_PATH)

conn = get_conn()
cursor = conn.cursor()

# Verifica colunas atuais
colunas = cursor.execute("PRAGMA table_info(pneus)").fetchall()
nomes_colunas = [coluna[1] for coluna in colunas]

if "custos_adicionais" not in nomes_colunas:
    cursor.execute("""
        ALTER TABLE pneus
        ADD COLUMN custos_adicionais REAL DEFAULT 0
    """)
    print("Coluna custos_adicionais adicionada com sucesso.")
else:
    print("A coluna custos_adicionais já existe.")

conn.commit()

# Confirma as colunas depois da alteração
colunas = cursor.execute("PRAGMA table_info(pneus)").fetchall()
print("Colunas da tabela pneus:")
for coluna in colunas:
    print("-", coluna[1])

conn.close()