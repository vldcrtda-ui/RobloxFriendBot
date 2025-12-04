from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

user_games_table = Table(
    "user_games",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("game_id", ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user id
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    roblox_nick: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    languages: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    games: Mapped[list["Game"]] = relationship(
        "Game",
        secondary=user_games_table,
        back_populates="users",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("roblox_nick", name="uq_users_roblox_nick"),
    )


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    alias: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_games_table,
        back_populates="games",
        lazy="selectin",
    )
