from typing import List
import requests
from src.config import TMDB_API_KEY, TMDB_BASE_URL
from src.models.movie import Keyword


class TMDBService:
    def __init__(self) -> None:
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_API_KEY}"
        }

    def get_movie_keywords(self, tmdb_id: int) -> List[Keyword]:
        """Fetch keywords for a specific movie"""
        if not tmdb_id:
            return []
            
        url = f"{TMDB_BASE_URL}/movie/{tmdb_id}/keywords"
        response = requests.get(url, headers=self.headers)
        
        # If movie not found in TMDB, return empty keywords
        if response.status_code == 404:
            return []
            
        response.raise_for_status()
        return [Keyword(**keyword) for keyword in response.json()["keywords"]]
    

