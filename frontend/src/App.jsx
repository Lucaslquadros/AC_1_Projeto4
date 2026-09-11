/**
 * App.jsx — o componente de cima, dono do estado da lista.
 *
 * A lista de eventos mora aqui, e não dentro de ListaEventos, porque o
 * formulário também precisa mexer nela: ao criar um evento, a lista tem
 * que se atualizar. Estado compartilhado por dois componentes sobe para o
 * pai comum dos dois.
 */

import { useCallback, useEffect, useState } from "react";

import { listarEventos } from "./api";
import FormularioEvento from "./FormularioEvento";
import ListaEventos from "./ListaEventos";

export default function App() {
  // Os três estados que toda tela que fala com API precisa ter.
  const [eventos, setEventos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);

    try {
      setEventos(await listarEventos());
    } catch (e) {
      setErro(e.message);
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  return (
    <main>
      <header>
        <h1>Eventos do Campus</h1>
        <p className="subtitulo">
          IBM4028 — AC1: aplicação de eventos publicada na nuvem.
        </p>
      </header>

      <FormularioEvento aoCriar={carregar} />

      <ListaEventos
        eventos={eventos}
        carregando={carregando}
        erro={erro}
        aoAtualizar={carregar}
        aoTentarDeNovo={carregar}
      />
    </main>
  );
}
