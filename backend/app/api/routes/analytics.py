from fastapi import APIRouter

from app.schemas.stats import StatsResponse
from app.services.movie_store import store

router = APIRouter(tags=["Analytics"])


@router.get("/stats", response_model=StatsResponse)
def get_stats():
    """Return aggregate movie stats."""
    return store.get_stats()
