#!/bin/sh
set -e

cd /app/web

# Check if .next directory exists and has BUILD_ID
if [ ! -d .next ] || [ ! -f .next/BUILD_ID ]; then
  echo "⚠️  .next directory not found or incomplete. Building Next.js application..."
  npm run build
  echo "✅ Build completed successfully"
else
  echo "✅ .next directory exists, skipping build"
fi

echo "🚀 Starting Next.js server..."
exec npm start
