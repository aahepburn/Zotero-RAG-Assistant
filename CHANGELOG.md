# Changelog

All notable changes to the Zotero LLM Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.5] - 2026-01-19

### Fixed
- **Critical: Fixed macOS Intel (x64) compatibility** - Intel Mac users were getting "error -86" spawn failures due to arm64 backend being shipped in x64 builds
- Implemented architecture-specific builds for macOS (separate x64 and arm64 binaries)
- Added automatic YML manifest merging for electron-updater multi-architecture support
- Increased backend initialization timeout for all platforms (70s max vs 25s) to prevent false-positive startup errors
- Added architecture verification in build process to catch mismatches early

### Changed
- Split macOS builds into separate Intel (macos-13) and Apple Silicon (macos-14) runners
- Unified backend startup timeouts across all platforms (3000ms health checks, 1000ms → 3000ms retry intervals)
- Added `minimumSystemVersion: 11.0` for macOS compatibility documentation

### Added
- New `scripts/merge-mac-yml.js` to merge update manifests from multiple architectures
- Architecture verification step in GitHub Actions workflow
- Added `js-yaml` dependency for manifest processing

## [0.2.4] - 2026-01-06

### Changed
- Reverted Debian packaging metadata to v0.2.0 configuration to eliminate potential dpkg parsing issues
- Removed custom FPM fields from deb configuration
- Simplified maintainer and vendor metadata

### Fixed
- Updated Linux installation guidance in README to remove outdated version references and AppImage instructions

## [0.2.3] - 2026-01-06

### Fixed
- Fixed "address already in use" crash on startup when port 8000 is occupied
- Added automatic cleanup of orphaned backend processes before app startup
- Implemented dynamic port selection (8000-8010) if default port is unavailable
- Enhanced graceful shutdown with proper port release verification
- Added backend `/shutdown` endpoint for clean server termination
- Improved signal handling (SIGTERM, SIGINT) to ensure cleanup on force quit
- Backend now automatically retries with available ports if requested port is in use

## [0.2.2] - 2026-01-05

### Added
- Application icons for macOS, Windows, and Linux builds

### Fixed
- Fixed duplicate indexing operations during vector database updates
- Resolved indexing progress double-counting bug

## [0.2.1] - 2026-01-05

### Fixed
- Fixed incremental sync progress bar getting stuck at low counts
- Removed skip warnings from navbar during sync to prevent UI disruption
- Warnings still logged to backend console for diagnostics

## [0.2.0] - 2026-01-05

### Added

- **Profile-Specific Vector Databases** - Major improvement to profile isolation
  - Each profile now has its own isolated ChromaDB instance
  - Automatic profile-specific paths: `~/.zotero-llm/profiles/{profile-id}/chroma`
  - Switch between profiles without reindexing - each maintains separate embeddings
  - Support for different embedding models per profile without conflicts
  - No more shared `user-1` paths

- **Full Windows Support** - Native Windows builds and installers
  - PyInstaller build scripts for Windows (PowerShell and batch file)
  - NSIS installer with Desktop shortcut and Start Menu entry
  - Portable ZIP distribution option
  - Comprehensive Windows build documentation
  - Automated Windows builds via GitHub Actions

- **Improved GitHub Actions CI/CD**
  - Automated builds for macOS, Windows, and Linux on tag push
  - Parallel builds across all platforms
  - Automatic GitHub release creation with all artifacts
  - Build time ~15-25 minutes for all platforms

### Changed

- Vector database path now defaults to profile-specific location instead of hardcoded `user-1`
- `load_settings()` function now automatically uses profile-specific chroma path
- Settings UI displays correct profile-specific vector database path
- Removed global `CHROMA_PATH` constant dependency (now profile-managed)

### Fixed

- Vector database paths not respecting profile system
- Profiles sharing the same vector database causing data conflicts
- Inability to use different embedding models in different profiles
- Settings showing incorrect default chroma path

### Documentation

- Added comprehensive Windows build guide (`docs/WINDOWS_BUILD_GUIDE.md`)
- Added Windows quick reference (`docs/WINDOWS_BUILD_QUICKREF.md`)
- Added Windows support tracking document (`docs/WINDOWS_SUPPORT_TODO.md`)
- Added complete release plan for v0.2.0 (`docs/RELEASE_PLAN_v0.2.0.md`)
- Updated profile system documentation with vector database isolation details

### Migration Notes

- **Existing Users**: Old vector database at `~/.zotero-llm/chroma/user-1` will not be automatically migrated
- **To Keep Old Data**: Manually copy `~/.zotero-llm/chroma/user-1` to `~/.zotero-llm/profiles/default/chroma`
- **Fresh Start**: Just create a new profile and re-index your library

## [0.1.10] - 2025-12-31

### Fixed

- **Memory Leak** - Fixed orphaned backend processes on app quit
  - Process tree cleanup kills Python backend and ChromaDB child processes
  - Unix: Uses negative PID to kill entire process group
  - Windows: Uses `taskkill /T` for tree termination
  - Prevents memory accumulation from repeated app launches

### Changed

- **Linux Packaging** - Reverted to venv approach (from PyInstaller bundle)
  - PyInstaller bundle exceeded GitHub's 2GB file size limit (2.5GB DEB)
  - Linux now uses system Python + venv with auto-setup and repair logic
  - Validates uvicorn installation and auto-repairs if missing
  - Mac/Windows still use PyInstaller bundles (self-contained)
  - Smaller Linux DEB (~250MB vs 2.5GB)

## [0.1.9] - 2025-12-16

### Fixed

- **Linux Backend Startup** - Bundled PyInstaller executable for Linux (like Mac/Windows)
  - Eliminates dependency on system Python and manual venv setup
  - Fixes "No module named uvicorn" errors on Linux installations
  - More reliable: self-contained executable with all dependencies
  - Larger DEB file size (~150MB more) but eliminates installation issues

### Changed

- **Linux Packaging** - Now uses PyInstaller bundle instead of system Python + venv
  - Consistent backend deployment across all platforms
  - Simplified Linux installation (no Python prerequisites)
  - Auto-repair logic removed (no longer needed with bundled approach)

## [0.1.8] - 2025-12-16

### Added

- **2025 Academic Prompting System** - Major upgrade to AI response quality
  - Citation-aware RAG prompting with mandatory inline citations [N]
  - Chain-of-thought reasoning for transparent logic
  - Improved generation parameters (temp=0.35, top_p=0.9, top_k=50)
  - Explicit handling of uncertainty and research gaps
  - Structured responses: Direct answer → Evidence → Synthesis → Limitations
  - New `AcademicPrompts` module with comprehensive prompt templates
  - New `AcademicGenerationParams` with research-backed parameter sets

### Changed

- **System Prompt** - Enhanced from 54 to ~400 words with comprehensive academic guidelines
  - Detailed citation requirements with examples
  - Explicit responsibilities and quality gates
  - Chain-of-thought reasoning instructions
- **Generation Parameters** - Optimized for academic content synthesis:
  - Temperature: 0.3 → 0.35 (reduces repetition, maintains factuality)
  - Max tokens: 512 → 600 (allows detailed academic responses)
  - Top-k: 40 → 50 (better vocabulary diversity)
  - Repeat penalty: 1.1 → 1.15 (prevents citation repetition)
- **All LLM Providers** - Updated defaults for better academic output:
  - Ollama: Enhanced top_k and repeat_penalty
  - OpenAI: Added frequency_penalty, optimized top_p
  - Anthropic: Added top_k parameter
  - Perplexity, Groq, OpenRouter: Enhanced sampling parameters

### Improved

- **Citation Accuracy** - Expected ~60% reduction in citation mismatches (based on CiteFix research)
- **Response Quality** - More natural academic writing with proper grounding
- **Transparency** - Clear distinction between findings, synthesis, and gaps
- **Repetition Control** - Eliminated citation and concept repetition in long responses
- **Uncertainty Handling** - Explicit "I don't know" when evidence is insufficient

### Documentation

- Added `docs/ACADEMIC_PROMPTING_2025.md` - Comprehensive implementation guide
- Added `docs/PROMPTING_QUICKSTART.md` - User migration guide

### Technical Notes

- Based on 2025 research: CiteFix (ACL 2025), Perplexity Academic Mode, RAG evaluation frameworks
- All changes are backward compatible - no breaking changes
- No re-indexing required - works with existing vector databases
- Pure Python code changes - no dependency updates needed

## [0.1.7] - 2025-12-08

### Fixed

- **Linux Installation Path** - Removed spaces from productName to fix Electron zygote spawn issues
  - Changed from `/opt/Zotero RAG Assistant/` to `/opt/ZoteroRAG/`
  - Fixes "failed to execvp" and zygote_host_impl_linux.cc errors on launch
  - Fixed postinstall script to correctly set chrome-sandbox permissions
- **Security** - Removed vulnerable icon generation dependencies
  - Removed `electron-icon-maker`, `icon-gen`, `svg2png`, `phantomjs-prebuilt`
  - Using electron-builder's built-in icon generation
  - Zero npm audit vulnerabilities

### Changed

- **Product Name** - Changed to `ZoteroRAG` (no spaces) for Linux compatibility

## [0.1.6] - 2025-12-08

### Fixed

- **PyInstaller Backend Bundle** - Fixed backend startup issues in packaged Electron app
  - Changed to import FastAPI app object directly instead of string reference
  - Added PIL/Pillow to bundled dependencies (required by sentence-transformers)
  - Backend now starts correctly in production builds
- **Debian Package Dependencies** - Removed obsolete packages from `.deb` dependencies
  - Removed `gconf2`, `gconf-service`, `libappindicator1` (no longer available in modern repos)
  - Added `libgtk-3-0`, `libgbm1` (required Electron runtime libraries)
  - Fixes "unmet dependencies" errors during `apt` installation on Ubuntu 22.04+

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

### Added - Desktop App Release 

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
