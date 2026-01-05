#!/bin/bash
# Build Linux PyInstaller bundle using Docker
# This creates a Linux-native PyInstaller executable

set -e

echo "========================================"
echo "Building Linux PyInstaller bundle"
echo "========================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Clean previous bundle
if [ -d "python-dist-linux" ]; then
    echo "🧹 Cleaning previous Linux bundle..."
    rm -rf python-dist-linux
fi

mkdir -p python-dist-linux

# Build for amd64
echo " Building Docker image for amd64..."
docker build --platform linux/amd64 -f Dockerfile.pyinstaller-linux -t zotero-pyinstaller-linux-amd64 .

echo " Extracting amd64 bundle..."
docker run --rm --platform linux/amd64 -v "$PWD/python-dist-linux:/app/python-dist-linux" zotero-pyinstaller-linux-amd64

# Verify the bundle
if [ -f "python-dist-linux/backend_server" ]; then
    echo " Linux PyInstaller bundle created successfully!"
    echo " Bundle location: python-dist-linux/"
    ls -lh python-dist-linux/
    file python-dist-linux/backend_server
else
    echo " Bundle creation failed!"
    exit 1
fi

echo "========================================"
echo " Build complete!"
echo "========================================"
