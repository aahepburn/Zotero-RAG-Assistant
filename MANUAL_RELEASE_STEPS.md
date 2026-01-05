# Manual Release Steps for v0.2.0

Since CI/CD is having issues, we'll build locally and upload manually.

## Step 1: Build macOS (Current Machine) ✅ IN PROGRESS

```bash
# 1. Build Python bundle (running now)
./scripts/bundle-python-pyinstaller.sh

# 2. Build Electron app
npm run build
npm run package:mac

# Output: release/*.dmg, release/*.zip, release/latest-mac.yml
```

## Step 2: Build Windows (Need Windows Machine)

On a Windows 10/11 machine:

```powershell
# Clone the repo
git clone https://github.com/aahepburn/Zotero-RAG-Assistant.git
cd Zotero-RAG-Assistant
git checkout v0.2.0

# Install dependencies
npm install
cd frontend
npm install
cd ..

# Build Python bundle
.\scripts\bundle-python-pyinstaller-windows.bat

# Build Electron app
npm run build
npm run package:win

# Output: release/*.exe, release/*.zip, release/latest.yml
```

## Step 3: Build Linux (Optional - Use Docker or Skip)

Linux can be skipped for now since CI/CD was closest to working for Linux.

OR use Docker on Mac:

```bash
# Build Linux AppImage using Docker
docker build -f Dockerfile.linux-build -t zotero-rag-linux .
docker run -v $(pwd)/release:/app/release zotero-rag-linux npm run package:linux
```

## Step 4: Create GitHub Release Manually

1. Go to: https://github.com/aahepburn/Zotero-RAG-Assistant/releases

2. Click "Draft a new release"

3. **Tag**: `v0.2.0` (already exists)

4. **Title**: `Zotero RAG Assistant v0.2.0`

5. **Description**:
```markdown
# Zotero RAG Assistant v0.2.0

## 🎉 What's New

### Profile-Specific Vector Databases
Each profile now maintains its own isolated ChromaDB instance. Switch between profiles without reindexing!

- ✅ Automatic profile-specific paths: `~/.zotero-llm/profiles/{profile}/chroma`
- ✅ Different embedding models per profile
- ✅ No more hardcoded `user-1` paths
- ✅ Complete data isolation between profiles

### Full Windows Support
Windows users can now enjoy native installers and portable distributions!

- ✅ NSIS installer with desktop shortcuts
- ✅ PyInstaller-bundled Python backend
- ✅ Comprehensive Windows build documentation
- ✅ Portable ZIP option

## 🐛 Bug Fixes

- Fixed vector database paths not respecting profile system
- Improved profile switching reliability
- Better error handling for missing vector databases

## 📥 Installation

### macOS
Download `ZoteroRAG-0.2.0-mac-arm64.dmg` (Apple Silicon) or `ZoteroRAG-0.2.0-mac-x64.dmg` (Intel)

### Windows
Download `ZoteroRAG-0.2.0-win-x64.exe` and run the installer.

**Note:** Windows SmartScreen may warn about an unrecognized app. Click "More info" → "Run anyway". The app is safe but not code-signed.

### Linux
Linux builds coming soon. For now, run from source:
```bash
git clone https://github.com/aahepburn/Zotero-RAG-Assistant.git
cd Zotero-RAG-Assistant
npm install
cd frontend && npm install && cd ..
source .venv/bin/activate  # Create venv first: python3 -m venv .venv
pip install -r requirements.txt
npm run dev
```

## 📚 Documentation

- [Windows Build Guide](docs/WINDOWS_BUILD_GUIDE.md)
- [Profile System Guide](docs/profile_system_guide.md)
- [Release Process](docs/RELEASE_PROCESS.md)

## 🔄 Upgrading from 0.1.x

The app will auto-update if you have v0.1.8+. Otherwise, download and install the new version.

**Data Migration:** Your existing profiles and vector databases will be preserved. The old `user-1` path will need to be migrated manually if you want to keep that data:

```bash
# Copy old data to default profile
cp -r ~/.zotero-llm/chroma/user-1/* ~/.zotero-llm/profiles/default/chroma/
```

Or just re-index your library (recommended for clean start).

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.
```

6. **Upload Files**:
   - Drag and drop all files from `release/` folder
   - macOS: DMG, ZIP files + latest-mac.yml
   - Windows: EXE, ZIP files + latest.yml
   - Linux: AppImage, DEB files + latest-linux.yml (if available)

7. **Publish**:
   - Uncheck "Set as a pre-release" for stable release
   - Click "Publish release"

## Quick Upload Command

After building, you can use GitHub CLI:

```bash
# Install GitHub CLI if needed: brew install gh

# Create release and upload
gh release create v0.2.0 \
  release/*.dmg \
  release/*.zip \
  release/*.yml \
  --title "Zotero RAG Assistant v0.2.0" \
  --notes-file release_notes.md
```

## Files to Upload

Expected files:

**macOS** (built locally):
- [ ] ZoteroRAG-0.2.0-mac-arm64.dmg
- [ ] ZoteroRAG-0.2.0-mac-x64.dmg
- [ ] ZoteroRAG-0.2.0-mac-arm64.zip
- [ ] ZoteroRAG-0.2.0-mac-x64.zip
- [ ] latest-mac.yml

**Windows** (need Windows machine):
- [ ] ZoteroRAG-0.2.0-win-x64.exe
- [ ] ZoteroRAG-0.2.0-win-ia32.exe
- [ ] ZoteroRAG-0.2.0-win-x64.zip
- [ ] ZoteroRAG-0.2.0-win-ia32.zip
- [ ] latest.yml

**Linux** (optional for this release):
- [ ] ZoteroRAG-0.2.0-linux-x64.AppImage
- [ ] zotero-rag-assistant_0.2.0_amd64.deb
- [ ] latest-linux.yml

## Alternative: macOS Only Release

If you don't have Windows/Linux access, you can:

1. Release macOS builds only
2. Add note: "Windows and Linux builds coming soon"
3. Update release later with additional platforms

## Verification

After uploading:

1. Download and test each installer
2. Verify auto-update metadata files are present
3. Test installation on clean machine
4. Verify profile switching works

---

**Current Status**: Building macOS Python bundle...
