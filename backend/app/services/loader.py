from app.schemas.movie import MovieRead
from app.core.structured_log import log_event
from app.services.drive import load_movies_from_drive
from app.services.movie_store import store


def load_data() -> None:
    """Load Drive movie data into the in-memory store."""
    try:
        log_event("movie_load_task_start")
        store.set_loading()
        raw = load_movies_from_drive()
        movies = [MovieRead(**m) for m in raw]
        store.load(movies)
        log_event("movie_load_task_complete", movie_count=len(movies))
    except Exception as exc:
        store.set_error(str(exc))
        log_event("movie_load_task_error", error=str(exc))
        print(f"Drive load failed: {exc}")
