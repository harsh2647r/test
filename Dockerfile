# Use official Python slim image
FROM python:3.12-slim

# Install Linux dependencies needed for Playwright browsers
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libxshmfence1 \
    libxss1 \
    libxcursor1 \
    libxinerama1 \
    libxi6 \
    libdbus-1-3 \
    libdrm2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libwayland-client0 \
    libwayland-cursor0 \
    libwayland-egl1 \
    libxext6 \
    libexpat1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory in container
WORKDIR /app

# Copy requirements file and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install

# Copy all app files into container
COPY . .

# Expose port 5000 (Flask default)
EXPOSE 5000

# Run your Flask app with no-sandbox arg for Playwright
CMD ["python", "app.py"]
