import pandas as pd
from database import get_conn, criar_banco
from database import DB_PATH

print("Banco usado:", DB_PATH)

ARQUIVO_EXCEL = r"D:\WebApp Pneus\backend\importacao.xlsx"

criar_banco()


def limpar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip().upper()


def limpar_numero(valor):
    if pd.isna(valor) or valor == "":
        return 0

    try:
        return float(valor)
    except ValueError:
        return 0


def importar_pneus(conn):
    try:
        df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Pneus")
    except Exception as e:
        print(f"Erro ao ler aba Pneus: {e}")
        return

    colunas_obrigatorias = ["fogo"]

    for coluna in colunas_obrigatorias:
        if coluna not in df.columns:
            print(f"Coluna obrigatória ausente na aba Pneus: {coluna}")
            return

    cursor = conn.cursor()
    total = 0
    ignorados = 0

    for _, row in df.iterrows():
        fogo = limpar_texto(row.get("fogo"))

        if not fogo:
            ignorados += 1
            continue

        medida = limpar_texto(row.get("medida"))
        marca = limpar_texto(row.get("marca"))
        modelo = limpar_texto(row.get("modelo"))
        status = limpar_texto(row.get("status")) or "ESTOQUE"
        valor_compra = limpar_numero(row.get("valor_compra"))
        observacao = str(row.get("observacao", "") or "").strip()

        if status not in ["ESTOQUE", "EM USO", "CONSERTO", "RECAPAGEM", "DESCARTADO"]:
            status = "ESTOQUE"

        cursor.execute("""
            INSERT INTO pneus
            (fogo, medida, marca, modelo, status, valor_compra, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(fogo) DO UPDATE SET
                medida = excluded.medida,
                marca = excluded.marca,
                modelo = excluded.modelo,
                status = excluded.status,
                valor_compra = excluded.valor_compra,
                observacao = excluded.observacao
        """, (
            fogo,
            medida,
            marca,
            modelo,
            status,
            valor_compra,
            observacao
        ))

        total += 1

    print(f"Pneus importados: {total}")
    print(f"Pneus ignorados/duplicados: {ignorados}")


def importar_veiculos(conn):
    try:
        df = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Veiculos")
    except Exception as e:
        print(f"Erro ao ler aba Veiculos: {e}")
        return

    colunas_obrigatorias = ["placa"]

    for coluna in colunas_obrigatorias:
        if coluna not in df.columns:
            print(f"Coluna obrigatória ausente na aba Veiculos: {coluna}")
            return

    cursor = conn.cursor()
    total = 0
    ignorados = 0

    for _, row in df.iterrows():
        placa = limpar_texto(row.get("placa"))

        if not placa:
            ignorados += 1
            continue

        modelo = limpar_texto(row.get("modelo"))
        tipo = limpar_texto(row.get("tipo"))
        km_atual = int(limpar_numero(row.get("km_atual")))
        status = limpar_texto(row.get("status")) or "ATIVO"

        if status not in ["ATIVO", "INATIVO"]:
            status = "ATIVO"

        cursor.execute("""
            INSERT OR IGNORE INTO veiculos
            (placa, modelo, tipo, km_atual, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            placa,
            modelo,
            tipo,
            km_atual,
            status
        ))

        if cursor.rowcount > 0:
            total += 1
        else:
            ignorados += 1

    print(f"Veículos importados: {total}")
    print(f"Veículos ignorados/duplicados: {ignorados}")


def main():
    conn = get_conn()

    importar_pneus(conn)
    importar_veiculos(conn)

    conn.commit()
    conn.close()

    print("Importação finalizada.")


if __name__ == "__main__":
    main()