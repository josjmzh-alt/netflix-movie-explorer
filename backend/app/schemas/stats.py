from typing import Dict, List

from pydantic import BaseModel


class GenreCount(BaseModel):
    genre: str
    count: int


class YearData(BaseModel):
    count: int
    movies: List[str]


class StatsResponse(BaseModel):
    total_count: int
    average_rating: float
    top_genres: List[GenreCount]
    by_year: Dict[str, YearData]
