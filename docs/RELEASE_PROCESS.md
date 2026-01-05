# Release Process Guide

This guide walks you through creating a new release of the Zotero LLM Desktop App with automatic updates.

## Prerequisites

- [ ] Git access to the repository
- [ ] GitHub account with release permissions
- [ ] Access to all three platforms (macOS, Windows, Linux) OR CI/CD pipeline
- [ ] Code signing certificates (optional but recommended)

## Release Checklist

### 1. Prepare the Release

- [ ] Test all features thoroughly on each platform
- [ ] Update `CHANGELOG.md` with new features and fixes
- [ ] Review and close related GitHub issues
- [ ] Update version numbers

### 2. Version Numbers

Update version in `package.json`:

```json
{
  "version": "0.1.0"
}
```

**Version Scheme:** Follow [Semantic Versioning](https://semver.org/)
- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes only

**Pre-release tags:**
- `0.1.0-alpha.1`: Early testing
- `0.1.0-beta.1`: Feature complete, testing
- `0.1.0-rc.1`: Release candidate

### 3. Build Installers

You need to build on each platform or use CI/CD:

#### macOS (on a Mac)

```bash
# 1. Install dependencies
npm install

# 2. Build backend binary (optional, can skip for now)
source .venv/bin/activate
./build-backend.sh

# 3. Build Electron app
npm run build
npm run package:mac

# Output: release/*.dmg, release/*.zip, release/latest-mac.yml
```

#### Windows (on Windows)

```bash
# 1. Install dependencies
npm install

# 2. Build backend binary (optional)
.venv\Scripts\activate
# Run PyInstaller manually (see build-backend.sh for commands)

# 3. Build Electron app
npm run build
npm run package:win

# Output: release/*.exe, release/*.zip, release/latest.yml
```

#### Linux (on Ubuntu)

```bash
# 1. Install dependencies
sudo apt-get install -y build-essential libfuse2
npm install

# 2. Build backend binary (optional)
source .venv/bin/activate
./build-backend.sh

# 3. Build Electron app
npm run build
npm run package:linux

# Output: release/*.AppImage, release/*.deb, release/latest-linux.yml
```

### 4. Verify Builds

Test each installer before uploading:

**macOS:**
```bash
# Mount DMG and drag to Applications
open release/*.dmg

# Or extract ZIP
unzip release/*.zip
# Run the app
```

**Windows:**
```bash
# Run the installer
release\*.exe

# Or extract ZIP and run
```

**Linux:**
```bash
# Make AppImage executable
chmod +x release/*.AppImage

# Run directly
./release/*.AppImage

# Or install DEB
sudo dpkg -i release/*.deb
```

**Test checklist:**
- [ ] App launches without errors
- [ ] Backend starts and responds
- [ ] Can index Zotero library
- [ ] Can chat with library
- [ ] Settings persist
- [ ] Auto-update check works (if previous version installed)

### 5. Commit and Tag

```bash
# Commit version bump
git add package.json CHANGELOG.md
git commit -m "Release v0.1.0"

# Create and push tag
git tag v0.1.0
git push origin master
git push origin v0.1.0
```

### 6. Create GitHub Release

1. **Go to Releases page:**
   https://github.com/aahepburn/zotero-llm-plugin/releases/new

2. **Select your tag:** `v0.1.0`

3. **Release title:** `v0.1.0 - Brief Description`

4. **Description:** Use this template:

```markdown
## What's New

-  Feature: Added XYZ capability
-  Fix: Resolved issue with ABC
-  Performance: Improved indexing speed by 50%

## Installation

Download the installer for your platform:

- **macOS**: [Zotero-LLM-Assistant-0.1.0-mac.dmg](link)
- **Windows**: [Zotero-LLM-Assistant-0.1.0-win.exe](link)
- **Linux**: [Zotero-LLM-Assistant-0.1.0-linux.AppImage](link)

## Upgrade Notes

If you're upgrading from v0.0.x:
- Settings will be preserved
- Re-indexing is recommended for improved search
- See [Migration Guide](docs/migration_guide.md) for details

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete changes.
```

5. **Upload artifacts:**

   Drag and drop ALL files from `release/` directory:

   **Required for each platform:**
   - macOS: `*.dmg`, `*.zip`, `latest-mac.yml`
   - Windows: `*.exe`, `*.zip`, `latest.yml`
   - Linux: `*.AppImage`, `*.deb`, `*.tar.gz`, `latest-linux.yml`

   **Critical:** The `.yml` files are required for auto-updates!

6. **Pre-release checkbox:**
   - Check this for alpha/beta/rc releases
   - Uncheck for stable releases

7. **Publish release**

### 7. Verify Auto-Updates

Install a previous version and verify update works:

1. Install previous version on a test machine
2. Launch the app
3. Wait for "Update Available" notification (or check manually)
4. Download and install update
5. Verify new version launches correctly

### 8. Announce Release

- [ ] Post in GitHub Discussions
- [ ] Update documentation site (if applicable)
- [ ] Social media announcement
- [ ] Email newsletter (if applicable)

## Automation with GitHub Actions

To automate builds, create `.github/workflows/release.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - uses: actions/setup-python@v4
      - run: npm install
      - run: npm run build
      - run: npm run package:mac
      - uses: actions/upload-artifact@v3
        with:
          name: macos-build
          path: release/*
  
  build-windows:
    runs-on: windows-latest
    steps:
      # Similar to macOS
      
  build-linux:
    runs-on: ubuntu-latest
    steps:
      # Similar to macOS
  
  release:
    needs: [build-macos, build-windows, build-linux]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v3
      - uses: softprops/action-gh-release@v1
        with:
          files: |
            macos-build/*
            windows-build/*
            linux-build/*
```

## Troubleshooting

### Build fails with "Module not found"

```bash
# Clean and reinstall
rm -rf node_modules dist release
npm install
npm run build
```

### Auto-update not detected

- Verify `.yml` files are uploaded
- Check version in `package.json` is greater than installed
- Check GitHub release is published (not draft)
- Look for errors in app console

### Binary too large

The app will be large (100-500 MB) due to Python dependencies. To reduce:

1. Use `--exclude-module` in PyInstaller for unused packages
2. Remove development dependencies
3. Strip debug symbols (platform-specific)

### Code signing errors (macOS)

```bash
# Verify certificate
security find-identity -v -p codesigning

# Sign manually if needed
codesign --force --sign "Developer ID" YourApp.app
```

### Windows SmartScreen warning

- Get an EV code signing certificate (expensive)
- Or accumulate reputation (users will see warning initially)
- Include instructions in README for users to click "More info" → "Run anyway"

## Beta Testing

Before public release, do a beta test:

1. Create release with `-beta.X` tag
2. Check "pre-release" checkbox
3. Share with beta testers
4. Gather feedback
5. Fix issues
6. Create stable release

## Version History Maintenance

Keep `CHANGELOG.md` updated:

```markdown
# Changelog

## [0.1.0] - 2024-12-02

### Added
- Desktop app with Electron
- Auto-update functionality
- Native installers for all platforms

### Changed
- Improved indexing performance

### Fixed
- Bug where settings weren't saved

## [0.0.1] - 2024-11-01

### Added
- Initial web app release
```

## Support

After release, monitor:
- [ ] GitHub Issues for bug reports
- [ ] GitHub Discussions for questions
- [ ] Download statistics in Release insights
- [ ] Update adoption (check server logs if applicable)

## Next Release

Plan ahead:
- Create milestone for next version
- Label issues for inclusion
- Set target date
- Communicate roadmap to users
