# Use Node.js as base
FROM node:18-slim

# Install Python and Chrome for Selenium scrapers
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    chromium \
    chromium-driver \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy execution requirements first to leverage cache
COPY execution/requirements.txt ./execution/
RUN pip3 install --no-cache-dir -r execution/requirements.txt

# Copy web files
COPY web/package*.json ./web/
WORKDIR /app/web
RUN npm install

# Copy the rest of the code
WORKDIR /app
COPY . .

# Build Next.js
WORKDIR /app/web
RUN npm run build

# Set environment variables for Selenium to find Chromium in Linux
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Expose port
EXPOSE 3000

# Start Next.js
CMD ["npm", "start"]
