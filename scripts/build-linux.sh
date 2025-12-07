#!/bin/bash
#
# Build Linux AppImage with bundled Python environment
# This script should be run on Linux (or in a Linux Docker container)
#

set -e

echo "=========================================="
echo "Building Linux AppImage"
echo "=========================================="

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Warning: Not running on Linux. The bundled Python will not work on Linux!"
    echo "Consider building on Linux or using Docker."
fi

# 1. Create a fresh Python virtual environment for Linux
echo "Creating Linux Python environment..."
rm -rf python-dist-linux
python3 -m venv python-dist-linux

# 2. Install backend dependencies
echo "Installing backend dependencies in virtual environment..."
source python-dist-linux/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "✓ Python environment ready at: python-dist-linux/"

# 3. Temporarily swap python-dist directories
echo "Swapping Python environments..."
if [ -d "python-dist" ]; then
    mv python-dist python-dist-backup
fi
mv python-dist-linux python-dist

# 4. Build the AppImage
echo "Building Electron app for Linux..."
npm run build
electron-builder --linux --publish never

# 5. Restore original python-dist
echo "Restoring original Python environment..."
mv python-dist python-dist-linux
if [ -d "python-dist-backup" ]; then
    mv python-dist-backup python-dist
fi

echo "=========================================="
echo "✓ Build complete!"
echo "AppImages are in: release/"
echo "=========================================="
