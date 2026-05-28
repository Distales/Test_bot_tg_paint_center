# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create .env file from example if it doesn't exist (optional)
# RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Expose port (if using FastAPI for health check)
# EXPOSE 8000

# Command to run the bot
CMD ["python", "-m", "app.main"]