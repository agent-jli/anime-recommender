# Anime Recommender

A machine learning-powered anime recommendation system that suggests anime based on user preferences and similarity matching.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python main.py
```

Or run the Flask web app:

```bash
python app/app.py
```

### Docker

```bash
docker build -t anime-recommender .
docker run -p 5000:5000 anime-recommender
```

## Features

- **Intelligent Recommendations**: Uses vector embeddings and similarity matching
- **Web Interface**: Simple Flask-based API
- **Data Processing Pipeline**: Automated data ingestion and processing
- **Containerized**: Docker and Kubernetes ready

## Project Structure

- `src/` - Core recommendation engine
- `app/` - Flask web application  
- `data/` - Anime datasets
- `pipeline/` - Data processing pipeline
- `config/` - Configuration files

## Data

The system uses anime datasets with synopsis information to generate embeddings and provide personalized recommendations.
