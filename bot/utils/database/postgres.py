from typing import Union

import asyncpg
from asyncpg import Connection, DuplicateTableError
from asyncpg.pool import Pool

from bot.utils.config_reader import config


# Управление базами данных.
class DataBaseClass:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create_pool(self):
        self.pool = self.pool = await asyncpg.create_pool(
            user=config.postgres_user,
            password=config.postgres_pass,
            host=config.postgres_host,
            database=config.postgres_db
        )

    async def execute(self, command: str, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
        return result

    async def create_tables(self):
        # Создаем базы данных.
        try:
            await self.execute(
                """CREATE TABLE public.messages_data
                (
                    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
                    sender_group_id bigint NOT NULL,
                    recipient_group_id bigint NOT NULL,
                    sender_message_id bigint NOT NULL,
                    recipient_message_id bigint NOT NULL,
                    sender_name varchar(35),
                    CONSTRAINT messages_data_pkey PRIMARY KEY (id)
                )""", execute=True
            )
        except DuplicateTableError:
            pass

        try:
            await self.execute(
                """CREATE TABLE public.breakthrough_messages
                (
                    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
                    sender_user_id bigint NOT NULL,
                    message text,
                    CONSTRAINT breakthrough_messages_pkey PRIMARY KEY (id)
                )""", execute=True
            )
        except DuplicateTableError:
            pass

        try:
            await self.execute(
                """CREATE TABLE public.breakthrough_messages_2
                (
                    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
                    sender_user_id bigint NOT NULL,
                    message text,
                    date text,
                    CONSTRAINT breakthrough_messages_2_pkey PRIMARY KEY (id)
                )""", execute=True
            )
        except DuplicateTableError:
            pass


DataBase = DataBaseClass()
