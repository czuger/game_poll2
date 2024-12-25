import argparse
import logging

from pymongo import MongoClient

logger = logging.getLogger(__name__)


class GameDatabaseManager:
    def __init__(self, db_name="games_database", collection_name="games"):
        """
        Initialiser la connexion à la base de données et à la collection.
        """
        self.client = MongoClient('localhost', 27017, username='root', password='example')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def add_game_or_variant(self, game_name, variants=[]):
        """
        Ajoute un jeu ou des variantes à un jeu existant.

        :param game_name: Le nom du jeu à ajouter ou à mettre à jour.
        :param variants: La liste des variantes à ajouter au jeu.
        """
        existing_game = self.collection.find_one({'name': game_name})
        if existing_game:
            for variant in variants:
                if variant not in existing_game["variants"]:
                    existing_game["variants"].append(variant)
            self.collection.update_one({'name': game_name}, {'$set': {'variants': existing_game["variants"]}})
            logger.debug(f"Variantes ajoutées pour le jeu '{game_name}'.")
        else:
            self.collection.insert_one({'name': game_name, 'variants': variants})
            logger.debug(f"Le jeu '{game_name}' et ses variantes ont été ajoutés avec succès.")

    def delete_game_or_variant(self, game_name, variants=[]):
        """
        Supprime un jeu ou certaines de ses variantes.

        :param game_name: Le nom du jeu à supprimer ou à mettre à jour.
        :param variants: La liste des variantes à supprimer du jeu.
        """
        existing_game = self.collection.find_one({'name': game_name})
        if not existing_game:
            logger.debug(f"Le jeu '{game_name}' n'existe pas.")
            return

        if not variants:
            self.collection.delete_one({'name': game_name})
            logger.debug(f"Le jeu '{game_name}' a été supprimé.")
        else:
            existing_game['variants'] = [v for v in existing_game['variants'] if v not in variants]
            self.collection.update_one({'name': game_name}, {'$set': {'variants': existing_game['variants']}})
            logger.debug(f"Variantes {', '.join(variants)} du jeu '{game_name}' supprimées.")

    def list_games(self):
        """
        Liste tous les jeux et leurs variantes de la base de données.
        """
        all_games = self.collection.find()

        if all_games.collection.count_documents({}) == 0:
            logger.debug("Aucun jeu trouvé dans la base de données.")
            return

        for game in all_games:
            logger.debug(f"Nom du jeu: {game['name']}")
            if game['variants']:
                logger.debug("Variantes:", ", ".join(game['variants']))
            logger.debug("------")


def main():
    parser = argparse.ArgumentParser(description="Gérez des jeux et leurs variantes dans une base de données MongoDB.")

    parser.add_argument("variants", nargs='*', default=[], help="Nom du jeu suivi de ses variantes.")
    parser.add_argument("-l", "--list", action="store_true", help="Lister tous les jeux et leurs variantes.")
    parser.add_argument("-d", "--delete", action="store_true", help="Supprimer le jeu ou la variante spécifiée.")

    args = parser.parse_args()
    manager = GameDatabaseManager()

    if args.list:
        manager.list_games()
        return

    if not args.variants:
        logger.debug("Erreur: Vous devez spécifier un nom de jeu.")
        return

    game_name = args.variants[0]
    actual_variants = args.variants[1:]

    if args.delete:
        manager.delete_game_or_variant(game_name, actual_variants)
    else:
        manager.add_game_or_variant(game_name, actual_variants)


if __name__ == "__main__":
    main()
