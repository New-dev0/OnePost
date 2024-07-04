import json
from os import path
from decouple import RepositoryEnv, RepositoryIni


class Config:
    def __init__(self) -> None:
        self._env = RepositoryEnv(".env").data

    def set(self, key: str, value: str) -> None:
        self._env[key] = value
        self.save()

    def get(self, key: str) -> str:
        return self._env.get(key, None)

    def save(self) -> None:
        with open(".env", "w") as file:
            for key, value in self._env.items():
                file.write(f"{key}={value}\n")

def get_settings():
    if not path.exists("settings.json"):
        return {}

    with open("settings.json", "r") as file:
        return json.load(file)

def save_settings(settings: dict):
    with open("settings.json", "w") as file:
        json.dump(settings, file)

config = Config()