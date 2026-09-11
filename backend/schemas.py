"""
schemas.py — o contrato da API (Pydantic), separado da tabela (SQLAlchemy).

`EventoCreate` é o que o cliente ENVIA; `EventoResponse` é o que a API
DEVOLVE. São coisas diferentes: o cartaz não entra na criação, e a resposta
troca a URL guardada por um link assinado (SAS) antes de sair.
"""

from datetime import date

from pydantic import BaseModel, Field


class EventoCreate(BaseModel):
    """O que o cliente ENVIA no POST /eventos."""

    nome: str = Field(
        min_length=3,
        max_length=100,
        description="Nome do evento",
        examples=["Hackathon IBMEC"],
    )
    data: date = Field(
        description="Data do evento no formato AAAA-MM-DD",
        examples=["2026-09-12"],
    )
    local: str = Field(
        min_length=3,
        max_length=120,
        examples=["Auditório – Campus Barra"],
    )
    vagas: int = Field(
        ge=1,
        le=1000,
        description="Número de vagas (de 1 a 1000)",
        examples=[80],
    )


class EventoResponse(BaseModel):
    """
    O que a API DEVOLVE.

    `cartaz_url` é opcional e vem como null enquanto ninguém enviou imagem.
    """

    id: int
    nome: str
    data: date
    local: str
    vagas: int
    cartaz_url: str | None = None
