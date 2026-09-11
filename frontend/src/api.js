/**
 * api.js — o único arquivo que conhece a API.
 *
 * Isola quem fala com o mundo de fora: os componentes chamam funções com
 * nome de negócio ("listarEventos") e não precisam saber nada sobre URL,
 * método HTTP ou formato de erro.
 */

// import.meta.env é como o Vite entrega as variáveis de ambiente. Só
// entram no bundle as que começam com VITE_. NUNCA coloque segredo aqui:
// tudo o que está no .env do frontend vai para o navegador do usuário.
const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

/**
 * Traduz uma resposta com erro na mensagem que o backend escreveu.
 */
async function mensagemDeErro(resposta) {
  let corpo;

  try {
    corpo = await resposta.json();
  } catch {
    return `Erro ${resposta.status} ao falar com a API.`;
  }

  if (typeof corpo.detail === "string") {
    return corpo.detail;
  }

  if (Array.isArray(corpo.detail)) {
    // 422: cada item traz o caminho do campo e o que está errado.
    return corpo.detail
      .map((erro) => `${erro.loc.at(-1)}: ${erro.msg}`)
      .join(" · ");
  }

  return `Erro ${resposta.status} ao falar com a API.`;
}

export async function listarEventos() {
  const resposta = await fetch(`${API_URL}/eventos`);

  if (!resposta.ok) {
    throw new Error(await mensagemDeErro(resposta));
  }

  return resposta.json();
}

export async function criarEvento(dados) {
  const resposta = await fetch(`${API_URL}/eventos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });

  if (!resposta.ok) {
    throw new Error(await mensagemDeErro(resposta));
  }

  return resposta.json();
}

export async function enviarCartaz(eventoId, arquivo) {
  const dados = new FormData();
  dados.append("arquivo", arquivo);

  const resposta = await fetch(`${API_URL}/eventos/${eventoId}/cartaz`, {
    method: "POST",
    // Sem o header Content-Type de propósito: em multipart ele precisa de
    // um "boundary" gerado na hora, e quem monta isso é o navegador a
    // partir do FormData.
    body: dados,
  });

  if (!resposta.ok) {
    throw new Error(await mensagemDeErro(resposta));
  }

  return resposta.json();
}
