# 🎬 Movie Fetcher & Analyzer

A Python application that fetches popular movies from Trakt API (2010-2023), enriches them with additional data from TMDB, and provides comprehensive data analysis tools to extract insights about movie ratings, consistency, and success factors.

## ✨ Features

- 🎥 Fetches most popular movies from 2010-2023 via Trakt API
- 🔍 Enriches movie data with keywords from TMDB
- 💾 Saves data in organized JSON format
- 🔄 Smart duplicate detection for multiple runs
- 📊 Real-time progress tracking with colorful indicators
- 📑 Maintains a searchable movie index with timestamps
- 🔬 Advanced movie data analysis:
  - 📊 Rating consistency analysis
  - 🎭 Genre impact analysis
  - 🏆 Success index calculation
  - 📈 Rating distribution visualization
  - 📋 Comprehensive analytics reports

## 🛠️ Setup

### Prerequisites
- Python 3.8 or higher
- Trakt API key (Client ID & secret)
- TMDB API key

### 🔑 API Keys

1. **Trakt API Key**:
   - Create an account at [Trakt.tv](https://trakt.tv)
   - Go to [Your API Apps](https://trakt.tv/oauth/applications)
   - Create a new application
   - Copy the Client ID & secret

2. **TMDB API Key**:
   - Create an account at [TMDB](https://www.themoviedb.org)
   - Go to [API Settings](https://www.themoviedb.org/settings/api)
   - Generate a new API key

### ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd web-tech-project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory:
   ```env
   TMDB_API_KEY=your_tmdb_api_key
   TRAKT_CLIENT_ID=your_trakt_client_id
   TRAKT_CLIENT_SECRET=your_trakt_client_secret
   ```

## 🚀 Usage

### 🎬 Main Application
Run the main script to fetch and save movies:
```bash
python movie_fetcher/main.py
```

### 📊 Analysis
Run the analysis script to generate insights:
```bash
python movie_processing/analyze_movies.py
```

The analysis will:
1. Load movie data from the `data/movies` directory
2. Generate visualizations in the `plots` directory
3. Save a detailed report in the `results` directory
4. Print key highlights to the console

### 🔍 Check Available Movies
To check how many movies are available:
```bash
python -m movie_fetcher.scripts.check_movie_counts
```

### 🎯 What it does:

1. **Fetches Movies**:
   - Gets popular movies from 2010-2023
   - Sorts by overall popularity
   - Shows real-time progress with movie titles
   - Respects API rate limits

2. **Enriches Data**:
   - Fetches detailed movie information
   - Gets movie statistics and ratings
   - Adds keywords from TMDB
   - Includes comprehensive metadata

3. **Saves Data**:
   - Creates organized file structure
   - Avoids duplicate entries
   - Maintains a timestamped index file
   - Tracks when movies were added

## 📁 Project Structure

The project is organized as follows:
```
web-tech-project/           # Root directory
├── movie_fetcher/         # Movie fetching application
│   ├── src/              # Core fetching logic
│   ├── helper_scripts/   # Utility scripts
│   ├── main.py          # Main fetching script
│   ├── .env             # API configuration
│   └── .env.example     # Example configuration
├── movie_processing/     # Movie analysis application
│   ├── movie_analyzer.py # Core analysis logic
│   ├── analyze_movies.py # Analysis script
│   └── results/         # Analysis outputs
│       ├── plots/       # Generated visualizations
│       └── movie_analysis_report.json # Analysis report
├── data/                # Data storage
│   ├── movies_index.json # Master index with timestamps
│   └── movies/         # Individual movie files
│       ├── Movie_Title_1_ID.json
│       └── Movie_Title_2_ID.json
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

### 📋 Index File Includes:
- List of all saved movies
- Last update timestamp
- Movie metadata:
  - Title and year
  - Trakt ID
  - File location
  - Addition timestamp

### 🎬 Movie Data Includes:
- Basic information (title, year, overview)
- Extended details (tagline, runtime, country)
- Statistics (watchers, plays, ratings)
- Keywords and genres
- Media links (trailer, homepage)
- Release information
- Ratings distribution

## ⚙️ Configuration

The application uses environment variables for configuration:
- `TMDB_API_KEY`: Your TMDB API key
- `TRAKT_CLIENT_ID`: Your Trakt Client ID
- `TRAKT_CLIENT_SECRET`: Your Trakt Client Secret

Year range can be modified in `src/services/trakt_service.py`:
- `START_YEAR`: Currently set to 2010
- `END_YEAR`: Currently set to 2023

## 🔄 API Rate Limits

The application automatically respects API rate limits:
- **Trakt API**: 1000 requests per 5 minutes (1 request every 0.3 seconds)
- **TMDB API**: 40 requests per 10 seconds

Each API request is throttled to ensure we stay within these limits. The application will automatically pause if needed to avoid hitting rate limits.

## 📦 Dependencies

### Core Dependencies
- `requests`: HTTP requests to APIs
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation and serialization
- `tqdm`: Progress bars and status indicators
- `colorama`: Colored terminal output

### Analysis Dependencies
- `numpy`: Numerical computations and array operations
- `pandas`: Data manipulation and analysis
- `scikit-learn`: Machine learning and data normalization
- `matplotlib`: Basic plotting capabilities
- `seaborn`: Statistical data visualization
- `textblob`: Natural language processing for sentiment analysis
- `scipy`: Scientific computing and statistics
- `ipython`: Interactive computing and notebook support for analysis visualization

## 📊 Analysis Features

### 📈 Rating Consistency Score
Measures how consistent the ratings are for each movie using a weighted standard deviation of individual ratings. This helps identify movies with:
- Universal appeal vs. polarizing reception
- Consistent vs. varied audience reactions
- Rating stability across different viewer segments

### ⭐ Engagement Score
A composite metric combining multiple user interaction factors:
- Watchers (30%): Number of unique viewers
- Plays (20%): Total viewing count
- Collectors (15%): Users who added to collections
- Comments (15%): User discussion activity
- Lists (10%): Inclusion in user lists
- Votes (10%): Rating participation

### 🏆 Success Index
A normalized score that combines multiple success indicators:
- Rating (40%): Overall quality assessment
- Number of votes (20%): Rating participation
- Engagement score (20%): User interaction level
- Translation count (20%): Global reach

### 📊 Analysis Outputs

#### Main Notebook
Main analysis output notebook is `movie_analysis.ipynb`. It contains visualizations made by `movie_processing/analyze_movies.py` as well as some other visualisations and their interpretations.

#### Visualizations
Generated in the `results/plots` directory:
- 📈 `rating_consistency.png`: Scatter plot showing:
  - Movie ratings on the x-axis
  - Rating consistency (standard deviation) on the y-axis
  - Point size indicating number of votes
  - Helps identify both high-quality and consistently-rated movies

- 📊 `genre_ratings.png`: Box plot showing:
  - Rating distribution for each genre
  - Median, quartiles, and outliers
  - Helps identify most and least successful genres

- 📈 `timeline_analysis.png`: Dual-panel visualization showing:
  - Top Panel:
    * Average movie ratings over time (2010-2023)
    * Number of movies per year
    * Trends in rating quality and quantity
  - Bottom Panel:
    * Audience engagement trends
    * Global reach (translations availability)
    * Evolution of movie industry metrics

#### 📑 Analysis Report
Generated as `results/movie_analysis_report.json`, includes:
- Basic Statistics:
  - Total number of movies analyzed
  - Average rating across all movies
  - Average rating consistency
  - Average engagement score

- 📋 Rating Consistency Analysis:
  - Most consistently rated movies (top 5)
  - Most divisive movies (top 5)
  - Correlation between ratings and consistency
  - Correlation between votes and consistency

- 🎭 Genre Impact Analysis:
  - Average rating per genre
  - Rating consistency per genre
  - Number of movies per genre
  - Most and least successful genres

- 🏆 Success Rankings:
  - Top 10 movies by success index
  - Success factors breakdown
  - Comparative performance metrics


  ## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
