#!/bin/bash
# setup.sh - Initialize Zotero LLM Plugin on a new machine

set -e  # Exit on error

echo " Setting up Zotero LLM Plugin..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo " Python 3 is required but not installed."
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo " Node.js is required but not installed."
    exit 1
fi

# Create Python virtual environment
if [ ! -d ".venv" ]; then
    echo " Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo " Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo " Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Install Node.js dependencies
echo " Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo " Creating .env file from template..."
    cp .env.example .env
    echo "  Please edit .env file with your Zotero database path"
fi

# Initialize profile directory structure
echo " Initializing profile directory..."
mkdir -p ~/.zotero-llm/profiles/default/chroma

# Create initial settings if they don't exist
SETTINGS_FILE="$HOME/.zotero-llm/profiles/default/settings.json"
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "  Creating default settings..."
    cat > "$SETTINGS_FILE" << 'EOF'
{
  "activeProviderId": "ollama",
  "activeModel": "",
  "embeddingModel": "bge-base",
  "zoteroPath": "/Users/$USER/Zotero/zotero.sqlite",
  "chromaPath": "",
  "providers": {
    "ollama": {
      "enabled": true,
      "credentials": {
        "base_url": "http://localhost:11434"
      }
    },
    "openai": {
      "enabled": false,
      "credentials": {
        "api_key": ""
      }
    },
    "anthropic": {
      "enabled": false,
      "credentials": {
        "api_key": ""
      }
    },
    "perplexity": {
      "enabled": false,
      "credentials": {
        "api_key": ""
      }
    },
    "google": {
      "enabled": false,
      "credentials": {
        "api_key": ""
      }
    },
    "groq": {
      "enabled": false,
      "credentials": {
        "api_key": ""
      }
    },
    "openrouter": {
      "enabled": false,
      "credentials": {
        "api_key": ""
      }
    }
  }
}
EOF
fi

# Create active profile marker
ACTIVE_PROFILE="$HOME/.zotero-llm/active_profile.json"
if [ ! -f "$ACTIVE_PROFILE" ]; then
    echo " Setting default profile as active..."
    echo '{"profileId": "default"}' > "$ACTIVE_PROFILE"
fi

echo ""
echo " Setup complete!"
echo ""
echo " Next steps:"
echo "1. Edit .env and set your ZOTERO_DB_PATH"
echo "2. Update settings in ~/.zotero-llm/profiles/default/settings.json if needed"
echo "3. If using Ollama, make sure it's running: ollama serve"
echo "4. Start the backend: source .venv/bin/activate && uvicorn backend.main:app --reload"
echo "5. Start the frontend: cd frontend && npm run dev"
echo ""
echo " API Keys:"
echo "   Configure provider API keys via the Settings UI after starting the app"
echo ""
