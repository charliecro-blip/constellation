"""Database configuration and session management."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

DEFAULT_DATABASE_URL = "sqlite:///./constellation_dev.db"


def get_database_url() -> str:
    return os.getenv("CONSTELLATION_DATABASE_URL", DEFAULT_DATABASE_URL)


def create_db_engine(url: str | None = None):
    database_url = url or get_database_url()
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


engine = create_db_engine()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
