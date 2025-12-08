# Changelog

All notable changes to the Zotero LLM Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.6] - 2025-12-08

### Fixed

- **macOS DMG Installation** - Added Applications folder shortcut for easy drag-and-drop installation
- **Auto-Updates** - Fixed missing `latest-mac.yml`, `latest.yml`, and `latest-linux.yml` files
  - macOS: Enabled `writeUpdateInfo: true` for DMG
  - Windows: Added `differentialPackage: true` for delta updates
  - Linux: Proper auto-update metadata generation
- **Python Bundling** - Migrated from venv symlinks to PyInstaller for truly portable bundles
  - No more "Python interpreter missing" errors
  - Self-contained executable includes all dependencies
  - Works without system Python installation

### Added

- **Native Linux .deb packages** for Debian/Ubuntu with proper sandbox configuration
  - Automatic chrome-sandbox setup via post-install script
  - No `--no-sandbox` flag needed
  - System integration via package manager
  - Support for both amd64 and arm64 architectures
- **PyInstaller-based Python bundling** for all platforms
  - Complete standalone backend executable
  - No symlinks to system Python
  - Truly relocatable application bundle
- **Comprehensive Linux packaging documentation** (docs/LINUX_PACKAGING.md)
- **PyInstaller build guide** (docs/PYINSTALLER_BUNDLE_GUIDE.md)

### Changed

- **Documentation cleanup** - Consolidated and removed redundant docs
  - Installation instructions now in README for all platforms
  - Merged auto-update documentation into single comprehensive guide
  - Removed 12 redundant/outdated documentation files
  - Clear separation of user vs developer documentation

## [0.1.3] - 2025-12-02

### Fixed

- **Linux AppImage Python detection** - Fixed "Python Not Found" errors on Linux systems
  - Now correctly detects `python3` command (standard on modern Linux distros)
  - Tries bundled Python first, falls back to system Python gracefully
  - Added multiple fallback paths: `python3`, `python`, `/usr/bin/python3`, etc.
  - Shows platform-specific installation instructions if Python is missing
- **Development mode backend conflict** - Fixed port 8000 conflict in dev mode
  - Electron no longer tries to start its own backend in development
  - Uses the backend started by `npm run dev:backend` instead
- **Working directory resolution** - Fixed backend module import errors in dev mode
  - Correctly resolves project root directory on all platforms
  - Backend can now find Python modules in development and production

### Added

- Comprehensive Python detection system with smart fallback logic
- Platform-specific error messages for missing Python installations
- Detailed logging for Python detection and backend startup process
- New documentation:
  - `docs/PYTHON_DETECTION.md` - Technical architecture
  - `docs/LINUX_PYTHON_GUIDE.md` - User guide for Linux
  - `docs/BUILD_CHECKLIST.md` - Build and testing procedures
  - `docs/PYTHON_DETECTION_FLOW.txt` - Visual flow diagram

## [0.1.0] - 2024-12-02

### Added - Desktop App Release 🎉

- **Native desktop application** using Electron for macOS, Windows, and Linux
- **Automatic updates** via GitHub Releases - future versions install automatically
- **Bundled backend** - no need to install Python or dependencies manually
- **Cross-platform installers**:
  - macOS: DMG installer (Universal: Intel + Apple Silicon)
  - Windows: NSIS installer with auto-updates
  - Linux: AppImage (portable) and DEB packages
- **One-command development** - `npm run dev` runs everything
- **Professional packaging** with code signing support
- **Comprehensive documentation** for development and deployment

### Changed

- Backend now supports HEAD requests for health checks
- Development workflow simplified with concurrent script execution
- Repository structure reorganized for desktop app

### Fixed

- Backend process management and cleanup on app quit
- IPC communication security with context isolation
- TypeScript compilation errors in Electron code

## Previous Versions (Web App)

### [0.0.x] - Pre-Desktop Era

Previous versions were web-based only, requiring manual setup of Python backend and Node.js frontend.

See git history for details: https://github.com/aahepburn/zotero-llm-plugin/commits/master

---

## Release Notes Format

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements
