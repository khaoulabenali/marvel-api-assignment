import polars as pl
from fastapi import Query
from typing import Optional
import app.config as config
import time
from hashlib import md5
import requests as rq
import polars as pl

def get_comics_count_per_character(
        character_name,
        limit
    ):
    data, error  = fetch(limit)
    if not error:
        df = aggregate(data,character_name)
        print(df)
        return df 
    print(f"Error fetching data: {error}")
    return {"error": str(error)}
    

def fetch(limit = None):
    ts = str(time.time())  
    hash_str = md5(f"{ts}{config.MARVEL_API_PRIVATE_KEY}{config.MARVEL_API_PUBLIC_KEY}".encode("utf8")).hexdigest()
    
    params = {
        "apikey": config.MARVEL_API_PUBLIC_KEY,
        "ts": ts,
        "hash": hash_str,
        "orderBy": "name",
    }

    if limit:
        params["limit"] = limit
    
    try:
        r = rq.get(config.CHARACTERS_API_URL, params=params) 
        r.raise_for_status()  # Raise an error for bad responses
    except rq.exceptions.RequestException as e:
        return None, e
    else:
        return r.json(), None
    

# Function to get the list of comics for a given character ID
def get_comics_count(character_id):
    ts = str(time.time())  
    hash_str = md5(f"{ts}{config.MARVEL_API_PRIVATE_KEY}{config.MARVEL_API_PUBLIC_KEY}".encode("utf8")).hexdigest()
    
    params = {
        "apikey": config.MARVEL_API_PUBLIC_KEY,
        "ts": ts,
        "hash": hash_str,

    }
    response = rq.get(config.COMICS_PER_CHARACTER_API_URL.format(character_id=character_id), params=params)
    
    # Check if the response is successful (status code 200)
    if response.status_code == 200:
        comics_data = response.json()
        comics_list = comics_data.get('data', {}).get('results', [])
        print(f"comics_list :: {comics_list}")
        return len(comics_list)
    else:
        print(f"Error fetching comics for character ID {character_id}")
        return 0
# Transform data to Polars DataFrame
def aggregate(data,character_name):
    results = data['data']['results']
    characters = list(
        map(
            lambda char: {"character_name": char['name'], "character_id": char['id']},
            results
        )
    )
    characters_df = pl.DataFrame(characters)
    # Apply filters based on optional query parameters
    if characters_df is not None:
        if character_name:
            characters_df = characters_df.filter(pl.col("character_name") == character_name)
        characters_df = characters_df.with_columns(
            pl.col("character_id").apply(lambda id: get_comics_count(id)).alias("comics_count")
        )
        print(characters_df)
        # Convert the Polars DataFrame to a list of dictionaries for JSON response
        data = characters_df.select(["character_name","comics_count"]).to_dicts()
        print(f"data :: {data}")
        return data

    return {"error": "Data could not be fetched"}
    
