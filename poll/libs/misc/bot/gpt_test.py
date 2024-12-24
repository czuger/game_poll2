import logging
import ssl

import aiohttp
import certifi
from discord import Message

from poll.libs.objects.database import DbConnector
from poll.libs.misc.logging.set_logging import GPT_LOG_NAME

logger = logging.getLogger(GPT_LOG_NAME)
# Settings
MODEL = "gpt-4o"


async def ask_and_save(db: DbConnector, _type: str, prompt: str, message: str, key: str):
    payload = {
        'model': MODEL,
        'messages': [
            {"role": "user", "content": f"{prompt} {message}"}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                url='https://api.openai.com/v1/chat/completions',
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
                json=payload,
                ssl=ssl.create_default_context(cafile=certifi.where())
        ) as response:
            response = await response.json()

        logger.debug(f"response= {response}")

        if "error" in response:
            logger.error(f"OpenAI request failed with error {response['error']}")

        result_dict = {
            "type": _type,
            "prompt": prompt,
            "message": message,
            "response": f"{response['choices'][0]['message']['content']}"
        }

        logger.debug(f"about to insert = {result_dict}")

        result = await db.db.gpt_results.insert_one(result_dict)
        logger.debug(f"Insertion result = {result}")


# Call ChatGPT with the given prompt, asynchronously.
async def call_chatgpt_async(db: DbConnector, message: Message, key: str):
    if key is None:
        logger.error("Key not set")
        return

    words = message.content.split()
    word_count = len(words)
    if word_count > 30 or word_count < 5:
        logger.info(f"Sentence too short or too long {word_count} words")
        return

    prompt = "Résume cette phrase en un seul mot"
    logger.debug(f"About to test {prompt}")
    await ask_and_save(db, "summary", prompt, message.content, key)

    prompt = "Une réponse simple et humoristique (12 mots maximum) au message suivant"
    logger.debug(f"About to test {prompt}")
    await ask_and_save(db, "humor", prompt, message.content, key)

    prompt = "Est ce que cette phrase est humoristique ? Repond uniquement par oui ou par non."
    logger.debug(f"About to test {prompt}")
    await ask_and_save(db, "is_humor", prompt, message.content, key)
