/**
 * FormularioEvento.jsx — cria um evento pelo POST /eventos.
 *
 * Campos controlados: o valor do input vem do estado e toda digitação
 * atualiza o estado.
 */

import { useState } from "react";

import { criarEvento } from "./api";

const VAZIO = { nome: "", data: "", local: "", vagas: "" };

export default function FormularioEvento({ aoCriar }) {
  const [campos, setCampos] = useState(VAZIO);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);

  function alterar(evento) {
    const { name, value } = evento.target;
    setCampos((atual) => ({ ...atual, [name]: value }));
  }

  async function enviar(evento) {
    evento.preventDefault();

    setEnviando(true);
    setErro(null);

    try {
      await criarEvento({
        nome: campos.nome,
        data: campos.data,
        local: campos.local,
        // O input devolve string mesmo com type="number"; o schema espera int.
        vagas: Number(campos.vagas),
      });

      setCampos(VAZIO);
      aoCriar();
    } catch (e) {
      setErro(e.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <form className="formulario" onSubmit={enviar}>
      <h2>Novo evento</h2>

      <div className="campos">
        <label>
          Nome
          <input name="nome" value={campos.nome} onChange={alterar} required />
        </label>

        <label>
          Data
          <input
            name="data"
            type="date"
            value={campos.data}
            onChange={alterar}
            required
          />
        </label>

        <label>
          Local
          <input name="local" value={campos.local} onChange={alterar} required />
        </label>

        <label>
          Vagas
          <input
            name="vagas"
            type="number"
            min="1"
            value={campos.vagas}
            onChange={alterar}
            required
          />
        </label>
      </div>

      {erro && <p className="erro-inline">{erro}</p>}

      <button type="submit" disabled={enviando}>
        {enviando ? "Salvando…" : "Criar evento"}
      </button>
    </form>
  );
}
