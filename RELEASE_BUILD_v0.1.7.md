# Release v0.1.7 - Build Instructions

## ✅ Code Changes Committed and Pushed

**Commit:** `f43a354`  
**Tag:** `v0.1.7`  
**Status:** Pushed to GitHub

## Build Process

### Step 1: Python Bundle (In Progress)
```bash
./scripts/bundle-python-pyinstaller.sh
```
This creates `python-dist/` with a standalone Python executable. Takes 5-10 minutes.

### Step 2: Build Electron App
After Python bundle completes:
```bash
npm run build
npm run package:mac
```

### Step 3: Verify Build Outputs
Check `release/` directory contains:
- [ ] `Zotero-RAG-Assistant-0.1.7-mac-arm64.dmg`
- [ ] `Zotero-RAG-Assistant-0.1.7-mac-x64.dmg`
- [ ] `Zotero-RAG-Assistant-0.1.7-mac-arm64.zip`
- [ ] `Zotero-RAG-Assistant-0.1.7-mac-x64.zip`
- [ ] `*.blockmap` files
- [ ] **`latest-mac.yml`** ← Critical for auto-updates!

### Step 4: Test Before Publishing
1. Mount the DMG
2. Verify Applications folder shortcut appears
3. Install to /Applications
4. Launch and verify:
   - Backend starts (no Python errors)
   - Can send a chat message
   - Settings shows v0.1.7

### Step 5: Publish to GitHub
```bash
# Set your GitHub token
export GH_TOKEN=your_github_personal_access_token

# Publish release
npm run publish:mac
```

This will:
- Create GitHub Release for v0.1.7
- Upload all DMG, ZIP, and blockmap files
- Upload `latest-mac.yml` for auto-updates
- Use CHANGELOG.md content for release notes

### Step 6: Verify GitHub Release
Go to: https://github.com/aahepburn/Zotero-RAG-Assistant/releases/tag/v0.1.7

Check:
- [ ] Both .dmg files uploaded
- [ ] Both .zip files uploaded
- [ ] Both .blockmap files uploaded
- [ ] **`latest-mac.yml` uploaded** ← Most critical!
- [ ] Release notes populated from CHANGELOG

### Step 7: Test Auto-Update (Optional)
1. Install v0.1.6 from old release
2. Launch app
3. Go to Settings
4. Click "Check for Updates"
5. Should detect v0.1.7 and offer to download

## What's Fixed in v0.1.7

### For Users:
1. **macOS DMG now shows Applications folder** - Easy drag-and-drop installation
2. **Auto-updates work** - No more 404 errors when checking for updates
3. **No "Python missing" errors** - True standalone app with PyInstaller

### For Linux Users:
4. **Native .deb packages** - Proper system integration
5. **No `--no-sandbox` needed** - Chromium sandbox configured automatically

### Technical:
- PyInstaller replaces venv-based bundling (no more symlinks)
- Auto-update metadata generation for all platforms
- Documentation consolidated and cleaned up

## If You Need to Build for Other Platforms

### Windows:
```bash
npm run package:win
npm run publish:win
```

### Linux:
```bash
npm run package:linux
npm run publish:linux
```

## Rollback Plan

If v0.1.7 has issues, users can:
1. Download v0.1.6 from releases page
2. Install over v0.1.7
3. Auto-update system will respect version downgrade

To fix issues:
1. Make code changes
2. Bump to v0.1.8
3. Follow this process again

## Notes

- The PyInstaller bundle is ~800MB (includes PyTorch models)
- First build takes longer, subsequent builds are faster
- electron-builder caches dependencies
- GitHub token needs `repo` scope (or `public_repo` for public repos)
