# Dead code, keeping for history

import time
from typing import Dict


class AddGameUserDict:
    _instance: 'AddGameUserDict' = None  # Singleton instance
    _dict: Dict[int, float]  # Dictionary to store user_id (int) and timestamp (float)
    TIME_THRESHOLD: int = 300  # Class variable for the 5-minute threshold in seconds

    def __new__(cls, *args, **kwargs) -> 'AddGameUserDict':
        # Ensure only one instance of the class is created
        if cls._instance is None:
            cls._instance = super(AddGameUserDict, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize the dictionary only if it hasn't been initialized before
        if not hasattr(self, '_dict'):
            self._dict = {}

    def set(self, user_id: int) -> None:
        """
        Set the user_id in the dictionary with the current timestamp.
        """
        current_time = time.time()  # Get the current timestamp
        self._dict[user_id] = current_time  # Modify the dictionary

    def clear(self, user_id: int) -> None:
        """
        Remove the user_id from the dictionary if it exists.
        """
        if user_id in self._dict:
            del self._dict[user_id]  # Delete the user_id from the dictionary

    def user_waiting(self, user_id: int) -> bool:
        """
        Check if the user_id has been in the dictionary for more than TIME_THRESHOLD seconds.
        Returns True if the user_id's timestamp is older than the threshold, else False.
        """
        if user_id in self._dict:
            current_time = time.time()
            stored_time = self._dict[user_id]
            # Check if the difference between the current time and the stored time exceeds TIME_THRESHOLD
            return (current_time - stored_time) < self.TIME_THRESHOLD
        return False  # Return False if the user_id is not found

    def get_dict(self) -> Dict[int, float]:
        """
        Returns the internal dictionary.
        """
        return self._dict

    def __repr__(self) -> str:
        """
        Return a string representation of the class.
        """
        return f"AddGameUserDict({self._dict})"
