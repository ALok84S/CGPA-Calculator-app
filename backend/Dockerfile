# Use Python 3.10 slim image as the base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies for Chromium
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl ca-certificates \
    chromium chromium-driver \
    libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libxss1 libgtk-3-0 \
    libasound2 libatspi2.0-0 fonts-liberation \
    libappindicator3-1 xdg-utils \
    fonts-dejavu-core fonts-freefont-ttf \
    && chmod +x /usr/bin/chromedriver \
    && ln -sf /usr/bin/chromium /usr/bin/google-chrome \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Set Chrome/Chromium environment variables
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99
ENV CHROME_NO_SANDBOX=true

# Create app directory
WORKDIR /app

# Create non-root user first (better security practice)
RUN groupadd -r appuser && useradd -r -g appuser appuser

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

# Command optimized for both Render and Railway
# CHANGE THIS LINE
# CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 300 --keep-alive 5 --max-requests 100 --preload --access-logfile - --error-logfile - --log-level info all:app"]
# TO THIS
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:${PORT:-8000}", "--timeout", "300", "--keep-alive", "5", "--max-requests", "100", "--preload", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "all:app"]