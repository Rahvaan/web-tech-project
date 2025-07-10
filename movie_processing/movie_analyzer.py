from typing import Dict, List, Any
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from textblob import TextBlob
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns


class MovieAnalyzer:
    def __init__(self, data_dir: str = "data/movies"):
        """Initialize the MovieAnalyzer with the path to movie data."""
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise ValueError(
                f"Data directory '{data_dir}' does not exist! "
                f"Number of movies to process: 0"
            )
        self.movies_data: List[Dict] = []
        self.df: pd.DataFrame = None
        self.load_data()
        if not self.movies_data:
            raise ValueError(
                "No movie data found! Please check if the data directory "
                f"is correct.\nExpected data directory: {self.data_dir.absolute()}"
            )
        self.process_data()

    def load_data(self) -> None:
        """Load all movie JSON files into a list."""
        for file_path in self.data_dir.glob("*.json"):
            with open(file_path, 'r') as f:
                self.movies_data.append(json.load(f))

    def process_data(self) -> None:
        """Transform raw movie data into a pandas DataFrame with calculated metrics."""
        processed_data = []
        
        for movie in self.movies_data:
            try:
                # # Skip movies with missing required fields
                # if not all(key in movie for key in ['rating', 'stats', 'keywords', 'title', 'year']):
                #     continue
                # if not all(key in movie['rating'] for key in ['distribution', 'rating', 'votes']):
                #     continue
                # if not all(key in movie['stats'] for key in ['watchers', 'plays', 'collectors', 'comments', 'lists', 'votes']):
                #     continue

                # Calculate rating consistency score
                distribution = movie['rating']['distribution']
                if not distribution:  # Skip if distribution is empty
                    continue
                    
                ratings = np.array([int(k) for k in distribution.keys()])
                counts = np.array(list(distribution.values()))
                if len(counts) == 0 or sum(counts) == 0:  # Skip if no valid counts
                    continue
                    
                weighted_std = np.sqrt(
                    np.average((ratings - movie['rating']['rating'])**2, weights=counts)
                )
                
                # Calculate engagement score
                stats = movie['stats']
                max_stats = max(stats.values()) if stats.values() else 0
                if max_stats == 0:  # Skip if no engagement data
                    continue
                    
                engagement_score = (
                    stats['watchers'] * 0.3 +
                    stats['plays'] * 0.2 +
                    stats['collectors'] * 0.15 +
                    stats['comments'] * 0.15 +
                    stats['lists'] * 0.1 +
                    stats['votes'] * 0.1
                ) / max_stats

                # Calculate keyword sentiment (handle empty keywords)
                keyword_sentiment = 0.0
                if movie['keywords']:
                    sentiments = [TextBlob(kw['name']).sentiment.polarity 
                                for kw in movie['keywords'] if 'name' in kw]
                    keyword_sentiment = np.mean(sentiments) if sentiments else 0.0

                processed_movie = {
                    'title': movie['title'],
                    'year': movie['year'],
                    'rating': movie['rating']['rating'],
                    'votes': movie['rating']['votes'],
                    'rating_std': weighted_std,
                    'engagement_score': engagement_score,
                    'runtime': movie.get('runtime', 0),
                    'language': movie.get('language', 'unknown'),
                    'translation_count': len(movie.get('available_translations', [])),
                    'genre_count': len(movie.get('genres', [])),
                    'genres': movie.get('genres', []),
                    'keyword_sentiment': keyword_sentiment,
                    'keyword_count': len(movie.get('keywords', [])),
                    'watchers': stats['watchers'],
                    'plays': stats['plays']
                }
                processed_data.append(processed_movie)
            except Exception as e:
                print(f"Skipping movie due to error: {movie.get('title', 'Unknown')}")
                continue
        
        if not processed_data:
            raise ValueError("No valid movies found after processing!")
            
        self.df = pd.DataFrame(processed_data)

    def analyze_rating_consistency(self) -> Dict[str, Any]:
        """Analyze rating consistency and its relationships with other features."""
        results = {
            'most_consistent': self.df.nsmallest(5, 'rating_std')[
                ['title', 'rating', 'rating_std']
            ].to_dict('records'),
            'most_inconsistent': self.df.nlargest(5, 'rating_std')[
                ['title', 'rating', 'rating_std']
            ].to_dict('records'),
            'correlation_with_votes': self.df['rating_std'].corr(self.df['votes']),
            'correlation_with_rating': self.df['rating_std'].corr(self.df['rating'])
        }
        return results

    def analyze_genre_impact(self) -> Dict[str, Any]:
        """Analyze how different genres and their combinations affect ratings."""
        genre_stats = defaultdict(list)
        
        for _, movie in self.df.iterrows():
            for genre in movie['genres']:
                genre_stats[genre].append({
                    'rating': movie['rating'],
                    'consistency': movie['rating_std']
                })
        
        genre_analysis = {}
        for genre, stats in genre_stats.items():
            ratings = [s['rating'] for s in stats]
            consistencies = [s['consistency'] for s in stats]
            genre_analysis[genre] = {
                'avg_rating': np.mean(ratings),
                'avg_consistency': np.mean(consistencies),
                'movie_count': len(ratings)
            }
        
        return genre_analysis

    def create_success_index(self) -> pd.DataFrame:
        """Create a success index combining multiple metrics."""
        # Normalize all components using StandardScaler
        scaler = StandardScaler()
        components = [
            'rating',
            'votes',
            'engagement_score',
            'translation_count'
        ]
        normalized_data = scaler.fit_transform(self.df[components])
        
        # Calculate weighted success index (weights sum to 1.0)
        weights = [0.4, 0.2, 0.2, 0.2]
        success_index = np.dot(normalized_data, weights)
        
        results_df = self.df[['title', 'year']].copy()
        results_df['success_index'] = success_index
        return results_df.sort_values('success_index', ascending=False)

    def plot_rating_distribution(self, save_path: str = "results") -> None:
        """Create and save rating distribution plots."""
        plots_dir = Path(save_path) / "plots"
        plots_dir.mkdir(parents=True, exist_ok=True)
        
        plt.style.use('bmh')
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.grid': True,
            'grid.alpha': 0.3
        })
        
        # 1. Rating vs Consistency Plot
        plt.figure(figsize=(12, 8))
        
        # Sort dataframe by votes to plot high-vote movies last (on top)
        plot_df = self.df.sort_values('votes', ascending=True)
        
        # Create custom colormap
        colors = plt.cm.Blues(np.linspace(0.3, 1, 256))
        custom_blues = mcolors.LinearSegmentedColormap.from_list('custom_blues', colors)
        
        # Plot all movies
        scatter = plt.scatter(
            plot_df['rating'],
            plot_df['rating_std'],
            c=plot_df['votes'],
            alpha=0.8,
            cmap=custom_blues,
            label='Movies'
        )
        
        # Get distinct movie groups
        success_index_df = self.create_success_index()
        top_movies = success_index_df.head(5)
        most_consistent = self.df.nsmallest(5, 'rating_std')
        most_inconsistent = self.df.nlargest(5, 'rating_std')
        
        plt.scatter(
            top_movies.merge(self.df, on=['title', 'year'])['rating'],
            top_movies.merge(self.df, on=['title', 'year'])['rating_std'],
            color='red', marker='*', s=200, label='Top Movies', alpha=0.8,
            zorder=5
        )
        plt.scatter(
            most_consistent['rating'],
            most_consistent['rating_std'],
            color='green', marker='P', s=150, label='Most Consistent', alpha=0.8,
            zorder=5
        )
        plt.scatter(
            most_inconsistent['rating'],
            most_inconsistent['rating_std'],
            color='purple', marker='X', s=150, label='Most Inconsistent', alpha=0.8,
            zorder=5
        )
        
        plt.colorbar(scatter, label='Number of Votes')
        plt.xlabel('Rating')
        plt.ylabel('Rating Standard Deviation')
        plt.title('Rating vs Consistency Analysis')
        plt.legend(bbox_to_anchor=(1.15, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/rating_consistency.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Genre Performance Plot
        genre_data = []
        for _, row in self.df.iterrows():
            for genre in row['genres']:
                genre_data.append({
                    'genre': genre,
                    'rating': row['rating']
                })
        genre_df = pd.DataFrame(genre_data)
        
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=genre_df, x='genre', y='rating')
        plt.xticks(rotation=45, ha='right')
        plt.title('Rating Distribution by Genre')
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/genre_ratings.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Timeline Analysis Plot
        yearly_stats = self.df.groupby('year').agg({
            'rating': ['mean', 'count'],
            'engagement_score': 'mean',
            'votes': 'mean',
            'translation_count': 'mean'
        })
        yearly_stats.columns = [
            'avg_rating', 'movie_count', 'avg_engagement',
            'avg_votes', 'avg_translations'
        ]
        yearly_stats = yearly_stats.reset_index()
        
        fig = plt.figure(figsize=(15, 12))
        gs = plt.GridSpec(2, 1, height_ratios=[2, 1], hspace=0.3)
        
        # Top subplot: Ratings and Movies per Year
        ax1 = fig.add_subplot(gs[0])
        
        # Plot average rating
        ln1 = ax1.plot(
            yearly_stats['year'],
            yearly_stats['avg_rating'],
            'o-',
            color='tab:blue',
            label='Average Rating',
            linewidth=2
        )
        ax1.set_ylabel('Average Rating', color='tab:blue')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        
        # Add movie count on secondary y-axis
        ax1_twin = ax1.twinx()
        ln2 = ax1_twin.plot(
            yearly_stats['year'],
            yearly_stats['movie_count'],
            's-',
            color='tab:orange',
            label='Number of Movies',
            linewidth=2
        )
        ax1_twin.set_ylabel('Number of Movies', color='tab:orange')
        ax1_twin.tick_params(axis='y', labelcolor='tab:orange')
        
        # Combine legends
        lns = ln1 + ln2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc='upper left')
        ax1.set_title('Movie Ratings and Volume Over Time', pad=20)
        
        # Bottom subplot: Engagement and Global Reach
        ax2 = fig.add_subplot(gs[1])
        
        # Plot engagement score
        ln3 = ax2.plot(
            yearly_stats['year'],
            yearly_stats['avg_engagement'],
            'o-',
            color='tab:green',
            label='Engagement Score',
            linewidth=2
        )
        ax2.set_ylabel('Average Engagement', color='tab:green')
        ax2.tick_params(axis='y', labelcolor='tab:green')
        
        # Add translations on secondary y-axis
        ax2_twin = ax2.twinx()
        ln4 = ax2_twin.plot(
            yearly_stats['year'],
            yearly_stats['avg_translations'],
            's-',
            color='tab:red',
            label='Available Translations',
            linewidth=2
        )
        ax2_twin.set_ylabel('Average Translations', color='tab:red')
        ax2_twin.tick_params(axis='y', labelcolor='tab:red')
        
        # Combine legends
        lns = ln3 + ln4
        labs = [l.get_label() for l in lns]
        ax2.legend(lns, labs, loc='upper left')
        ax2.set_title('Engagement and Global Reach Trends', pad=20)
        
        # Common settings for both subplots
        for ax in [ax1, ax2]:
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('Year')
            ax.set_xticks(yearly_stats['year'])
            ax.tick_params(axis='x', rotation=45)
        
        fig.text(
            0.02, 0.98,
            'Movie Industry Evolution Analysis:\n'
            '• Top: Rating trends and movie volume amongst 12000 popular movies\n'
            '• Bottom: Audience engagement and global reach',
            fontsize=10,
            ha='left',
            va='top'
        )
        
        plt.savefig(
            f"{plots_dir}/timeline_analysis.png",
            dpi=300,
            bbox_inches='tight',
            facecolor='white'
        )
        plt.close()

    def generate_report(self) -> Dict[str, Any]:
        """Generate analysis report."""
        report = {
            'basic_stats': {
                'total_movies': len(self.df),
                'avg_rating': self.df['rating'].mean(),
                'avg_consistency': self.df['rating_std'].mean(),
                'avg_engagement': self.df['engagement_score'].mean()
            },
            'rating_consistency': self.analyze_rating_consistency(),
            'genre_impact': self.analyze_genre_impact(),
            'top_movies': self.create_success_index().head(10).to_dict('records')
        }
        
        self.plot_rating_distribution()
        
        return report
