from __future__ import annotations

import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import from_url as redis_from_url

from bot.config import load_settings
from bot.db.session import create_engine, create_session_factory, init_models, session_scope
from bot.handlers.common import router as common_router
from bot.handlers.profile import router as profile_router
from bot.handlers.register import router as register_router
from bot.middlewares.context import ContextMiddleware
from bot.services.games import seed_games
from bot.utils.i18n import Translator
from bot.utils.logging import setup_logging


async def main() -> None:
    setup_logging()
    settings = load_settings()
    translator = Translator(default_locale=settings.default_language)

    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    await init_models(engine)

    data_path = Path(__file__).resolve().parent.parent / "data" / "games.json"
    async with session_scope(session_factory) as session:
        await seed_games(session, data_path)

    storage = RedisStorage(redis=redis_from_url(settings.redis_url))
    bot = Bot(settings.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)

    context_middleware = ContextMiddleware(settings, session_factory, translator)
    dp.message.middleware(context_middleware)
    dp.callback_query.middleware(context_middleware)

    dp.include_router(common_router)
    dp.include_router(register_router)
    dp.include_router(profile_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
