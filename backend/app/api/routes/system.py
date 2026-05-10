from fastapi import APIRouter

from app.schemas.status import StatusResponse
from app.services.drive import is_authenticated
from app.services.movie_store import store

router = APIRouter(tags=["System"])


@router.get("/status", response_model=StatusResponse)
def get_status():
    """Return auth state, load state, and current movie count."""
    return {**store.status, "authenticated": is_authenticated()}
