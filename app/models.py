from pydantic import BaseModel


class CharacterComicsData(BaseModel):
    """
    Pydantic model that represents the data of a character and their associated comic count.

    This model is used to return the character's name along with the number of unique comics in which they appear.

    Attributes:
        character_name (str): The name of the character.
        comics_count (int): The total number of unique comics the character appears in.

    Example:
        {
            "character_name": "Spider-Man",
            "comics_count": 500
        }
    """

    character_name: str  # Name of the character (e.g., "Spider-Man")
    comics_count: int  # The number of unique comics the character appears in

    class Config:
        """
        Pydantic configuration for customizing the generated JSON schema for this model.
        """

        json_schema_extra = {
            "example": {"character_name": "Spider-Man", "comics_count": 500}
        }
