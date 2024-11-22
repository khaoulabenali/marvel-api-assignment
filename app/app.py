from app.utils import get_comics_count_from_characters, get_comics_count_from_comics, plot_comics_count_bar_graph
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from app.models import CharacterComicsData
from fastapi import FastAPI
import matplotlib.pyplot as plt
from io import BytesIO
import random
from fastapi.responses import StreamingResponse


app = FastAPI()


@app.get(
    "/api/characters/comics-counts/from-characters", 
    response_model=List[CharacterComicsData],
    description=(
        "Fetch the count of distinct comics in which a character appears. "
        "This endpoint can optionally filter the result by a character name, "
        "and you can also limit the number of results returned.\n\n"
        "### Query Parameters:\n"
        "- `character_name`: (Optional) The name of the character to filter by.\n"
        "- `limit`: (Optional) The maximum number of results to return.\n\n"
        "### Example Request:\n"
        "GET /api/characters/comics-counts/from-characters?character_name=Spider-Man&limit=5\n\n"
        "### Example Response (200 OK):\n"
        "```json\n"
        "[\n"
        "    {\n"
        "        \"character_name\": \"Spider-Man\",\n"
        "        \"comics_count\": 500\n"
        "    },\n"
        "    {\n"
        "        \"character_name\": \"Iron Man\",\n"
        "        \"comics_count\": 400\n"
        "    }\n"
        "]\n"
        "```"
    ),
    responses={
        200: {
            "description": "A list of characters and their distinct comic counts.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "character_name": "Spider-Man",
                            "comics_count": 500
                        },
                        {
                            "character_name": "Iron Man",
                            "comics_count": 400
                        }
                    ]
                }
            }
        },
        500: {
            "description": "Internal server error. Indicates an issue with the data fetching process.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred during processing."
                    }
                }
            }
        }
    }
)
def get_data_from_characters(
    character_name: Optional[str] = Query(None, description="Filter by character name"),
    limit: Optional[int] = Query(None, description="Limit the number of results returned")
):
    """
    Fetches the count of distinct comics in which a character appears.

    - **character_name**: Optionally filter by a specific character name (e.g., "Spider-Man").
    - **limit**: Optionally limit the number of results returned (e.g., 10).

    ### Example Input:
    - `character_name`: "Spider-Man"
    - `limit`: 10

    ### Example Output:
    ```json
    [
        {
            "character_name": "Spider-Man",
            "comics_count": 500
        },
        {
            "character_name": "Iron Man",
            "comics_count": 400
        }
    ]
    ```
    """
    try:
        result = get_comics_count_from_characters(character_name, limit)
        print(f"result :: {result}")
        return result
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/characters/comics-counts/from-comics", 
    response_model=List[CharacterComicsData],
    description=(
        "Fetch the count of distinct comics for characters, based on comic data, "
        "with an optional filter for character name.\n\n"
        "### Query Parameters:\n"
        "- `character_name`: (Optional) The name of the character to filter by.\n\n"
        "### Example Request:\n"
        "GET /api/characters/comics-counts/from-comics?character_name=Wolverine\n\n"
        "### Example Response (200 OK):\n"
        "```json\n"
        "[\n"
        "    {\n"
        "        \"character_name\": \"Wolverine\",\n"
        "        \"comics_count\": 300\n"
        "    },\n"
        "    {\n"
        "        \"character_name\": \"Thor\",\n"
        "        \"comics_count\": 250\n"
        "    }\n"
        "]\n"
        "```"
    ),
    responses={
        200: {
            "description": "A list of characters and their distinct comic counts.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "character_name": "Wolverine",
                            "comics_count": 300
                        },
                        {
                            "character_name": "Thor",
                            "comics_count": 250
                        }
                    ]
                }
            }
        },
        500: {
            "description": "Internal server error. Indicates an issue with the data fetching process.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred during processing."
                    }
                }
            }
        }
    }
)
def get_data_from_comics(
    character_name: Optional[str] = Query(None, description="Filter by character name")
):
    """
    Fetches the count of distinct comics for characters based on comic data.

    - **character_name**: Optionally filter by a specific character name (e.g., "Wolverine").
    
    ### Example Input:
    - `character_name`: "Wolverine"

    ### Example Output:
    ```json
    [
        {
            "character_name": "Wolverine",
            "comics_count": 300
        },
        {
            "character_name": "Thor",
            "comics_count": 250
        }
    ]
    ```
    """
    try:
        result = get_comics_count_from_comics(character_name)
        print(f"result :: {result}")
        return result
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/visualize/comics-counts")
def visualize_comics_counts(character_name: Optional[str] = Query(None, description="Filter by character name")):
    """
    Fetches and visualizes the count of distinct comics for characters, sorted by the number of comics.

    This endpoint generates a vertical bar graph where:
    - The x-axis represents character indices.
    - The y-axis represents the count of distinct comics each character appears in.
    - Character names are displayed in a separate box on the right side of the graph.

    Query Parameters:
    - character_name: (Optional) Filter by character name (case-insensitive).
    
    Example Request:
    GET /visualize/comics-counts?character_name=Spider-Man

    Example Response:
    A vertical bar graph where:
    - Character names are listed in a legend box on the right side.
    - The bar heights represent the number of comics each character appears in.
    """
    # Sample data: Replace this with actual data from your primary app or database
    comics_data = get_comics_count_from_comics(character_name)
    
    if character_name:
        comics_data = [data for data in comics_data if data["character_name"].lower() == character_name.lower()]

    # Call the utility function to plot the bar chart
    buf = plot_comics_count_bar_graph(comics_data, character_name)

    # Return the generated graph as a PNG image
    return StreamingResponse(buf, media_type="image/png")