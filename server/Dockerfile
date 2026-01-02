FROM python:3.14-slim

# Set environment variables for Python and pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create and switch to a non-root user
RUN useradd -m appuser
WORKDIR /app

# Install system dependencies (if you need build tools, add them here)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./src .

# Switch to non-root user for better security
USER appuser

# Expose the app port (adjust as needed)
EXPOSE 8080

# Use exec form for CMD
CMD ["python", "main.py"]
