import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "";

const POSICOES_PERMITIDAS = [
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
];

function dataHojeBR() {
  const hoje = new Date();
  const dia = String(hoje.getDate()).padStart(2, "0");
  const mes = String(hoje.getMonth() + 1).padStart(2, "0");
  const ano = hoje.getFullYear();

  return `${dia}/${mes}/${ano}`;
}

export default function App() {
  const [tela, setTela] = useState("dashboard");

  const [usuarioLogado, setUsuarioLogado] = useState(() => {
    const salvo = localStorage.getItem("usuarioLogado");
    return salvo ? JSON.parse(salvo) : null;
  });

  const [formLogin, setFormLogin] = useState({
    usuario: "",
    senha: "",
  });

  const [pneus, setPneus] = useState([]);
  const [veiculos, setVeiculos] = useState([]);

  const [formPneu, setFormPneu] = useState({
    fogo: "",
    medida: "",
    marca: "",
    modelo: "",
    valor_compra: "",
    observacao: "",
  });

  const [formVeiculo, setFormVeiculo] = useState({
    placa: "",
    modelo: "",
    tipo: "",
    km_atual: "",
  });

  const [formLancamento, setFormLancamento] = useState({
    fogo: "",
    placa: "",
    posicao: "",
    km_entrada: "",
    data_movimento: new Date().toISOString().slice(0, 10),
    movimentacao_antiga: false,
    observacao: "",
  });

  const [formSaida, setFormSaida] = useState({
    fogo: "",
    km_saida: "",
    destino: "",
    data_movimento: new Date().toISOString().slice(0, 10),
    observacao: "",
  });

  const [formStatus, setFormStatus] = useState({
    fogo: "",
    novo_status: "",
    data_movimento: new Date().toISOString().slice(0, 10),
    observacao: "",
    custo_adicional: "",
  });

  const pneuStatusSelecionado = pneus.find(
    (p) => String(p.fogo).toUpperCase() === formStatus.fogo.toUpperCase()
  );

  const mostrarCustoAdicional =
    pneuStatusSelecionado?.status === "RECAPAGEM" ||
    pneuStatusSelecionado?.status === "CONSERTO";
    
  const [buscaFogo, setBuscaFogo] = useState("");
  const [resultadoPneu, setResultadoPneu] = useState(null);

  const [buscaPlaca, setBuscaPlaca] = useState("");
  const [resultadoVeiculo, setResultadoVeiculo] = useState(null);

  const [usuarios, setUsuarios] = useState([]);

  const [formUsuario, setFormUsuario] = useState({
    usuario: "",
    senha: "",
    perfil: "",
  });

  const [modoRodizio, setModoRodizio] = useState("alterarPosicao");

  const [formAlterarPosicao, setFormAlterarPosicao] = useState({
    fogo: "",
    nova_posicao: "",
    km_movimento: "",
    data_movimento: dataHojeBR(),
    movimentacao_antiga: false,
    observacao: "",
  });

  const [formRodizio, setFormRodizio] = useState({
    fogo_1: "",
    fogo_2: "",
    km_movimento: "",
    data_movimento: dataHojeBR(),
    movimentacao_antiga: false,
    observacao: "",
  });

  async function fazerLogin(e) {
    e.preventDefault();

    const resp = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formLogin),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      alert(dados.detail || "Erro ao fazer login.");
      return;
    }

    const usuario = {
      usuario: dados.usuario,
      perfil: dados.perfil,
    };

    localStorage.setItem("usuarioLogado", JSON.stringify(usuario));
    setUsuarioLogado(usuario);

    setFormLogin({
      usuario: "",
      senha: "",
    });
  }

  function sair() {
    localStorage.removeItem("usuarioLogado");
    setUsuarioLogado(null);
    setTela("dashboard");
  }

  function podeAcessar(telaNome) {
    if (!usuarioLogado) return false;

    const perfil = usuarioLogado.perfil;

    const permissoes = {
      ADM: [
        "dashboard",
        "pneus",
        "veiculos",
        "lancamento",
        "saidaPneu",
        "alterarStatus",
        "rodizio",
        "consultaPneu",
        "consultaVeiculo",
        "relatorios",
        "usuarios"
      ],
      UTILIZADOR: [
        "dashboard",
        "lancamento",
        "saidaPneu",
        "alterarStatus",
        "rodizio",
        "consultaPneu",
        "consultaVeiculo",
        "relatorios",
      ],
      GESTAO: [
        "dashboard",
        "consultaPneu",
        "consultaVeiculo",
        "relatorios",
      ],
    };

    return permissoes[perfil]?.includes(telaNome);
  }

  async function carregarDados() {
    const pneusResp = await fetch(`${API_URL}/pneus`);
    const veiculosResp = await fetch(`${API_URL}/veiculos`);

    setPneus(await pneusResp.json());
    setVeiculos(await veiculosResp.json());

    if (usuarioLogado?.perfil === "ADM") {
      const usuariosResp = await fetch(`${API_URL}/usuarios`);
      setUsuarios(await usuariosResp.json());
    }
  }

  useEffect(() => {
    carregarDados();
  }, []);

  async function cadastrarUsuario(e) {
    e.preventDefault();

    const resp = await fetch(`${API_URL}/usuarios`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formUsuario),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      alert(dados.detail || "Erro ao cadastrar usuário.");
      return;
    }

    setFormUsuario({
      usuario: "",
      senha: "",
      perfil: "",
    });

    carregarDados();

    alert(dados.mensagem || "Usuário cadastrado com sucesso.");
  }

  async function cadastrarPneu(e) {
    e.preventDefault();

    const resp = await fetch(`${API_URL}/pneus`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...formPneu,
        valor_compra: Number(formPneu.valor_compra || 0),
      }),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      alert(dados.detail || "Erro ao cadastrar pneu.");
      return;
    }

    setFormPneu({
      fogo: "",
      medida: "",
      marca: "",
      modelo: "",
      valor_compra: "",
      observacao: "",
    });

    carregarDados();
    alert(dados.mensagem || "Pneu cadastrado com sucesso!");
  }

  async function cadastrarVeiculo(e) {
    e.preventDefault();

    const resp = await fetch(`${API_URL}/veiculos`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...formVeiculo,
        placa: formVeiculo.placa.toUpperCase().trim(),
        modelo: formVeiculo.modelo.toUpperCase().trim(),
        tipo: formVeiculo.tipo.toUpperCase().trim(),
        km_atual: Number(formVeiculo.km_atual || 0),
      }),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      alert(dados.detail || "Erro ao cadastrar veículo.");
      return;
    }

    setFormVeiculo({
      placa: "",
      modelo: "",
      tipo: "",
      km_atual: "",
    });

    carregarDados();
    alert(dados.mensagem || "Veículo cadastrado com sucesso!");
  }

  async function lancarPneu(e) {
    e.preventDefault();

    const pneuSelecionado = pneus.find(
      (p) => String(p.fogo).toUpperCase() === formLancamento.fogo.toUpperCase()
    );

    if (!pneuSelecionado) {
      alert("Pneu não encontrado. Verifique o número de fogo digitado.");
      return;
    }

    const veiculoSelecionado = veiculos.find(
      (v) => String(v.placa).toUpperCase() === formLancamento.placa.toUpperCase()
    );

    if (!veiculoSelecionado) {
      alert("Veículo não encontrado. Verifique a placa digitada.");
      return;
    }
    
    const posicaoDigitada = formLancamento.posicao.toUpperCase().trim();

    if (!POSICOES_PERMITIDAS.includes(posicaoDigitada)) {
      alert(
        `Posição inválida. Use uma destas opções: ${POSICOES_PERMITIDAS.join(", ")}`
      );
      return;
    }

    const resp = await fetch(`${API_URL}/lancamentos`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        pneu_id: Number(pneuSelecionado.id),
        veiculo_id: Number(veiculoSelecionado.id),
        posicao: posicaoDigitada,
        km_entrada: Number(formLancamento.km_entrada),
        data_movimento: formLancamento.data_movimento,
        movimentacao_antiga: formLancamento.movimentacao_antiga,
        observacao: formLancamento.observacao,
      }),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      alert(dados.detail || "Erro ao lançar pneu.");
      return;
    }

    setFormLancamento({
      fogo: "",
      placa: "",
      posicao: "",
      km_entrada: "",
      data_movimento: new Date().toISOString().slice(0, 10),
      movimentacao_antiga: false,
      observacao: "",
    });

    carregarDados();
    alert(dados.mensagem || "Pneu lançado com sucesso!");
  }

  async function registrarSaidaPneu(e) {
    e.preventDefault();

    const pneuSelecionado = pneus.find(
      (p) => String(p.fogo).toUpperCase() === formSaida.fogo.toUpperCase()
    );

    if (!pneuSelecionado) {
      alert("Pneu não encontrado. Verifique o número de fogo digitado.");
      return;
    }

    const resp = await fetch(`${API_URL}/saida-pneu`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        pneu_id: Number(pneuSelecionado.id),
        km_saida: Number(formSaida.km_saida),
        destino: formSaida.destino,
        data_movimento: formSaida.data_movimento,
        observacao: formSaida.observacao,
      }),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      alert(dados.detail || "Erro ao registrar saída.");
      return;
    }

    setFormSaida({
      fogo: "",
      km_saida: "",
      destino: "",
      data_movimento: new Date().toISOString().slice(0, 10),
      observacao: "",
    });

    carregarDados();

    alert(
      `${dados.mensagem}\nKM rodado: ${dados.km_rodado}\nNovo status: ${dados.novo_status}`
    );
  }

  async function alterarStatusPneu(e) {
    e.preventDefault();

    const pneuSelecionado = pneus.find(
      (p) => String(p.fogo).toUpperCase() === formStatus.fogo.toUpperCase()
    );

    if (!pneuSelecionado) {
      alert("Pneu não encontrado. Verifique o número de fogo digitado.");
      return;
    }

    const resp = await fetch(`${API_URL}/alterar-status-pneu`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        pneu_id: Number(pneuSelecionado.id),
        novo_status: formStatus.novo_status,
        data_movimento: formStatus.data_movimento,
        observacao: formStatus.observacao,
        custo_adicional: Number(formStatus.custo_adicional || 0),
      }),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      alert(dados.detail || "Erro ao alterar status.");
      return;
    }

    setFormStatus({
      fogo: "",
      novo_status: "",
      data_movimento: new Date().toISOString().slice(0, 10),
      observacao: "",
      custo_adicional: "",
    });

    carregarDados();

    alert(`${dados.mensagem}\nNovo status: ${dados.novo_status}`);
  }

  async function consultarPneu(e) {
    e.preventDefault();

    const resp = await fetch(`${API_URL}/consulta-pneu/${buscaFogo}`);
    const dados = await resp.json();

    setResultadoPneu(dados);
  }

  async function consultarPneu(e) {
    e.preventDefault();

    const resp = await fetch(`${API_URL}/consulta-pneu/${buscaFogo}`);
    const dados = await resp.json();

    setResultadoPneu(dados);
  }

  async function consultarVeiculo(e) {
    e.preventDefault();

    const resp = await fetch(`${API_URL}/consulta-veiculo/${buscaPlaca}`);
    const dados = await resp.json();

    setResultadoVeiculo(dados);
  }

  async function alterarPosicaoPneu(e) {
  e.preventDefault();

  const resp = await fetch(`${API_URL}/alterar-posicao-pneu`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      fogo: formAlterarPosicao.fogo,
      nova_posicao: formAlterarPosicao.nova_posicao,
      km_movimento: Number(formAlterarPosicao.km_movimento),
      data_movimento: formAlterarPosicao.data_movimento,
      movimentacao_antiga: formAlterarPosicao.movimentacao_antiga,
      observacao: formAlterarPosicao.observacao,
    }),
  });

  const dados = await resp.json();

  if (!resp.ok) {
    alert(dados.detail || "Erro ao alterar posição.");
    return;
  }

  setFormAlterarPosicao({
    fogo: "",
    nova_posicao: "",
    km_movimento: "",
    data_movimento: dataHojeBR(),
    movimentacao_antiga: false,
    observacao: "",
  });

  carregarDados();

  alert(
    `${dados.mensagem}\n${dados.fogo}: ${dados.posicao_anterior} → ${dados.nova_posicao}`
  );
}


  async function realizarRodizio(e) {
    e.preventDefault();

    const resp = await fetch(`${API_URL}/rodizio-pneus`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        fogo_1: formRodizio.fogo_1,
        fogo_2: formRodizio.fogo_2,
        km_movimento: Number(formRodizio.km_movimento),
        data_movimento: formRodizio.data_movimento,
        movimentacao_antiga: formRodizio.movimentacao_antiga,
        observacao: formRodizio.observacao,
      }),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      alert(dados.detail || "Erro ao realizar rodízio.");
      return;
    }

    setFormRodizio({
      fogo_1: "",
      fogo_2: "",
      km_movimento: "",
      data_movimento: dataHojeBR(),
      movimentacao_antiga: false,
      observacao: "",
    });

    carregarDados();

    alert(
      `${dados.mensagem}\n` +
        `${dados.pneu_1}: ${dados.pneu_1_posicao_anterior} → ${dados.pneu_1_nova_posicao}\n` +
        `${dados.pneu_2}: ${dados.pneu_2_posicao_anterior} → ${dados.pneu_2_nova_posicao}`
    );
  }

  function exportarExcel() {
    window.open(`${API_URL}/exportar-excel`, "_blank");
  }

  function exportarPneusEstoque() {
    window.open(`${API_URL}/exportar-pneus-estoque`, "_blank");
  }

  function exportarPneusRecapagem() {
    window.open(`${API_URL}/exportar-pneus-recapagem`, "_blank");
  }

  function exportarCustosPneus() {
    window.open(`${API_URL}/exportar-custos-pneus`, "_blank");
  }

  function exportarPneusDescartados() {
    window.open(`${API_URL}/exportar-pneus-descartados`, "_blank");
  }

  function exportarPneusConserto() {
    window.open(`${API_URL}/exportar-pneus-conserto`, "_blank");
  }

  if (!usuarioLogado) {
    return (
      <div className="login-page">
        <form onSubmit={fazerLogin} className="login-card">
          <div className="logo-login">
            <img src="/logo.png" alt="Transvarzea" />
          </div>
          <h1>Controle de Pneus</h1>
          <p>Entre com seu usuário e senha</p>

          <input
            placeholder="Usuário"
            value={formLogin.usuario}
            onChange={(e) =>
              setFormLogin({
                ...formLogin,
                usuario: e.target.value.toLowerCase(),
              })
            }
            required
          />

          <input
            placeholder="Senha"
            type="password"
            value={formLogin.senha}
            onChange={(e) =>
              setFormLogin({
                ...formLogin,
                senha: e.target.value,
              })
            }
            required
          />

          <button type="submit">Entrar</button>
        </form>
      </div>
    );
  }

  return (
    <div className="app">
      <aside className="menu">
        <div className="logo-menu">
          <img src="/logo.png" alt="Transvarzea" />
        </div>

        <h2>Controle de Pneus</h2>

        <div className="usuario-box">
          <strong>{usuarioLogado.usuario}</strong>
          <span>{usuarioLogado.perfil}</span>
        </div>

        {podeAcessar("dashboard") && (
          <button onClick={() => setTela("dashboard")}>Início</button>
        )}

        {podeAcessar("pneus") && (
          <button onClick={() => setTela("pneus")}>Pneus</button>
        )}

        {podeAcessar("veiculos") && (
          <button onClick={() => setTela("veiculos")}>Veículos</button>
        )}

        {podeAcessar("lancamento") && (
          <button onClick={() => setTela("lancamento")}>Lançar Pneu</button>
        )}

        {podeAcessar("saidaPneu") && (
          <button onClick={() => setTela("saidaPneu")}>Saída de Pneu</button>
        )}

        {podeAcessar("alterarStatus") && (
          <button onClick={() => setTela("alterarStatus")}>Alterar Status</button>
        )}

        {podeAcessar("rodizio") && (
          <button onClick={() => setTela("rodizio")}>Rodízio</button>
        )}

        {podeAcessar("consultaPneu") && (
          <button onClick={() => setTela("consultaPneu")}>Consultar Pneu</button>
        )}

        {podeAcessar("consultaVeiculo") && (
          <button onClick={() => setTela("consultaVeiculo")}>Consultar Veículo</button>
        )}

        {podeAcessar("relatorios") && (
          <button onClick={() => setTela("relatorios")}>Relatórios</button>
        )}

        {podeAcessar("usuarios") && (
          <button onClick={() => setTela("usuarios")}>Usuários</button>
        )}

        <button onClick={sair} className="botao-sair">
          Sair
        </button>
      </aside>

      <main className="conteudo">
        {!podeAcessar(tela) && (
          <section>
            <h1>Acesso negado</h1>
            <p>Seu perfil não tem permissão para acessar esta tela.</p>
          </section>
        )}
        
        {tela === "dashboard" && podeAcessar("dashboard") && (
          <section>
            <h1>Dashboard</h1>

            <div className="cards">
              <div className="card">
                <span>Total de Pneus</span>
                <strong>{pneus.length}</strong>
              </div>

              <div className="card">
                <span>Total de Veículos</span>
                <strong>{veiculos.length}</strong>
              </div>

              <div className="card">
                <span>Pneus em Uso</span>
                <strong>
                  {pneus.filter((p) => p.status === "EM USO").length}
                </strong>
              </div>

              <div className="card">
                <span>Pneus em Estoque</span>
                <strong>
                  {pneus.filter((p) => p.status === "ESTOQUE").length}
                </strong>
              </div>
              <div className="card">
                <span>Pneus em Recapagem</span>
                <strong>
                  {pneus.filter((p) => p.status === "RECAPAGEM").length}
                </strong>
              </div>
              <div className="card">
                <span>Pneus em Conserto</span>
                <strong>
                  {pneus.filter((p) => p.status === "CONSERTO").length}
                </strong>
              </div>
              <div className="card">
                <span>Pneus Descartados</span>
                <strong>
                  {pneus.filter((p) => p.status === "DESCARTADO").length}
                </strong>
              </div>
            </div>
          </section>
        )}

        {tela === "pneus" && podeAcessar("pneus") && (
          <section>
            <h1>Cadastro de Pneus</h1>

            <form onSubmit={cadastrarPneu} className="form">
              <input
                placeholder="Número de fogo"
                value={formPneu.fogo}
                onChange={(e) =>
                  setFormPneu({ ...formPneu, fogo: e.target.value })
                }
                required
              />

              <input
                placeholder="Medida"
                value={formPneu.medida}
                onChange={(e) =>
                  setFormPneu({ ...formPneu, medida: e.target.value })
                }
              />

              <input
                placeholder="Marca"
                value={formPneu.marca}
                onChange={(e) =>
                  setFormPneu({ ...formPneu, marca: e.target.value })
                }
              />

              <input
                placeholder="Modelo"
                value={formPneu.modelo}
                onChange={(e) =>
                  setFormPneu({ ...formPneu, modelo: e.target.value })
                }
              />

              <input
                placeholder="Valor de compra"
                type="number"
                value={formPneu.valor_compra}
                onChange={(e) =>
                  setFormPneu({ ...formPneu, valor_compra: e.target.value })
                }
              />

              <input
                placeholder="Observação"
                value={formPneu.observacao}
                onChange={(e) =>
                  setFormPneu({ ...formPneu, observacao: e.target.value })
                }
              />

              <button type="submit">Cadastrar Pneu</button>
            </form>

            <TabelaPneus pneus={pneus} />
          </section>
        )}
        
        {tela === "saidaPneu" && podeAcessar("saidaPneu") && (
          <section>
            <h1>Saída de Pneu</h1>

            <form onSubmit={registrarSaidaPneu} className="form">
              <input
                list="lista-pneus-em-uso"
                placeholder="Digite o número de fogo"
                value={formSaida.fogo}
                onChange={(e) =>
                  setFormSaida({
                    ...formSaida,
                    fogo: e.target.value,
                  })
                }
                required
              />

              <datalist id="lista-pneus-em-uso">
                {pneus
                  .filter((pneu) => pneu.status === "EM USO")
                  .map((pneu) => (
                    <option key={pneu.id} value={pneu.fogo}>
                      {pneu.fogo} - {pneu.marca} {pneu.modelo}
                    </option>
                  ))}
              </datalist>

              <input
                placeholder="KM de saída"
                type="number"
                value={formSaida.km_saida}
                onChange={(e) =>
                  setFormSaida({
                    ...formSaida,
                    km_saida: e.target.value,
                  })
                }
                required
              />

              <select
                value={formSaida.destino}
                onChange={(e) =>
                  setFormSaida({
                    ...formSaida,
                    destino: e.target.value,
                  })
                }
                required
              >

              <input
                type="date"
                value={formSaida.data_movimento}
                onChange={(e) =>
                  setFormSaida({
                    ...formSaida,
                    data_movimento: e.target.value,
                  })
                }
                required
              />  

                <option value="">Destino</option>
                <option value="ESTOQUE">Estoque</option>
                <option value="GARANTIA">Garantia</option>
                <option value="RECAPAGEM">Recapagem</option>
                <option value="CONSERTO">Conserto</option>
                <option value="DESCARTE">Descarte</option>
              </select>

              {formSaida.destino === "RECAPAGEM" ? (
                <select
                  value={formSaida.observacao}
                  onChange={(e) =>
                    setFormSaida({
                      ...formSaida,
                      observacao: e.target.value,
                    })
                  }
                  required
                >
                  <option value="">Selecione a recapadora</option>
                  <option value="SANTA CRUZ">SANTA CRUZ</option>
                  <option value="VOLPE">VOLPE</option>
                  <option value="NILCAP">NILCAP</option>
                  <option value="FM PNEUS">FM PNEUS</option>
                </select>
              ) : formSaida.destino === "CONSERTO" ? (
                <select
                  value={formSaida.observacao}
                  onChange={(e) =>
                    setFormSaida({
                      ...formSaida,
                      observacao: e.target.value,
                    })
                  }
                  required
                >
                  <option value="">Selecione o local do conserto</option>
                  <option value="INTERNO">INTERNO</option>
                  <option value="FAM PNEUS">FAM PNEUS</option>
                </select>
              ) : (
                <input
                  placeholder="Observação"
                  value={formSaida.observacao}
                  onChange={(e) =>
                    setFormSaida({
                      ...formSaida,
                      observacao: e.target.value,
                    })
                  }
                />
              )}

              <button type="submit">Registrar Saída</button>
            </form>
          </section>
        )}

        {tela === "veiculos" && podeAcessar("veiculos") && (
          <section>
            <h1>Cadastro de Veículos</h1>

            <form onSubmit={cadastrarVeiculo} className="form">
              <input
                placeholder="Placa"
                value={formVeiculo.placa}
                onChange={(e) =>
                  setFormVeiculo({
                    ...formVeiculo,
                    placa: e.target.value.toUpperCase(),
                  })
                }
                required
              />

              <input
                placeholder="Modelo"
                value={formVeiculo.modelo}
                onChange={(e) =>
                  setFormVeiculo({ ...formVeiculo, modelo: e.target.value })
                }
              />

              <input
                placeholder="Tipo"
                value={formVeiculo.tipo}
                onChange={(e) =>
                  setFormVeiculo({ ...formVeiculo, tipo: e.target.value })
                }
              />

              <input
                placeholder="KM atual"
                type="number"
                value={formVeiculo.km_atual}
                onChange={(e) =>
                  setFormVeiculo({ ...formVeiculo, km_atual: e.target.value })
                }
              />

              <button type="submit">Cadastrar Veículo</button>
            </form>

            <TabelaVeiculos veiculos={veiculos} />
          </section>
        )}

        {tela === "lancamento" && podeAcessar("lancamento") && (
          <section>
            <h1>Lançar Pneu em Veículo</h1>

            <form onSubmit={lancarPneu} className="form">
              <input
                list="lista-pneus"
                placeholder="Digite o número de fogo"
                value={formLancamento.fogo}
                onChange={(e) =>
                  setFormLancamento({
                    ...formLancamento,
                    fogo: e.target.value,
                  })
                }
                required
              />

              <datalist id="lista-pneus">
                {pneus.map((pneu) => (
                  <option key={pneu.id} value={pneu.fogo}>
                    {pneu.fogo} - {pneu.marca} {pneu.modelo} - {pneu.status}
                  </option>
                ))}
              </datalist>

              <input
                list="lista-veiculos"
                placeholder="Digite a placa"
                value={formLancamento.placa}
                onChange={(e) =>
                  setFormLancamento({
                    ...formLancamento,
                    placa: e.target.value.toUpperCase(),
                  })
                }
                required
              />

              <datalist id="lista-veiculos">
                {veiculos.map((veiculo) => (
                  <option key={veiculo.id} value={veiculo.placa}>
                    {veiculo.placa} - {veiculo.modelo}
                  </option>
                ))}
              </datalist>

              <input
                list="lista-posicoes"
                placeholder="Digite a posição"
                value={formLancamento.posicao}
                onChange={(e) =>
                  setFormLancamento({
                    ...formLancamento,
                    posicao: e.target.value.toUpperCase(),
                  })
                }
                required
              />

              <datalist id="lista-posicoes">
                {POSICOES_PERMITIDAS.map((posicao) => (
                  <option key={posicao} value={posicao} />
                ))}
              </datalist>

              <input
                placeholder="KM de entrada"
                type="number"
                value={formLancamento.km_entrada}
                onChange={(e) =>
                  setFormLancamento({
                    ...formLancamento,
                    km_entrada: e.target.value,
                  })
                }
                required
              />

              <input
                type="date"
                value={formLancamento.data_movimento}
                onChange={(e) =>
                  setFormLancamento({
                    ...formLancamento,
                    data_movimento: e.target.value,
                  })
                }
                required
              />

              <input
                placeholder="Observação"
                value={formLancamento.observacao}
                onChange={(e) =>
                  setFormLancamento({
                    ...formLancamento,
                    observacao: e.target.value,
                  })
                }
              />
              <label className="checkbox-linha">
                <input
                  type="checkbox"
                  checked={formLancamento.movimentacao_antiga}
                  onChange={(e) =>
                    setFormLancamento({
                      ...formLancamento,
                      movimentacao_antiga: e.target.checked,
                    })
                  }
                />
                Movimentação antiga: permitir KM menor que o atual da placa
              </label>
              <button type="submit">Lançar Pneu</button>
            </form>
          </section>
        )}

        {tela === "consultaPneu" && podeAcessar("consultaPneu") && (
          <section>
            <h1>Consulta por Número de Fogo</h1>

            <form onSubmit={consultarPneu} className="form linha">
              <input
                list="lista-pneus-consulta"
                placeholder="Digite o número de fogo"
                value={buscaFogo}
                onChange={(e) => setBuscaFogo(e.target.value)}
                required
              />

              <datalist id="lista-pneus-consulta">
                {pneus.map((pneu) => (
                  <option key={pneu.id} value={pneu.fogo}>
                    {pneu.fogo} - {pneu.marca} {pneu.modelo} - {pneu.status}
                  </option>
                ))}
              </datalist>

              <button type="submit">Buscar</button>
            </form>

            {resultadoPneu?.erro && <p className="erro">{resultadoPneu.erro}</p>}

            {resultadoPneu?.pneu && (
              <div>
                <h2>
                  Pneu {resultadoPneu.pneu.fogo} - {resultadoPneu.pneu.marca}{" "}
                  {resultadoPneu.pneu.modelo}
                </h2>

                <p>Status: {resultadoPneu.pneu.status}</p>
                <p>Medida: {resultadoPneu.pneu.medida}</p>
                <p>
                  KM total rodado:{" "}
                  {Number(resultadoPneu.pneu.km_total || 0).toLocaleString("pt-BR")}
                </p>
                
                <h3>Histórico</h3>

                <table>
                  <thead>
                    <tr>
                      <th>Placa</th>
                      <th>Posição</th>
                      <th>Entrada</th>
                      <th>KM Entrada</th>
                      <th>Saída</th>
                      <th>KM Saída</th>
                      <th>KM Rodado</th>
                      <th>Status</th>
                    </tr>
                  </thead>

                  <tbody>
                    {resultadoPneu.historico.map((h) => (
                      <tr key={h.id}>
                        <td>{h.placa || "-"}</td>
                        <td>{h.posicao || "-"}</td>
                        <td>{h.data_entrada}</td>
                        <td>{h.km_entrada}</td>
                        <td>{h.data_saida || "-"}</td>
                        <td>{h.km_saida || "-"}</td>
                        <td>{h.km_rodado || "-"}</td>
                        <td>{h.status_movimento}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}

        {tela === "consultaVeiculo" && podeAcessar("consultaVeiculo") && (
          <section>
            <h1>Consulta por Veículo</h1>

            <form onSubmit={consultarVeiculo} className="form linha">
              <input
              list="lista-veiculos-consulta"
              placeholder="Digite a placa"
              value={buscaPlaca}
              onChange={(e) => setBuscaPlaca(e.target.value.toUpperCase())}
              required
            />

            <datalist id="lista-veiculos-consulta">
              {veiculos.map((veiculo) => (
                <option key={veiculo.id} value={veiculo.placa}>
                  {veiculo.placa} - {veiculo.modelo}
                </option>
              ))}
            </datalist>

              <button type="submit">Buscar</button>
            </form>

            {resultadoVeiculo?.erro && (
              <p className="erro">{resultadoVeiculo.erro}</p>
            )}

            {resultadoVeiculo?.veiculo && (
              <div>
                <h2>Veículo {resultadoVeiculo.veiculo.placa}</h2>

                <p>Modelo: {resultadoVeiculo.veiculo.modelo}</p>
                <p>KM atual: {resultadoVeiculo.veiculo.km_atual}</p>

                <h3>Pneus montados</h3>

                <table>
                  <thead>
                    <tr>
                      <th>Posição</th>
                      <th>Fogo</th>
                      <th>Medida</th>
                      <th>Marca</th>
                      <th>Modelo</th>
                      <th>KM Entrada</th>
                      <th>Data Aplicação</th>
                    </tr>
                  </thead>

                  <tbody>
                    {resultadoVeiculo.pneus.map((p, index) => (
                      <tr key={index}>
                        <td>{p.posicao}</td>
                        <td>{p.fogo}</td>
                        <td>{p.medida}</td>
                        <td>{p.marca}</td>
                        <td>{p.modelo}</td>
                        <td>{p.km_entrada}</td>
                        <td>{p.data_entrada ? p.data_entrada.split(" ")[0] : "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}

        {tela === "alterarStatus" && podeAcessar("alterarStatus") && (
          <section>
            <h1>Alterar Status do Pneu</h1>

            <form onSubmit={alterarStatusPneu} className="form">
              <input
                list="lista-pneus-status"
                placeholder="Digite o número de fogo"
                value={formStatus.fogo}
                onChange={(e) =>
                  setFormStatus({
                    ...formStatus,
                    fogo: e.target.value,
                  })
                }
                required
              />

              <datalist id="lista-pneus-status">
                {pneus.map((pneu) => (
                  <option key={pneu.id} value={pneu.fogo}>
                    {pneu.fogo} - {pneu.marca} {pneu.modelo} - {pneu.status}
                  </option>
                ))}
              </datalist>

              <select
                value={formStatus.novo_status}
                onChange={(e) =>
                  setFormStatus({
                    ...formStatus,
                    novo_status: e.target.value,
                  })
                }
                required
              >
                <option value="">Novo status</option>
                <option value="ESTOQUE">Estoque</option>
                <option value="GARANTIA">Garantia</option>
                <option value="RECAPAGEM">Recapagem</option>
                <option value="CONSERTO">Conserto</option>
                <option value="DESCARTADO">Descartado</option>
              </select>
              
              {mostrarCustoAdicional && (
                <input
                  placeholder="Custo adicional"
                  type="number"
                  step="0.01"
                  value={formStatus.custo_adicional}
                  onChange={(e) =>
                    setFormStatus({
                      ...formStatus,
                      custo_adicional: e.target.value,
                    })
                  }
                />
              )}

              <input
                type="date"
                value={formStatus.data_movimento}
                onChange={(e) =>
                  setFormStatus({
                    ...formStatus,
                    data_movimento: e.target.value,
                  })
                }
                required
              />

              {formStatus.novo_status === "RECAPAGEM" ? (
                <select
                  value={formStatus.observacao}
                  onChange={(e) =>
                    setFormStatus({
                      ...formStatus,
                      observacao: e.target.value,
                    })
                  }
                  required
                >
                  <option value="">Selecione a recapadora</option>
                  <option value="SANTA CRUZ">SANTA CRUZ</option>
                  <option value="VOLPE">VOLPE</option>
                  <option value="NILCAP">NILCAP</option>
                  <option value="FM PNEUS">FM PNEUS</option>
                </select>
              ) : formStatus.novo_status === "CONSERTO" ? (
                <select
                  value={formStatus.observacao}
                  onChange={(e) =>
                    setFormStatus({
                      ...formStatus,
                      observacao: e.target.value,
                    })
                  }
                  required
                >
                  <option value="">Selecione o local do conserto</option>
                  <option value="INTERNO">INTERNO</option>
                  <option value="FAM PNEUS">FAM PNEUS</option>
                </select>
              ) : (
                <input
                  placeholder="Observação. Ex: Retorno da garantia"
                  value={formStatus.observacao}
                  onChange={(e) =>
                    setFormStatus({
                      ...formStatus,
                      observacao: e.target.value,
                    })
                  }
                />
              )}

              <button type="submit">Alterar Status</button>
            </form>
          </section>
        )}

        {tela === "rodizio" && podeAcessar("rodizio") && (
          <section>
            <h1>Rodízio</h1>

            <div className="botoes-modo">
              <button
                type="button"
                onClick={() => setModoRodizio("alterarPosicao")}
                className={modoRodizio === "alterarPosicao" ? "ativo" : ""}
              >
                Alterar Posição Pneu
              </button>

              <button
                type="button"
                onClick={() => setModoRodizio("rodizio")}
                className={modoRodizio === "rodizio" ? "ativo" : ""}
              >
                Rodízio
              </button>
            </div>

            {modoRodizio === "alterarPosicao" && (
              <form onSubmit={alterarPosicaoPneu} className="form">
                <input
                  list="lista-pneus-rodizio"
                  placeholder="Digite o número de fogo"
                  value={formAlterarPosicao.fogo}
                  onChange={(e) =>
                    setFormAlterarPosicao({
                      ...formAlterarPosicao,
                      fogo: e.target.value,
                    })
                  }
                  required
                />

                <input
                  list="lista-posicoes"
                  placeholder="Nova posição"
                  value={formAlterarPosicao.nova_posicao}
                  onChange={(e) =>
                    setFormAlterarPosicao({
                      ...formAlterarPosicao,
                      nova_posicao: e.target.value.toUpperCase(),
                    })
                  }
                  required
                />

                <input
                  placeholder="KM do veículo"
                  type="number"
                  value={formAlterarPosicao.km_movimento}
                  onChange={(e) =>
                    setFormAlterarPosicao({
                      ...formAlterarPosicao,
                      km_movimento: e.target.value,
                    })
                  }
                  required
                />

                <input
                  type="text"
                  placeholder="Data. Ex: 04/05/2026"
                  value={formAlterarPosicao.data_movimento}
                  onChange={(e) =>
                    setFormAlterarPosicao({
                      ...formAlterarPosicao,
                      data_movimento: e.target.value,
                    })
                  }
                  required
                />

                <input
                  placeholder="Observação"
                  value={formAlterarPosicao.observacao}
                  onChange={(e) =>
                    setFormAlterarPosicao({
                      ...formAlterarPosicao,
                      observacao: e.target.value,
                    })
                  }
                />

                <label className="checkbox-linha">
                  <input
                    type="checkbox"
                    checked={formAlterarPosicao.movimentacao_antiga}
                    onChange={(e) =>
                      setFormAlterarPosicao({
                        ...formAlterarPosicao,
                        movimentacao_antiga: e.target.checked,
                      })
                    }
                  />
                  Movimentação antiga: permitir KM menor que o atual da placa
                </label>

                <button type="submit">Alterar Posição</button>
              </form>
            )}

            {modoRodizio === "rodizio" && (
              <form onSubmit={realizarRodizio} className="form">
                <input
                  list="lista-pneus-rodizio"
                  placeholder="Fogo 1"
                  value={formRodizio.fogo_1}
                  onChange={(e) =>
                    setFormRodizio({
                      ...formRodizio,
                      fogo_1: e.target.value,
                    })
                  }
                  required
                />

                <input
                  list="lista-pneus-rodizio"
                  placeholder="Fogo 2"
                  value={formRodizio.fogo_2}
                  onChange={(e) =>
                    setFormRodizio({
                      ...formRodizio,
                      fogo_2: e.target.value,
                    })
                  }
                  required
                />

                <input
                  placeholder="KM do veículo"
                  type="number"
                  value={formRodizio.km_movimento}
                  onChange={(e) =>
                    setFormRodizio({
                      ...formRodizio,
                      km_movimento: e.target.value,
                    })
                  }
                  required
                />

                <input
                  type="text"
                  placeholder="Data. Ex: 04/05/2026"
                  value={formRodizio.data_movimento}
                  onChange={(e) =>
                    setFormRodizio({
                      ...formRodizio,
                      data_movimento: e.target.value,
                    })
                  }
                  required
                />

                <input
                  placeholder="Observação"
                  value={formRodizio.observacao}
                  onChange={(e) =>
                    setFormRodizio({
                      ...formRodizio,
                      observacao: e.target.value,
                    })
                  }
                />

                <label className="checkbox-linha">
                  <input
                    type="checkbox"
                    checked={formRodizio.movimentacao_antiga}
                    onChange={(e) =>
                      setFormRodizio({
                        ...formRodizio,
                        movimentacao_antiga: e.target.checked,
                      })
                    }
                  />
                  Movimentação antiga: permitir KM menor que o atual da placa
                </label>

                <button type="submit">Realizar Rodízio</button>
              </form>
            )}

            <datalist id="lista-pneus-rodizio">
              {pneus
                .filter((pneu) => pneu.status === "EM USO")
                .map((pneu) => (
                  <option key={pneu.id} value={pneu.fogo}>
                    {pneu.fogo} - {pneu.marca} {pneu.modelo}
                  </option>
                ))}
            </datalist>

            <datalist id="lista-posicoes">
              {POSICOES_PERMITIDAS.map((posicao) => (
                <option key={posicao} value={posicao} />
              ))}
            </datalist>
          </section>
        )}

        {tela === "relatorios" && podeAcessar("relatorios") && (
          <section>
            <h1>Relatórios</h1>

            <div className="relatorios-grid">
              <div className="relatorio-card" onClick={exportarExcel}>
                <h2>Movimentações de Pneus</h2>
                <p>
                  Exporta o histórico geral de movimentações, entradas, saídas,
                  veículos, posições, KM rodado e status.
                </p>
                <button type="button">Exportar Excel</button>
              </div>

              <div className="relatorio-card" onClick={exportarPneusEstoque}>
                <h2>Pneus em Estoque</h2>
                <p>
                  Exporta todos os pneus disponíveis em estoque, com fogo, medida,
                  marca, modelo, valor e observação.
                </p>
                <button type="button">Exportar Excel</button>
              </div>

              <div className="relatorio-card" onClick={exportarPneusRecapagem}>
                <h2>Pneus em Recapagem</h2>
                <p>
                  Exporta todos os pneus que estão com status de recapagem.
                </p>
                <button type="button">Exportar Excel</button>
              </div>

              <div className="relatorio-card" onClick={exportarPneusConserto}>
                <h2>Pneus em Conserto</h2>
                <p>
                  Exporta todos os pneus com status de conserto, incluindo data de entrada,
                  custos adicionais e observação.
                </p>
                <button type="button">Exportar Excel</button>
              </div>

              <div className="relatorio-card" onClick={exportarCustosPneus}>
                <h2>Custos dos Pneus</h2>
                <p>
                  Exporta o valor de compra, custos adicionais e custo total de cada pneu.
                </p>
                <button type="button">Exportar Excel</button>
              </div>

              <div className="relatorio-card" onClick={exportarPneusDescartados}>
                <h2>Pneus Descartados</h2>
                <p>
                  Exporta todos os pneus com status descartado, incluindo valor de compra,
                  custos adicionais e custo total.
                </p>
                <button type="button">Exportar Excel</button>
              </div>

            </div>
          </section>
        )}

        {tela === "usuarios" && podeAcessar("usuarios") && (
          <section>
            <h1>Cadastro de Usuários</h1>

            <form onSubmit={cadastrarUsuario} className="form">
              <input
                placeholder="Usuário. Ex: joao.silva"
                value={formUsuario.usuario}
                onChange={(e) =>
                  setFormUsuario({
                    ...formUsuario,
                    usuario: e.target.value.toLowerCase(),
                  })
                }
                required
              />

              <input
                placeholder="Senha"
                type="password"
                value={formUsuario.senha}
                onChange={(e) =>
                  setFormUsuario({
                    ...formUsuario,
                    senha: e.target.value,
                  })
                }
                required
              />

              <select
                value={formUsuario.perfil}
                onChange={(e) =>
                  setFormUsuario({
                    ...formUsuario,
                    perfil: e.target.value,
                  })
                }
                required
              >
                <option value="">Selecione o perfil</option>
                <option value="ADM">ADM</option>
                <option value="UTILIZADOR">UTILIZADOR</option>
                <option value="GESTAO">GESTAO</option>
              </select>

              <button type="submit">Cadastrar Usuário</button>
            </form>

            <h2>Usuários cadastrados</h2>

            <table>
              <thead>
                <tr>
                  <th>Usuário</th>
                  <th>Perfil</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {usuarios.map((u) => (
                  <tr key={u.id}>
                    <td>{u.usuario}</td>
                    <td>{u.perfil}</td>
                    <td>{u.ativo === 1 ? "ATIVO" : "INATIVO"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </main>
    </div>
  );
}

function TabelaPneus({ pneus }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Fogo</th>
          <th>Medida</th>
          <th>Marca</th>
          <th>Modelo</th>
          <th>Status</th>
        </tr>
      </thead>

      <tbody>
        {pneus.map((pneu) => (
          <tr key={pneu.id}>
            <td>{pneu.fogo}</td>
            <td>{pneu.medida}</td>
            <td>{pneu.marca}</td>
            <td>{pneu.modelo}</td>
            <td>{pneu.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function TabelaVeiculos({ veiculos }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Placa</th>
          <th>Modelo</th>
          <th>Tipo</th>
          <th>KM Atual</th>
          <th>Status</th>
        </tr>
      </thead>

      <tbody>
        {veiculos.map((veiculo) => (
          <tr key={veiculo.id}>
            <td>{veiculo.placa}</td>
            <td>{veiculo.modelo}</td>
            <td>{veiculo.tipo}</td>
            <td>{veiculo.km_atual}</td>
            <td>{veiculo.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}