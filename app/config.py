import os
import sys
from dotenv import load_dotenv

load_dotenv()

REQUIRED = [
    "BOT_TOKEN",
    "TMDB_API_KEY",
    "OWNER_ID",
    "DATABASE_PATH",
    "PUBLIC_MODE",
]

class Config:
    BOT_TOKEN: str
    TMDB_API_KEY: str
    OWNER_ID: int
    DATABASE_PATH: str
    PUBLIC_MODE: bool

def load_config() -> Config:
    missing = []
    values = {}

    for key in REQUIRED:
        val = os.getenv(key)
        if val is None:
            missing.append(key)
        values[key] = val

    if missing:
        print("Missing environment variables:")
        for k in missing:
            print(f"- {k}")
        sys.exit(1)

    cfg = Config()
    cfg.BOT_TOKEN = values["BOT_TOKEN"]
    cfg.TMDB_API_KEY = values["TMDB_API_KEY"]
    cfg.OWNER_ID = int(values["OWNER_ID"])
    cfg.DATABASE_PATH = values["DATABASE_PATH"]
    cfg.PUBLIC_MODE = values["PUBLIC_MODE"] == "1"

    return cfg
