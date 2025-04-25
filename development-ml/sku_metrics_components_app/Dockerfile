ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies for Selenium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies separately to leverage Docker cache
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt --prefer-binary --index-url https://pypi.org/simple

# Copy project files
COPY . /app

# Override DB_HOST for Docker environment
ENV DB_HOST=ml-postgresql

# Copy .env file into the container
COPY .env /app/.env

# Run the scheduler with unbuffered output
CMD ["python", "-u", "scheduler_main.py"]
