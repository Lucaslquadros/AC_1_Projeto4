/**
 * EnviarCartaz.jsx — envia a imagem para POST /eventos/{id}/cartaz.
 *
 * O input de arquivo é o único que NÃO é controlado: o navegador não
 * deixa o código definir o valor de um <input type="file">.
 */

import { useRef, useState } from "react";

import { enviarCartaz } from "./api";

export default function EnviarCartaz({ eventoId, aoEnviar }) {
  const inputRef = useRef(null);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState(null);

  async function selecionou(evento) {
    const arquivo = evento.target.files[0];
    if (!arquivo) return;

    setEnviando(true);
    setErro(null);

    try {
      await enviarCartaz(eventoId, arquivo);

      // Limpa o input para que escolher o MESMO arquivo de novo dispare o onChange.
      if (inputRef.current) inputRef.current.value = "";

      aoEnviar();
    } catch (e) {
      setErro(e.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="upload">
      <label className="botao-arquivo">
        {enviando ? "Enviando…" : "Trocar cartaz"}
        <input
          ref={inputRef}
          type="file"
          accept="image/png, image/jpeg, image/webp"
          onChange={selecionou}
          disabled={enviando}
        />
      </label>

      {erro && <p className="erro-inline">{erro}</p>}
    </div>
  );
}
