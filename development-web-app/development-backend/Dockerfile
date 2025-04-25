# Base image with Python
ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies using cache for pip
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt

# Set environment variable dynamically
ENV DB_HOST=db

# Copy .env file into the container
COPY backend/.env /app/.env

# Run
CMD python backend/manage.py runserver 0.0.0.0:8700
