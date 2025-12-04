from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable
import logging

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.db.models import Game, User
from bot.services.schemas import RegistrationData

logger = logging.getLogger(__name__)


async def get_user(session: AsyncSession, tg_id: int) -> User | None:
    try:
        result = await session.execute(
            select(User).where(User.id == tg_id).options(selectinload(User.games))
        )
        return result.scalar_one_or_none()
    except Exception:
        logger.exception("Failed to get user from DB", extra={"tg_id": tg_id})
        return None


async def upsert_user(session: AsyncSession, payload: RegistrationData) -> User:
    user = await get_user(session, payload.tg_id)
    games = await _load_games(session, payload.game_ids)

    if user:
        user.username = payload.username
        user.roblox_nick = payload.roblox_nick
        user.age = payload.age
        user.languages = payload.languages
        user.description = payload.description
        user.photo_id = payload.photo_id
        user.is_deleted = False
        user.games = games
    else:
        user = User(
            id=payload.tg_id,
            username=payload.username,
            roblox_nick=payload.roblox_nick,
            age=payload.age,
            languages=payload.languages,
            description=payload.description,
            photo_id=payload.photo_id,
            games=games,
        )
        session.add(user)

    await session.flush()
    return user


async def delete_user(session: AsyncSession, tg_id: int) -> bool:
    user = await get_user(session, tg_id)
    if not user:
        return False
    await session.delete(user)
    await session.flush()
    return True


async def touch_user(session: AsyncSession, tg_id: int) -> None:
    await session.execute(
        update(User)
        .where(User.id == tg_id)
        .values(last_active=datetime.now(timezone.utc))
    )


async def _load_games(session: AsyncSession, game_ids: Iterable[int]) -> list[Game]:
    result = await session.execute(
        select(Game).where(Game.id.in_(list(game_ids)))
    )
    return list(result.scalars().all())
