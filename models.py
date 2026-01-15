from pydantic import BaseModel
from typing import List, Optional

class ReviewInput(BaseModel):
    username: str
    movie_title: str
    year: int
    genres: List[str]
    rating: int
    comment: str

class ReviewOutput(BaseModel):
    id: str
    user: Optional[str]
    rating: Optional[int]
    comment: Optional[str]
    title: str
    year: Optional[int] = None
    genres: List[str] = []
