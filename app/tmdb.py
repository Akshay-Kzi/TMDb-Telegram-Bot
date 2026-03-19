import requests
from app.config import load_config

cfg = load_config()

BASE_URL = "https://api.themoviedb.org/3"


def search_movie(query: str):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": cfg.TMDB_API_KEY,
        "query": query,
        "include_adult": False,
    }

    r = requests.get(url, params=params, timeout=5)
    r.raise_for_status()
    return r.json().get("results", [])


def get_movie_details(tmdb_id: int):
    url = f"{BASE_URL}/movie/{tmdb_id}"
    params = {
        "api_key": cfg.TMDB_API_KEY,
        "append_to_response": "credits",
    }

    r = requests.get(url, params=params, timeout=5)
    r.raise_for_status()
    return r.json()


def normalize_movie(data: dict):
    # Extract credits
    credits = data.get("credits", {})
    crew = credits.get("crew", [])
    cast = credits.get("cast", [])
    
    # Get directors
    directors = [person["name"] for person in crew if person.get("job") == "Director"]
    
    # Get writers (screenplay, writer, etc.)
    writers = [person["name"] for person in crew if person.get("job") in ["Screenplay", "Writer", "Story"]]
    
    # Get top 5 cast members
    top_cast = [person["name"] for person in cast[:5]]
    
    # Get languages
    languages = [lang["english_name"] for lang in data.get("spoken_languages", [])]
    
    return {
        "title": data.get("title"),
        "year": (data.get("release_date") or "")[:4],
        "rating": data.get("vote_average"),
        "votes": data.get("vote_count"),
        "runtime": data.get("runtime"),
        "genres": ", ".join(g["name"] for g in data.get("genres", [])),
        "plot": data.get("overview"),
        "poster": (
            f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
            if data.get("poster_path") else None
        ),
        "language": ", ".join(languages),
        "director": ", ".join(directors),
        "writer": ", ".join(writers),
        "cast": ", ".join(top_cast),
    }
