# Use Python 3.10 slim image as the base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1

# Set Chrome/Chromium environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99
ENV CHROME_NO_SANDBOX=true

# Create app directory first
WORKDIR /app

# Install system dependencies for Chromium with optimizations
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl ca-certificates \
    chromium chromium-driver \
    libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libxss1 libgtk-3-0 \
    libasound2 libatspi2.0-0 fonts-liberation \
    libappindicator3-1 xdg-utils \
    fonts-dejavu-core fonts-freefont-ttf \
    procps \
    && chmod +x /usr/bin/chromedriver \
    && ln -sf /usr/bin/chromium /usr/bin/google-chrome \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create non-root user first (better security practice)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create directories for Chrome user data with proper permissions
RUN mkdir -p /tmp/chrome-data \
    && mkdir -p /app/chrome-sessions \
    && mkdir -p /dev/shm \
    && chown -R appuser:appuser /tmp/chrome-data \
    && chown -R appuser:appuser /app/chrome-sessions \
    && chmod 755 /tmp/chrome-data \
    && chmod 755 /app/chrome-sessions \
    && chmod 1777 /dev/shm

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code and set ownership
COPY . .
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (optional, platforms auto-detect)
EXPOSE 8000

# Health check for better deployment monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Optimized CMD with better resource management
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --threads 4 --timeout 300 --keep-alive 5 --max-requests 100 --max-requests-jitter 50 --preload --access-logfile - --error-logfile - --log-level info all:app"]
