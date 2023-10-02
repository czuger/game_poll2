import discord


class NoPoll(RuntimeError):
    pass


polls_messages_dict = {}


class PollManager:

    def __init__(self, mongo_client):
        self.db = mongo_client["games_database"]
        self.games_collection = self.db["games"]
        self.polls_collection = self.db["poll_instance"]

    def get_poll(self, channel_id):
        poll = self.polls_collection.find_one({"channel_id": str(channel_id)})
        return poll

    async def refresh_poll_messages(self, message_refresh_function):
        print("in")
        for poll in self.polls_collection.find():
            await message_refresh_function(poll["channel_id"], poll["message_id"])

    def toggle_activity(self, channel, user, activity, activity_type):
        user_key = str(user.id)
        poll = self.get_poll(channel.id)

        activities = poll[activity_type]

        if activity not in activities:
            activities[activity] = [user_key]
        else:
            if user_key in activities[activity]:
                activities[activity].remove(user_key)
            else:
                activities[activity].append(user_key)

        self.polls_collection.update_one({"channel_id": str(channel.id)}, {"$set": {activity_type: activities}})

    def toggle_vote(self, channel, user, game_voted):
        self.toggle_activity(channel, user, game_voted, "choices")

    def toggle_others(self, channel, user, other_action):
        self.toggle_activity(channel, user, other_action, "others")

    def __get_user_names(self, users_ids, guild):
        user_names = []
        for id in users_ids:
            user = guild.get_member(int(id))
            if user:
                name = user.display_name
                user_names.append(name)
            else:
                print(f"Cant find user for {id}")
        return sorted(user_names)

    def __process_data_into_embed(self, data, guild, label_mapping=None):
        info_list = []

        for key, users_ids in data.items():
            if len(users_ids) == 0:
                continue
            user_names = self.__get_user_names(users_ids, guild)
            users_line = ",".join(user_names)
            if label_mapping and key in label_mapping:
                priority = label_mapping[key].get('priority', 5)
                label = label_mapping[key]['label']
            else:
                priority = 5  # Default priority for items without a label mapping.
                label = key
            info_list.append((priority, label, users_line))

        return info_list

    def get_players_embed(self, channel):
        activity_labels = {
            "other": {"label": "Autres activités", "priority": 10},
            "tournament": {"label": "En tournoi", "priority": 9},
            "pkey": {"label": "🔑 Présent avec les clés", "priority": 1}
        }

        embed = discord.Embed(title="A quoi allez vous jouer ?", color=discord.Color.blue())

        activities_info = []
        poll = self.get_poll(channel.id)
        if poll:
            # Autres activités
            activities_info = self.__process_data_into_embed(poll["others"], channel.guild, activity_labels)
            # Joueurs
            activities_info += self.__process_data_into_embed(poll["choices"], channel.guild, None)

            # Sorting by priority and then by label
            activities_info.sort(key=lambda x: (x[0], x[1]))

        for _, label, users_line in activities_info:
            embed.add_field(name="", value="**" + label + "** : " + users_line, inline=False)

        return embed
