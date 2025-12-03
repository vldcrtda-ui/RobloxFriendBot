from __future__ import annotations

from typing import Iterable, Mapping, Set, Any

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.i18n import Translator


def language_keyboard(tr: Translator, locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=tr.t("language_ru", locale), callback_data="lang:ru")
    builder.button(text=tr.t("language_en", locale), callback_data="lang:en")
    builder.adjust(2)
    return builder.as_markup()


def games_keyboard(
    tr: Translator,
    locale: str,
    games: Iterable[Any],
    selected_ids: Set[int],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for game in games:
        if isinstance(game, Mapping):
            game_id = int(game["id"])
            name = str(game["name"])
        else:
            game_id = getattr(game, "id")
            name = getattr(game, "name")
        marker = "✅ " if game_id in selected_ids else ""
        builder.button(text=f"{marker}{name}", callback_data=f"game:{game_id}")
    builder.adjust(2)
    builder.button(text=f"✔️ {tr.t('done', locale)}", callback_data="games:done")
    builder.adjust(2, 1)
    return builder.as_markup()


def skip_keyboard(text: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="skip")
    return builder.as_markup()
