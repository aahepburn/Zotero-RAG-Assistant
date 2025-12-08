# Build & Release Checklist

Quick reference for building and releasing new versions.

## Pre-Build

### 1. Code Quality
```bash
# Verify TypeScript compiles
npm run build:electron

# Test in development
npm run dev
```
- [ ] No TypeScript errors
- [ ] Backend starts (http://localhost:8000/health)
- [ ] Frontend loads (http://localhost:5173)
- [ ] Basic functionality works

### 2. Bundle Python
```bash
# Clean previous bundle
rm -rf python-dist/

# Create PyInstaller bundle
./scripts/bundle-python-pyinstaller.sh
```
- [ ] Script completes without errors
- [ ] `python-dist/backend_server` exists and is not a symlink
- [ ] Bundle size ~800MB (includes PyTorch models)

### 3. Version Bump
- [ ] Update version in `package.json`
- [ ] Update `CHANGELOG.md`
- [ ] Commit: `git commit -am "Bump version to x.x.x"`
- [ ] Tag: `git tag vx.x.x`
- [ ] Push: `git push origin master && git push origin vx.x.x`

## Build

### macOS
```bash
npm run build
npm run package:mac
```
**Verify output:**
- [ ] `release/Zotero-RAG-Assistant-*-mac-arm64.dmg`
- [ ] `release/Zotero-RAG-Assistant-*-mac-x64.dmg`
- [ ] `release/*.zip` files (both architectures)
- [ ] `release/*.blockmap` files
- [ ] `release/latest-mac.yml` ← Critical for auto-updates!

### Windows
```bash
npm run build
npm run package:win
```
**Verify output:**
- [ ] `release/Zotero-RAG-Assistant-*-win-x64.exe`
- [ ] `release/*.zip` files
- [ ] `release/latest.yml` ← Critical for auto-updates!

### Linux
```bash
npm run build
npm run package:linux
```
**Verify output:**
- [ ] `release/zotero-rag-assistant_*_amd64.deb`
- [ ] `release/zotero-rag-assistant_*_arm64.deb`
- [ ] `release/Zotero-RAG-Assistant-*-linux-x64.AppImage`
- [ ] `release/latest-linux.yml` ← Critical for auto-updates!

## Testing

### Quick Test (All Platforms)
1. Install the built package
2. Launch the app
3. Verify version in Settings
4. Test basic features:
   - [ ] Zotero library loads
   - [ ] Can send a chat message
   - [ ] Backend responds (check console for errors)
   - [ ] Settings panel opens

### Platform-Specific Tests

**macOS:**
- [ ] DMG opens and shows Applications folder shortcut
- [ ] Can drag to Applications
- [ ] App launches from Applications folder
- [ ] No "unidentified developer" warning (if code signed)

**Windows:**
- [ ] Installer runs without SmartScreen warning (if code signed)
- [ ] Creates Start Menu shortcut
- [ ] Can launch from Start Menu

**Linux (.deb):**
```bash
sudo apt install ./zotero-rag-assistant_*_amd64.deb
zotero-rag-assistant
```
- [ ] Dependencies install automatically
- [ ] No sandbox warnings (no `--no-sandbox` needed)
- [ ] Appears in application menu
- [ ] Can launch from terminal

**Linux (AppImage):**
```bash
chmod +x Zotero-RAG-Assistant-*-linux-x64.AppImage
./Zotero-RAG-Assistant-*-linux-x64.AppImage
```
- [ ] Runs without `--no-sandbox` on modern systems
- [ ] If sandbox issues occur, verify in docs/LINUX_PACKAGING.md

### Backend Verification
Check that Python bundle works:
- [ ] Backend logs show successful startup
- [ ] No "Python interpreter missing" errors
- [ ] Can process chat requests
- [ ] Vector database operations work

## Publishing

### Publish to GitHub Releases
```bash
# Set GitHub token
export GH_TOKEN=your_token_here

# Publish for your platform
npm run publish:mac    # or :win, :linux
```

### Verify GitHub Release
- [ ] Release created with correct version tag
- [ ] All installers uploaded
- [ ] Update metadata files present:
  - [ ] `latest-mac.yml` (macOS)
  - [ ] `latest.yml` (Windows)
  - [ ] `latest-linux.yml` (Linux)
- [ ] Release notes populated

### Post-Release
- [ ] Download installer from GitHub to verify
- [ ] Test update from previous version (if available)
- [ ] Announce release (if applicable)

## Troubleshooting

### Python Bundle Issues
```bash
# Verify bundle is correct
file python-dist/backend_server
# Should show: executable (NOT symlink)

# For macOS, check in built app:
ls -la "release/mac-arm64/Zotero RAG Assistant.app/Contents/Resources/python/"
```

### Auto-Update Files Missing
- Check `package.json` has correct `publish` configuration
- Verify `writeUpdateInfo: true` for DMG (macOS)
- Verify `differentialPackage: true` for NSIS (Windows)
- Check electron-builder console output for errors

### Build Failures
- Clean and rebuild: `rm -rf release/ dist/ build/`
- Check Node.js version (16+ required)
- Check npm install completed without errors
- Check Python bundle was created before packaging

## Quick Reference

**Clean everything:**
```bash
rm -rf python-dist/ release/ dist/ build/ node_modules/
npm install
```

**Complete build from scratch:**
```bash
./scripts/bundle-python-pyinstaller.sh
npm run build
npm run package:mac  # or :win, :linux
```

**Publish release:**
```bash
export GH_TOKEN=your_token
npm run publish:mac  # or :win, :linux
```

See [PYINSTALLER_BUNDLE_GUIDE.md](PYINSTALLER_BUNDLE_GUIDE.md) for detailed build information.
