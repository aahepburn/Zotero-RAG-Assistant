# Desktop App Development Guide

## Quick Start - Desktop Development

### Prerequisites
1. **Node.js 16+** and **npm**
2. **Python 3.8+** with venv
3. **Zotero** installed with a local library

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/aahepburn/zotero-llm-plugin.git
cd zotero-llm-plugin

# 2. Install dependencies
npm install              # Root dependencies (Electron)
cd frontend && npm install && cd ..  # Frontend dependencies

# 3. Setup Python environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 4. Configure settings (optional - can also do via UI)
cp .env.example .env
# Edit .env with your Zotero database path
```

### Running in Development

The easiest way is to use the combined dev script:

```bash
npm run dev
```

This runs three processes concurrently:
1. **Frontend** - Vite dev server on http://localhost:5173
2. **Backend** - FastAPI server on http://localhost:8000
3. **Electron** - Desktop window loading the frontend

Or run them separately in different terminals:

```bash
# Terminal 1: Frontend
npm run dev:frontend

# Terminal 2: Backend (activate venv first!)
source .venv/bin/activate
npm run dev:backend

# Terminal 3: Electron
npm run dev:electron
```

### Platform-Specific Setup

#### macOS
No additional setup needed. Everything should work out of the box.

```bash
# If you want to build installers, install dependencies
npm install
```

#### Windows
Use PowerShell or Git Bash:

```bash
# Activate venv
.venv\Scripts\activate

# Rest is the same
npm run dev
```

#### Ubuntu/Linux
Install additional build dependencies:

```bash
# For building native modules
sudo apt-get install -y build-essential

# For packaging AppImage
sudo apt-get install -y libfuse2

# Then proceed normally
npm run dev
```

## Building Installers

### Build All Platform-Specific Files

```bash
# Make sure you're in the project root
npm run build          # Build frontend + Electron TypeScript
npm run package:mac    # macOS: DMG + ZIP
npm run package:win    # Windows: NSIS + ZIP
npm run package:linux  # Linux: AppImage + DEB
```

Output will be in `release/` directory.

### Building for Distribution

For a complete release that supports auto-updates:

1. **Increment version** in `package.json`:
   ```json
   "version": "0.1.1"
   ```

2. **Build on each platform**:
   - macOS: Run `npm run package:mac` on a Mac
   - Windows: Run `npm run package:win` on Windows
   - Linux: Run `npm run package:linux` on Ubuntu

3. **Tag the release**:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

4. **Create GitHub Release**:
   - Go to: https://github.com/aahepburn/zotero-llm-plugin/releases/new
   - Select tag `v0.1.1`
   - Title: `v0.1.1 - Description`
   - Upload all files from `release/` directory:
     - `*.dmg`, `*.zip`, `latest-mac.yml` (macOS)
     - `*.exe`, `latest.yml` (Windows)  
     - `*.AppImage`, `*.deb`, `latest-linux.yml` (Linux)
   - Publish release

5. **Users get auto-updates**:
   - Installed apps will check for updates
   - Download and install automatically (or with user confirmation)

## Packaging Python Backend

For production builds, you need to create a standalone Python binary:

### Using PyInstaller

```bash
# Activate your venv
source .venv/bin/activate

# Install PyInstaller
pip install pyinstaller

# Build backend binary (single file)
pyinstaller --onefile \
  --name backend \
  --hidden-import backend.main \
  --hidden-import backend.interface \
  --hidden-import backend.zotero_dbase \
  --hidden-import backend.vector_db \
  --hidden-import backend.embed_utils \
  --hidden-import backend.model_providers \
  --collect-all chromadb \
  --collect-all sentence_transformers \
  --collect-all transformers \
  backend/main.py

# Binary will be in dist/backend/backend (or backend.exe on Windows)
```

**Important:** Build on each target platform:
- Build on macOS for macOS binaries
- Build on Windows for Windows binaries
- Build on Linux for Linux binaries

### Alternative: Bundle Python Runtime

Instead of PyInstaller, you can bundle the Python runtime and dependencies:

1. Create a minimal Python environment
2. Include it in `extraResources`
3. Modify `main.ts` to use the bundled Python

This is more reliable but increases app size.

## Directory Structure

```
zotero-llm-plugin/
├── electron/              # Electron main process
│   ├── main.ts           # Main process logic
│   ├── preload.ts        # Preload script (context bridge)
│   └── tsconfig.json     # TypeScript config
├── frontend/             # React frontend
│   ├── src/
│   └── dist/             # Built frontend (after npm run build)
├── backend/              # Python FastAPI backend
│   ├── main.py
│   └── ...
├── build/                # Build resources (icons, etc.)
│   ├── icon.icns        # macOS icon
│   ├── icon.ico         # Windows icon
│   ├── icons/           # Linux icons (various sizes)
│   └── entitlements.mac.plist
├── dist/                 # Built Electron code
│   └── electron/
├── release/              # Built installers
│   ├── *.dmg
│   ├── *.exe
│   └── *.AppImage
├── package.json          # Root package.json (Electron)
└── requirements.txt      # Python dependencies
```

## Development Workflow

### Making Changes

1. **Frontend changes**: Edit files in `frontend/src/` - Vite hot-reloads automatically
2. **Backend changes**: Edit files in `backend/` - uvicorn reloads automatically
3. **Electron changes**: Edit `electron/main.ts` or `preload.ts` - restart Electron

### Testing Production Build Locally

```bash
# Build everything
npm run build

# Package for your platform
npm run package:mac  # or :win, :linux

# Install and test the generated installer
```

### Debugging

#### Frontend Debug
- Electron automatically opens DevTools in development
- Use `console.log()` as normal
- Check Network tab for backend requests

#### Backend Debug
- Backend logs appear in the terminal running `dev:backend`
- Or in Electron's console (stdout is captured)
- Check FastAPI docs at http://localhost:8000/docs

#### Electron Main Process Debug
- Main process logs appear in the terminal running Electron
- Use `console.log()` in `main.ts`
- Check for process spawn errors

## Configuration

### Application Settings

Settings are stored in:
- **Development**: `~/.zotero-llm/profiles/default/settings.json`
- **Production**: Same location

### Environment Variables

Create `.env` in project root:

```env
# Zotero database path
ZOTERO_DB_PATH=/Users/yourname/Zotero/zotero.sqlite

# Development mode (optional)
NODE_ENV=development
```

### Build Configuration

Edit `package.json` → `build` section:

```json
{
  "build": {
    "appId": "com.aahepburn.zotero-llm",
    "productName": "Zotero LLM Assistant",
    "mac": { ... },
    "win": { ... },
    "linux": { ... }
  }
}
```

## Icons and Branding

Place your app icons in the `build/` directory:

- **macOS**: `build/icon.icns` (1024x1024 base)
- **Windows**: `build/icon.ico` (256x256 base)
- **Linux**: `build/icons/` with various sizes:
  - `16x16.png`
  - `32x32.png`
  - `48x48.png`
  - `64x64.png`
  - `128x128.png`
  - `256x256.png`
  - `512x512.png`

Generate icons from a master PNG:

```bash
# Install icon tools
npm install --global electron-icon-maker

# Generate all icon sizes
electron-icon-maker --input=./icon-source.png --output=./build
```

## Code Signing (Optional but Recommended)

### macOS

1. Get an Apple Developer account
2. Create certificates in Xcode
3. Add to package.json:

```json
{
  "build": {
    "mac": {
      "identity": "Developer ID Application: Your Name (TEAMID)"
    }
  }
}
```

### Windows

1. Get a code signing certificate (e.g., from DigiCert)
2. Add to package.json:

```json
{
  "build": {
    "win": {
      "certificateFile": "path/to/cert.pfx",
      "certificatePassword": "password"
    }
  }
}
```

## Troubleshooting

### "Cannot find module 'electron'"
```bash
npm install  # Make sure root dependencies are installed
```

### Backend won't start in Electron
- Check Python is installed: `python3 --version`
- Check venv is set up: `ls .venv/`
- Try running backend manually: `python3 -m uvicorn backend.main:app`

### Build fails on macOS
- Install Xcode command line tools: `xcode-select --install`
- Accept Xcode license: `sudo xcodebuild -license accept`

### Build fails on Windows
- Install Visual Studio Build Tools
- Or install the full Visual Studio Community edition

### Build fails on Linux
```bash
sudo apt-get install -y build-essential libfuse2
```

### App crashes on startup (production)
- Check backend binary is included in `extraResources`
- Verify binary has execute permissions (Linux/macOS)
- Check main process logs for errors

### Auto-updates not working
- Verify GitHub release is published (not draft)
- Check all platform `.yml` files are uploaded
- Ensure version in package.json matches Git tag
- Check app console for update errors

## Advanced Topics

### Custom Backend Port

Edit `electron/main.ts`:

```typescript
const BACKEND_PORT = 8001;  // Change from 8000
```

### Multiple Window Support

Add window management in `main.ts`:

```typescript
let windows: BrowserWindow[] = [];

function createWindow() {
  const win = new BrowserWindow({ ... });
  windows.push(win);
  return win;
}
```

### Native Menus

Add application menu in `main.ts`:

```typescript
import { Menu } from 'electron';

const template = [
  {
    label: 'File',
    submenu: [
      { role: 'quit' }
    ]
  },
  // ... more menu items
];

Menu.setApplicationMenu(Menu.buildFromTemplate(template));
```

### Deep Linking

Register custom protocol handler:

```typescript
app.setAsDefaultProtocolClient('zotero-llm');

app.on('open-url', (event, url) => {
  // Handle zotero-llm:// URLs
});
```

## Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [electron-builder](https://www.electron.build/)
- [electron-updater](https://www.electron.build/auto-update)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)

## Getting Help

- **Issues**: https://github.com/aahepburn/zotero-llm-plugin/issues
- **Discussions**: https://github.com/aahepburn/zotero-llm-plugin/discussions
- **Electron Discord**: https://discord.gg/electron
