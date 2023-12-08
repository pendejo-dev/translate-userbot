from telethon import TelegramClient

from bot.utils.database.postgres import DataBase
from bot.utils.translator import translate_message, GlossaryEnum


async def edit_message_helper(client: TelegramClient, message_id: int, group_id: int, text: str,
                              source_lang: str, target_lang: str, glossary_id: GlossaryEnum) -> None:
    reply_message_data = await DataBase.execute(
        "SELECT recipient_message_id, sender_name FROM messages_data WHERE sender_message_id = $1",
        message_id, fetch=True
    )

    if not reply_message_data:
        return

    translate_text = await translate_message(text, source_lang, target_lang, glossary_id)

    await client.edit_message(
        entity=group_id,
        message=reply_message_data[0]['recipient_message_id'],
        text=translate_text + f'\n<b>«{reply_message_data[0]["sender_name"]}»</b>'
    )
