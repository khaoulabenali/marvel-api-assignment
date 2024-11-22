from typing import Optional, Tuple, Any, Union, Dict, List
import app.config as config
import time
from hashlib import md5
import requests as rq
import polars as pl
from functools import reduce
import matplotlib.pyplot as plt
from io import BytesIO
import random

def get_comics_count_from_characters(
    character_name: str, limit: int
) -> Union[pl.DataFrame, Dict[str, str]]:
    """
    Fetches comics data and calculates the count of distinct comics featuring the specified character.

    Args:
        character_name (str): The name of the character to filter comics for.
        limit (int): The maximum number of comics to fetch.

    Returns:
        Union[pl.DataFrame, Dict[str, str]]:
            - A Polars DataFrame with the aggregated results if successful.
            - A dictionary with an error message if fetching or processing fails.
    """
    try:
        # Fetch data and handle potential issues
        data: Tuple[Any, Union[None, str]] = fetch_characters(limit)
        comics_data, error = data

        if error:
            error_message: str = f"Error fetching data: {error}"
            print(error_message)
            return {"error": error_message}

        try:
            # Aggregate data based on the specified character name
            result: Dict = aggregate_characters(comics_data, character_name)

            # Display the result for debugging or confirmation
            print(result)

            # Return the aggregated DataFrame
            return result
        except Exception as agg_error:
            agg_error_message: str = f"Error during data aggregation: {agg_error}"
            print(agg_error_message)
            return {"error": agg_error_message}

    except Exception as fetch_error:
        fetch_error_message: str = (
            f"Unexpected error during data fetching: {fetch_error}"
        )
        print(fetch_error_message)
        return {"error": fetch_error_message}


def fetch_characters(
    limit: Union[int, None] = None
) -> Tuple[Union[dict, None], Union[Exception, None]]:
    """
    Fetches data from the Marvel API with optional limit on the number of characters.

    Args:
        limit (Union[int, None]): The maximum number of characters to fetch. If None, no limit is applied.

    Returns:
        Tuple[Union[dict, None], Union[Exception, None]]:
            - A dictionary containing the API response data if successful.
            - An Exception object if an error occurs.
    """
    try:
        # Generate the API hash using timestamp, private key, and public key
        ts: str = str(time.time())
        hash_str: str = md5(
            f"{ts}{config.MARVEL_API_PRIVATE_KEY}{config.MARVEL_API_PUBLIC_KEY}".encode(
                "utf8"
            )
        ).hexdigest()

        # Build request parameters
        params = {
            "apikey": config.MARVEL_API_PUBLIC_KEY,
            "ts": ts,
            "hash": hash_str,
            "orderBy": "name",
        }
        if limit:
            params["limit"] = limit

        # Make the API request
        r = rq.get(config.CHARACTERS_API_URL, params=params)
        r.raise_for_status()  # Raise an error for non-2xx responses
        return r.json(), None

    except rq.exceptions.RequestException as e:
        # Handle errors related to the HTTP request
        return None, e

    except Exception as e:
        # Handle other unexpected errors
        return None, e


def aggregate_characters(
    data: dict, character_name: Optional[str] = None
) -> Union[List[Dict[str, Union[str, int]]], Dict[str, str]]:
    """
    Aggregates character data from the Marvel API, filters by character name if provided,
    and adds a column for the count of comics associated with each character.

    Args:
        data (dict): The API response containing character data.
        character_name (Optional[str]): The name of the character to filter by. If None, no filtering is applied.

    Returns:
        Union[List[Dict[str, Union[str, int]]], Dict[str, str]]:
            - A list of dictionaries containing character names and their comic counts if successful.
            - A dictionary with an error message if the data could not be fetched or processed.
    """
    try:
        # Extract character results from the response
        results = data.get("data", {}).get("results", [])
        if not results:
            return {"error": "No characters found in the data"}

        # Prepare the character data
        characters = [
            {"character_name": char["name"], "character_id": char["id"]}
            for char in results
        ]

        # Create a Polars DataFrame
        characters_df = pl.DataFrame(characters)

        # Apply filters if a character name is provided
        if character_name:
            characters_df = characters_df.filter(
                pl.col("character_name") == character_name
            )

        # Add a new column for comics count based on the character ID
        characters_df = characters_df.with_columns(
            pl.col("character_id")
            .apply(lambda id: get_comics_count(id))
            .alias("comics_count")
        )

        # Convert the DataFrame to a list of dictionaries for JSON response
        data = characters_df.select(["character_name", "comics_count"]).to_dicts()
        print(f"data :: {data}")
        return data

    except Exception as e:
        # Handle errors during data processing
        error_message = f"Error processing character data: {e}"
        print(error_message)
        return {"error": error_message}


def get_comics_count(character_id: int) -> int:
    """
    Fetches the count of comics associated with a specific character from the Marvel API.

    Args:
        character_id (int): The ID of the character whose comics need to be fetched.

    Returns:
        int: The count of comics for the given character. Returns 0 if an error occurs.
    """
    try:
        # Generate the API hash using timestamp, private key, and public key
        ts: str = str(time.time())
        hash_str: str = md5(
            f"{ts}{config.MARVEL_API_PRIVATE_KEY}{config.MARVEL_API_PUBLIC_KEY}".encode(
                "utf8"
            )
        ).hexdigest()

        # Prepare request parameters
        params = {
            "apikey": config.MARVEL_API_PUBLIC_KEY,
            "ts": ts,
            "hash": hash_str,
        }

        # Make the API request
        response: rq.Response = rq.get(
            config.COMICS_PER_CHARACTER_API_URL.format(character_id=character_id),
            params=params,
        )

        # Check if the response is successful
        if response.status_code == 200:
            comics_data: dict = response.json()
            comics_list: list = comics_data.get("data", {}).get("results", [])
            print(f"comics_list :: {comics_list}")
            return len(comics_list)

        # Handle non-200 status codes
        error_message: str = (
            f"Error fetching comics for character ID {character_id}: {response.status_code} - {response.reason}"
        )
        print(error_message)
        return 0

    except rq.exceptions.RequestException as e:
        # Handle request-related errors
        error_message: str = (
            f"Request error fetching comics for character ID {character_id}: {e}"
        )
        print(error_message)
        return 0

    except Exception as e:
        # Handle unexpected errors
        error_message: str = (
            f"Unexpected error fetching comics for character ID {character_id}: {e}"
        )
        print(error_message)
        return 0


def get_comics_count_from_comics(
    character_name: str,
) -> Union[pl.DataFrame, Dict[str, str]]:
    """
    Fetches the list of comics and their associated characters, aggregates the results,
    and returns the count of distinct comics per character, optionally filtering by character name.

    Args:
        character_name (str): The name of the character to filter by. If None, no filtering is applied.

    Returns:
        Union[pl.DataFrame, Dict[str, str]]:
            - A Polars DataFrame containing character names and the count of distinct comics.
            - A dictionary containing an error message if the request or processing fails.
    """
    try:
        # Fetch the comics data using the get_comics function
        result = get_comics()

        # If an error occurred, return the error message
        if isinstance(result, dict) and "error" in result:
            return result

        # Aggregate the comics data
        aggregated_data = aggregate_comics_results(result, character_name)

        # Return the aggregated data as a list of dictionaries
        return aggregated_data.to_dicts()

    except Exception as e:
        # Handle any unforeseen errors in get_comics_count_from_comics
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)
        return {"error": error_message}


def get_comics() -> Union[Dict[str, str], list]:
    """
    Sends a request to the Marvel Comics API to retrieve comic data.

    Returns:
        Union[Dict[str, str], list]:
            - A list of comic data if the request is successful.
            - A dictionary with an error message if the request fails or the response is invalid.
    """
    try:
        # Generate API hash using timestamp, private and public keys
        ts: str = str(time.time())
        hash_str: str = md5(
            f"{ts}{config.MARVEL_API_PRIVATE_KEY}{config.MARVEL_API_PUBLIC_KEY}".encode(
                "utf8"
            )
        ).hexdigest()

        # Prepare request parameters
        params = {
            "apikey": config.MARVEL_API_PUBLIC_KEY,
            "ts": ts,
            "hash": hash_str,
        }

        # Make the request to the Marvel API
        response = rq.get(config.COMICS_API_URL, params=params)

        # Raise exception if the request fails
        response.raise_for_status()

        # Extract the comic data from the response
        result = response.json().get("data", {}).get("results", [])

        # Check if there is any data to process
        if not result:
            return {"error": "No comic data found in the response."}

        return result

    except rq.exceptions.RequestException as e:
        # Handle HTTP request errors
        error_message = f"Request error: {str(e)}"
        print(error_message)
        return {"error": error_message}

    except Exception as e:
        # Handle any other unforeseen errors
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)
        return {"error": error_message}


def aggregate_comics_results(
    comics_data: List[Dict], character_name: str
) -> pl.DataFrame:
    """
    Processes the fetched comic data, aggregates the count of distinct comics per character.

    Args:
        comics_data (list): A list of comic data containing comic IDs and associated characters.
        character_name (str): The character name to filter by, if provided.

    Returns:
        pl.DataFrame: A Polars DataFrame containing the character names and the count of distinct comics per character.
    """
    try:
        # Process the comic data to extract character names using map and lambda
        data = list(
            map(
                lambda comic: {
                    "id": comic["id"],
                    "characters": list(
                        map(
                            lambda character: character["name"],
                            comic["characters"]["items"],
                        )
                    ),
                },
                filter(lambda comic: comic["characters"]["available"] > 0, comics_data),
            )
        )

        # Create a Polars DataFrame from the extracted data using map and lambda
        df = pl.DataFrame(
            {
                "comic_id": list(
                    map(
                        lambda item: item["id"],
                        reduce(
                            lambda x, y: x + y,
                            map(
                                lambda item: [
                                    {"id": item["id"]} for _ in item["characters"]
                                ],
                                data,
                            ),
                        ),
                    )
                ),
                "character_name": list(
                    reduce(
                        lambda x, y: x + y, map(lambda item: item["characters"], data)
                    )
                ),
            }
        )

        # Apply filters if a character name is provided
        if character_name:
            df = df.filter(pl.col("character_name") == character_name)

        # Group by character name and count unique comics per character
        aggregated_data = df.groupby("character_name").agg(
            pl.col("comic_id").n_unique().alias("comics_count")
        )

        return aggregated_data

    except KeyError as e:
        # Handle case when a key is missing in the expected data structure
        print(f"Error: Missing key {str(e)} in the comic data.")
        return pl.DataFrame({"error": [f"Missing key {str(e)} in the comic data."]})

    except TypeError as e:
        # Handle any type errors (e.g., unexpected data type in the comics_data)
        print(f"Error: Type error encountered - {str(e)}")
        return pl.DataFrame({"error": ["Type error encountered during processing."]})

    except Exception as e:
        # Handle any unforeseen errors
        print(f"Unexpected error: {str(e)}")
        return pl.DataFrame(
            {"error": ["An unexpected error occurred during processing."]}
        )



def plot_comics_count_bar_graph(comics_data: List[dict], character_name: Optional[str]) -> BytesIO:
    """
    Generates a vertical bar graph representing comics count per character.

    Args:
        comics_data (list): List of comics data, each containing character names and comics count.
        character_name (str, optional): The character name to filter the data.

    Returns:
        BytesIO: A buffer containing the generated image in PNG format.
    """
    # Sort the comics data by comics count in descending order
    comics_data_sorted = sorted(comics_data, key=lambda x: x["comics_count"], reverse=True)
    
    # Extract sorted character names and comics counts
    characters = [data["character_name"] for data in comics_data_sorted]
    comics_count = [data["comics_count"] for data in comics_data_sorted]

    # Generate distinct colors for each character
    colors = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(len(characters))]

    # Create a vertical bar chart using Matplotlib
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot bars with colors and indexes
    bars = ax.bar(range(len(comics_count)), comics_count, color=colors)
    
    # Set labels and title
    ax.set_xlabel("Character Index")
    ax.set_ylabel("Comics Count")
    ax.set_title(f"Comics Count per Character")

    # Add the character names in a separate box to the right of the chart
    ax.legend(
        bars,
        characters,
        loc='upper left',
        bbox_to_anchor=(1, 1),
        title="Character Names",
        frameon=False,
    )

    # Save the plot to a BytesIO buffer and return as an image
    buf = BytesIO()
    plt.tight_layout()  # Ensure the layout fits well with the legend box
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf