from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
from pathlib import Path
import hashlib

from database import get_conn, criar_banco

app = FastAPI(title="API Controle de Pneus")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

criar_banco()


class PneuCreate(BaseModel):
    fogo: str
    medida: str = ""
    marca: str = ""
    modelo: str = ""
    valor_compra: float = 0
    observacao: str = ""


class VeiculoCreate(BaseModel):
    placa: str
    modelo: str = ""
    tipo: str = ""
    km_atual: int = 0


class LancamentoCreate(BaseModel):
    pneu_id: int
    veiculo_id: int
    posicao: str
    km_entrada: int
    data_movimento: str = ""
    movimentacao_antiga: bool = False
    observacao: str = ""


class SaidaPneuCreate(BaseModel):
    pneu_id: int
    km_saida: int
    destino: str
    data_movimento: str = ""
    observacao: str = ""
    

class AlterarStatusPneuCreate(BaseModel):
    pneu_id: int
    novo_status: str
    data_movimento: str = ""
    observacao: str = ""
    custo_adicional: float = 0
    
    
class LoginCreate(BaseModel):
    usuario: str
    senha: str
    

class UsuarioCreate(BaseModel):
    usuario: str
    senha: str
    perfil: str
    
class AlterarPosicaoPneuCreate(BaseModel):
    fogo: str
    nova_posicao: str
    km_movimento: int
    data_movimento: str = ""
    movimentacao_antiga: bool = False
    observacao: str = ""


class RodizioPneusCreate(BaseModel):
    fogo_1: str
    fogo_2: str
    km_movimento: int
    data_movimento: str = ""
    movimentacao_antiga: bool = False
    observacao: str = ""
    
def gerar_hash(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def verificar_usuario(usuario, senha):
    conn = get_conn()
    user = conn.execute("""
        SELECT id, usuario, perfil, ativo
        FROM usuarios
        WHERE usuario = ?
        AND senha_hash = ?
        AND ativo = 1
    """, (
        usuario.strip().lower(),
        gerar_hash(senha)
    )).fetchone()

    conn.close()

    if not user:
        return None

    return dict(user)

def formatar_data_br(data):
    if not data:
        return None

    try:
        return datetime.strptime(data, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return data

def obter_data_movimento(data_movimento: str = ""):
    if data_movimento:
        try:
            return datetime.strptime(data_movimento, "%Y-%m-%d").strftime("%Y-%m-%d 00:00:00")
        except Exception:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def formatar_data_br_sem_hora(data):
    if not data:
        return None

    try:
        return datetime.strptime(data, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
    except Exception:
        return data

def obter_posicoes_permitidas():
    return [
        "DD",
        "DE",
        "2DD",
        "2DE",
        "TDE",
        "TDI",
        "TEI",
        "TEE",
        "1DE",
        "1DI",
        "1EI",
        "1EE",
        "2DI",
        "2EI",
        "2EE",
        "3DE",
        "3DI",
        "3EI",
        "3EE",
        "4DE",
        "4DI",
        "4EI",
        "4EE",
        "ESTEPE1",
        "ESTEPE2",
    ]

# -------------------------
# LOGIN
# -------------------------

@app.post("/login")
def login(dados: LoginCreate):
    usuario = verificar_usuario(dados.usuario, dados.senha)

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos."
        )

    return {
        "mensagem": "Login realizado com sucesso.",
        "usuario": usuario["usuario"],
        "perfil": usuario["perfil"]
    }

# -------------------------
# CADASTRO NOVOS USUARIOS
# -------------------------

@app.get("/usuarios")
def listar_usuarios():
    conn = get_conn()

    usuarios = conn.execute("""
        SELECT id, usuario, perfil, ativo
        FROM usuarios
        ORDER BY usuario
    """).fetchall()

    conn.close()

    return [dict(u) for u in usuarios]

@app.post("/usuarios")
def cadastrar_usuario(dados: UsuarioCreate):
    usuario = dados.usuario.strip().lower()
    senha = dados.senha.strip()
    perfil = dados.perfil.upper().strip()

    perfis_permitidos = ["ADM", "UTILIZADOR", "GESTAO"]

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="Informe o usuário."
        )

    if not senha:
        raise HTTPException(
            status_code=400,
            detail="Informe a senha."
        )

    if perfil not in perfis_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Perfil inválido."
        )

    conn = get_conn()
    cursor = conn.cursor()

    usuario_existente = cursor.execute("""
        SELECT id
        FROM usuarios
        WHERE usuario = ?
    """, (usuario,)).fetchone()

    if usuario_existente:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Usuário já cadastrado."
        )

    cursor.execute("""
        INSERT INTO usuarios
        (usuario, senha_hash, perfil, ativo)
        VALUES (?, ?, ?, 1)
    """, (
        usuario,
        gerar_hash(senha),
        perfil
    ))

    conn.commit()
    conn.close()

    return {
        "mensagem": "Usuário cadastrado com sucesso.",
        "usuario": usuario,
        "perfil": perfil
    }

# -------------------------
# PNEUS
# -------------------------

@app.get("/pneus")
def listar_pneus():
    conn = get_conn()
    pneus = conn.execute("SELECT * FROM pneus ORDER BY fogo").fetchall()
    conn.close()
    return [dict(p) for p in pneus]


@app.post("/pneus")
def cadastrar_pneu(pneu: PneuCreate):
    conn = get_conn()
    cursor = conn.cursor()

    fogo = pneu.fogo.strip().upper()

    pneu_existente = cursor.execute("""
        SELECT id
        FROM pneus
        WHERE fogo = ?
    """, (fogo,)).fetchone()

    if pneu_existente:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu com fogo {fogo} já está cadastrado."
        )

    cursor.execute("""
        INSERT INTO pneus 
        (fogo, medida, marca, modelo, valor_compra, observacao)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        fogo,
        pneu.medida.upper().strip(),
        pneu.marca.upper().strip(),
        pneu.modelo.upper().strip(),
        pneu.valor_compra,
        pneu.observacao
    ))

    conn.commit()
    conn.close()

    return {"mensagem": "Pneu cadastrado com sucesso"}


# -------------------------
# VEÍCULOS
# -------------------------

@app.get("/veiculos")
def listar_veiculos():
    conn = get_conn()
    veiculos = conn.execute("""
        SELECT *
        FROM veiculos
        ORDER BY placa
    """).fetchall()
    conn.close()

    return [dict(v) for v in veiculos]


@app.post("/veiculos")
def cadastrar_veiculo(veiculo: VeiculoCreate):
    conn = get_conn()
    cursor = conn.cursor()

    placa = veiculo.placa.upper().strip()

    veiculo_existente = cursor.execute("""
        SELECT id
        FROM veiculos
        WHERE placa = ?
    """, (placa,)).fetchone()

    if veiculo_existente:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O veículo com placa {placa} já está cadastrado."
        )

    cursor.execute("""
        INSERT INTO veiculos
        (placa, modelo, tipo, km_atual)
        VALUES (?, ?, ?, ?)
    """, (
        placa,
        veiculo.modelo.upper().strip(),
        veiculo.tipo.upper().strip(),
        veiculo.km_atual
    ))

    conn.commit()
    conn.close()

    return {"mensagem": "Veículo cadastrado com sucesso"}

# -------------------------
# LANÇAMENTO DE PNEU
# -------------------------

@app.post("/lancamentos")
def lancar_pneu(lancamento: LancamentoCreate):
    conn = get_conn()
    cursor = conn.cursor()

    data_atual = obter_data_movimento(lancamento.data_movimento)

    posicoes_permitidas = obter_posicoes_permitidas()

    posicao = lancamento.posicao.upper().strip()

    if posicao not in posicoes_permitidas:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                "Posição inválida. Use uma destas opções: "
                + ", ".join(posicoes_permitidas)
            )
        )
    
    # -------------------------
    # Valida KM informado
    # -------------------------
    if lancamento.km_entrada < 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="O KM de entrada não pode ser negativo."
        )

    # -------------------------
    # Verifica se o pneu existe
    # -------------------------
    pneu = cursor.execute("""
        SELECT * FROM pneus
        WHERE id = ?
    """, (lancamento.pneu_id,)).fetchone()

    if not pneu:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Pneu não encontrado."
        )

    # -------------------------
    # Bloqueia pneu descartado
    # -------------------------
    if pneu["status"] == "DESCARTADO":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {pneu['fogo']} está descartado e não pode ser lançado."
        )

    # -------------------------
    # Bloqueia pneu em recapagem
    # -------------------------
    if pneu["status"] == "RECAPAGEM":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {pneu['fogo']} está em recapagem e não pode ser lançado."
        )

    # -------------------------
    # Bloqueia pneu em garantia
    # -------------------------
    if pneu["status"] == "GARANTIA":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {pneu['fogo']} está em garantia e não pode ser lançado."
        )
    # -------------------------
    # Bloqueia pneu em conserto
    # -------------------------        
    
    if pneu["status"] == "CONSERTO":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {pneu['fogo']} está em conserto e não pode ser lançado."
        )

    # -------------------------
    # Verifica se o veículo existe
    # -------------------------
    veiculo = cursor.execute("""
        SELECT * FROM veiculos
        WHERE id = ?
    """, (lancamento.veiculo_id,)).fetchone()

    if not veiculo:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Veículo não encontrado."
        )

    # -------------------------
    # Bloqueia veículo inativo
    # -------------------------
    if veiculo["status"] != "ATIVO":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O veículo {veiculo['placa']} está inativo."
        )

    # -------------------------
    # Não deixa lançar com KM menor que o KM atual do veículo
    # -------------------------
    if not lancamento.movimentacao_antiga and lancamento.km_entrada < veiculo["km_atual"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O KM informado ({lancamento.km_entrada}) é menor que o KM atual "
                f"do veículo {veiculo['placa']} ({veiculo['km_atual']}). "
                f"Se for uma movimentação antiga, marque a opção correspondente."
            )
        )

    # -------------------------
    # Bloqueia se o pneu já estiver lançado
    # -------------------------
    mov_aberta = cursor.execute("""
        SELECT 
            m.*,
            v.placa
        FROM movimentacoes m
        LEFT JOIN veiculos v ON v.id = m.veiculo_id
        WHERE m.pneu_id = ?
        AND m.status_movimento = 'ABERTO'
    """, (lancamento.pneu_id,)).fetchone()

    if mov_aberta:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O pneu {pneu['fogo']} já está lançado no veículo "
                f"{mov_aberta['placa']}, posição {mov_aberta['posicao']}."
            )
        )

    # -------------------------
    # Bloqueia se a posição já estiver ocupada
    # -------------------------
    posicao_ocupada = cursor.execute("""
        SELECT 
            m.*,
            p.fogo
        FROM movimentacoes m
        JOIN pneus p ON p.id = m.pneu_id
        WHERE m.veiculo_id = ?
        AND m.posicao = ?
        AND m.status_movimento = 'ABERTO'
    """, (
        lancamento.veiculo_id,
        posicao
    )).fetchone()

    if posicao_ocupada:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"A posição {posicao} do veículo {veiculo['placa']} "
                f"já está ocupada pelo pneu {posicao_ocupada['fogo']}."
            )
        )

    # -------------------------
    # Cria nova movimentação
    # -------------------------
    cursor.execute("""
        INSERT INTO movimentacoes
        (
            pneu_id,
            veiculo_id,
            posicao,
            data_entrada,
            km_entrada,
            observacao
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        lancamento.pneu_id,
        lancamento.veiculo_id,
        posicao,
        data_atual,
        lancamento.km_entrada,
        lancamento.observacao
    ))

    # Atualiza status do pneu
    cursor.execute("""
        UPDATE pneus
        SET status = 'EM USO'
        WHERE id = ?
    """, (lancamento.pneu_id,))

    # Atualiza KM do veículo
    if not lancamento.movimentacao_antiga:
        cursor.execute("""
            UPDATE veiculos
            SET km_atual = ?
            WHERE id = ?
        """, (
            lancamento.km_entrada,
            lancamento.veiculo_id
        ))

    conn.commit()
    conn.close()

    return {"mensagem": "Pneu lançado com sucesso."}


@app.post("/saida-pneu")
def registrar_saida_pneu(saida: SaidaPneuCreate):
    conn = get_conn()
    cursor = conn.cursor()

    data_atual = obter_data_movimento(saida.data_movimento)

    if saida.km_saida < 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="O KM de saída não pode ser negativo."
        )

    pneu = cursor.execute("""
        SELECT * FROM pneus
        WHERE id = ?
    """, (saida.pneu_id,)).fetchone()

    if not pneu:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Pneu não encontrado."
        )

    mov_aberta = cursor.execute("""
        SELECT 
            m.*,
            v.placa
        FROM movimentacoes m
        LEFT JOIN veiculos v ON v.id = m.veiculo_id
        WHERE m.pneu_id = ?
        AND m.status_movimento = 'ABERTO'
    """, (saida.pneu_id,)).fetchone()

    if not mov_aberta:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {pneu['fogo']} não possui lançamento aberto."
        )

    if saida.km_saida < mov_aberta["km_entrada"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O KM de saída ({saida.km_saida}) não pode ser menor que o KM "
                f"de entrada ({mov_aberta['km_entrada']})."
            )
        )

    km_rodado = saida.km_saida - mov_aberta["km_entrada"]

    # Busca o veículo onde o pneu está lançado
    veiculo = cursor.execute("""
        SELECT * FROM veiculos
        WHERE id = ?
    """, (mov_aberta["veiculo_id"],)).fetchone()

    # Não deixa informar KM menor que o KM atual da placa
    if veiculo and saida.km_saida < veiculo["km_atual"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O KM informado ({saida.km_saida}) é menor que o KM atual "
                f"do veículo {veiculo['placa']} ({veiculo['km_atual']})."
            )
        )

    destino = saida.destino.upper().strip()
    observacao_saida = saida.observacao.upper().strip()
    
    cursor.execute("""
        UPDATE movimentacoes
        SET
            data_saida = ?,
            km_saida = ?,
            km_rodado = ?,
            destino = ?,
            status_movimento = 'FECHADO',
            observacao = CASE
                WHEN observacao IS NULL OR observacao = ''
                THEN ?
                ELSE observacao || ' | Saída: ' || ?
            END
        WHERE id = ?
    """, (
        data_atual,
        saida.km_saida,
        km_rodado,
        destino,
        observacao_saida,
        observacao_saida,
        mov_aberta["id"]
    ))

    
    recapadoras_permitidas = [
        "SANTA CRUZ",
        "VOLPE",
        "NILCAP",
        "FM PNEUS"
    ]

    consertos_permitidos = [
        "INTERNO",
        "FAM PNEUS"
    ]

    if destino == "RECAPAGEM":
        if not observacao_saida:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Selecione a recapadora antes de enviar o pneu para recapagem."
            )

        if observacao_saida not in recapadoras_permitidas:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Recapadora inválida. Selecione: SANTA CRUZ, VOLPE, NILCAP ou FM PNEUS."
            )

    if destino == "CONSERTO":
        if not observacao_saida:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Selecione o local do conserto."
            )

        if observacao_saida not in consertos_permitidos:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Local de conserto inválido. Selecione: INTERNO ou FAM PNEUS."
            )

    if destino == "DESCARTE":
        novo_status = "DESCARTADO"
    elif destino == "RECAPAGEM":
        novo_status = "RECAPAGEM"
    elif destino == "CONSERTO":
        novo_status = "CONSERTO"
    elif destino == "GARANTIA":
        novo_status = "GARANTIA"
    else:
        novo_status = "ESTOQUE"

    cursor.execute("""
        UPDATE pneus
        SET status = ?
        WHERE id = ?
    """, (
        novo_status,
        saida.pneu_id
    ))

    # Atualiza o KM atual do veículo com o KM informado na saída
    if mov_aberta["veiculo_id"]:
        cursor.execute("""
            UPDATE veiculos
            SET km_atual = ?
            WHERE id = ?
        """, (
            saida.km_saida,
            mov_aberta["veiculo_id"]
        ))

    conn.commit()
    conn.close()

    return {
        "mensagem": "Saída registrada com sucesso.",
        "km_rodado": km_rodado,
        "novo_status": novo_status,
        "km_atual_veiculo": saida.km_saida
    }
    
@app.post("/alterar-status-pneu")
def alterar_status_pneu(dados: AlterarStatusPneuCreate):
    conn = get_conn()
    cursor = conn.cursor()

    data_atual = obter_data_movimento(dados.data_movimento)

    status_permitidos = [
        "ESTOQUE",
        "GARANTIA",
        "RECAPAGEM",
        "CONSERTO",
        "DESCARTADO"
    ]

    novo_status = dados.novo_status.upper().strip()
    observacao = dados.observacao.upper().strip()

    recapadoras_permitidas = [
        "SANTA CRUZ",
        "VOLPE",
        "NILCAP",
        "FM PNEUS"
    ]

    consertos_permitidos = [
    "INTERNO",
    "FAM PNEUS"
    ]

    if novo_status == "RECAPAGEM":
        if not observacao:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Selecione a recapadora antes de enviar o pneu para recapagem."
            )

        if observacao not in recapadoras_permitidas:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Recapadora inválida. Selecione: SANTA CRUZ, VOLPE, NILCAP ou FM PNEUS."
            )

    if novo_status == "CONSERTO":
        if not observacao:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Selecione o local do conserto."
            )

        if observacao not in consertos_permitidos:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Local de conserto inválido. Selecione: INTERNO ou FAM PNEUS."
            )

    if novo_status not in status_permitidos:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Status inválido."
        )
    
    pneu = cursor.execute("""
        SELECT * FROM pneus
        WHERE id = ?
    """, (dados.pneu_id,)).fetchone()

    if not pneu:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Pneu não encontrado."
        )
    
    status_atual = str(pneu["status"]).upper().strip()

    if novo_status == status_atual:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O pneu {pneu['fogo']} já está com o status {status_atual}. "
                f"Selecione um status diferente."
            )
        )
    
    if pneu["status"] == "DESCARTADO" and novo_status != "DESCARTADO":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O pneu {pneu['fogo']} está descartado e não pode voltar "
                f"para {novo_status}."
            )
        )
    
    mov_aberta = cursor.execute("""
        SELECT 
            m.*,
            v.placa
        FROM movimentacoes m
        LEFT JOIN veiculos v ON v.id = m.veiculo_id
        WHERE m.pneu_id = ?
        AND m.status_movimento = 'ABERTO'
    """, (dados.pneu_id,)).fetchone()

    if mov_aberta:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O pneu {pneu['fogo']} está aplicado no veículo "
                f"{mov_aberta['placa']}, posição {mov_aberta['posicao']}. "
                f"Para alterar o status, registre a saída primeiro."
            )
        )

    custo_adicional = dados.custo_adicional or 0

    if custo_adicional < 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="O custo adicional não pode ser negativo."
        )

    if custo_adicional > 0 and status_atual not in ["RECAPAGEM", "CONSERTO"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Só é permitido informar custo adicional para pneu em recapagem ou conserto."
        )
        
    # Atualiza o status atual do pneu
    cursor.execute("""
        UPDATE pneus
        SET status = ?,
            custos_adicionais = COALESCE(custos_adicionais, 0) + ?,
            observacao = CASE
                WHEN observacao IS NULL OR observacao = ''
                THEN ?
                ELSE observacao || ' | Status: ' || ?
            END
        WHERE id = ?
    """, (
        novo_status,
        custo_adicional,
        dados.observacao,
        dados.observacao,
        dados.pneu_id
    ))
    
    observacao_historico = (
        f"{dados.observacao} | Custo adicional: R$ {custo_adicional:.2f}"
        if custo_adicional > 0
        else dados.observacao
    )
    
    # Grava a alteração no histórico do pneu
    cursor.execute("""
        INSERT INTO movimentacoes
        (
            pneu_id,
            veiculo_id,
            posicao,
            data_entrada,
            km_entrada,
            data_saida,
            km_saida,
            km_rodado,
            motivo_saida,
            destino,
            status_movimento,
            observacao
        )
        VALUES (?, NULL, NULL, ?, 0, NULL, NULL, NULL, NULL, ?, ?, ?)
    """, (
        dados.pneu_id,
        data_atual,
        novo_status,
        novo_status,
        observacao_historico
    ))

    conn.commit()
    conn.close()

    return {
        "mensagem": "Status do pneu alterado com sucesso.",
        "novo_status": novo_status
    }

#Rodizio pneu para posição vazia
@app.post("/alterar-posicao-pneu")
def alterar_posicao_pneu(dados: AlterarPosicaoPneuCreate):
    conn = get_conn()
    cursor = conn.cursor()

    data_atual = obter_data_movimento(dados.data_movimento)
    fogo = dados.fogo.strip().upper()
    nova_posicao = dados.nova_posicao.strip().upper()

    posicoes_permitidas = obter_posicoes_permitidas()

    if nova_posicao not in posicoes_permitidas:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Posição inválida."
        )

    if dados.km_movimento < 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="O KM não pode ser negativo."
        )

    mov_atual = cursor.execute("""
        SELECT
            m.*,
            p.fogo,
            p.status,
            v.placa,
            v.km_atual
        FROM movimentacoes m
        JOIN pneus p ON p.id = m.pneu_id
        JOIN veiculos v ON v.id = m.veiculo_id
        WHERE p.fogo = ?
        AND m.status_movimento = 'ABERTO'
    """, (fogo,)).fetchone()

    if not mov_atual:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {fogo} não está aplicado em nenhum veículo."
        )

    if mov_atual["status"] != "EM USO":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {fogo} não está com status EM USO."
        )

    if nova_posicao == mov_atual["posicao"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {fogo} já está na posição {nova_posicao}."
        )

    if dados.km_movimento < mov_atual["km_entrada"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O KM informado ({dados.km_movimento}) não pode ser menor que "
                f"o KM de entrada do pneu ({mov_atual['km_entrada']})."
            )
        )

    if not dados.movimentacao_antiga and dados.km_movimento < mov_atual["km_atual"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O KM informado ({dados.km_movimento}) é menor que o KM atual "
                f"do veículo {mov_atual['placa']} ({mov_atual['km_atual']}). "
                f"Se for movimentação antiga, marque a opção correspondente."
            )
        )

    posicao_ocupada = cursor.execute("""
        SELECT
            m.*,
            p.fogo
        FROM movimentacoes m
        JOIN pneus p ON p.id = m.pneu_id
        WHERE m.veiculo_id = ?
        AND m.posicao = ?
        AND m.status_movimento = 'ABERTO'
    """, (
        mov_atual["veiculo_id"],
        nova_posicao
    )).fetchone()

    if posicao_ocupada:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"A posição {nova_posicao} já está ocupada pelo pneu "
                f"{posicao_ocupada['fogo']}."
            )
        )

    km_rodado = dados.km_movimento - mov_atual["km_entrada"]

    # Fecha movimentação atual
    cursor.execute("""
        UPDATE movimentacoes
        SET
            data_saida = ?,
            km_saida = ?,
            km_rodado = ?,
            destino = 'RODÍZIO',
            status_movimento = 'FECHADO',
            observacao = CASE
                WHEN ? IS NULL OR TRIM(?) = ''
                THEN observacao
                WHEN observacao IS NULL OR TRIM(observacao) = ''
                THEN ?
                ELSE observacao || ' | ' || ?
            END
        WHERE id = ?
    """, (
        data_atual,
        dados.km_movimento,
        km_rodado,
        dados.observacao,
        dados.observacao,
        dados.observacao,
        dados.observacao,
        mov_atual["id"]
    ))

    # Abre nova movimentação na nova posição
    cursor.execute("""
        INSERT INTO movimentacoes
        (
            pneu_id,
            veiculo_id,
            posicao,
            data_entrada,
            km_entrada,
            destino,
            status_movimento,
            observacao
        )
        VALUES (?, ?, ?, ?, ?, 'RODÍZIO', 'ABERTO', ?)
    """, (
        mov_atual["pneu_id"],
        mov_atual["veiculo_id"],
        nova_posicao,
        data_atual,
        dados.km_movimento,
        dados.observacao
    ))

    if not dados.movimentacao_antiga:
        cursor.execute("""
            UPDATE veiculos
            SET km_atual = ?
            WHERE id = ?
        """, (
            dados.km_movimento,
            mov_atual["veiculo_id"]
        ))

    conn.commit()
    conn.close()

    return {
        "mensagem": "Posição alterada por rodízio com sucesso.",
        "fogo": fogo,
        "posicao_anterior": mov_atual["posicao"],
        "nova_posicao": nova_posicao,
        "km_rodado": km_rodado
    }

#Rodizio entre 2 pneus
@app.post("/rodizio-pneus")
def rodizio_pneus(dados: RodizioPneusCreate):
    conn = get_conn()
    cursor = conn.cursor()

    data_atual = obter_data_movimento(dados.data_movimento)
    fogo_1 = dados.fogo_1.strip().upper()
    fogo_2 = dados.fogo_2.strip().upper()

    if fogo_1 == fogo_2:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Informe dois pneus diferentes."
        )

    if dados.km_movimento < 0:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="O KM não pode ser negativo."
        )

    mov_1 = cursor.execute("""
        SELECT
            m.*,
            p.fogo,
            p.status,
            v.placa,
            v.km_atual
        FROM movimentacoes m
        JOIN pneus p ON p.id = m.pneu_id
        JOIN veiculos v ON v.id = m.veiculo_id
        WHERE p.fogo = ?
        AND m.status_movimento = 'ABERTO'
    """, (fogo_1,)).fetchone()

    mov_2 = cursor.execute("""
        SELECT
            m.*,
            p.fogo,
            p.status,
            v.placa,
            v.km_atual
        FROM movimentacoes m
        JOIN pneus p ON p.id = m.pneu_id
        JOIN veiculos v ON v.id = m.veiculo_id
        WHERE p.fogo = ?
        AND m.status_movimento = 'ABERTO'
    """, (fogo_2,)).fetchone()

    if not mov_1:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {fogo_1} não está aplicado em nenhum veículo."
        )

    if not mov_2:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"O pneu {fogo_2} não está aplicado em nenhum veículo."
        )

    if mov_1["status"] != "EM USO" or mov_2["status"] != "EM USO":
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Os dois pneus precisam estar com status EM USO."
        )

    if mov_1["veiculo_id"] != mov_2["veiculo_id"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"Os pneus não estão na mesma placa. "
                f"{fogo_1} está na placa {mov_1['placa']} e "
                f"{fogo_2} está na placa {mov_2['placa']}."
            )
        )

    if dados.km_movimento < mov_1["km_entrada"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O KM informado não pode ser menor que o KM de entrada "
                f"do pneu {fogo_1}: {mov_1['km_entrada']}."
            )
        )

    if dados.km_movimento < mov_2["km_entrada"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O KM informado não pode ser menor que o KM de entrada "
                f"do pneu {fogo_2}: {mov_2['km_entrada']}."
            )
        )

    if not dados.movimentacao_antiga and dados.km_movimento < mov_1["km_atual"]:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=(
                f"O KM informado ({dados.km_movimento}) é menor que o KM atual "
                f"do veículo {mov_1['placa']} ({mov_1['km_atual']}). "
                f"Se for movimentação antiga, marque a opção correspondente."
            )
        )

    km_rodado_1 = dados.km_movimento - mov_1["km_entrada"]
    km_rodado_2 = dados.km_movimento - mov_2["km_entrada"]

    # Fecha pneu 1
    cursor.execute("""
        UPDATE movimentacoes
        SET
            data_saida = ?,
            km_saida = ?,
            km_rodado = ?,
            destino = 'RODÍZIO',
            status_movimento = 'FECHADO',
            observacao = CASE
                WHEN ? IS NULL OR TRIM(?) = ''
                THEN observacao
                WHEN observacao IS NULL OR TRIM(observacao) = ''
                THEN ?
                ELSE observacao || ' | ' || ?
            END
        WHERE id = ?
    """, (
        data_atual,
        dados.km_movimento,
        km_rodado_1,
        dados.observacao,
        dados.observacao,
        dados.observacao,
        dados.observacao,
        mov_1["id"]
    ))

    # Fecha pneu 2
    cursor.execute("""
        UPDATE movimentacoes
        SET
            data_saida = ?,
            km_saida = ?,
            km_rodado = ?,
            destino = 'RODÍZIO',
            status_movimento = 'FECHADO',
            observacao = CASE
                WHEN ? IS NULL OR TRIM(?) = ''
                THEN observacao
                WHEN observacao IS NULL OR TRIM(observacao) = ''
                THEN ?
                ELSE observacao || ' | ' || ?
            END
        WHERE id = ?
    """, (
        data_atual,
        dados.km_movimento,
        km_rodado_2,
        dados.observacao,
        dados.observacao,
        dados.observacao,
        dados.observacao,
        mov_2["id"]
    ))

    # Abre pneu 1 na posição do pneu 2
    cursor.execute("""
        INSERT INTO movimentacoes
        (
            pneu_id,
            veiculo_id,
            posicao,
            data_entrada,
            km_entrada,
            destino,
            status_movimento,
            observacao
        )
        VALUES (?, ?, ?, ?, ?, 'RODÍZIO', 'ABERTO', ?)
    """, (
        mov_1["pneu_id"],
        mov_1["veiculo_id"],
        mov_2["posicao"],
        data_atual,
        dados.km_movimento,
        dados.observacao
    ))

    # Abre pneu 2 na posição do pneu 1
    cursor.execute("""
        INSERT INTO movimentacoes
        (
            pneu_id,
            veiculo_id,
            posicao,
            data_entrada,
            km_entrada,
            destino,
            status_movimento,
            observacao
        )
        VALUES (?, ?, ?, ?, ?, 'RODÍZIO', 'ABERTO', ?)
    """, (
        mov_2["pneu_id"],
        mov_2["veiculo_id"],
        mov_1["posicao"],
        data_atual,
        dados.km_movimento,
        dados.observacao
    ))

    if not dados.movimentacao_antiga:
        cursor.execute("""
            UPDATE veiculos
            SET km_atual = ?
            WHERE id = ?
        """, (
            dados.km_movimento,
            mov_1["veiculo_id"]
        ))

    conn.commit()
    conn.close()

    return {
        "mensagem": "Rodízio realizado com sucesso.",
        "placa": mov_1["placa"],
        "pneu_1": fogo_1,
        "pneu_1_posicao_anterior": mov_1["posicao"],
        "pneu_1_nova_posicao": mov_2["posicao"],
        "pneu_2": fogo_2,
        "pneu_2_posicao_anterior": mov_2["posicao"],
        "pneu_2_nova_posicao": mov_1["posicao"]
    }
# -------------------------
# CONSULTAS
# -------------------------

@app.get("/consulta-pneu/{fogo}")
def consultar_pneu(fogo: str):
    conn = get_conn()

    pneu = conn.execute("""
        SELECT * FROM pneus WHERE fogo = ?
    """, (fogo,)).fetchone()

    if not pneu:
        conn.close()
        return {"erro": "Pneu não encontrado"}

    historico = conn.execute("""
        SELECT 
            m.*,
            v.placa
        FROM movimentacoes m
        LEFT JOIN veiculos v ON v.id = m.veiculo_id
        WHERE m.pneu_id = ?
        ORDER BY m.id DESC
    """, (pneu["id"],)).fetchall()

    km_total = conn.execute("""
        SELECT COALESCE(SUM(km_rodado), 0) AS km_total
        FROM movimentacoes
        WHERE pneu_id = ?
    """, (pneu["id"],)).fetchone()
    
    conn.close()
    
    historico_formatado = []

    for h in historico:
        item = dict(h)
        item["data_entrada"] = formatar_data_br(item.get("data_entrada"))
        item["data_saida"] = formatar_data_br(item.get("data_saida"))
        historico_formatado.append(item)

    pneu_dict = dict(pneu)
    pneu_dict["km_total"] = km_total["km_total"] if km_total else 0

    return {
        "pneu": pneu_dict,
        "historico": historico_formatado
    }


@app.get("/consulta-veiculo/{placa}")
def consultar_veiculo(placa: str):
    conn = get_conn()

    veiculo = conn.execute("""
        SELECT * FROM veiculos WHERE placa = ?
    """, (placa.upper(),)).fetchone()

    if not veiculo:
        conn.close()
        return {"erro": "Veículo não encontrado"}

    pneus = conn.execute("""
        SELECT
            m.posicao,
            m.km_entrada,
            m.data_entrada,
            p.fogo,
            p.medida,
            p.marca,
            p.modelo
        FROM movimentacoes m
        JOIN pneus p ON p.id = m.pneu_id
        WHERE m.veiculo_id = ?
        AND m.status_movimento = 'ABERTO'
        ORDER BY m.posicao
    """, (veiculo["id"],)).fetchall()

    conn.close()

    pneus_formatados = []

    for p in pneus:
        item = dict(p)
        item["data_entrada"] = formatar_data_br(item.get("data_entrada"))
        pneus_formatados.append(item)

    return {
        "veiculo": dict(veiculo),
        "pneus": pneus_formatados
    }

# -------------------------
# EXPORTAÇÃO EXCEL
# -------------------------

@app.get("/exportar-excel")
def exportar_excel():
    conn = get_conn()

    dados = conn.execute("""
        SELECT
            p.fogo,
            p.medida,
            p.marca,
            p.modelo,
            p.status,
            v.placa,
            m.posicao,
            m.data_entrada,
            m.km_entrada,
            m.data_saida,
            m.km_saida,
            m.km_rodado,
            m.motivo_saida,
            m.destino,
            m.status_movimento
        FROM movimentacoes m
        JOIN pneus p ON p.id = m.pneu_id
        LEFT JOIN veiculos v ON v.id = m.veiculo_id
        ORDER BY m.id DESC
    """).fetchall()

    conn.close()

    df = pd.DataFrame([dict(d) for d in dados])

    arquivo = "relatorio_pneus.xlsx"
    df.to_excel(arquivo, index=False)

    return FileResponse(
        arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=arquivo
    )

@app.get("/exportar-pneus-estoque")
def exportar_pneus_estoque():
    conn = get_conn()

    dados = conn.execute("""
        SELECT
            fogo,
            medida,
            marca,
            modelo,
            status,
            valor_compra,
            observacao
        FROM pneus
        WHERE status = 'ESTOQUE'
        ORDER BY fogo
    """).fetchall()

    conn.close()

    df = pd.DataFrame([dict(d) for d in dados])

    arquivo = "relatorio_pneus_estoque.xlsx"
    df.to_excel(arquivo, index=False)

    return FileResponse(
        arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=arquivo
    )


@app.get("/exportar-pneus-recapagem")
def exportar_pneus_recapagem():
    conn = get_conn()

    dados = conn.execute("""
        SELECT
            p.fogo,
            p.medida,
            p.marca,
            p.modelo,
            p.status,
            p.valor_compra,
            p.custos_adicionais,
            (
                SELECT MAX(COALESCE(m.data_saida, m.data_entrada))
                FROM movimentacoes m
                WHERE m.pneu_id = p.id
                AND (
                    m.destino = 'RECAPAGEM'
                    OR m.status_movimento = 'RECAPAGEM'
                )
            ) AS data_entrada_recapagem,
            p.observacao
        FROM pneus p
        WHERE p.status = 'RECAPAGEM'
        ORDER BY p.fogo
    """).fetchall()

    conn.close()

    df = pd.DataFrame([dict(d) for d in dados])

    if not df.empty and "data_entrada_recapagem" in df.columns:
        df["data_entrada_recapagem"] = df["data_entrada_recapagem"].apply(formatar_data_br_sem_hora)

    arquivo = "relatorio_pneus_recapagem.xlsx"
    df.to_excel(arquivo, index=False)

    return FileResponse(
        arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=arquivo
    )
    
@app.get("/exportar-custos-pneus")
def exportar_custos_pneus():
    conn = get_conn()

    dados = conn.execute("""
        SELECT
            p.fogo,
            p.medida,
            p.marca,
            p.modelo,
            p.status,
            COALESCE(p.valor_compra, 0) AS valor_compra,
            COALESCE(p.custos_adicionais, 0) AS custos_adicionais,
            COALESCE(p.valor_compra, 0) + COALESCE(p.custos_adicionais, 0) AS custo_total,
            COALESCE(SUM(m.km_rodado), 0) AS km_rodado_total,
            CASE
                WHEN COALESCE(SUM(m.km_rodado), 0) > 0
                THEN ROUND(
                    (COALESCE(p.valor_compra, 0) + COALESCE(p.custos_adicionais, 0)) 
                    / COALESCE(SUM(m.km_rodado), 0), 
                    4
                )
                ELSE 0
            END AS custo_por_km,
            p.observacao
        FROM pneus p
        LEFT JOIN movimentacoes m ON m.pneu_id = p.id
        GROUP BY
            p.id,
            p.fogo,
            p.medida,
            p.marca,
            p.modelo,
            p.status,
            p.valor_compra,
            p.custos_adicionais,
            p.observacao
        ORDER BY p.fogo
    """).fetchall()

    conn.close()

    df = pd.DataFrame([dict(d) for d in dados])

    arquivo = "relatorio_custos_pneus.xlsx"
    df.to_excel(arquivo, index=False)

    return FileResponse(
        arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=arquivo
    )

@app.get("/exportar-pneus-descartados")
def exportar_pneus_descartados():
    conn = get_conn()

    dados = conn.execute("""
        SELECT
            p.fogo,
            p.medida,
            p.marca,
            p.modelo,
            p.status,
            p.valor_compra,
            p.custos_adicionais,
            COALESCE(p.valor_compra, 0) + COALESCE(p.custos_adicionais, 0) AS custo_total,
            (
                SELECT MAX(COALESCE(m.data_saida, m.data_entrada))
                FROM movimentacoes m
                WHERE m.pneu_id = p.id
                AND (
                    m.destino = 'DESCARTE'
                    OR m.destino = 'DESCARTADO'
                    OR m.status_movimento = 'DESCARTADO'
                )
            ) AS data_entrada_descarte,
            p.observacao
        FROM pneus p
        WHERE p.status = 'DESCARTADO'
        ORDER BY p.fogo
    """).fetchall()

    conn.close()

    df = pd.DataFrame([dict(d) for d in dados])

    if not df.empty and "data_entrada_descarte" in df.columns:
        df["data_entrada_descarte"] = df["data_entrada_descarte"].apply(formatar_data_br_sem_hora)

    arquivo = "relatorio_pneus_descartados.xlsx"
    df.to_excel(arquivo, index=False)

    return FileResponse(
        arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=arquivo
    )
    
@app.get("/exportar-pneus-conserto")
def exportar_pneus_conserto():
    conn = get_conn()

    dados = conn.execute("""
        SELECT
            p.fogo,
            p.medida,
            p.marca,
            p.modelo,
            p.status,
            p.valor_compra,
            p.custos_adicionais,
            COALESCE(p.valor_compra, 0) + COALESCE(p.custos_adicionais, 0) AS custo_total,
            (
                SELECT MAX(COALESCE(m.data_saida, m.data_entrada))
                FROM movimentacoes m
                WHERE m.pneu_id = p.id
                AND (
                    m.destino = 'CONSERTO'
                    OR m.status_movimento = 'CONSERTO'
                )
            ) AS data_entrada_conserto,
            p.observacao
        FROM pneus p
        WHERE p.status = 'CONSERTO'
        ORDER BY p.fogo
    """).fetchall()

    conn.close()

    df = pd.DataFrame([dict(d) for d in dados])

    if not df.empty and "data_entrada_conserto" in df.columns:
        df["data_entrada_conserto"] = df["data_entrada_conserto"].apply(formatar_data_br_sem_hora)

    arquivo = "relatorio_pneus_conserto.xlsx"
    df.to_excel(arquivo, index=False)

    return FileResponse(
        arquivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=arquivo
    )
# -------------------------
# SERVIR FRONTEND REACT
# -------------------------

@app.get("/")
def servir_index():
    index_path = FRONTEND_DIST / "index.html"

    if index_path.exists():
        return FileResponse(index_path)

    return {"erro": "Frontend não encontrado. Rode npm run build."}

@app.get("/logo.png")
def servir_logo():
    logo_path = FRONTEND_DIST / "logo.png"

    if logo_path.exists():
        return FileResponse(logo_path)

    return {"erro": "Logo não encontrada."}

@app.get("/{full_path:path}")
def servir_react(full_path: str):
    index_path = FRONTEND_DIST / "index.html"

    if index_path.exists():
        return FileResponse(index_path)

    return {"erro": "Frontend não encontrado. Rode npm run build."}