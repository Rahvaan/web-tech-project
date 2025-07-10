from datetime import date, datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class Keyword(BaseModel):
    id: int
    name: str


class Ids(BaseModel):
    trakt: int
    slug: str
    imdb: Optional[str] = None
    tmdb: Optional[int] = None


class Stats(BaseModel):
    watchers: int
    plays: int
    collectors: int
    comments: int
    lists: int
    votes: int
    recommended: int


class Rating(BaseModel):
    rating: float
    votes: int
    distribution: Dict[str, int] = Field(default_factory=dict)


class Movie(BaseModel):
    # Basic information
    title: str
    year: int
    ids: Ids
    tagline: Optional[str] = None
    overview: Optional[str] = None
    released: Optional[date] = None
    runtime: Optional[int] = None
    country: Optional[str] = None
    updated_at: Optional[datetime] = None
    trailer: Optional[str] = None
    homepage: Optional[str] = None
    status: Optional[str] = None
    language: Optional[str] = None
    available_translations: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    certification: Optional[str] = None

    # Statistics
    stats: Stats
    rating: Rating

    # Additional data
    keywords: List[Keyword] = Field(default_factory=list)  # From TMDB

    def get_filename(self) -> str:
        """Generate a clean filename for the movie data"""
        clean_title = "".join(
            c if c.isalnum() else "_" for c in self.title
        )
        return f"{clean_title}_{self.ids.trakt}.json"
