"""Home page blueprint."""
from flask import Blueprint, redirect, url_for


home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    """Redirect to the purpose page by default."""
    return redirect(url_for('about.purpose')) 