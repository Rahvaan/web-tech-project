from pathlib import Path
import json
from typing import List, Dict, Optional, Set
from datetime import datetime
from tqdm.auto import tqdm
from colorama import Fore, Style
from src.models.movie import Movie
from src.config import DATA_DIR


class FileHandler:
    MOVIES_DIR = DATA_DIR / "movies"
    INDEX_FILE = DATA_DIR / "movies_index.json"

    @classmethod
    def _load_index(cls) -> Dict:
        """Load existing index file if it exists"""
        cls.MOVIES_DIR.mkdir(exist_ok=True)
        if cls.INDEX_FILE.exists():
            with open(cls.INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "movies": [],
            "last_updated": None,
            "last_page": 0,
            "fetched_ids": []
        }

    @classmethod
    def _save_index(cls, movie_index: List[Dict], last_page: int) -> None:
        """Save the updated index file"""
        with open(cls.INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "movies": movie_index,
                "last_updated": datetime.now().isoformat(),
                "last_page": last_page,
                "fetched_ids": [m["id"] for m in movie_index]
            }, f, indent=2)

    @classmethod
    def get_saved_count(cls) -> int:
        """Get the number of movies already saved"""
        if not cls.MOVIES_DIR.exists():
            return 0
        return len(list(cls.MOVIES_DIR.glob("*.json")))

    @classmethod
    def get_last_saved_movie(cls) -> Optional[Dict]:
        """Get information about the last saved movie"""
        index_data = cls._load_index()
        if not index_data["movies"]:
            return None
        return index_data["movies"][-1]

    @classmethod
    def get_last_page(cls) -> int:
        """Get the last page number we fetched"""
        index_data = cls._load_index()
        return index_data.get("last_page", 0)

    @classmethod
    def get_fetched_ids(cls) -> Set[int]:
        """Get set of movie IDs we've already fetched"""
        index_data = cls._load_index()
        return set(index_data.get("fetched_ids", []))

    @classmethod
    def save_movies(cls, movies: List[Movie], current_page: int) -> None:
        """Save new movies to the movies directory, avoiding duplicates"""
        # Load existing index
        index_data = cls._load_index()
        existing_movies = {m["id"] for m in index_data["movies"]}
        
        # Create progress bar for saving
        new_movies = [m for m in movies if m.ids.trakt not in existing_movies]
        if not new_movies:
            print(f"\r{Fore.GREEN}📝 No new movies to save{Style.RESET_ALL}")
            return
            
        # Create main progress bar
        pbar = tqdm(
            new_movies,
            desc=f"{Fore.GREEN}💾 Saving Movies{Style.RESET_ALL}",
            bar_format="{desc}: {percentage:3.0f}%|{bar}| "
            "{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            colour="green",
            position=0,
            leave=False
        )
        
        # Create status bar for current movie
        status_bar = tqdm(
            bar_format="{desc}",
            position=1,
            leave=False
        )
        
        # Process new movies
        for movie in pbar:
            title = movie.title[:40]
            year = movie.year
            status_bar.set_description_str(
                f"{Fore.GREEN}💾 Processing:{Style.RESET_ALL} "
                f"{Fore.YELLOW}{title} ({year}){Style.RESET_ALL}"
            )
            
            filename = movie.get_filename()
            file_path = cls.MOVIES_DIR / filename
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(movie.model_dump(), f, indent=2, default=str)
            
            index_data["movies"].append({
                "id": movie.ids.trakt,
                "title": movie.title,
                "year": movie.year,
                "filename": filename,
                "file_path": str(file_path),
                "added_at": datetime.now().isoformat()
            })
        
        # Save updated index with current page
        cls._save_index(index_data["movies"], current_page)
        
        # Close progress bars and print final status
        pbar.close()
        status_bar.close()
        print(
            f"\r{Fore.GREEN}📝 Saved {len(new_movies)} new "
            f"movie{'s' if len(new_movies) != 1 else ''}{Style.RESET_ALL}",
            end="\r"
        )