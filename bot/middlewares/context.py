from __future__ import annotations

from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot.config import Settings
from bot.utils.i18n import Translator


class ContextMiddleware(BaseMiddleware):
    """Injects common dependencies into handler data."""

    def __init__(
        self,
        settings: Settings,
        session_factory: async_sessionmaker[AsyncSession],
        translator: Translator,
    ) -> None:
        super().__init__()
        self.settings = settings
        self.session_factory = session_factory
        self.translator = translator

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["settings"] = self.settings
        data["session_factory"] = self.session_factory
        data["translator"] = self.translator
        return await handler(event, data)
