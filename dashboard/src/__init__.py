"""Flask application factory."""
from flask import Flask
from flask_bootstrap import Bootstrap

from .pages.home import home_bp
from .pages.about import about_bp
from .pages.popularity import popularity_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    Bootstrap(app)

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(popularity_bp)

    return app 