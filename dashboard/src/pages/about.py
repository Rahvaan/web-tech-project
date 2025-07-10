"""About pages blueprint."""
from flask import Blueprint, render_template


about_bp = Blueprint('about', __name__, url_prefix='/about')


@about_bp.route('/team')
def team():
    """Render the team page."""
    team_members = [
        {
            'name': 'Emilia Włodek',
            'role': '',
            'description': (
                'Studentka Matematyki na wydziale Matematyki Politechniki Wrocławskiej.'
            ),
            'image': 'img/avatar1.png'
        },
        {
            'name': 'Marcin Bartodziej',
            'role': '',
            'description': (
                'Student Matematyki na wydziale Matematyki Politechniki Wrocławskiej.'
            ),
            'image': 'img/avatar2.png'
        },
        {
            'name': 'Maciej Łosiewicz',
            'role': '',
            'description': (
                'Student Matematyki na wydziale Matematyki Politechniki Wrocławskiej.'
            ),
            'image': 'img/avatar3.png'
        }
    ]
    
    return render_template(
        'about/team.html',
        title='Nasz Zespół',
        team_members=team_members
    )


@about_bp.route('/data')
def data():
    """Render the data sources page."""
    data_sources = {
        'backend': {
            'name': 'Backend',
            'description': 'Aplikacja zbudowana jest w oparciu o mikroframework Flask, używany do tworzenia aplikacji webowych.',
            'metrics': ['Python', 'Flask']
        },
        'frontend': {
            'name': 'Frontend',
            'description': 'Styl strony i responsywny design został osiągnięty dzięki Flask-Bootstrap.',
            'metrics': ['HTML/CSS/JS', 'Jinja2 Templates', 'Bootstrap via Flask-Bootstrap']
        },
        'data_processing': {
            'name': 'Przetwarzanie Danych',
            'description': 'Do analizy i wizualizacji danych wykorzystujemy biblioteki do przetwarzania danych, uczenia maszynowego i wizualizacji.',
            'metrics': ['Pandas', 'NumPy', 'Scikit-learn', 'Vega Altair', 'DataTables']
        }
    }
    
    return render_template(
        'about/data.html',
        title='Technologie i Źródła Danych',
        data_sources=data_sources
    )


@about_bp.route('/purpose')
def purpose():
    """Render the purpose page."""
    analysis_goals = [
        {
            'title': 'Analiza Trendów',
            'description': 'Badanie zmian w popularności filmów na przestrzeni lat i identyfikacja wzorców w preferencjach widzów.',
            'icon': '📈'
        },
        {
            'title': 'Wpływ Gatunków',
            'description': 'Zrozumienie, jak różne gatunki filmowe wpływają na popularność i oceny widzów.',
            'icon': '🎭'
        },
        {
            'title': 'Analiza Słów Kluczowych',
            'description': 'Odkrywanie związków między słowami kluczowymi a sukcesem filmu.',
            'icon': '🔍'
        },
        {
            'title': 'Kompleksowa Baza filmów',
            'description': 'Dostęp do ogromnej bazy popularnych filmów, zawierającej szczegółowe informacje o ocenach i statystykach.',
            'icon': '🎥'
        }
    ]
    
    return render_template(
        'about/purpose.html',
        title='Cel Analizy',
        analysis_goals=analysis_goals
    ) 