from typing import List, Optional, Dict
from collections import Counter, defaultdict
import uuid

from app.schemas.movie import MovieCreate, MovieRead
from app.schemas.stats import GenreCount, StatsResponse, YearData


class MovieStore:
    """
    In-memory store for all movie data.
    Loaded once from Google Drive at startup; supports live additions.
    All operations are O(n) scans — acceptable for thousands of movies in memory.
    """

    def __init__(self):
        self._movies: List[MovieRead] = []
        self.loaded: bool = False
        self.loading: bool = False
        self.error: Optional[str] = None

    # ──────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────

    def set_loading(self):
        self.loading = True
        self.error = None

    def load(self, movies: List[MovieRead]):
        self._movies = movies
        self.loaded = True
        self.loading = False
        self.error = None

    def set_error(self, message: str):
        self.error = message
        self.loading = False

    @property
    def status(self) -> dict:
        return {
            "loaded": self.loaded,
            "loading": self.loading,
            "count": len(self._movies),
            "error": self.error,
        }

    # ──────────────────────────────────────────
    # Read operations
    # ──────────────────────────────────────────

    def search(self, title: str) -> List[MovieRead]:
        """Case-insensitive substring search on title."""
        needle = title.lower().strip()
        return [m for m in self._movies if needle in m.title.lower()]

    def get_stats(self) -> StatsResponse:
        if not self._movies:
            return StatsResponse(
                total_count=0,
                average_rating=0.0,
                top_genres=[],
                by_year={},
            )

        # Top 5 genres
        genre_counter = Counter(m.genre for m in self._movies)
        top_genres = [
            GenreCount(genre=g, count=c)
            for g, c in genre_counter.most_common(5)
        ]

        # Average rating (exclude movies with rating 0 as likely missing data)
        rated = [m for m in self._movies if m.rating > 0]
        avg_rating = (
            round(sum(m.rating for m in rated) / len(rated), 2) if rated else 0.0
        )

        # Movies grouped by year, sorted descending
        by_year: Dict[str, List[str]] = defaultdict(list)
        for m in self._movies:
            year_key = str(m.year) if m.year else "Unknown"
            by_year[year_key].append(m.title)

        by_year_response = {
            year: YearData(count=len(titles), movies=titles)
            for year, titles in sorted(by_year.items(), reverse=True)
        }

        return StatsResponse(
            total_count=len(self._movies),
            average_rating=avg_rating,
            top_genres=top_genres,
            by_year=by_year_response,
        )

    def top_rated(self, limit: int = 10) -> List[MovieRead]:
        """Return movies sorted by rating descending."""
        return sorted(self._movies, key=lambda m: m.rating, reverse=True)[:limit]

    def filter_movies(
        self,
        genre: Optional[str] = None,
        min_rating: Optional[float] = None,
        year: Optional[int] = None,
    ) -> List[MovieRead]:
        """Filter API for technical users — all params optional and combinable."""
        results = self._movies

        if genre:
            results = [m for m in results if m.genre.lower() == genre.lower()]
        if min_rating is not None:
            results = [m for m in results if m.rating >= min_rating]
        if year is not None:
            results = [m for m in results if m.year == year]

        return results

    # ──────────────────────────────────────────
    # Write operations
    # ──────────────────────────────────────────

    def add_movie(self, req: MovieCreate) -> MovieRead:
        """Add a new movie to the in-memory store (does NOT write to Drive)."""
        movie = MovieRead(
            id=str(uuid.uuid4()),
            title=req.title,
            genre=req.genre,
            rating=req.rating,
            year=req.year,
            description=req.description,
            director=req.director,
            source="added",
        )
        self._movies.append(movie)
        return movie


# Module-level singleton shared by route handlers and loader service.
store = MovieStore()
