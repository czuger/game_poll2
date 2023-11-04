class Guild:

    def __init__(self, record):
        self.key = record["key"]
        self.games = record["games"]

    @classmethod
    async def find_or_create(cls, database, channel):
        key = str(channel.guild.id)

        games_collection_dict = {}
        for e in database["games"].find():
            games_collection_dict[e["key"]] = e

        guilds = database["guilds"]

        query = {"key": key}
        existing_record = guilds.find_one(query)

        if not existing_record:
            existing_record = {
                "key": key,
                "games": games_collection_dict
            }

            guilds.insert_one(existing_record)

        return cls(existing_record)



