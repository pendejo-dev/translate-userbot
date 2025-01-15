import asyncio

from loguru import logger
from telethon import TelegramClient, events
from telethon.tl.custom import Message

from bot.utils.config_reader import config
from bot.utils.database.postgres import DataBase
from bot.utils.delete_message_helper import delete_message_helper
from bot.utils.edit_message_helper import edit_message_helper
from bot.utils.get_id_with_username_helper import get_id_with_username_helper
from bot.utils.translate_message_helper import translate_message_helper
from bot.utils.translator import GlossaryEnum

client = TelegramClient('anon_prod', config.api_id, config.api_hash)


async def main():
    client.parse_mode = "html"
    await client.start()
    logger.info("Starting userbot...")
    await client.run_until_disconnected()


with (client):
    @client.on(events.MessageDeleted(chats=[int(config.blacklist_chat)]))
    async def delete_message_blacklist(event):
        await delete_message_helper(client, event.deleted_ids, int(config.blacklist_en_chat))


    @client.on(events.MessageDeleted(chats=[int(config.blacklist_en_chat)]))
    async def delete_message_blacklist_en(event):
        await delete_message_helper(client, event.deleted_ids, int(config.blacklist_chat))

    @client.on(events.MessageEdited(chats=[int(config.blacklist_chat)]))
    async def edit_message_blacklist(event: Message):
        await edit_message_helper(client, event.message.id, int(config.blacklist_en_chat), event.message.message,
                                  "ru", "en", GlossaryEnum.RU_to_EN)

    @client.on(events.MessageEdited(chats=[int(config.blacklist_en_chat)]))
    async def edit_message_blacklist_en(event: Message):
        await edit_message_helper(client, event.message.id, int(config.blacklist_chat), event.message.message,
                                  "en", "ru", GlossaryEnum.EN_to_RU)

    @client.on(events.NewMessage(chats=[int(config.blacklist_chat)]))
    async def message_blacklist(event: Message):
        # await translate_message_helper(
        #     client, event, int(config.blacklist_chat), int(config.blacklist_en_chat), '@bb_list',
        #     "ru", "en", GlossaryEnum.RU_to_EN
        # )
        await get_id_with_username_helper(
            client, event, int(config.blacklist_chat), int(config.blacklist_en_chat), "ru", "en",
            GlossaryEnum.RU_to_EN
        )

    @client.on(events.NewMessage(chats=[6577533785]))
    async def message_owner(event: Message):
        if event.raw_text.strip().lower() == "собери все пробивы":
            counter = 0
            async for log in client.iter_admin_log(int(config.blacklist_chat), delete=True, search="Telegram ID"):
                await DataBase.execute(
                    "INSERT INTO breakthrough_messages_2(sender_user_id, message, date) VALUES($1, $2, $3)",
                    int(log.user_id), log.action.message.message,
                    log.action.message.date.strftime('%Y-%m-%d %H:%M:%S'), execute=True
                )
                counter = counter + 1
                await asyncio.sleep(0.1)

            logger.debug("Все данные собраны")
            await event.reply(f"Все данные собраны. Всего: {counter}")

    @client.on(events.NewMessage(chats=[int(config.blacklist_en_chat)]))
    async def english_blacklist_message_handler(event: Message):
        # await translate_message_helper(
        #     client, event, int(config.blacklist_en_chat), int(config.blacklist_chat), '@bb_list_eng',
        #     "en", "ru", GlossaryEnum.EN_to_RU
        # )
        await get_id_with_username_helper(
            client, event, int(config.blacklist_en_chat), int(config.blacklist_chat), "en", "ru",
            GlossaryEnum.EN_to_RU
        )

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(DataBase.create_pool())
        client.loop.run_until_complete(DataBase.create_tables())
        client.loop.run_until_complete(main())
