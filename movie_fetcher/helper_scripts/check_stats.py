#!/usr/bin/env python3
"""Script to check statistics about fetched movies."""

import os
import sys
from collections import Counter
from datetime import datetime
from colorama import Fore, Style

# Add parent directory to Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

# Now we can import from src
from src.utils.file_handler import FileHandler  # noqa: E402


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format."""
    dt = datetime.fromisoformat(date_str)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def main() -> None:
    try:
        print(f"\n{Fore.CYAN}📊 Movie Collection Statistics{Style.RESET_ALL}")
        print("=" * 50)

        # Load index data
        index_data = FileHandler._load_index()
        movies = index_data["movies"]
        
        if not movies:
            print(f"{Fore.YELLOW}No movies found in the collection.{Style.RESET_ALL}")
            return

        # Basic stats
        total_movies = len(movies)
        years = Counter(movie["year"] for movie in movies)
        last_updated = format_date(index_data["last_updated"]) if index_data["last_updated"] else "Never"
        last_page = index_data["last_page"]

        # Print statistics
        print(f"{Fore.GREEN}Total Movies:{Style.RESET_ALL} {total_movies}")
        print(f"{Fore.GREEN}Last Updated:{Style.RESET_ALL} {last_updated}")
        print(f"{Fore.GREEN}Last Page Fetched:{Style.RESET_ALL} {last_page}")
        
        # Year distribution
        print(f"\n{Fore.CYAN}Movies by Year:{Style.RESET_ALL}")
        print("-" * 50)
        for year in sorted(years.keys()):
            count = years[year]
            percentage = (count / total_movies) * 100
            bar = "█" * int(percentage / 2)
            print(
                f"{year}: {count:3d} movies "
                f"({percentage:4.1f}%) {Fore.YELLOW}{bar}{Style.RESET_ALL}"
            )

        # Recent additions
        print(f"\n{Fore.CYAN}Recent Additions:{Style.RESET_ALL}")
        print("-" * 50)
        for movie in sorted(
            movies[-5:], key=lambda x: x["added_at"], reverse=True
        ):
            added = format_date(movie["added_at"])
            print(
                f"{Fore.YELLOW}{movie['title']}{Style.RESET_ALL} "
                f"({movie['year']}) - Added: {added}"
            )

    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    main() 