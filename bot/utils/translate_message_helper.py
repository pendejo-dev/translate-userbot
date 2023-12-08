from contextlib import suppress

from telethon import TelegramClient
from telethon.tl.custom import Message

from bot.utils.database.postgres import DataBase
from bot.utils.translator import translate_message, GlossaryEnum


async def translate_message_helper(client: TelegramClient, event: Message,
                                   sender_chat_id: int, recipient_chat_id: int, sender_name: str,
                                   source_lang: str, target_lang: str, glossary_id: GlossaryEnum) -> None:
    if event.sticker or event.gif:
        return

    translate_text = await translate_message(event.raw_text, source_lang, target_lang, glossary_id)

    sender = await event.get_sender()
    if sender:
        sender_first_name = sender.first_name
    else:
        sender_first_name = sender_name

    reply_message_id = None
    if event.reply_to_msg_id:
        reply_message_id = await DataBase.execute(
            "SELECT recipient_message_id FROM messages_data WHERE sender_message_id = $1",
            event.reply_to_msg_id, fetchval=True
        )

        if not reply_message_id:
            reply_message_id = await DataBase.execute(
                "SELECT sender_message_id FROM messages_data WHERE recipient_message_id = $1",
                event.reply_to_msg_id, fetchval=True
            )

    with suppress(ValueError):
        if event.photo:
            recipient_message = await client.send_message(
                recipient_chat_id,
                f"{translate_text}\n<b>«{sender_first_name}»</b>",
                file=event.message.media,
                reply_to=reply_message_id
            )
        else:
            recipient_message = await client.send_message(
                recipient_chat_id,
                f"{translate_text}\n<b>«{sender_first_name}»</b>",
                reply_to=reply_message_id
            )

        await DataBase.execute(
            "INSERT INTO messages_data (sender_group_id, recipient_group_id, sender_message_id, "
            "recipient_message_id, sender_name) VALUES($1, $2, $3, $4, $5)",
            sender_chat_id, recipient_chat_id, event.id, recipient_message.id,
            sender_first_name, execute=True
        )
