# Security and Privacy Guide

## What Gets Excluded from Git

The following sensitive files and directories are excluded from version control (see `.gitignore`):

### User Data and Configuration
- `~/.zotero-llm/` - Your entire profile directory containing:
  - API keys for LLM providers
  - Local file paths specific to your machine
  - Chat history and sessions
  - Vector database indices
  - Profile settings

### Environment Files
- `.env` - Contains environment-specific configuration
- `settings.json` - User settings with API credentials
- `active_profile.json` - Current active profile

### Generated Data
- `vector_db/` - ChromaDB embeddings database
- `*.sqlite3` - Local database files
- `__pycache__/` - Python bytecode cache

## Data Storage Locations

### Profile Directory Structure
```
~/.zotero-llm/
 active_profile.json          # Current active profile
 profiles/
     default/                 # Profile ID
         profile.json         # Profile metadata
         settings.json        # Settings with API keys
         sessions.json        # Chat history
         chroma/             # Vector database
```

### What's Stored Where

**API Keys and Credentials** (`~/.zotero-llm/profiles/{profile}/settings.json`):
- OpenAI API key
- Anthropic API key
- Mistral API key
- Google API key
- Groq API key
- OpenRouter API key
- Ollama base URL

**Local Paths** (profile settings):
- Zotero database path (e.g., `/Users/you/Zotero/zotero.sqlite`)
- ChromaDB storage path
- PDF attachment locations

**Personal Data** (`~/.zotero-llm/profiles/{profile}/sessions.json`):
- Chat conversations
- Research queries
- Generated summaries
- Session metadata

**Vector Embeddings** (`~/.zotero-llm/profiles/{profile}/chroma/`):
- Embedded PDF content
- Metadata indices
- BM25 indices

## Setting Up on a New Machine

### Automated Setup (Recommended)

```bash
./setup.sh
```

This script:
1. Creates Python virtual environment
2. Installs all dependencies
3. Creates `.env` from template
4. Initializes profile directory structure
5. Creates default settings files

### Manual Setup

1. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** with your paths:
   ```bash
   ZOTERO_DB_PATH=/path/to/your/Zotero/zotero.sqlite
   ```

3. **Initialize profile directory**:
   ```bash
   mkdir -p ~/.zotero-llm/profiles/default/chroma
   ```

4. **The application will auto-generate**:
   - Default settings on first run
   - Profile metadata
   - Active profile marker

5. **Configure API keys** via Settings UI after starting the app

## Best Practices

### For Developers

1. **Never commit**:
   - `.env` files with real values
   - `settings.json` with API keys
   - Any file from `~/.zotero-llm/`
   - Personal Zotero database paths

2. **Always commit**:
   - `.env.example` with placeholder values
   - `setup.sh` initialization script
   - Documentation about setup process
   - Default configuration templates

3. **Before committing**:
   ```bash
   git status  # Check what's staged
   git diff    # Review changes
   # Verify no sensitive data is included
   ```

### For Users

1. **Backup your data**:
   ```bash
   # Backup profile data
   tar -czf zotero-llm-backup.tar.gz ~/.zotero-llm/
   ```

2. **Restore from backup**:
   ```bash
   tar -xzf zotero-llm-backup.tar.gz -C ~/
   ```

3. **Switch machines**:
   - Don't copy `.zotero-llm` directory
   - Use `setup.sh` on new machine
   - Reconfigure API keys via Settings UI
   - Re-index library (database will be rebuilt)

4. **Secure your API keys**:
   - Never share screenshots of Settings page
   - Don't commit or share `.env` or `settings.json`
   - Rotate keys if accidentally exposed

## Privacy Features

### Local-First Architecture
- All data stays on your device
- No cloud sync by default
- No telemetry or tracking
- API calls go directly to provider (not through our servers)

### Profile Isolation
- Each profile has separate:
  - Settings and API keys
  - Chat history
  - Vector database
  - Zotero library connection

### Data Control
- Delete profiles to remove all associated data
- Export chat history as JSON or Markdown
- Clear vector database without losing settings

## Sharing and Collaboration

### Safe to Share
- Source code (via Git)
- Documentation
- Feature requests and bug reports
- General configuration templates

### DO NOT Share
- Your `.zotero-llm/` directory
- API keys
- `.env` file with real values
- Settings JSON with credentials
- Chat history or sessions
- Vector database files

### Collaborative Development
If working on a team:
1. Each developer has their own `.zotero-llm/` directory
2. Share code via Git (sensitive data excluded)
3. Use `.env.example` to document required variables
4. Test with personal/test API keys
5. Never commit real credentials

## Troubleshooting

### "Profile not found" Error
```bash
# Reinitialize profile structure
./setup.sh
```

### "Missing API key" Error
- Check Settings UI and add API keys
- Or set in `.env` file
- Verify `~/.zotero-llm/profiles/default/settings.json` exists

### After Git Pull
```bash
# Reinstall dependencies if needed
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install

# Your settings are preserved (not in Git)
# No need to reconfigure
```

### Fresh Start
```bash
# Remove all user data
rm -rf ~/.zotero-llm/

# Reinitialize
./setup.sh

# Reconfigure settings via UI
```

## Security Recommendations

1. **API Key Management**:
   - Use environment-specific keys (dev/prod)
   - Rotate keys periodically
   - Monitor API usage for anomalies

2. **File Permissions**:
   ```bash
   # Restrict profile directory access
   chmod 700 ~/.zotero-llm/
   ```

3. **Git Safety**:
   ```bash
   # Verify .gitignore is working
   git status --ignored
   
   # Check for accidentally tracked sensitive files
   git ls-files | grep -E '\.env$|settings\.json|\.zotero-llm'
   ```

4. **Before Publishing**:
   ```bash
   # Search for potential secrets in history
   git log -p | grep -i "api.key\|password\|secret"
   ```

## Questions?

- Check [docs/profile_system_guide.md](docs/profile_system_guide.md) for profile details
- See [docs/multi_provider_system.md](docs/multi_provider_system.md) for provider configuration
- Open an issue for security concerns
