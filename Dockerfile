## Parent image
FROM python:3.12-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

## Work directory inside the docker container
WORKDIR /app

## Installing system dependancies and uv
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

## Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock README.md ./

## Install dependencies using uv (much faster than pip)
RUN uv sync --frozen

## Copy the rest of the application
COPY . .

## Install the package in development mode
RUN uv pip install -e .

# Used PORTS
EXPOSE 8501

# Run the app 
CMD ["uv", "run", "streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0","--server.headless=true"]