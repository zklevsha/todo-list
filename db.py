import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, select, func, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from settings import connection_string

engine = create_engine(connection_string)
Base = declarative_base()

class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    creation_date = Column(DateTime, default=func.now())
    is_finished = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"Todos(id={self.id!r}, title={self.title!r}, description={self.description!r}, creation_date={self.creation_date!r}, is_finished={self.is_finished!r})"


def connect_test():
    try:
        with engine.connect() as connection:
            return {'status': 'success', 'message': 'Successfully connected to the server.'}
    except SQLAlchemyError as error:
        return {'status': 'error', 'message': str(error)}

async def connect():
    try:
        connection = engine.connect()
        return connection
    except SQLAlchemyError as error:
        return {'status': 'error', 'message': str(error)}

def get_schema():
    alembic_table = Table('alembic_version', Base.metadata, autoload_with=engine)
    with Session(engine) as session:
        query = session.execute(select(alembic_table)).fetchone()
        result = query[0]
        return result