# Movie Analysis Dashboard

Web application for analyzing movie data with visualizations. Built with Python, Flask, Flask-Bootstrap.

## Setup Instructions

### 1. Download Movie Data
1. Download the movie data files from [Google Drive](https://drive.google.com/drive/folders/1fEuksk0hiYSdCbw2Pa_f5VgYWPrIasJl?usp=sharing)
2. Create a `data` directory in the project root if it doesn't exist
3. Extract the downloaded files and place them in the following structure:
```
data/
├── movies_index.json     # Main index file with basic movie metadata
└── movies/              # Directory containing individual movie files
    ├── Movie1_ID.json   # Individual movie data files
    ├── Movie2_ID.json
    └── ...
```
You can place the movie data files anywhere else, but you will need to update the `DATA_DIR` in `src/main.py`.

### 2. Navigate to Dashboard Directory
First, ensure you're in the correct directory:
```bash
# Check your current directory
pwd

# If you see .../web-tech-project/dashboard at the end, you're in the right place
# If not, navigate to the dashboard directory using one of these:
cd dashboard                                    # If you're in web-tech-project
cd path/to/web-tech-project/dashboard          # From any other location
```

### 3. Set Up Python Environment
**Note: This project requires Python 3.11.11 for optimal compatibility with all dependencies. Using older Python versions may cause issues with some visualization packages.**

Create and activate a virtual environment:
```bash
# Create new virtual environment with Python 3.11.11
# If using conda:
conda create -n dashboard python=3.11.11
conda activate dashboard

# OR if using venv (make sure you have Python 3.11.11 installed):
python3.11 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies
Install required Python packages:
```bash
pip install -r requirements.txt
```

### 5. Configure Data Directory
- By default, the application looks for data in `../data/movies/` relative to the dashboard directory
- If you placed the data files elsewhere, update `DATA_DIR` in `src/main.py`

### 6. Run the Application
Start the dashboard:
```bash
# Make sure you're in the dashboard directory
python src/main.py
```
The dashboard will be available at `http://localhost:5000`

## Project Structure

```
.
├── dashboard/              # Main web application
│   ├── src/
│   │   ├── pages/         # Route definitions and view logic
│   │   ├── static/        # Static assets
│   │   ├── templates/     # HTML templates
│   │   ├── utils/         # Utility functions
│   │   ├── __init__.py    # Application factory
│   │   └── main.py        # Application entry point
│   ├── requirements.txt    # Dashboard-specific dependencies
│   └── README.md          # Dashboard documentation
├── data/                  # Data directory
│   ├── movies_index.json  # Index of all movies with basic metadata
│   └── movies/           # Individual movie data files
│       ├── Movie1_ID.json    # Detailed data for movie 1
│       ├── Movie2_ID.json    # Detailed data for movie 2
│       └── ...              # More movie files
├── movie_fetcher/        # Data collection scripts
├── movie_processing/     # Data processing scripts
├── results/              # Analysis results and plots
├── requirements.txt      # Project-wide dependencies
├── setup.py             # Project installation script
└── README.md            # Project documentation
```