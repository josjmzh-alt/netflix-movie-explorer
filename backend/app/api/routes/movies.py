from typing import Optional

from fastapi import APIRouter, Query

from app.schemas.movie import MovieCreate, MovieRead
from app.services.movie_store import store

router = APIRouter(tags=["Movies"])


@router.get("/movies/search", response_model=list[MovieRead])
def search_movies(
    title: str = Query(..., min_length=1, description="Movie title (partial match)")
):
    """Search movies by title using a case-insensitive substring match."""
    return store.search(title)


@router.get("/movies/top-rated", response_model=list[MovieRead])
def get_top_rated(
    limit: int = Query(default=10, ge=1, le=100, description="Number of results")
):
    """Return movies sorted by rating descending."""
    return store.top_rated(limit)


@router.get("/movies", response_model=list[MovieRead])
def filter_movies(
    genre: Optional[str] = Query(default=None, description="Filter by genre (exact match)"),
    min_rating: Optional[float] = Query(default=None, ge=0, le=10, description="Minimum rating"),
    year: Optional[int] = Query(default=None, ge=1888, le=2100, description="Filter by release year"),
):
    """Return movies matching the optional genre, minimum rating, and year filters."""
    return store.filter_movies(genre=genre, min_rating=min_rating, year=year)


@router.post("/movies", response_model=MovieRead, status_code=201)
def add_movie(movie: MovieCreate):
    """Add a new movie to the in-memory store."""
    return store.add_movie(movie)
