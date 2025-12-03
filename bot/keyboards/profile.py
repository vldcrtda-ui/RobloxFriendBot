from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.i18n import Translator


def profile_actions_keyboard(tr: Translator, locale: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=tr.t("profile_buttons_edit", locale), callback_data="profile:edit")
    builder.button(text=tr.t("profile_buttons_delete", locale), callback_data="profile:delete")
    builder.adjust(2)
    return builder.as_markup()
