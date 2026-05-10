from typing import Optional

from pydantic import BaseModel, Field


class MovieRead(BaseModel):
    id: str
    title: str
    genre: str = "Unknown"
    rating: float = 0.0
    year: int = 0
    description: Optional[str] = None
    director: Optional[str] = None
    source: str = "drive"  # "drive" | "added"


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1)
    genre: str = Field(..., min_length=1)
    rating: float = Field(..., ge=0.0, le=10.0)
    year: int = Field(..., ge=1888, le=2100)
    description: Optional[str] = None
    director: Optional[str] = None
