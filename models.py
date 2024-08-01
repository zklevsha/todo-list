"""
models.py
This module contains the model for the "todos" database.
"""
from datetime import datetime
from sqlalchemy import Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

func: callable # Fix for E1102

class Base(DeclarativeBase): # pylint: disable=R0903
    """
    Base class for the ORM models in the project.
    """

class Todo(Base): # pylint: disable=R0903
    """
    Represents the 'todos' table in the database.
    """
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(100))
    creation_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    is_finished: Mapped[bool] = mapped_column(insert_default=False)

    def __repr__(self) -> str:
        return f"Todo(id={self.id!r}, title={self.title!r}, description={self.description!r}, \
            creation_date={self.creation_date!r}, is_finished={self.is_finished!r})"
