
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()


CHARACTERS_API_URL = "https://gateway.marvel.com:443/v1/public/characters"
COMICS_PER_CHARACTER_API_URL = "https://gateway.marvel.com/v1/public/characters/{character_id}/comics"

MARVEL_API_PUBLIC_KEY = os.getenv("MARVEL_API_PUBLIC_KEY")
MARVEL_API_PRIVATE_KEY = os.getenv("MARVEL_API_PRIVATE_KEY")
# MARVEL_API_PUBLIC_KEY = "76a71a1ec9fc531098a3ec3d9e097043"
# MARVEL_API_PRIVATE_KEY = "75eee547aa8004201ab02df0f976043d9607b232"
