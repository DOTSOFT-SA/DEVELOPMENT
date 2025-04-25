# Base image with Python
ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

# Set working directory
WORKDIR /app

# Copy and install dependencies separately to leverage Docker cache
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /app

# Override DB_HOST for Docker environment
ENV DB_HOST=ml-postgresql

# Copy .env file into the container
COPY .env /app/.env

# Run the scheduler
CMD ["python", "-u", "scheduler_prediction.py"]
