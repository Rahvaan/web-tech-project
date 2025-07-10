#!/usr/bin/env python3
from typing import Dict, Any
import json
from pathlib import Path
from movie_analyzer import MovieAnalyzer


def save_report(report: Dict[str, Any], output_dir: str = "results") -> None:
    """Save the analysis report to a JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    with open(output_path / "movie_analysis_report.json", "w") as f:
        json.dump(report, f, indent=2)


def print_report_highlights(report: Dict[str, Any]) -> None:
    """Print key highlights from analysis report."""
    print("\n=== Movie Analysis Highlights ===\n")
    
    # Basic Stats
    stats = report['basic_stats']
    print(f"Total Movies Analyzed: {stats['total_movies']}")
    print(f"Average Rating: {stats['avg_rating']:.2f}")
    print(f"Average Rating Consistency: {stats['avg_consistency']:.2f}")
    print(f"Average Engagement Score: {stats['avg_engagement']:.2f}\n")
    
    # Most Consistent Movies
    print("Most Consistently Rated Movies:")
    for movie in report['rating_consistency']['most_consistent']:
        print(f"- {movie['title']}: {movie['rating']:.2f} "
              f"(std: {movie['rating_std']:.2f})")
    print()
    
    # Genre Impact
    print("Genre Performance:")
    genres = report['genre_impact']
    for genre, stats in genres.items():
        if stats['movie_count'] >= 5:  # Only show genres with enough movies
            print(f"- {genre.title()}: {stats['avg_rating']:.2f} "
                  f"(consistency: {stats['avg_consistency']:.2f}, "
                  f"movies: {stats['movie_count']})")
    print()
    
    # Top Movies
    print("Top Movies by Success Index:")
    for i, movie in enumerate(report['top_movies'][:5], 1):
        print(f"{i}. {movie['title']} ({movie['year']}) - "
              f"Score: {movie['success_index']:.2f}")


def main() -> None:
    """Run the movie analysis pipeline."""
    analyzer = MovieAnalyzer()
    
    report = analyzer.generate_report()
    
    save_report(report)
    
    print_report_highlights(report)
    
    print("\nAnalysis complete! Check the 'results' directory for the full "
          "report and visualizations in results/plots/.")


if __name__ == "__main__":
    main() 