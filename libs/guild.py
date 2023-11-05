class Guild:

    def __init__(self, db, record):
        self.key = record["key"]
        self.games = record["games"]

        self.db = db

    @classmethod
    async def find_or_create(cls, db, channel):
        key = str(channel.guild.id)

        games_collection = [e["key"] for e in list(db.games.find())]

        query = {"key": key}
        existing_record = db.guilds.find_one(query)

        if not existing_record:
            existing_record = {
                "key": key,
                "games": games_collection
            }

            db.guilds.insert_one(existing_record)

        return cls(db, existing_record)
