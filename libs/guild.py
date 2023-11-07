from libs.games import Games


class Guild:

    def __init__(self, db, record):
        self.key = record["key"]
        self.games = record["games"]

        self.db = db

    @classmethod
    async def find_or_create(cls, db, channel):
        key = str(channel.guild.id)

        query = {"key": key}
        existing_record = db.guilds.find_one(query)

        if not existing_record:
            existing_record = {
                "key": key,
                "games": (await Games.get_default_games_keys(db))[0:20]
                # We can't show more than 20 games due to Discord limitations
            }

            db.guilds.insert_one(existing_record)

        return cls(db, existing_record)
