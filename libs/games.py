class Games:

    def __init__(self, db, games_collection_dict):
        self.dict = games_collection_dict

        self.db = db

    @classmethod
    async def get_games(cls, db):
        games_collection_dict = {e["key"]: e for e in list(db.games.find())}

        return cls(db, games_collection_dict)
