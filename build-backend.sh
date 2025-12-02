#!/bin/bash
# build-backend.sh - Package Python backend as standalone binary
# This script uses PyInstaller to create a single executable that includes
# all Python dependencies, making it easy to bundle with the Electron app.

set -e  # Exit on error

echo "🔧 Building Python backend binary..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/backend build/backend backend.spec

# Build the backend binary
echo "🏗️  Building backend with PyInstaller..."
pyinstaller \
    --onefile \
    --name backend \
    --hidden-import backend.main \
    --hidden-import backend.interface \
    --hidden-import backend.zotero_dbase \
    --hidden-import backend.vector_db \
    --hidden-import backend.embed_utils \
    --hidden-import backend.pdf \
    --hidden-import backend.external_api_utils \
    --hidden-import backend.conversation_store \
    --hidden-import backend.profile_manager \
    --hidden-import backend.model_providers \
    --hidden-import backend.model_providers.ollama \
    --hidden-import backend.model_providers.openai \
    --hidden-import backend.model_providers.anthropic \
    --hidden-import backend.model_providers.additional \
    --collect-all chromadb \
    --collect-all sentence_transformers \
    --collect-all transformers \
    --collect-all onnxruntime \
    --collect-all fastapi \
    --collect-all uvicorn \
    --collect-all pydantic \
    --collect-all starlette \
    --add-data "backend:backend" \
    backend/main.py

# Check if build succeeded
if [ -f "dist/backend/backend" ] || [ -f "dist/backend/backend.exe" ]; then
    echo "✅ Backend binary built successfully!"
    echo "📍 Location: dist/backend/"
    
    # Make executable on Unix systems
    if [ -f "dist/backend/backend" ]; then
        chmod +x dist/backend/backend
        echo "🔓 Made binary executable"
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Test the binary: ./dist/backend/backend (or backend.exe on Windows)"
    echo "2. Copy to Electron resources: Handled automatically by electron-builder"
    echo "3. Build Electron app: npm run package:mac (or :win, :linux)"
else
    echo "❌ Build failed! Check errors above."
    exit 1
fi
