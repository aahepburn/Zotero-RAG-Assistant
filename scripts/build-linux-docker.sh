#!/bin/bash
#
# Build Linux AppImage using Docker
# This ensures the bundled Python environment is Linux-compatible
#

set -e

echo "=========================================="
echo "Building Linux AppImage with Docker"
echo "=========================================="

# Build Docker image
echo "Building Docker image..."
docker build -f Dockerfile.linux-build -t zotero-llm-builder .

# Run build in container
echo "Running build in container..."
docker run --rm \
    -v "$(pwd)/release:/app/release" \
    zotero-llm-builder

echo "=========================================="
echo "✓ Build complete!"
echo "AppImages are in: release/"
echo "=========================================="
ls -lh release/*.AppImage
