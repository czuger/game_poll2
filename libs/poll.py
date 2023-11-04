from libs.guild import Guild


class Poll:

    def __init__(self, record):
        self.key = record["key"]
        self.games = record["games"]

    @classmethod
    async def find_or_create(cls, database, channel):
        key = str(channel.id)

        guild = await Guild.find_or_create(database, channel)
        polls = database["poll_instances"]

        query = {"key": key}
        existing_record = polls.find_one(query)

        if not existing_record:
            existing_record = {
                "key": key,
                "games": guild.games
            }

            polls.insert_one(existing_record)

        return cls(existing_record)
