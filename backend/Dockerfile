# Use a Python 3.10 slim image as the base
FROM python:3.10-slim

# Set environment variables for Railway
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Chromium (Railway-optimized)
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl ca-certificates \
    chromium chromium-driver \
    # Essential libraries for Chromium in Railway's environment
    libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libxss1 libgtk-3-0 \
    libasound2 libatspi2.0-0 fonts-liberation \
    libappindicator3-1 xdg-utils \
    # Clean up to reduce image size (important for Railway)
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Set Chrome/Chromium environment variables for Railway
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99
ENV CHROME_NO_SANDBOX=true

# Create app directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user (Railway recommends this)
RUN groupadd -r railwayuser && useradd -r -g railwayuser railwayuser \
    && chown -R railwayuser:railwayuser /app

# Switch to non-root user
USER railwayuser

# Railway automatically sets PORT environment variable
# Use it if available, otherwise default to 5000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 --max-requests 100 --max-requests-jitter 10 all:app"]