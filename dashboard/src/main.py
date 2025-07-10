from typing import Any
from flask import Flask
from flask_bootstrap import Bootstrap
from pathlib import Path

class Config:
    """Flask application configuration."""
    TEMPLATES_AUTO_RELOAD = True

    # Data paths
    ROOT_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = ROOT_DIR / "data" / "movies"
    
    @staticmethod
    def init_app(app: Flask) -> None:
        """Initialize application with this configuration."""
        pass

def create_app(config_class: Any = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    Bootstrap(app)
    
    # Prevents circular imports
    from pages import register_blueprints  # noqa: E402
    register_blueprints(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)