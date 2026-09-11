/**
 * ListaEventos.jsx — mostra os eventos e trata os estados da busca.
 *
 * Este componente não busca nada: recebe tudo pronto por props.
 */

import EnviarCartaz from "./EnviarCartaz";

export default function ListaEventos({
  eventos,
  carregando,
  erro,
  aoAtualizar,
  aoTentarDeNovo,
}) {
  if (carregando) {
    return <p className="aviso">Carregando eventos…</p>;
  }

  if (erro) {
    return (
      <div className="aviso erro">
        <p>{erro}</p>
        <p className="dica">
          O backend está rodando? Se o erro no console mencionar CORS, a
          origem deste site não está na lista do <code>CORSMiddleware</code>.
        </p>
        <button onClick={aoTentarDeNovo}>Tentar de novo</button>
      </div>
    );
  }

  if (eventos.length === 0) {
    return <p className="aviso">Nenhum evento cadastrado ainda.</p>;
  }

  return (
    <ul className="lista">
      {eventos.map((evento) => (
        // A key precisa ser o id do banco, nunca o índice do array.
        <li key={evento.id} className="card">
          {evento.cartaz_url ? (
            <img
              className="cartaz"
              src={evento.cartaz_url}
              alt={`Cartaz do evento ${evento.nome}`}
            />
          ) : (
            <div className="cartaz vazio">sem cartaz</div>
          )}

          <div className="conteudo">
            <h2>{evento.nome}</h2>
            <p className="meta">
              {/* new Date() na string "AAAA-MM-DD" interpreta como UTC e
                  pode voltar um dia em fuso negativo — formatamos pelas partes. */}
              {evento.data.split("-").reverse().join("/")} · {evento.local}
            </p>
            <p className="meta">{evento.vagas} vagas</p>

            <EnviarCartaz eventoId={evento.id} aoEnviar={aoAtualizar} />
          </div>
        </li>
      ))}
    </ul>
  );
}
