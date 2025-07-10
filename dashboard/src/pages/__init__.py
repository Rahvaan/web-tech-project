"""Pages package initialization."""
from flask import Flask

from .popularity import popularity_bp
from .about import about_bp


def register_blueprints(app: Flask) -> None:
    """Register all blueprints with the application."""
    app.register_blueprint(popularity_bp)
    app.register_blueprint(about_bp) 