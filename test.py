from typing import Generator
from sqlalchemy.orm import Session, sessionmaker
from contextlib import contextmanager
from sqlalchemy import create_engine

# Предположим, что engine уже определен где-то в коде
engine = create_engine('sqlite:///example.db')  # Замените на ваш движок базы данных
SessionLocal = sessionmaker(bind=engine)

@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def test_database_connection():
    with get_session() as session:
        result = session.execute('SELECT 1').scalar()
        print(f"Database connection test result: {result}")

# Вызов теста подключения
test_database_connection()
