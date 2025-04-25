# Base image with Python
ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

# Set working directory
WORKDIR /app

# Copy the rest of the application files
COPY . /app

# Install dependencies efficiently
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Override DB_HOST for Docker environment
ENV DB_HOST=db
ENV API_HOST="http://development-backend:"

# Copy .env file into the container
COPY .env /app/.env

# Use a script to gracefully handle the start
ENTRYPOINT [ "sh", "-c", "echo '⏳ Waiting for 20 seconds before starting development-db...' && sleep 20 && echo '🚀 Starting development-db now...' && exec python -u main.py" ]