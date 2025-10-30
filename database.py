import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./proyectos.db")
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
