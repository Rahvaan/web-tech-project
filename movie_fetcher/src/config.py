from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Keep TMDB API just for keywords
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY is not set in the environment variables")

# Trakt API Configuration
TRAKT_CLIENT_ID = os.getenv("TRAKT_CLIENT_ID")
if not TRAKT_CLIENT_ID:
    raise ValueError("TRAKT_CLIENT_ID is not set in the environment variables")

TRAKT_CLIENT_SECRET = os.getenv("TRAKT_CLIENT_SECRET")
if not TRAKT_CLIENT_SECRET:
    raise ValueError("TRAKT_CLIENT_SECRET is not set in the environment variables")

# API Base URLs
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TRAKT_BASE_URL = "https://api.trakt.tv"

# Extended info to request from Trakt API
TRAKT_EXTENDED_INFO = "full,stats"

# Get the root directory (one level up from movie_fetcher)
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)