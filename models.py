from datetime import datetime
from sqlalchemy import Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


class Base(DeclarativeBase):
    pass

class Todos(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(100))
    creation_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    is_finished: Mapped[bool] = mapped_column(insert_default=False)

    def __repr__(self) -> str:
        return f"Todos(id={self.id!r}, title={self.title!r}, description={self.description!r}, creation_date={self.creation_date!r}, is_finished={self.is_finished!r})"


