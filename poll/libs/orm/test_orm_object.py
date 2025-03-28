import asyncio
from datetime import datetime

from beanie import Document, init_beanie
from pydantic import BaseModel

from poll.libs.objects.database import DbConnector


class Misc(BaseModel):
    schedule: int
    last_schedule: datetime


class TestOrmObject(Document):
    key: str
    buttons: dict
    misc: Misc
    votes: dict

    class Settings:
        name = "test_instances"


async def main():
    client = DbConnector()
    client.connect()

    await init_beanie(database=client.db_connection.games_database, document_models=[TestOrmObject])

    product = await TestOrmObject.find_one(TestOrmObject.key == "666558870126329857")
    print(product.misc)


if __name__ == "__main__":
    asyncio.run(main())
