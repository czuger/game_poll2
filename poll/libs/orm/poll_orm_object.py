import asyncio
from datetime import datetime

from beanie import Document, init_beanie
from pydantic import BaseModel

from poll.libs.objects.database import DbConnector


class Misc(BaseModel):
    schedule: int
    last_schedule: datetime


class PollOrmObject(Document):
    key: str
    buttons: dict
    misc: Misc
    votes: dict

    class Settings:
        name = "poll_instances"


async def main():
    client = DbConnector()
    client.connect()

    await init_beanie(database=client.db_connection.games_database, document_models=[PollOrmObject])

    product = await PollOrmObject.find_one(PollOrmObject.key == "487195843091365888")
    print(product.buttons["games"].keys())


if __name__ == "__main__":
    asyncio.run(main())
