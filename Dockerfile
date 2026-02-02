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
RUN pip3 install --no-cache-dir -r execution/requirements.txt --break-system-packages

# Copy web package files first for better caching
WORKDIR /app/web
COPY web/package.json web/package-lock.json* ./
RUN npm ci --only=production=false

# Copy web source files (excluding node_modules)
COPY web/tsconfig.json web/next.config.ts web/postcss.config.mjs web/eslint.config.mjs ./
COPY web/src ./src
COPY web/public ./public

# Build Next.js
RUN npm run build

# Copy the rest of the project files (execution scripts, directives, etc.)
WORKDIR /app
COPY execution ./execution
COPY directives ./directives
COPY .env* ./

# Create .tmp directory for runtime data (if it doesn't exist)
RUN mkdir -p .tmp

# Set environment variables for Selenium to find Chromium in Linux
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PORT=3000
ENV NODE_ENV=production

# Expose port (Replit will use PORT env var)
EXPOSE 3000

# Start Next.js (Next.js automatically reads PORT env var)
WORKDIR /app/web
CMD ["npm", "start"]
