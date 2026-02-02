#!/usr/bin/env node
const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

const nextDir = path.join(__dirname, '.next');
const buildId = path.join(nextDir, 'BUILD_ID');

if (!fs.existsSync(nextDir) || !fs.existsSync(buildId)) {
  console.log('⚠️  .next directory not found or incomplete. Building Next.js application...');
  try {
    execSync('npm run build', { stdio: 'inherit', cwd: __dirname });
    console.log('✅ Build completed successfully');
  } catch (error) {
    console.error('❌ Build failed:', error.message);
    process.exit(1);
  }
} else {
  console.log('✅ .next directory exists, skipping build');
}
