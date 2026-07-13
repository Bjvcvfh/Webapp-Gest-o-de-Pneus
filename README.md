# Webapp Gestão de Pneus e Frota

Sistema web para controle operacional de pneus, veículos, movimentações, rodízios e relatórios de frota.

O projeto foi desenvolvido para organizar o ciclo de vida dos pneus dentro de uma operação de transporte: entrada em estoque, aplicação em veículos, controle por posição, acompanhamento de quilometragem, saída para recapagem/conserto/garantia/descarte e geração de relatórios.

## Problema Resolvido

Em operações com frota, o controle manual de pneus costuma gerar dificuldade para acompanhar:

- quais pneus estão em estoque, em uso, em recapagem, em conserto, em garantia ou descartados;
- em qual veículo e posição cada pneu está aplicado;
- histórico de movimentações por número de fogo;
- quilometragem rodada por pneu;
- custos de compra, recapagem e manutenção;
- relatórios para tomada de decisão.

Este sistema centraliza essas informações e aplica validações para reduzir erros operacionais.

## Principais Funcionalidades

- Login de usuários com perfis de acesso.
- Cadastro de pneus por número de fogo.
- Cadastro de veículos por placa, modelo, tipo e KM atual.
- Lançamento de pneus em veículos e posições específicas.
- Validação de posições permitidas por tipo de eixo.
- Controle de KM de entrada e saída.
- Validação histórica para evitar inconsistência de quilometragem.
- Registro de saída de pneu para estoque, recapagem, conserto, garantia ou descarte.
- Alteração de status com registro de observação e custo adicional.
- Rodízio de pneus entre posições.
- Consulta detalhada por pneu.
- Consulta detalhada por veículo.
- Histórico de movimentações.
- Exportação de relatórios em Excel.
- Controle de permissões por perfil: ADM, UTILIZADOR e GESTAO.

## Tecnologias Utilizadas

### Frontend

- React
- Vite
- JavaScript
- HTML
- CSS

### Backend

- Python
- FastAPI
- Pydantic
- SQLite
- Pandas
- OpenPyXL
- Uvicorn

## Arquitetura

```txt
Webapp-Gest-o-de-Pneus/
├─ backend/
│  ├─ main.py              # API FastAPI e regras de negócio
│  ├─ database.py          # conexão SQLite e criação das tabelas principais
│  ├─ requirements.txt     # dependências Python
│  └─ data/                # banco SQLite local, não versionado
│
└─ frontend/
   ├─ src/
   │  ├─ App.jsx           # interface principal e fluxos do sistema
   │  └─ App.css           # estilos da aplicação
   ├─ public/
   ├─ package.json
   └─ vite.config.js
```

## Regras de Negócio Implementadas

O backend possui validações para manter a consistência operacional:

- impede cadastro duplicado de pneus por número de fogo;
- impede cadastro duplicado de veículos por placa;
- bloqueia lançamento de pneu descartado, em recapagem, em conserto ou em garantia;
- impede lançar pneu em posição já ocupada;
- impede lançar o mesmo pneu em dois veículos ao mesmo tempo;
- valida se a posição informada é permitida;
- valida KM negativo;
- impede KM menor que o histórico do veículo, exceto em movimentações antigas marcadas;
- calcula KM rodado na saída do pneu;
- atualiza automaticamente o status do pneu conforme o destino;
- registra movimentações de recapagem, conserto, garantia, descarte e rodízio;
- calcula custo por KM nos relatórios.

## Perfis de Acesso

| Perfil | Permissões principais |
| --- | --- |
| ADM | Acesso completo, incluindo cadastro de usuários |
| UTILIZADOR | Operação diária: lançamentos, saídas, rodízios, consultas e relatórios |
| GESTAO | Consultas e relatórios |

## Relatórios

O sistema exporta relatórios em Excel para apoiar a gestão da frota:

- relatório geral de pneus;
- pneus em estoque;
- pneus em recapagem;
- pneus em conserto;
- pneus descartados;
- custos de pneus;
- custo por KM rodado.

## Como Rodar Localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/Bjvcvfh/Webapp-Gest-o-de-Pneus.git
cd Webapp-Gest-o-de-Pneus
```

### 2. Rodar o backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Por padrão, a API fica disponível em:

```txt
http://localhost:8000
```

### 3. Rodar o frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Por padrão, o frontend fica disponível em:

```txt
http://localhost:5173
```

## Build de Produção

O frontend pode ser compilado e servido pelo backend FastAPI:

```bash
cd frontend
npm install
npm run build
```

Depois, suba o backend:

```bash
cd ../backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Se a pasta `frontend/dist` existir, o backend serve a interface React junto com a API.

## Observações

- O banco SQLite local fica em `backend/data/pneus.db`.
- Arquivos de banco, backups e relatórios gerados não devem ser versionados.
- Em uma instalação nova, crie/preparare o usuário inicial de acesso antes do primeiro login.
- O projeto foi pensado para uso operacional interno e pode ser evoluído para deploy em servidor, Docker ou banco relacional externo.

## Diferenciais Técnicos

Este projeto demonstra:

- construção de API REST com FastAPI;
- integração entre frontend React e backend Python;
- modelagem de dados com SQLite;
- regras de negócio aplicadas no backend;
- validações de consistência operacional;
- geração de relatórios em Excel;
- controle de permissões por perfil;
- organização de um sistema real para gestão de frota.

## Autor

Desenvolvido por Renan Ceolim Ramos.

GitHub: [Bjvcvfh](https://github.com/Bjvcvfh)
