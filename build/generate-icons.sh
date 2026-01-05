#!/bin/bash
# Icon generation script for electron-builder
# Creates placeholder icons if you don't have design assets yet

# This script creates basic icon files needed for building
# For production, replace these with proper branded icons

ICON_DIR="build/icons"
mkdir -p "$ICON_DIR"

# Create a simple text-based "icon" (1x1 transparent PNG)
# electron-builder will use this as a base
# In production, replace with actual 512x512+ PNG icons

echo "Creating placeholder icons..."

# For Linux (multiple sizes needed)
for size in 16 32 48 64 128 256 512; do
    # Create a minimal PNG (1x1 transparent pixel in base64)
    echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" | base64 -d > "$ICON_DIR/${size}x${size}.png"
done

echo " Linux icons created in $ICON_DIR"
echo ""
echo "  IMPORTANT: These are placeholder icons!"
echo "   For production releases, replace with proper branded icons:"
echo "   - macOS: build/icon.icns (512x512+)"
echo "   - Windows: build/icon.ico (256x256+)"
echo "   - Linux: build/icons/*.png (multiple sizes)"
echo ""
echo "   You can create icons from a PNG using:"
echo "   - macOS: iconutil or png2icns"
echo "   - Windows: png2ico or online converters"
echo "   - Linux: use ImageMagick to resize"
