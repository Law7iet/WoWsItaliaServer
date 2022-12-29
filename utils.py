from enum import Enum


class DBCollections(str, Enum):
    CONFIG = "config"
    CLANS = "clans"
    PLAYERS = "players"

    def __str__(self) -> str:
        return self.value
