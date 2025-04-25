# Base image with Python
ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as base

# Set working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Override DB_HOST for Docker environment
ENV DB_HOST=dolibarr-mysql

# Copy .env file into the container
COPY .env /app/.env

# Set the container to run and stop after the script finishes
ENTRYPOINT ["python", "-u", "main.py"]
