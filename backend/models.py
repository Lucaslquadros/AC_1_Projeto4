"""
models.py — a tabela `eventos`.

`cartaz_url` guarda o endereço do arquivo no Blob Storage, não a imagem em
si: o banco guarda texto, o arquivo mora fora dele.
"""

from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Evento(Base):
    """Esta classe vira a tabela `eventos` no banco."""

    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    local: Mapped[str] = mapped_column(String(120), nullable=False)
    vagas: Mapped[int] = mapped_column(Integer, nullable=False)

    # nullable=True de propósito: o evento nasce sem cartaz e ganha um
    # depois, numa requisição própria.
    cartaz_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<Evento id={self.id} nome={self.nome!r}>"
