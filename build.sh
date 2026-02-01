#!/usr/bin/env bash
# Render build script for backend deployment

# Exit on error
set -e

echo "=== Starting Render Build ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "=== Build Complete ==="
