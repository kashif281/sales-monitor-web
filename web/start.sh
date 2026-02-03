#!/bin/sh
set -e

cd /app/web

# Verify .next exists (should be built during Docker build)
if [ ! -d .next ] || [ ! -f .next/BUILD_ID ]; then
  echo "❌ ERROR: .next directory not found! This should have been built during Docker build."
  echo "Building now as fallback (this may cause startup delay)..."
  npm run build
fi

echo "🚀 Starting Next.js server on port ${PORT:-3000}..."
exec npm start
