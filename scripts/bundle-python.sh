#!/bin/bash
# bundle-python.sh - Create a relocatable Python virtual environment for bundling
# This creates a Python environment with all backend dependencies that can be
# bundled with the Electron app for distribution.

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUNDLE_DIR="$PROJECT_ROOT/python-dist"

echo "🐍 Creating bundled Python environment for distribution..."

# Detect platform
case "$(uname -s)" in
    Darwin*)    PLATFORM="darwin";;
    Linux*)     PLATFORM="linux";;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="win32";;
    *)          echo "❌ Unsupported platform"; exit 1;;
esac

echo "📦 Platform: $PLATFORM"

# Clean previous bundle
if [ -d "$BUNDLE_DIR" ]; then
    echo "🧹 Cleaning previous bundle..."
    rm -rf "$BUNDLE_DIR"
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_CMD=$(command -v python3)
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION at $PYTHON_CMD"

# Create virtual environment
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv "$BUNDLE_DIR"

# Activate virtual environment
if [ "$PLATFORM" = "win32" ]; then
    source "$BUNDLE_DIR/Scripts/activate"
    PIP_CMD="$BUNDLE_DIR/Scripts/pip"
    PYTHON_BUNDLE_CMD="$BUNDLE_DIR/Scripts/python"
else
    source "$BUNDLE_DIR/bin/activate"
    PIP_CMD="$BUNDLE_DIR/bin/pip"
    PYTHON_BUNDLE_CMD="$BUNDLE_DIR/bin/python"
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
$PIP_CMD install --upgrade pip setuptools wheel --quiet

# Install backend requirements
echo "📥 Installing backend dependencies (this may take a few minutes)..."
$PIP_CMD install -r "$PROJECT_ROOT/requirements.txt"

# Clean up to reduce size (but keep package metadata!)
echo "🗜️  Optimizing bundle size..."

# Remove __pycache__ directories
find "$BUNDLE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove .pyc files
find "$BUNDLE_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove test directories (but not test dependencies needed at runtime)
find "$BUNDLE_DIR/lib" -type d -path "*/tests" -exec rm -rf {} + 2>/dev/null || true
find "$BUNDLE_DIR/lib" -type d -path "*/test" -exec rm -rf {} + 2>/dev/null || true

# Remove documentation
find "$BUNDLE_DIR/lib" -type d -name "docs" -exec rm -rf {} + 2>/dev/null || true

# Remove examples
find "$BUNDLE_DIR/lib" -type d -name "examples" -exec rm -rf {} + 2>/dev/null || true

# Get bundle size
BUNDLE_SIZE=$(du -sh "$BUNDLE_DIR" | cut -f1)
echo "✅ Python bundle created successfully!"
echo "📊 Bundle size: $BUNDLE_SIZE"
echo "📍 Location: $BUNDLE_DIR"
echo ""

# Create python3 symlink for Linux compatibility (if it doesn't exist)
if [ "$PLATFORM" = "linux" ]; then
    PYTHON_BIN_DIR="$BUNDLE_DIR/bin"
    if [ ! -f "$PYTHON_BIN_DIR/python3" ] && [ -f "$PYTHON_BIN_DIR/python" ]; then
        echo "🔗 Creating python3 symlink for Linux compatibility..."
        ln -s python "$PYTHON_BIN_DIR/python3"
    fi
    # Also ensure python exists if only python3 exists
    if [ ! -f "$PYTHON_BIN_DIR/python" ] && [ -f "$PYTHON_BIN_DIR/python3" ]; then
        echo "🔗 Creating python symlink for compatibility..."
        ln -s python3 "$PYTHON_BIN_DIR/python"
    fi
fi

# Verify the bundle
echo "🔍 Verifying installation..."
if $PYTHON_BUNDLE_CMD -c "import fastapi, uvicorn, chromadb, sentence_transformers; print('✓ All critical imports successful')"; then
    echo ""
    echo "✅ Bundle verification passed!"
    echo ""
    echo "Next steps:"
    echo "1. Build Electron app: npm run package:mac (or :win, :linux)"
    echo "2. The bundled Python will be included automatically"
    echo "3. App will run standalone without requiring system Python"
    echo ""
    echo "💡 Note: App will also fall back to system Python if bundle is not available"
else
    echo "❌ Bundle verification failed!"
    exit 1
fi
