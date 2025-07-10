from src.services.trakt_service import TraktService
from src.utils.file_handler import FileHandler
from colorama import Fore, Style


def main() -> None:
    try:
        print("\n📽 Movie Fetcher Started")
        print("=" * 50)
        
        # Check existing progress
        saved_count = FileHandler.get_saved_count()
        last_movie = FileHandler.get_last_saved_movie()
        
        if saved_count > 0:
            print(f"{Fore.CYAN}📊 Found {saved_count:,} movies{Style.RESET_ALL}")
            if last_movie:
                print(
                    f"Last saved: {Fore.YELLOW}{last_movie['title']} "
                    f"({last_movie['year']}){Style.RESET_ALL}"
                )
            print("=" * 50)
        
        # Calculate how many more movies to fetch
        target_total = 12000  # Total movies we want to have
        remaining = max(0, target_total - saved_count)
        
        if remaining == 0:
            print(f"\n{Fore.GREEN}✨ Target number of movies already reached!")
            print(f"You have {saved_count:,} movies saved.{Style.RESET_ALL}")
            return
            
        print(
            f"\n{Fore.CYAN}🎯 Fetching {remaining:,} more movies "
            f"to reach target of {target_total:,}{Style.RESET_ALL}"
        )
        print("=" * 50)
        
        # Process remaining movies in batches
        trakt_service = TraktService()
        total_new = 0
        last_progress = 0
        progress_interval = 200  # Show progress every 200 movies
        
        for batch, current_page in trakt_service.get_top_movies(limit=remaining):
            FileHandler.save_movies(batch, current_page)
            total_new += len(batch)
            
            # Show progress only every progress_interval movies
            if total_new - last_progress >= progress_interval:
                print(
                    f"\r{Fore.GREEN}💾 Progress: {total_new:,}/{remaining:,} "
                    f"new movies ({saved_count + total_new:,} total)"
                    f"{Style.RESET_ALL}",
                    end="\r"
                )
                last_progress = total_new
        
        # Clear the progress line and show final status
        print("\n" + "=" * 50)
        print(f"{Fore.GREEN}✅ All data saved successfully{Style.RESET_ALL}")
        print(
            f"Total movies in collection: "
            f"{Fore.CYAN}{saved_count + total_new:,}{Style.RESET_ALL}"
        )
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
