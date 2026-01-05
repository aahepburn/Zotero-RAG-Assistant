# PyInstaller Bundle Migration Guide

## Overview

The Python bundling has been migrated from venv-based bundles to PyInstaller for better reliability and true standalone distribution.

## What Changed

### Before (venv with symlinks)
- Used `python3 -m venv` to create bundle
- Created **symlinks** to system Python
- Symlinks broke when app moved to /Applications
- **Result:** "Python interpreter missing" errors

### After (PyInstaller standalone)
- Uses PyInstaller to create standalone executable
- Bundles Python interpreter and all dependencies
- No symlinks - everything is self-contained
- **Result:** Truly portable, works anywhere

## Files Added/Modified

### New Files
1. **`backend_server_main.py`** - Entry point wrapper for PyInstaller bundle
2. **`backend_bundle.spec`** - PyInstaller specification file
3. **`scripts/bundle-python-pyinstaller.sh`** - Bundling script using PyInstaller

### Modified Files
1. **`package.json`** - DMG configuration with Applications folder link and auto-update enabled
2. **`electron/main.ts`** - Enhanced to detect and run PyInstaller bundles

## How to Build

### Step 1: Bundle Python Backend (Required before packaging)

**macOS/Linux:**
```bash
# Clean old bundle first
rm -rf python-dist/

# Create new PyInstaller bundle
./scripts/bundle-python-pyinstaller.sh
```

**Windows:**
```powershell
# Clean old bundle first
Remove-Item -Path python-dist -Recurse -Force

# Create new PyInstaller bundle (Option 1: Batch file)
.\scripts\bundle-python-pyinstaller-windows.bat

# Or Option 2: PowerShell directly
.\scripts\bundle-python-pyinstaller-windows.ps1
```

**What this does:**
- Installs PyInstaller and dependencies
- Builds standalone backend executable
- Creates `python-dist/` directory with:
  - `backend_server` (macOS/Linux) or `backend_server.exe` (Windows)
  - Supporting libraries and data files
  - No symlinks!

**Expected output:**
```
 PyInstaller bundle created successfully!
 Bundle size: ~800M
 Location: python-dist/
 Backend executable is a proper binary (not a symlink)
```

### Step 2: Build Electron App

```bash
# Build TypeScript and frontend
npm run build

# Package for your platform
npm run package:mac    # macOS
npm run package:win    # Windows
npm run package:linux  # Linux
```

**What this creates for macOS:**
- `release/Zotero RAG Assistant-{version}-mac-arm64.dmg`
- `release/Zotero RAG Assistant-{version}-mac-x64.dmg`
- `release/Zotero RAG Assistant-{version}-mac-arm64.zip`
- `release/Zotero RAG Assistant-{version}-mac-x64.zip`
- `release/*.blockmap` files
- **`release/latest-mac.yml`** - Critical for macOS auto-updates!

**What this creates for Windows:**
- `release/Zotero RAG Assistant-{version}-win-x64.exe`
- `release/Zotero RAG Assistant-{version}-win-ia32.exe`
- `release/Zotero RAG Assistant-{version}-win-x64.zip`
- `release/Zotero RAG Assistant-{version}-win-ia32.zip`
- **`release/latest.yml`** - Critical for Windows auto-updates!

**What this creates for Linux:**
- `release/zotero-rag-assistant_{version}_amd64.deb` (Debian/Ubuntu)
- `release/zotero-rag-assistant_{version}_arm64.deb` (ARM 64-bit)
- `release/Zotero-RAG-Assistant-{version}-linux-x64.AppImage` (Portable)
- **`release/latest-linux.yml`** - Critical for Linux auto-updates!

### Step 3: Verify DMG Layout

Mount the DMG and check:
-  App icon visible on left side
-  Applications folder shortcut on right side
-  Can drag app to Applications folder

### Step 4: Verify Python Bundle

**macOS:**
```bash
# Check the built app's bundle
ls -la "release/mac-arm64/Zotero RAG Assistant.app/Contents/Resources/python/"

# Should show backend_server (not a symlink)
file "release/mac-arm64/Zotero RAG Assistant.app/Contents/Resources/python/backend_server"
# Should show: Mach-O 64-bit executable arm64
```

**Windows:**
```powershell
# Check the python-dist directory before packaging
Get-ChildItem python-dist\backend_server.exe

# Test the executable
python-dist\backend_server.exe --help

# After packaging, check the app resources
# The installer places files in: C:\Users\{username}\AppData\Local\Programs\ZoteroRAG\resources\python\
```

**Linux:**
```bash
# Extract and check the .deb package
dpkg-deb -c release/zotero-rag-assistant_*_amd64.deb | grep backend_server
# Should show the backend_server executable

# For AppImage
./release/Zotero-RAG-Assistant-*-linux-x64.AppImage --appimage-extract
file squashfs-root/resources/python/backend_server
# Should show: ELF 64-bit executable
```

### Step 5: Test Installation

```bash
# Install from DMG
open "release/Zotero RAG Assistant-{version}-mac-arm64.dmg"
# Drag to Applications
# Launch and verify backend starts
```

## Publishing Release

```bash
# Set GitHub token
export GH_TOKEN=your_github_token

# Publish to GitHub releases
npm run publish:mac
```

**Critical:** Verify the release includes:
-  Both .dmg files (arm64 and x64)
-  Both .zip files (arm64 and x64)
-  Both .blockmap files
-  **latest-mac.yml** file (required for auto-updates!)

## Troubleshooting

### "Bundle creation failed"
- **Cause:** PyInstaller couldn't analyze dependencies
- **Fix:** Ensure all dependencies in `requirements.txt` are installed
- **Check:** Run `pip list` to verify packages

### "Backend executable is a symlink"
- **Cause:** Old venv-based bundle still present
- **Fix:** `rm -rf python-dist/` and re-run bundle script

### "Auto-update 404 error"
- **Cause:** `latest-mac.yml` not uploaded to GitHub release
- **Fix:** Ensure file exists in `release/` before publishing
- **Verify:** Check `writeUpdateInfo: true` in package.json

### "Python interpreter missing" after install
- **Cause:** PyInstaller bundle wasn't created before packaging
- **Fix:** Run `./scripts/bundle-python-pyinstaller.sh` first
- **Verify:** Check `python-dist/backend_server` exists

### DMG doesn't show Applications folder
- **Cause:** Old DMG configuration
- **Fix:** Verify `package.json` has `dmg.contents` array
- **Verify:** Rebuild with `npm run package:mac`

## Testing Checklist

- [ ] Clean build environment (`rm -rf python-dist/ release/ dist/ build/`)
- [ ] Run PyInstaller bundle script
- [ ] Verify `python-dist/backend_server` is not a symlink
- [ ] Build Electron app
- [ ] Verify `latest-mac.yml` exists in `release/`
- [ ] Mount DMG and check layout (app + Applications)
- [ ] Install app to `/Applications`
- [ ] Launch app and verify backend starts
- [ ] Check Settings for auto-update (should not error)
- [ ] Test basic functionality (chat, search, etc.)

## Performance Notes

### Build Times
- PyInstaller bundling: **5-10 minutes** (one-time per release)
- Electron packaging: **2-5 minutes**
- Total clean build: **~15 minutes**

### Bundle Sizes
- PyInstaller bundle: **~800MB** (includes PyTorch models)
- Final DMG: **~400MB** (arm64) / **~400MB** (x64)
- Installed app: **~800MB** per architecture

### Optimization Ideas (Future)
- Strip debug symbols from binaries
- Exclude unused PyTorch backends
- Use model quantization for smaller embeddings
- Lazy-load large dependencies

## Support

If issues persist:
1. Check electron app logs (Help → Toggle Developer Tools → Console)
2. Check backend logs in console output
3. Verify directory structure matches expectations
4. Create GitHub issue with logs and system info
