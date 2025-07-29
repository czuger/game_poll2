import json
import logging
import os

from poll.libs.misc.project_root import find_project_root


class ConfigReader:
    def __init__(self, config_file_path="config.json"):
        """
        Initialize the ConfigReader with the path to the config file.

        Args:
            config_file_path (str): Path to the configuration file. Defaults to "config.json".
        """
        self.config_file_path = config_file_path
        self.config = self._load_config()

    def _load_config(self):
        """
        Load the configuration from the JSON file.

        Returns:
            dict: The configuration as a dictionary.

        Raises:
            FileNotFoundError: If the config file doesn't exist.
            json.JSONDecodeError: If the config file is not valid JSON.
        """
        try:
            root_dir = find_project_root()

            self.config_file_path = root_dir / self.config_file_path

            if not os.path.exists(self.config_file_path):
                raise FileNotFoundError(f"Config file not found: {self.config_file_path}")

            with open(self.config_file_path, 'r') as config_file:
                return json.load(config_file)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in config file: {e.msg}", e.doc, e.pos)

    def get_discord_config(self):
        """
        Get the Discord configuration.

        Returns:
            dict: The Discord configuration.
        """
        return self.config.get("discord", {})

    def get_discord_token(self):
        """
        Get the Discord token.

        Returns:
            str: The Discord token.
        """
        return self.get_discord_config().get("token", None)

    def get_mongo_config(self):
        """
        Get the MongoDB configuration.

        Returns:
            dict: The MongoDB configuration.
        """
        return self.config["mongo"]

    def get_db_name(self):
        return self.get_mongo_config()["db_name"]

    def get_mongo_connection_string(self):
        """
        Get the MongoDB connection string.

        Returns:
            str: The MongoDB connection string.
        """
        mongo_config = self.get_mongo_config()
        user = mongo_config.get("user", "")
        password = mongo_config.get("pass", "")
        server = mongo_config.get("server", "localhost")

        if user and password:
            return f"mongodb://{user}:{password}@{server}"
        return f"mongodb://{server}"

    def get_logging_config(self):
        """
        Get the logging configuration.

        Returns:
            dict: The logging configuration.
        """
        return self.config.get("logging", {})

    def get_logging_level(self):
        """
        Get the logging level as a logging module constant.

        Returns:
            int: The logging level constant from the logging module.
        """
        level_str = self.get_logging_config().get("logging_level", "INFO").upper()

        # Map string logging levels to logging module constants
        level_map = {
            "CRITICAL": logging.CRITICAL,
            "FATAL": logging.FATAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "WARN": logging.WARN,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "NOTSET": logging.NOTSET
        }

        # Return the logging level constant or default to INFO if not found
        return level_map.get(level_str, logging.INFO)

    def get_log_directory(self):
        """
        Get the log directory.

        Returns:
            str: The log directory.
        """
        return self.get_logging_config().get("log_directory", "game_poll2_logs")
