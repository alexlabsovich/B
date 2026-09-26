from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

import config


class IsAllowedUser(BaseFilter):
    """Пропускает только сообщения/callback'и от разрешённого пользователя."""

    async def __call__(self, event: TelegramObject) -> bool:
        user = getattr(event, "from_user", None)
        return user is not None and user.id == config.ALLOWED_USER_ID
