"""
database.py — a fundação da conexão com o banco.

    engine        a conexão com o banco
    SessionLocal  a fábrica de sessões (uma por requisição)
    Base          a classe que todos os modelos herdam

DATABASE_URL não definida -> SQLite local (eventos.db). Definida -> Azure SQL,
sem alterar uma linha de lógica no resto da aplicação.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eventos.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Classe base dos modelos. É por ela que o SQLAlchemy descobre as tabelas."""


def get_db():
    """Entrega uma sessão para a rota e garante que ela seja fechada."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
