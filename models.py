"""
models.py
This module contains the model for the "todos" database.
"""
import enum
from sqlalchemy import Integer, String, Enum, LargeBinary, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):  # pylint: disable=R0903
    """
    Base class for the ORM models in the project.
    """


class UserRole(str, enum.Enum):
    """
    Class for the user roles.
    """
    ADMIN = "admin"
    USER = "user"


class User(Base):  # pylint: disable=R0903
    """
    Represents the 'users' table in the database.
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary(255), nullable=False)
    creation_date: Mapped[int] = mapped_column(Integer, nullable=False)
    timezone: Mapped[str] = mapped_column(String(30), nullable=False)
    daily_reminder: Mapped[bool] = mapped_column(Boolean, insert_default=False,
                                                 nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole),
                                           insert_default=UserRole.USER, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, email={self.email!r}, \
            creation_date={self.creation_date!r}, role={self.role!r})"


class Todo(Base):  # pylint: disable=R0903
    """
    Represents the 'todos' table in the database.
    """
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(255))
    creation_date: Mapped[int] = mapped_column(Integer, nullable=False)
    is_finished: Mapped[bool] = mapped_column(insert_default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self) -> str:
        return f"Todo(id={self.id!r}, title={self.title!r}, description={self.description!r}, \
            creation_date={self.creation_date!r}, \
            is_finished={self.is_finished!r}, user_id={self.user_id!r})"
