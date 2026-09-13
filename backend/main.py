"""
main.py — API de Eventos do Campus.

AC1 — IBM4028, Projeto em Ciência de Dados IV.

Junta o que foi construído aula a aula: persistência (Aula 06), upload de
cartaz no Blob Storage (Aulas 07-08) e CORS para o frontend em React
(Aula 09). Este mesmo código roda local (SQLite + .env) e publicado no
Azure (Azure SQL + App Settings) — só a variável de ambiente muda.

Para rodar local:
    fastapi dev main.py
"""

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import storage
from database import Base, engine, get_db
from schemas import EventoCreate, EventoResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Eventos do Campus",
    description="AC1 — IBM4028, Projeto em Ciência de Dados IV",
    version="1.0.0",
)

# As origens que podem chamar esta API pelo navegador.
#
# localhost e 127.0.0.1 são a MESMA máquina e origens DIFERENTES para o
# navegador — por isso os dois estão na lista. A origem do Static Web App
# publicado entra aqui no dia do deploy (Passo 4 da Aula 10).
ORIGENS_PERMITIDAS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://proud-sky-0c7380510.6.azurestaticapps.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXTENSAO_POR_TIPO = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

TAMANHO_MAXIMO_BYTES = 2 * 1024 * 1024  # 2 MB


def para_resposta(evento: models.Evento) -> EventoResponse:
    """Monta a resposta trocando a URL guardada por um link assinado (SAS)."""
    return EventoResponse(
        id=evento.id,
        nome=evento.nome,
        data=evento.data,
        local=evento.local,
        vagas=evento.vagas,
        cartaz_url=storage.url_com_sas(evento.cartaz_url) if evento.cartaz_url else None,
    )


@app.get("/")
async def raiz():
    return {"mensagem": "API de Eventos do Campus", "docs": "/docs"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    total = db.query(models.Evento).count()
    return {"status": "ok", "banco": "conectado", "eventos_cadastrados": total}


@app.get("/eventos", response_model=list[EventoResponse])
async def listar_eventos(db: Session = Depends(get_db)):
    return [para_resposta(e) for e in db.query(models.Evento).all()]


@app.post(
    "/eventos",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    novo = models.Evento(**evento.model_dump())

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return para_resposta(novo)


@app.get("/eventos/{evento_id}", response_model=EventoResponse)
async def buscar_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()

    if evento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento {evento_id} não encontrado",
        )

    return para_resposta(evento)


@app.post("/eventos/{evento_id}/cartaz", response_model=EventoResponse)
async def enviar_cartaz(
    evento_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Recebe a imagem, grava no Blob Storage e guarda a URL no evento."""
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()

    if evento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento {evento_id} não encontrado",
        )

    if arquivo.content_type not in EXTENSAO_POR_TIPO:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Tipo {arquivo.content_type!r} não aceito. "
                f"Envie um dos seguintes: {', '.join(EXTENSAO_POR_TIPO)}"
            ),
        )

    conteudo = await arquivo.read()

    if len(conteudo) > TAMANHO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo com {len(conteudo)} bytes; o limite é {TAMANHO_MAXIMO_BYTES}.",
        )

    url = storage.enviar_arquivo(
        nome_do_blob=storage.nome_do_cartaz(evento_id, EXTENSAO_POR_TIPO[arquivo.content_type]),
        conteudo=conteudo,
        content_type=arquivo.content_type,
    )

    evento.cartaz_url = url
    db.commit()
    db.refresh(evento)

    return para_resposta(evento)


@app.delete("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_evento(evento_id: int, db: Session = Depends(get_db)):
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()

    if evento is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento {evento_id} não encontrado",
        )

    db.delete(evento)
    db.commit()
