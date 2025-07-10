from typing import List, Dict, Generator
import requests
import time
from datetime import datetime
from tqdm.auto import tqdm
from colorama import Fore, Style
from src.config import (
    TRAKT_CLIENT_ID,
    TRAKT_BASE_URL,
    TRAKT_EXTENDED_INFO
)
from src.models.movie import Movie, Rating, Stats, Ids
from src.services.tmdb_service import TMDBService
from src.utils.file_handler import FileHandler


class TraktService:
    # Trakt API allows 1000 requests per 5 minutes
    MAX_REQUESTS = 1000
    WINDOW_SIZE = 300  # 5 minutes in seconds
    REQUEST_DELAY = WINDOW_SIZE / MAX_REQUESTS  # Time between requests
    
    # Year range for movies
    START_YEAR = 2010
    END_YEAR = 2023
    
    # Batch size for processing
    BATCH_SIZE = 50

    def __init__(self) -> None:
        self.headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": TRAKT_CLIENT_ID
        }
        self.tmdb_service = TMDBService()
        self.last_request_time = 0
        self.fetched_ids = FileHandler.get_fetched_ids()
        self.start_page = FileHandler.get_last_page() + 1

    def _respect_rate_limit(self) -> None:
        """Ensure we don't exceed Trakt's rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - time_since_last)
        
        self.last_request_time = time.time()

    @staticmethod
    def _parse_datetime(dt_str: str) -> datetime:
        """Parse datetime string from Trakt API."""
        return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    def get_movie_details(self, movie_id: str) -> Dict:
        """Fetch detailed movie information."""
        url = (
            f"{TRAKT_BASE_URL}/movies/{movie_id}"
            f"?extended={TRAKT_EXTENDED_INFO}"
        )
        self._respect_rate_limit()
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_movie_stats(self, movie_id: str) -> Dict:
        """Fetch movie statistics."""
        url = f"{TRAKT_BASE_URL}/movies/{movie_id}/stats"
        self._respect_rate_limit()
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_movie_ratings(self, movie_id: str) -> Dict:
        """Fetch movie ratings distribution."""
        url = f"{TRAKT_BASE_URL}/movies/{movie_id}/ratings"
        self._respect_rate_limit()
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_top_movies(self, limit: int = 100) -> Generator[List[Movie], None, None]:
        """Fetch most popular movies from Trakt with detailed information."""
        movies = []
        page = self.start_page
        total_processed = 0
        
        # Create progress bar for overall progress
        pbar = tqdm(
            total=limit,
            desc=f"{Fore.CYAN}🎬 Fetching Movies{Style.RESET_ALL}",
            bar_format="{desc}: {percentage:3.0f}%|{bar}| "
            "{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            colour="cyan",
            position=0,
            leave=True
        )
        
        # Create status bar for current movie
        status_bar = tqdm(
            bar_format="{desc}",
            position=1,
            leave=False
        )
        
        while total_processed < limit:
            # Get popular movies for the specified years
            url = f"{TRAKT_BASE_URL}/movies/popular"
            params = {
                "page": page,
                "limit": min(limit - total_processed, 20),  # Trakt page size limit
                "years": f"{self.START_YEAR}-{self.END_YEAR}",
                "extended": TRAKT_EXTENDED_INFO
            }
            
            self._respect_rate_limit()
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            page_movies = response.json()
            if not page_movies:
                break

            for movie_data in page_movies:
                if total_processed >= limit:
                    break
                    
                # Skip if we've already fetched this movie
                if movie_data["ids"]["trakt"] in self.fetched_ids:
                    continue
                    
                # Get detailed movie information
                movie_slug = movie_data["ids"]["slug"]
                movie = self.get_movie_details(movie_slug)
                
                title = movie["title"][:40]
                year = movie["year"]
                status_bar.set_description_str(
                    f"{Fore.CYAN}🎬 Processing:{Style.RESET_ALL} "
                    f"{Fore.YELLOW}{title} ({year}){Style.RESET_ALL}"
                )
                
                # Get additional stats and ratings
                stats_data = self.get_movie_stats(movie_slug)
                ratings_data = self.get_movie_ratings(movie_slug)
                
                # Get keywords from TMDB if available
                keywords = []
                if movie["ids"]["tmdb"]:
                    keywords = self.tmdb_service.get_movie_keywords(
                        movie["ids"]["tmdb"]
                    )

                # Create movie object with all data
                movie_obj = Movie(
                    title=movie["title"],
                    year=movie["year"],
                    ids=Ids(**movie["ids"]),
                    tagline=movie.get("tagline"),
                    overview=movie.get("overview"),
                    released=(
                        datetime.strptime(
                            movie["released"], "%Y-%m-%d"
                        ).date() if movie.get("released") else None
                    ),
                    runtime=movie.get("runtime"),
                    country=movie.get("country"),
                    updated_at=(
                        self._parse_datetime(movie["updated_at"])
                        if movie.get("updated_at") else None
                    ),
                    trailer=movie.get("trailer"),
                    homepage=movie.get("homepage"),
                    status=movie.get("status"),
                    language=movie.get("language"),
                    available_translations=movie.get(
                        "available_translations", []
                    ),
                    genres=movie.get("genres", []),
                    certification=movie.get("certification"),
                    stats=Stats(**stats_data),
                    rating=Rating(
                        rating=ratings_data["rating"],
                        votes=ratings_data["votes"],
                        distribution=ratings_data["distribution"]
                    ),
                    keywords=keywords
                )
                
                movies.append(movie_obj)
                total_processed += 1
                pbar.update(1)
                
                # Yield batch when it reaches BATCH_SIZE
                if len(movies) >= self.BATCH_SIZE:
                    yield movies, page
                    movies = []
            
            page += 1

        # Yield any remaining movies
        if movies:
            yield movies, page

        pbar.close()
        status_bar.close() 