"""Popularity visualization pages."""
from flask import Blueprint, render_template, redirect, url_for
from flask import current_app
from utils.data_loader import MovieDataLoader
import altair as alt
import pandas as pd
from collections import Counter
import numpy as np
from sklearn.preprocessing import StandardScaler

popularity_bp = Blueprint('popularity', __name__, url_prefix='')

# Enable VegaFusion transformer for large datasets
alt.data_transformers.enable('vegafusion')



@popularity_bp.route('/')
def index():
    """Redirect to table view by default."""
    return redirect(url_for('popularity.table'))


@popularity_bp.route('/table')
def table():
    """Render the popular movies table page."""
    data_loader = MovieDataLoader(current_app.config['DATA_DIR'])
    movies_df = data_loader.get_popularity_table()
    
    return render_template(
        'popularity/table.html',
        title='Popular Movies Table',
        movies=movies_df.to_dict('records')
    )


@popularity_bp.route('/trends')
def trends():
    """Render the popularity trends page."""
    data_loader = MovieDataLoader(current_app.config['DATA_DIR'])
    yearly_stats = data_loader.get_yearly_popularity_stats()
    genre_popularity = data_loader.get_genre_popularity()
    
    return render_template(
        'popularity/trends.html',
        title='Popularity Trends',
        yearly_stats=yearly_stats,
        genre_popularity=genre_popularity
    )


@popularity_bp.route('/interactive')
def interactive():
    """Render the interactive analysis page."""
    data_loader = MovieDataLoader(current_app.config['DATA_DIR'])
    movies_df = data_loader.get_movies_for_visualization()
    
    # Altair chart for watchers vs. rating
    scatter = create_interactive_scatter(movies_df)
    
    # Altair chart for genre popularity over time
    timeline = create_genre_timeline(movies_df)
    
    return render_template(
        'popularity/interactive.html',
        title='Interactive Analysis',
        scatter_spec=scatter.to_dict(format="vega"),
        timeline_spec=timeline.to_dict(format="vega")
    )


def create_interactive_scatter(df: pd.DataFrame) -> alt.Chart:
    """Create an interactive scatter plot of watchers vs. rating."""
    # Create a copy and preprocess the data
    chart_data = df.copy()
    # Convert genres list to comma-separated string
    chart_data['genres'] = chart_data['genres'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
    
    # Convert numeric columns to ensure they are float type
    chart_data['rating'] = chart_data['rating'].astype(float)
    chart_data['watchers'] = chart_data['watchers'].astype(float)
    chart_data['votes'] = chart_data['votes'].astype(float)
    chart_data['year'] = chart_data['year'].astype(str)
    
    year_selection = alt.selection_point(
        fields=['year'],
        bind=alt.binding_select(
            options=sorted(chart_data['year'].unique()),
            name='Wybierz Rok'
        )
    )
    
    point_selection = alt.selection_point(
        on='click',  # Specify click event
        fields=['title'],  # Select based on movie title
        clear='dblclick'  # Clear on double click
    )
    
    scatter = alt.Chart(chart_data).mark_circle(size=60).encode(
        x=alt.X(
            'rating:Q',
            title='Ocena',
            scale=alt.Scale(domain=[0, 10])
        ),
        y=alt.Y(
            'watchers:Q',
            title='Liczba Widzów',
            scale=alt.Scale(type='log')
        ),
        color=alt.Color(
            'year:N',
            title='Rok',
            scale=alt.Scale(scheme='viridis')
        ),
        size=alt.Size(
            'votes:Q',
            title='Liczba Głosów',
            scale=alt.Scale(range=[100, 1000])
        ),
        opacity=alt.condition(point_selection, alt.value(1), alt.value(0.2)),
        tooltip=[
            alt.Tooltip('title:N', title='Tytuł'),
            alt.Tooltip('year:N', title='Rok'),
            alt.Tooltip('rating:Q', title='Ocena', format='.2f'),
            alt.Tooltip('watchers:Q', title='Widzowie', format=','),
            alt.Tooltip('votes:Q', title='Głosy', format=','),
            alt.Tooltip('genres:N', title='Gatunki')
        ]
    ).add_params(
        year_selection,
        point_selection
    ).transform_filter(
        year_selection
    ).properties(
        width=600,
        height=400,
        title='Popularność vs. Ocena Filmów'
    ).configure_view(
        stroke=None
    )

    return scatter


def create_genre_timeline(df: pd.DataFrame) -> alt.Chart:
    """Create an interactive timeline of genre popularity."""
    # Create a copy and preprocess the data
    chart_data = df.copy()
    chart_data['year'] = chart_data['year'].astype(str)
    chart_data['watchers'] = chart_data['watchers'].astype(float)
    
    # Explode the genres list to create separate rows for each genre
    genre_df = chart_data.explode('genres')
    genre_df['genres'] = genre_df['genres'].astype(str)
    
    # Group by year and genre to get watchers count
    genre_yearly = (
        genre_df.groupby(['year', 'genres'])['watchers']
        .sum()
        .reset_index()
    )
    
    genre_selection = alt.selection_point(
        fields=['genres'],
        bind='legend',
        toggle='true'
    )
    
    timeline = alt.Chart(genre_yearly).mark_line(point=True).encode(
        x=alt.X('year:N', title='Rok'),
        y=alt.Y(
            'watchers:Q',
            title='Łączna Liczba Widzów',
            scale=alt.Scale(type='log')
        ),
        color=alt.Color(
            'genres:N',
            title='Gatunek',
            scale=alt.Scale(scheme='category20')
        ),
        opacity=alt.condition(genre_selection, alt.value(1), alt.value(0.2)),
        tooltip=[
            alt.Tooltip('genres:N', title='Gatunek'),
            alt.Tooltip('year:N', title='Rok'),
            alt.Tooltip('watchers:Q', title='Widzowie', format=',')
        ]
    ).add_params(
        genre_selection
    ).properties(
        width=800,
        height=400,
        title='Popularność Gatunków w Czasie'
    )
    
    return timeline


@popularity_bp.route('/keywords')
def keywords():
    """Render the keyword analysis page."""
    data_loader = MovieDataLoader(current_app.config['DATA_DIR'])
    movies_df = data_loader.get_movies_for_visualization()
    
    # keyword statistics
    keyword_stats = compute_keyword_stats(movies_df)
    
    # yearly keyword trends chart
    yearly_trends = create_yearly_keyword_trends(movies_df)
    
    # genre-keyword correlation chart
    genre_correlations = create_genre_keyword_correlations(movies_df)
 
    # success rate chart
    success_chart = create_keyword_success_rate(movies_df)

    return render_template(
        'popularity/keywords.html',
        title='Keyword Analysis',
        yearly_trends_spec=yearly_trends.to_dict(format="vega"),
        genre_correlations_spec=genre_correlations.to_dict(format="vega"),
        success_chart_spec=success_chart.to_dict(format="vega"),
        top_keywords=get_top_keywords(keyword_stats)
    )


def compute_keyword_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute statistics for movie keywords."""

    keyword_df = df[df['keywords'].notna()].copy()
    keyword_df = keyword_df.explode('keywords')
    
    # Group by keyword and compute statistics
    stats = keyword_df.groupby('keywords').agg({
        'watchers': ['count', 'mean', 'sum'],
        'rating': 'mean',
        'engagement_score': 'mean'
    }).reset_index()
    
    stats.columns = [
        'keyword', 'movie_count', 'avg_watchers',
        'total_watchers', 'avg_rating', 'avg_engagement'
    ]
    
    # Filter keywords that appear in at least 10 movies
    return stats[stats['movie_count'] >= 10].sort_values(
        'total_watchers', ascending=False
    )


def create_yearly_keyword_trends(df: pd.DataFrame) -> alt.Chart:
    """Create a visualization of how top keywords' popularity changes over time."""
    # Get top 20 keywords by total watchers
    keyword_df = df[df['keywords'].notna()].copy()
    all_keywords = [k for kw_list in keyword_df['keywords'] for k in kw_list]
    top_keywords = [k for k, _ in Counter(all_keywords).most_common(20)]
    
    # Yearly data for top keywords
    yearly_data = []
    for year in sorted(df['year'].unique()):
        year_movies = keyword_df[keyword_df['year'] == year]
        for keyword in top_keywords:
            movies_with_keyword = year_movies[
                year_movies['keywords'].apply(lambda x: keyword in x)
            ]
            if not movies_with_keyword.empty:
                yearly_data.append({
                    'year': year,
                    'keyword': keyword,
                    'movie_count': len(movies_with_keyword),
                    'avg_watchers': movies_with_keyword['watchers'].mean(),
                    'total_watchers': movies_with_keyword['watchers'].sum()
                })
    
    yearly_df = pd.DataFrame(yearly_data)
    
    keyword_selection = alt.selection_point(
        fields=['keyword'],
        bind='legend',
        toggle='true'
    )
    
    base = alt.Chart(yearly_df).encode(
        x=alt.X('year:O', title='Rok'),
        color=alt.Color(
            'keyword:N',
            title='Słowo Kluczowe',
            scale=alt.Scale(scheme='category20')
        ),
        tooltip=[
            alt.Tooltip('keyword:N', title='Słowo Kluczowe'),
            alt.Tooltip('year:O', title='Rok'),
            alt.Tooltip('movie_count:Q', title='Liczba Filmów'),
            alt.Tooltip('avg_watchers:Q', title='Średnia Liczba Widzów', format=','),
            alt.Tooltip('total_watchers:Q', title='Łączna Liczba Widzów', format=',')
        ]
    ).properties(
        width=800,
        height=400
    )
    
    lines = base.mark_line(size=2).encode(
        y=alt.Y(
            'total_watchers:Q',
            title='Łączna Liczba Widzów',
            scale=alt.Scale(type='log')
        ),
        opacity=alt.condition(keyword_selection, alt.value(1), alt.value(0.2))
    ).add_params(keyword_selection)
    
    points = base.mark_circle(size=50).encode(
        y=alt.Y(
            'total_watchers:Q',
            title='Łączna Liczba Widzów',
            scale=alt.Scale(type='log')
        ),
        opacity=alt.condition(keyword_selection, alt.value(1), alt.value(0.2)),
        size=alt.Size(
            'movie_count:Q',
            title='Liczba Filmów',
            scale=alt.Scale(range=[50, 300])
        )
    )
    
    return (lines + points).properties(
        title='Roczne Trendy Słów Kluczowych'
    )


def create_genre_keyword_correlations(df: pd.DataFrame) -> alt.Chart:
    """Create a heatmap showing which keywords are common in which genres."""
    # Get top 15 keywords and top 10 genres
    keyword_df = df[df['keywords'].notna()].copy()
    all_keywords = [k for kw_list in keyword_df['keywords'] for k in kw_list]
    top_keywords = [k for k, _ in Counter(all_keywords).most_common(15)]
    
    all_genres = [g for genre_list in df['genres'] for g in genre_list]
    top_genres = [g for g, _ in Counter(all_genres).most_common(10)]
    
    # Correlation data
    correlation_data = []
    for genre in top_genres:
        genre_movies = keyword_df[
            keyword_df['genres'].apply(lambda x: genre in x)
        ]
        total_genre_movies = len(genre_movies)
        
        for keyword in top_keywords:
            keyword_in_genre = len(genre_movies[
                genre_movies['keywords'].apply(lambda x: keyword in x)
            ])
            if total_genre_movies > 0:
                correlation_data.append({
                    'genre': genre,
                    'keyword': keyword,
                    'percentage': (keyword_in_genre / total_genre_movies) * 100,
                    'count': keyword_in_genre
                })
    
    correlation_df = pd.DataFrame(correlation_data)
    
    heatmap = alt.Chart(correlation_df).mark_rect().encode(
        x=alt.X('genre:N', title='Gatunek'),
        y=alt.Y('keyword:N', title='Słowo Kluczowe'),
        color=alt.Color(
            'percentage:Q',
            title='Procent Filmów',
            scale=alt.Scale(scheme='viridis')
        ),
        tooltip=[
            alt.Tooltip('genre:N', title='Gatunek'),
            alt.Tooltip('keyword:N', title='Słowo Kluczowe'),
            alt.Tooltip('percentage:Q', title='Procent', format='.1f'),
            alt.Tooltip('count:Q', title='Liczba Filmów')
        ]
    ).properties(
        width=600,
        height=400,
        title='Korelacje Gatunków i Słów Kluczowych'
    )
    
    return heatmap


def create_keyword_success_rate(df: pd.DataFrame) -> alt.Chart:
    """Create a visualization showing which keywords are associated with success."""

    keyword_df = df[df['keywords'].notna()].copy()
    
    median_watchers = keyword_df['watchers'].median()
    median_rating = keyword_df['rating'].median()
    
    # Success metrics for each keyword
    success_data = []
    all_keywords = [k for kw_list in keyword_df['keywords'] for k in kw_list]
    top_keywords = [k for k, _ in Counter(all_keywords).most_common(30)]
    
    for keyword in top_keywords:
        movies_with_keyword = keyword_df[
            keyword_df['keywords'].apply(lambda x: keyword in x)
        ]
        total_movies = len(movies_with_keyword)
        
        # Calculate success metrics
        high_watchers = movies_with_keyword['watchers'] > median_watchers
        high_rating = movies_with_keyword['rating'] > median_rating
        
        success_data.append({
            'keyword': keyword,
            'total_movies': total_movies,
            'high_watchers_pct': (high_watchers.sum() / total_movies) * 100,
            'high_rating_pct': (high_rating.sum() / total_movies) * 100,
            'avg_engagement': movies_with_keyword['engagement_score'].mean()
        })
    
    success_df = pd.DataFrame(success_data)
    
    base = alt.Chart(success_df).encode(
        x=alt.X(
            'high_watchers_pct:Q',
            title='Procent Filmów Powyżej Mediany Widzów',
            scale=alt.Scale(domain=[0, 100])
        ),
        y=alt.Y(
            'high_rating_pct:Q',
            title='Procent Filmów Powyżej Mediany Ocen',
            scale=alt.Scale(domain=[0, 100])
        )
    ).properties(
        width=700,
        height=500,
        title='Analiza Sukcesu Słów Kluczowych'
    )
    
    scatter = base.mark_circle(size=100).encode(
        color=alt.Color(
            'avg_engagement:Q',
            title='Średnie Zaangażowanie',
            scale=alt.Scale(scheme='viridis')
        ),
        size=alt.Size(
            'total_movies:Q',
            title='Liczba Filmów',
            scale=alt.Scale(range=[100, 1000])
        ),
        tooltip=[
            alt.Tooltip('keyword:N', title='Słowo Kluczowe'),
            alt.Tooltip('total_movies:Q', title='Liczba Filmów'),
            alt.Tooltip(
                'high_watchers_pct:Q',
                title='Powyżej Mediany Widzów (%)',
                format='.1f'
            ),
            alt.Tooltip(
                'high_rating_pct:Q',
                title='Powyżej Mediany Ocen (%)',
                format='.1f'
            ),
            alt.Tooltip(
                'avg_engagement:Q',
                title='Średnie Zaangażowanie',
                format='.2f'
            )
        ]
    )
    
    hover = alt.selection_point(
        fields=['keyword'],
        nearest=True,
        on='mouseover',
        empty='none'
    )
    
    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=7,
        fontSize=11,
        fontWeight='bold'
    ).encode(
        text='keyword:N',
        opacity=alt.condition(
            alt.datum.rank <= 5,  # Show only top 5 by default
            alt.value(1),
            alt.value(0)
        )
    ).transform_window(
        rank='rank(total_movies)',
        sort=[alt.SortField('total_movies', order='descending')]
    )
    
    hover_text = base.mark_text(
        align='left',
        baseline='middle',
        dx=7,
        fontSize=11,
        fontStyle='italic'
    ).encode(
        text='keyword:N',
        opacity=alt.condition(hover, alt.value(1), alt.value(0))
    ).add_params(hover)
    
    return (scatter + text + hover_text).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_view(
        strokeWidth=0
    )


def get_top_keywords(
    keyword_stats: pd.DataFrame, n: int = 20
) -> list:
    """Get the top N keywords by total watchers."""
    columns = ['keyword', 'movie_count', 'total_watchers', 'avg_rating']
    return keyword_stats.head(n)[columns].to_dict('records')


@popularity_bp.route('/ml_insights')
def ml_insights():
    """Render the ML-based keyword analysis page."""

    data_loader = MovieDataLoader(current_app.config['DATA_DIR'])
    movies_df = data_loader.get_movies_for_visualization()
    
    impact_df = analyze_keyword_impact(movies_df)
    
    impact_chart = create_keyword_impact_chart(impact_df)
    
    return render_template(
        'popularity/ml_insights.html',
        title='ML-Based Keyword Analysis',
        impact_chart_spec=impact_chart.to_dict(format="vega")
    )


def analyze_keyword_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze each keyword's impact on movie popularity using regression."""

    keyword_df = df[df['keywords'].notna()].copy()
    
    all_keywords = [k for kw_list in keyword_df['keywords'] for k in kw_list]
    keyword_counts = Counter(all_keywords)
    # Filter keywords that appear in at least 10 movies
    top_keywords = [k for k, v in keyword_counts.most_common(20) if v >= 10]
    
    keyword_presence = np.array([
        [1 if k in keywords else 0 for k in top_keywords]
        for keywords in keyword_df['keywords']
    ])
    
    scaler = StandardScaler()
    y_watchers = scaler.fit_transform(np.log1p(keyword_df['watchers'].values.reshape(-1, 1)))
    y_rating = scaler.fit_transform(keyword_df['rating'].values.reshape(-1, 1))
    
    watchers_impact = np.linalg.lstsq(keyword_presence, y_watchers, rcond=None)[0].flatten()
    rating_impact = np.linalg.lstsq(keyword_presence, y_rating, rcond=None)[0].flatten()
    
    return pd.DataFrame({
        'keyword': top_keywords,
        'watchers_impact': watchers_impact,
        'rating_impact': rating_impact,
        'frequency': keyword_presence.sum(axis=0)
    })


def create_keyword_impact_chart(impact_df: pd.DataFrame) -> alt.Chart:
    """Create a visualization of keyword impact on popularity and rating."""
    impact_chart = alt.Chart(impact_df).mark_circle(size=100).encode(
        x=alt.X(
            'watchers_impact:Q',
            title='Wpływ na Liczbę Widzów',
            scale=alt.Scale(domain=[-2, 2])
        ),
        y=alt.Y(
            'rating_impact:Q',
            title='Wpływ na Oceny',
            scale=alt.Scale(domain=[-2, 2])
        ),
        color=alt.Color(
            'frequency:Q',
            title='Częstotliwość',
            scale=alt.Scale(scheme='viridis')
        ),
        tooltip=[
            alt.Tooltip('keyword:N', title='Słowo Kluczowe'),
            alt.Tooltip('frequency:Q', title='Częstotliwość'),
            alt.Tooltip('watchers_impact:Q', 
                       title='Wpływ na Widzów',
                       format='.2f'),
            alt.Tooltip('rating_impact:Q',
                       title='Wpływ na Oceny',
                       format='.2f')
        ]
    ).properties(
        width=600,
        height=400,
        title='Analiza Wpływu Słów Kluczowych'
    )
    
    return impact_chart