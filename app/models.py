
from pydantic import BaseModel
from typing import Optional

# Response model to structure the data
class CharacterComicsData(BaseModel):
    character_name: str
    comics_count: int

