"""Utility for loading and processing movie data."""
from typing import Dict, List, Any
import json
from pathlib import Path
import pandas as pd


class MovieDataLoader:
    """Class for loading and processing movie data."""
    
    def __init__(self, data_dir: Path) -> None:
        """Initialize with path to movie data directory."""
        self.data_dir = data_dir
        self.movies_data: List[Dict[str, Any]] = []
        self.df: pd.DataFrame = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load all movie JSON files into memory."""
        if not self.data_dir.exists():
            raise ValueError(f"Data directory not found: {self.data_dir}")
            
        for file_path in self.data_dir.glob("*.json"):
            with open(file_path, 'r') as f:
                self.movies_data.append(json.load(f))
                
        if not self.movies_data:
            raise ValueError("No movie data found!")
            
        self._process_data()
    
    def _process_data(self) -> None:
        """Transform raw movie data into a pandas DataFrame."""
        processed_data = []
        
        for movie in self.movies_data:
            try:
                # Extract basic information
                processed_movie = {
                    'title': movie['title'],
                    'year': movie['year'],
                    'rating': movie['rating']['rating'],
                    'votes': movie['rating']['votes'],
                    'watchers': movie['stats']['watchers'],
                    'plays': movie['stats']['plays'],
                    'collectors': movie['stats']['collectors'],
                    'lists': movie['stats']['lists'],
                    'genres': movie.get('genres', []),
                    'runtime': movie.get('runtime', 0),
                    'language': movie.get('language', 'unknown'),
                    'translations': len(
                        movie.get('available_translations', [])
                    ),
                    'keywords': [
                        kw['name'] for kw in movie.get('keywords', [])
                    ]
                }
                
                # Calculate engagement score
                processed_movie['engagement_score'] = (
                    processed_movie['watchers'] * 0.3 +
                    processed_movie['plays'] * 0.2 +
                    processed_movie['collectors'] * 0.15 +
                    movie['stats']['comments'] * 0.15 +
                    processed_movie['lists'] * 0.1 +
                    processed_movie['votes'] * 0.1
                )
                
                processed_data.append(processed_movie)
                
            except KeyError as e:
                print(f"Skipping movie due to missing key: {e}")
                continue
                
        self.df = pd.DataFrame(processed_data)
    
    def get_popularity_table(self) -> pd.DataFrame:
        """Get movie data for the popularity table."""
        return self.df[[
            'title', 'year', 'rating', 'watchers', 'plays',
            'votes', 'engagement_score', 'genres', 'translations'
        ]].sort_values('engagement_score', ascending=False)
    
    def get_yearly_popularity_stats(self) -> pd.DataFrame:
        """Get yearly popularity statistics."""
        return self.df.groupby('year').agg({
            'watchers': 'sum',
            'plays': 'sum',
            'engagement_score': 'mean',
            'rating': 'mean'
        }).reset_index()
    
    def get_genre_popularity(self) -> pd.DataFrame:
        """Get popularity statistics by genre."""
        genre_stats = []
        
        for genre in self.get_unique_genres():
            genre_movies = self.df[
                self.df['genres'].apply(lambda x: genre in x)
            ]
            stats = {
                'genre': genre,
                'total_watchers': genre_movies['watchers'].sum(),
                'avg_engagement': genre_movies['engagement_score'].mean(),
                'movie_count': len(genre_movies)
            }
            genre_stats.append(stats)
            
        return pd.DataFrame(genre_stats)
    
    def get_movies_for_visualization(self) -> pd.DataFrame:
        """Get processed movie data for visualizations."""
        columns = [
            'title', 'year', 'rating', 'watchers', 'plays',
            'votes', 'engagement_score', 'genres', 'keywords'
        ]
        return self.df[columns]
    
    def get_unique_genres(self) -> List[str]:
        """Get list of unique genres."""
        genres = set()
        for genre_list in self.df['genres']:
            genres.update(genre_list)
        return sorted(list(genres)) 