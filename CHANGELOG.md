# Changelog

All notable changes to the Zotero LLM Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
