from __future__ import annotations

from aiogram.types import CallbackQuery, Message

from bot.utils.i18n import AVAILABLE_LOCALES


def resolve_locale(
    event: Message | CallbackQuery,
    default: str = "ru",
    user_locale: str | None = None,
) -> str:
    if user_locale in AVAILABLE_LOCALES:
        return user_locale

    language_code = getattr(event.from_user, "language_code", None) if event.from_user else None
    if language_code:
        short = language_code.split("-")[0]
        if short in AVAILABLE_LOCALES:
            return short
    if language_code in AVAILABLE_LOCALES:
        return language_code  # type: ignore[arg-type]
    return default if default in AVAILABLE_LOCALES else AVAILABLE_LOCALES[0]
