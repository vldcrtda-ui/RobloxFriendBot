from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Game


async def seed_games(session: AsyncSession, data_path: Path) -> None:
    if not data_path.exists():
        return
    raw = json.loads(data_path.read_text(encoding="utf-8"))
    for item in raw:
        alias = item.get("alias")
        if not alias:
            continue
        exists = await session.scalar(select(Game).where(Game.alias == alias))
        if exists:
            continue
        session.add(
            Game(
                name=item.get("name") or alias,
                alias=alias,
                category=item.get("category"),
            )
        )
    await session.flush()


async def list_games(session: AsyncSession) -> list[Game]:
    result = await session.execute(select(Game).order_by(Game.name))
    return list(result.scalars().all())


async def load_games_by_ids(session: AsyncSession, ids: Iterable[int]) -> list[Game]:
    result = await session.execute(select(Game).where(Game.id.in_(list(ids))))
    return list(result.scalars().all())
