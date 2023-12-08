from enum import Enum

import aiohttp
from loguru import logger


class GlossaryEnum(str, Enum):
    RU_to_EN = '0ab5f3ac-f47b-4170-a616-cc019a6f4eed'
    EN_to_RU = '23f9494f-ad06-47d1-9402-6fee21bf36eb'


async def translate_message(message: str, source_lang: str, target_lang: str, glossary_id: GlossaryEnum) -> str | None:
    params = {
        'text': message,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'split_sentences': '1',
        'glossary_id': glossary_id.value
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'api.deepl.com',
        'Authorization': 'DeepL-Auth-Key 2468d41c-6bfb-4595-0a95-ab2ed617d601'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f'https://api.deepl.com/v2/translate', headers=headers, params=params) as response:
            result = await response.json()

            if response.status == 429:
                logger.error(429)
                return None
            elif response.status == 456:
                logger.error('DeepL API превышена квота. Достигнут предел перевода вашего аккаунта.')
                return None

            if not response.ok:
                print(await response.text())
                logger.error('not response.ok')
                return None

            return result['translations'][0]['text']
