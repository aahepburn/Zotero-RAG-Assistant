# Quick Reference: Desktop App Commands

## Development

```bash
# Run everything (frontend + backend + Electron)
npm run dev

# Run individually
npm run dev:frontend   # Vite dev server
npm run dev:backend    # Python backend (needs venv activated)
npm run dev:electron   # Electron window
```

## Building

```bash
# Build TypeScript & frontend
npm run build

# Package for current platform
npm run package:mac     # macOS
npm run package:win     # Windows
npm run package:linux   # Linux

# Package for all platforms
npm run package:all
```

## First-Time Setup

```bash
# 1. Install dependencies
npm install
cd frontend && npm install && cd ..

# 2. Setup Python (if not done)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Run in development
npm run dev
```

## Release Process

```bash
# 1. Update version in package.json
# 2. Build on each platform
npm run build
npm run package:mac  # (or :win, :linux)

# 3. Tag and push
git tag v0.1.0
git push origin v0.1.0

# 4. Create GitHub Release at:
#    https://github.com/aahepburn/zotero-llm-plugin/releases/new
# 5. Upload ALL files from release/ directory
```

## Common Tasks

```bash
# Clean build
rm -rf dist release node_modules
npm install
npm run build

# Package Python backend (optional)
source .venv/bin/activate
./build-backend.sh

# Test production build locally
npm run package:mac
# Then install the generated .dmg/.exe/.AppImage
```

## Project Structure

```
zotero-llm-plugin/
├── electron/          # Main & preload processes
├── frontend/          # React app
├── backend/           # Python FastAPI
├── build/             # Icons & resources
├── dist/              # Built code (gitignored)
├── release/           # Installers (gitignored)
└── package.json       # Root config
```

## Documentation

- **Getting Started**: `/docs/DESKTOP_APP.md`
- **Release Process**: `/docs/RELEASE_PROCESS.md`
- **Architecture**: `/electron/README.md`
- **Summary**: `/DESKTOP_APP_SUMMARY.md`

## Troubleshooting

```bash
# Backend won't start
python3 --version  # Check Python
source .venv/bin/activate
python3 -m uvicorn backend.main:app

# Build fails
rm -rf node_modules dist release
npm install
npm run build

# Electron errors
npm install electron --save-dev
```

## Key URLs

- **Repo**: https://github.com/aahepburn/zotero-llm-plugin
- **Releases**: https://github.com/aahepburn/zotero-llm-plugin/releases
- **Issues**: https://github.com/aahepburn/zotero-llm-plugin/issues

## Dependencies

- Node.js 16+
- Python 3.8+
- npm or yarn
- (Optional) PyInstaller for backend binary

## Port Configuration

- Frontend Dev: `http://localhost:5173` (Vite)
- Backend: `http://localhost:8000` (FastAPI)
- Change in: `electron/main.ts` (BACKEND_PORT, FRONTEND_DEV_URL)
