
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from app.models import CharacterComicsData
from app.utils import get_comics_count_per_character

app = FastAPI()




@app.get("/api/characters/comics-counts", response_model=List[CharacterComicsData])
def get_data(
        character_name: Optional[str] = Query(None, description="Filter by character name"),
        limit: Optional[int] = Query(None, description="Data lenght limit")
    ):
    try:
        result = get_comics_count_per_character(character_name,limit)
        print(f"result :: {result}")
        return result
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(status_code=500, detail=str(e))
    


