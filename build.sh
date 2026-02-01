#!/usr/bin/env bash
# Render build script for backend deployment

# Exit on error
set -e

echo "=== Starting Render Build ==="

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies with binary-only flag to avoid Rust compilation
echo "Installing Python dependencies (binary wheels only)..."
pip install --only-binary=:all: -r backend/requirements.txt || {
    echo "Some packages don't have binary wheels, installing with fallback..."
    pip install -r backend/requirements.txt
}

echo "=== Build Complete ==="
