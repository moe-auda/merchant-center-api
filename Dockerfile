# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python scripts
COPY *.py .

# Copy CSV files
COPY csvs/ ./csvs/

# Copy service account key
COPY service_account_key.json .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# No default command added - i think we canspecify which script/all scripts to run when starting the container
# Example: docker run image_name python books_scraping.py
# Example: docker run image_name python subscriptions_scraping.py
# Example: docker run image_name python single_issue_scraping.py
