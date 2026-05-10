import json
import uuid
from typing import List, Optional

from app.core.structured_log import log_event


def _get(data: dict, *keys):
    """Return the first key found in data, case-insensitively."""
    lower_data = {k.lower(): v for k, v in data.items()}
    for key in keys:
        val = lower_data.get(key.lower())
        if val is not None:
            return val
    return None


def normalize_movie(data: dict) -> Optional[dict]:
    """Convert an arbitrary movie dict into the app's canonical shape."""
    title = _get(data, "title", "name", "movie_title", "film_title")
    if not title:
        log_event(
            "movie_normalize_skipped",
            debug=True,
            reason="missing_title",
            keys=sorted(data.keys()),
        )
        return None

    genre_raw = _get(data, "genre", "genres", "category", "categories")
    if isinstance(genre_raw, list):
        genre = str(genre_raw[0]) if genre_raw else "Unknown"
    else:
        genre = str(genre_raw) if genre_raw else "Unknown"

    rating_raw = _get(
        data, "rating", "score", "imdb_rating", "vote_average", "imdbRating"
    )
    try:
        rating = float(rating_raw) if rating_raw is not None else 0.0
        rating = round(min(10.0, max(0.0, rating)), 1)
    except (ValueError, TypeError):
        rating = 0.0

    year_raw = _get(
        data, "year", "release_year", "releaseYear", "release_date", "releaseDate"
    )
    try:
        year = int(str(year_raw)[:4]) if year_raw else None
    except (ValueError, TypeError):
        year = None

    movie = {
        "id": str(uuid.uuid4()),
        "title": str(title).strip(),
        "genre": genre.strip(),
        "rating": rating,
        "year": year,
        "description": _get(data, "description", "overview", "plot", "synopsis"),
        "director": _get(data, "director", "directors"),
        "source": "drive",
    }
    log_event(
        "movie_normalized",
        debug=True,
        title=movie["title"],
        genre=movie["genre"],
        rating=movie["rating"],
        year=movie["year"],
    )
    return movie


def parse_json_file(content: str, file_name: str) -> List[dict]:
    """
    Parse a JSON file into normalised movie dicts.

    Supported shapes:
    - array at root
    - wrapped array under common keys like movies/data/results
    - single movie object
    """
    movies: List[dict] = []
    log_event("movie_json_parse_start", debug=True, file_name=file_name, byte_count=len(content.encode("utf-8")))
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        log_event("movie_json_parse_error", debug=True, file_name=file_name, error=str(exc))
        print(f"Could not parse {file_name}: {exc}")
        return movies

    def extract_list(items):
        for item in items:
            if isinstance(item, dict):
                movie = normalize_movie(item)
                if movie:
                    movies.append(movie)

    if isinstance(data, list):
        log_event("movie_json_shape", debug=True, file_name=file_name, shape="root_array", item_count=len(data))
        extract_list(data)
    elif isinstance(data, dict):
        for wrapper_key in ("movies", "data", "results", "items", "films", "content"):
            if wrapper_key in data and isinstance(data[wrapper_key], list):
                log_event(
                    "movie_json_shape",
                    debug=True,
                    file_name=file_name,
                    shape="wrapped_array",
                    wrapper_key=wrapper_key,
                    item_count=len(data[wrapper_key]),
                )
                extract_list(data[wrapper_key])
                log_event("movie_json_parse_complete", debug=True, file_name=file_name, movie_count=len(movies))
                return movies

        log_event(
            "movie_json_shape",
            debug=True,
            file_name=file_name,
            shape="single_object",
            keys=sorted(data.keys()),
        )
        movie = normalize_movie(data)
        if movie:
            movies.append(movie)
    else:
        log_event(
            "movie_json_shape_unsupported",
            debug=True,
            file_name=file_name,
            shape=type(data).__name__,
        )

    log_event("movie_json_parse_complete", debug=True, file_name=file_name, movie_count=len(movies))
    return movies
