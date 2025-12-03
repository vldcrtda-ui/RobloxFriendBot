from __future__ import annotations

from typing import Any

AVAILABLE_LOCALES = ("ru", "en")


class Translator:
    def __init__(self, default_locale: str = "ru"):
        self.default_locale = default_locale if default_locale in AVAILABLE_LOCALES else "ru"

    def t(self, key: str, locale: str | None = None, **kwargs: Any) -> str:
        active_locale = locale if locale in AVAILABLE_LOCALES else self.default_locale
        template = MESSAGES.get(active_locale, {}).get(key) or MESSAGES["en"].get(key, key)
        return template.format(**kwargs)


MESSAGES: dict[str, dict[str, str]] = {
    "ru": {
        "start_greeting": "Привет, {username}! Я помогу найти напарников в Roblox. Давай настроим профиль.",
        "ask_nick": "Как тебя зовут в Roblox? Используй буквы, цифры и подчёркивания.",
        "invalid_nick": "Имя выглядит некорректно. Используй 3–30 символов: буквы, цифры, подчёркивания или дефис.",
        "ask_age": "Сколько тебе лет? Введи число от 8 до 99.",
        "invalid_age": "Возраст должен быть числом от 8 до 99.",
        "ask_language": "Выбери язык интерфейса и поиска.",
        "language_ru": "Русский",
        "language_en": "English",
        "ask_games": "Выбери до пяти любимых режимов. Нажимай, чтобы отметить, и жми «Готово», когда закончишь.",
        "games_limit": "Можно выбрать не больше пяти режимов.",
        "games_need_one": "Нужно выбрать хотя бы один режим.",
        "ask_bio": "Напиши пару слов о себе (до 300 символов) или нажми «Пропустить».",
        "bio_too_long": "Описание слишком длинное. Используй до 300 символов.",
        "ask_photo": "Пришли аватар (фото) или нажми «Пропустить».",
        "registration_complete": "Готово! Профиль сохранён. Доступные команды: /browse, /search, /chat, /profile, /help.",
        "profile_missing": "Профиль не найден. Нажми /start, чтобы зарегистрироваться.",
        "profile_title": "Твой профиль",
        "profile_username": "Username: @{username}",
        "profile_nick": "Roblox: {roblox_nick}",
        "profile_age": "Возраст: {age}",
        "profile_langs": "Язык: {languages}",
        "profile_games": "Режимы: {games}",
        "profile_bio": "О себе: {bio}",
        "profile_no_bio": "О себе: не заполнено",
        "profile_buttons_edit": "Редактировать",
        "profile_buttons_delete": "Удалить профиль",
        "edit_coming_soon": "Редактирование появится позже. Пока можно перезапустить регистрацию через /start.",
        "profile_deleted": "Профиль удалён. Можно пройти регистрацию заново: /start.",
        "already_registered": "Похоже, профиль уже есть. Можешь обновить через /start или открыть /profile.",
        "main_menu_hint": "Чем займёмся? /browse — лента игроков, /search — подбор по фильтрам, /chat — быстрый чат.",
        "photo_saved": "Фото сохранено.",
        "photo_skipped": "Фото пропущено.",
        "bio_saved": "Био сохранено.",
        "bio_skipped": "Био пропущено.",
        "done": "Готово",
        "skip": "Пропустить",
        "cancel": "Сценарий отменён.",
        "games_empty": "Список режимов пуст. Добавьте данные в data/games.json.",
        "help": "Команды: /start — регистрация, /profile — профиль, /browse — лента, /search — поиск, /chat — быстрый чат, /cancel — отменить текущий шаг.",
        "nick_taken": "Этот ник уже используется. Попробуй другой.",
    },
    "en": {
        "start_greeting": "Hi, {username}! I’ll help you find Roblox teammates. Let’s set up your profile.",
        "ask_nick": "What is your Roblox nickname? Use letters, digits, underscores.",
        "invalid_nick": "Nickname looks invalid. Use 3–30 characters: letters, digits, underscores or dash.",
        "ask_age": "How old are you? Enter a number between 8 and 99.",
        "invalid_age": "Age should be a number between 8 and 99.",
        "ask_language": "Choose your interface and search language.",
        "language_ru": "Русский",
        "language_en": "English",
        "ask_games": "Pick up to five favourite modes. Tap to toggle and press “Done” when ready.",
        "games_limit": "You can select at most five modes.",
        "games_need_one": "Pick at least one mode to continue.",
        "ask_bio": "Tell a bit about yourself (up to 300 chars) or tap “Skip”.",
        "bio_too_long": "Description is too long. Keep it under 300 characters.",
        "ask_photo": "Send an avatar photo or tap “Skip”.",
        "registration_complete": "All set! Profile saved. Commands: /browse, /search, /chat, /profile, /help.",
        "profile_missing": "Profile not found. Use /start to register.",
        "profile_title": "Your profile",
        "profile_username": "Username: @{username}",
        "profile_nick": "Roblox: {roblox_nick}",
        "profile_age": "Age: {age}",
        "profile_langs": "Language: {languages}",
        "profile_games": "Modes: {games}",
        "profile_bio": "About: {bio}",
        "profile_no_bio": "About: not provided",
        "profile_buttons_edit": "Edit",
        "profile_buttons_delete": "Delete profile",
        "edit_coming_soon": "Editing is coming later. You can restart onboarding with /start.",
        "profile_deleted": "Profile deleted. You can onboard again via /start.",
        "already_registered": "Looks like you already have a profile. You can refresh it with /start or view it via /profile.",
        "main_menu_hint": "What next? /browse — player feed, /search — filtered match, /chat — quick chat.",
        "photo_saved": "Photo saved.",
        "photo_skipped": "Photo skipped.",
        "bio_saved": "Bio saved.",
        "bio_skipped": "Bio skipped.",
        "done": "Done",
        "skip": "Skip",
        "cancel": "Flow cancelled.",
        "games_empty": "The game list is empty. Add entries to data/games.json.",
        "help": "Commands: /start — onboarding, /profile — profile, /browse — feed, /search — search, /chat — quick chat, /cancel — cancel current step.",
        "nick_taken": "This nickname is already taken. Try another one.",
    },
}
