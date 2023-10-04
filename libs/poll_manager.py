class NoPoll(RuntimeError):
    pass


class PollManager:

    def __init__(self, mongo_client):
        self.db = mongo_client["games_database"]
        self.games_collection = self.db["games"]
        self.polls_collection = self.db["poll_instance"]

    def get_poll(self, channel_id):
        poll = self.polls_collection.find_one({"channel_id": str(channel_id)})
        if not poll:
            raise NoPoll

        return poll

    def toggle_vote(self, channel, user, game_voted):
        user_id = user.id

        poll = self.get_poll(channel.id)

        user_key = str(user_id)
        if game_voted not in poll["choices"]:
            poll["choices"][game_voted] = [user_key]
        else:
            players = poll["choices"][game_voted]
            if user_key in players:
                players.remove(user_key)
            else:
                players.append(user_key)

            poll["choices"][game_voted] = players

        self.polls_collection.update_one({"channel_id": str(channel.id)}, {"$set": {"choices": poll["choices"]}})

    def toggle_others(self, channel, user, other_action):
        user_id = user.id

        poll = self.get_poll(channel.id)

        user_key = str(user_id)
        if other_action not in poll["others"]:
            poll["others"][other_action] = [user_key]
        else:
            players = poll["others"][other_action]
            if user_key in players:
                players.remove(user_key)
            else:
                players.append(user_key)

            poll["others"][other_action] = players

        self.polls_collection.update_one({"channel_id": str(channel.id)}, {"$set": {"others": poll["others"]}})

    def get_players_string(self, channel):
        poll = self.get_poll(channel.id)

        lines = ["A quoi allez vous jouer ?"]

        # Autres activités
        activity_labels = {
            "other": "Autres activités",
            "tournament": "En tournoi",
            "pkey": "🔑 Présent avec les clés"
        }

        for activity, users_ids in poll["others"].items():

            if len(users_ids) == 0:
                continue

            user_names = []
            for id in users_ids:
                user = channel.guild.get_member(int(id))
                if user:
                    name = user.display_name
                    user_names.append(name)
                else:
                    print(f"Cant find user for {id}")

            user_names.sort()
            users_line = ",".join(user_names)
            activity_name = activity_labels[activity]
            lines.append(f"{activity_name} : {users_line}")

        # Joueurs
        for game, users_ids in poll["choices"].items():

            if len(users_ids) == 0:
                continue

            user_names = []
            for id in users_ids:
                user = channel.guild.get_member(int(id))
                if user:
                    name = user.display_name
                    user_names.append(name)
                else:
                    print(f"Cant find user for {id}")

            user_names.sort()
            users_line = ",".join(user_names)
            lines.append(f"{game} : {users_line}")

        return "\n".join(lines)
