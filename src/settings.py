from dotenv import load_dotenv
from pathlib import Path
from os import getenv

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

ENVIROMENT = getenv("ENVIROMENT")
DEBUG = getenv("DEBUG")

DB_NAME = getenv("DATABASE_NAME")


KEY = getenv("KEY")
TRACK_MODIFICATIONS = getenv("TRACK_MODIFICATIONS")
