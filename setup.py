"""Setup file for the dashboard package."""

from setuptools import setup, find_packages

setup(
    name="movie-dashboard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.29.0",
        "pandas>=2.1.4",
        "plotly>=5.18.0",
        "numpy>=1.26.2",
        "altair>=5.2.0",
    ],
    python_requires=">=3.8",
)