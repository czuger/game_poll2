from beanie import Document, Indexed


class GameOrmObject(Document):
    key: Indexed(str, unique=True)
    short: str
    long: str
    game_type: str

    class Settings:
        name = "games"
