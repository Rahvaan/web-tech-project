#!/usr/bin/env python3
"""Script to check the number of movies from 2010-2023 in Trakt."""

import os
import sys
import requests
import time
from colorama import Fore, Style
from tqdm import tqdm

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

# Now we can import from src
from src.config import TRAKT_CLIENT_ID, TRAKT_BASE_URL  # noqa: E402


def get_total_movies() -> int:
    """Get total number of popular movies from 2010-2023."""
    headers = {
        "Content-Type": "application/json",
        "trakt-api-version": "2",
        "trakt-api-key": TRAKT_CLIENT_ID
    }

    # Initialize counters
    total_movies = 0
    
    # Create progress bars
    print(f"\n{Fore.CYAN}📊 Checking Trakt Movies (2010-2023){Style.RESET_ALL}")
    print("=" * 50)

    # Check all movies
    page = 1
    all_bar = tqdm(
        desc=f"{Fore.GREEN}Popular Movies{Style.RESET_ALL}",
        bar_format="{desc}: {n_fmt} found [{elapsed}]"
    )
    
    while True:
        # Respect rate limits
        time.sleep(0.3)
        
        response = requests.get(
            f"{TRAKT_BASE_URL}/movies/popular",
            headers=headers,
            params={
                "page": page,
                "limit": 100,  # Max page size
                "years": "2010-2023"
            }
        )
        response.raise_for_status()
        
        movies = response.json()
        if not movies:
            break
            
        total_movies += len(movies)
        all_bar.update(len(movies))
        page += 1

    all_bar.close()
    
    return total_movies


def main() -> None:
    try:
        total = get_total_movies()
        
        print("\n" + "=" * 50)
        print(f"{Fore.CYAN}📊 Results for 2010-2023:{Style.RESET_ALL}")
        print(
            f"🎬 Popular Movies: {Fore.GREEN}{total:,}{Style.RESET_ALL} "
            f"(sorted by popularity)"
        )
        print("=" * 50 + "\n")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    main() 