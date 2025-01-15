import re
from contextlib import suppress

from loguru import logger
from telethon import TelegramClient

from telethon.tl.custom import Message
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types.users import UserFull

from bot.utils.database.postgres import DataBase
from bot.utils.translator import translate_message, GlossaryEnum


async def get_id_with_username_helper(client: TelegramClient, event: Message,
                                      sender_chat_id: int, recipient_chat_id: int,
                                      source_lang: str, target_lang: str, glossary_id: GlossaryEnum) -> None:
    if '- Статус' in event.raw_text and 'Рекомендаций' in event.raw_text:
        return

    username_list = re.findall(r"@\w+", event.raw_text)
    user_full_list = ''

    count = 0
    for username in username_list:
        if count == 3:
            break

        try:
            user: UserFull = await client(GetFullUserRequest(username.replace('@', '').lower()))

            if user.users[0].username.lower() != username.replace('@', '').lower():
                logger.warning(
                    f"Юзернеймы {username.replace('@', '').lower()} и {user.users[0].username.lower()} не совпадают!")
                continue

            user_full_list += f'<b>{"Bot" if user.users[0].bot else "User"}</b> @{user.users[0].username}\n' \
                              f'<b>First Name:</b> <code>{user.users[0].first_name}</code>\n' \
                              f'<b>Telegram ID:</b> <code>{user.users[0].id}</code>\n\n'
            count += 1
        except Exception as e:
            logger.error(e)
            continue

    with suppress(ValueError):
        await event.reply(user_full_list)

        # translate_bot_text = await translate_message(user_full_list, source_lang, target_lang, glossary_id)
        # with suppress(ValueError):
        #     recipient_message = await client.send_message(
        #         recipient_chat_id,
        #         f"{translate_bot_text}"
        #     )
        #
        #     await DataBase.execute(
        #         "INSERT INTO messages_data (sender_group_id, recipient_group_id, sender_message_id, "
        #         "recipient_message_id) VALUES($1, $2, $3, $4)",
        #         sender_chat_id, recipient_chat_id, event.id, recipient_message.id,
        #         execute=True
        #     )
