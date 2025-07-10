"""Analysis pages blueprint."""
from flask import Blueprint, render_template
from utils.data_loader import MovieDataLoader
from flask import current_app


analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/ratings')
def ratings():
    """Render the ratings analysis page."""
    data_loader = MovieDataLoader(current_app.config['DATA_DIR'])
    rating_dist = data_loader.get_rating_distribution()
    yearly_stats = data_loader.get_yearly_stats()
    
    return render_template(
        'analysis/ratings.html',
        title='Rating Analysis',
        rating_dist=rating_dist,
        yearly_stats=yearly_stats
    )


@analysis_bp.route('/genres')
def genres():
    """Render the genre analysis page."""
    data_loader = MovieDataLoader(current_app.config['DATA_DIR'])
    genre_stats = data_loader.get_genre_stats()
    
    return render_template(
        'analysis/genres.html',
        title='Genre Analysis',
        genre_stats=genre_stats
    ) 