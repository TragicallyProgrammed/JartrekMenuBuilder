from dotenv import load_dotenv
from pathlib import Path
from os import getenv

load_dotenv()
env_path = Path('.')/'.env'  # Gets the path of the .env file
"""Path to the .env files."""

load_dotenv(dotenv_path=env_path)  # Opens the .env file

ENVIROMENT = getenv("ENVIROMENT")  # Retrieves the enviroment variable
"""String variable defining the enviroment to start flask in."""

DB_NAME = getenv("DATABASE_NAME")  # Retrieves the db_name variable
"""The name of the database."""

KEY = getenv("KEY")  # Retrieves the key variable
"""Secret key for Flask."""
