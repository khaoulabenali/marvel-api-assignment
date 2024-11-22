import os

# Marvel API Base URLs
# URL for fetching character data from the Marvel API
CHARACTERS_API_URL = "https://gateway.marvel.com:443/v1/public/characters"
# URL for fetching comics data related to a specific character from the Marvel API
COMICS_PER_CHARACTER_API_URL = (
    "https://gateway.marvel.com/v1/public/characters/{character_id}/comics"
)
# URL for fetching comic data from the Marvel API
COMICS_API_URL = "https://gateway.marvel.com:443/v1/public/comics"

# Marvel API Keys
# Public API key used for authentication when accessing Marvel's public API endpoints
MARVEL_API_PUBLIC_KEY = os.getenv("MARVEL_API_PUBLIC_KEY")
# Private API key used for hashing the request and ensuring security in API calls
MARVEL_API_PRIVATE_KEY = os.getenv("MARVEL_API_PRIVATE_KEY")
