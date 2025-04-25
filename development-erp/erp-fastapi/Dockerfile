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

# Expose the API port
EXPOSE 7000

### Run tests during the build (if fails will prevent to continue)
RUN pytest tests/tests.py --maxfail=1 --disable-warnings --exitfirst

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]
