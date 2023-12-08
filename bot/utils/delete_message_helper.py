from loguru import logger
from telethon import TelegramClient

from bot.utils.database.postgres import DataBase


async def delete_message_helper(client: TelegramClient, messages_id: list[int], group_id: int) -> None:
    for message_id in messages_id:
        delete_message_data = await DataBase.execute(
            "SELECT id, recipient_message_id FROM messages_data WHERE sender_message_id = $1",
            message_id, fetch=True
        )

        if not delete_message_data:
            delete_message_data = await DataBase.execute(
                "SELECT id, sender_message_id FROM messages_data WHERE recipient_message_id = $1",
                message_id, fetch=True
            )

            if not delete_message_data:
                return
            message_base_id: int = delete_message_data[0]['sender_message_id']
        else:
            message_base_id: int = delete_message_data[0]['recipient_message_id']

        try:
            await client.delete_messages(
                entity=group_id,
                message_ids=message_base_id
            )
        except Exception as e:
            logger.error(e)

        await DataBase.execute(
            "DELETE FROM messages_data WHERE id = $1",
            delete_message_data[0]['id'], execute=True
        )

