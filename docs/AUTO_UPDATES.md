# Auto-Update System

This document describes the automatic update system implemented in Zotero RAG Assistant.

## Overview

The application uses Electron's `electron-updater` module to provide seamless automatic updates from GitHub Releases. Users can check for updates, download them, and install them directly from the Settings page.

## Architecture

### Components

1. **Main Process (electron/main.ts)**
   - Configures `electron-updater` with GitHub as the update provider
   - Handles update lifecycle events (checking, available, downloading, downloaded)
   - Provides IPC handlers for renderer to trigger update actions
   - Automatically checks for updates on startup and periodically (every 4 hours)

2. **Preload Script (electron/preload.ts)**
   - Exposes secure update APIs to the renderer process via `contextBridge`
   - Provides event listeners for update status changes
   - Provides action methods (check, download, install)

3. **React Hook (frontend/src/hooks/useAppUpdater.ts)**
   - Encapsulates update state management
   - Provides a clean React interface for update functionality
   - Tracks update status, progress, and errors

4. **Settings UI (frontend/src/pages/Settings.tsx)**
   - Displays current version and update status
   - Shows download progress with visual progress bar
   - Provides buttons for checking, downloading, and installing updates
   - Only visible when running in Electron environment

## Update Flow

### 1. Checking for Updates

**Automatic:**
- On app startup (after 10 second delay)
- Every 4 hours while app is running

**Manual:**
- User clicks "Check for Updates" button in Settings

### 2. Update Available

When an update is found:
- User is notified in Settings page
- Update version and release notes are displayed
- "Download Update" button becomes available

### 3. Downloading Update

When user clicks "Download Update":
- Download begins in background
- Progress bar shows download percentage and size
- User can continue using the app during download

### 4. Update Downloaded

When download completes:
- User is notified that update is ready
- "Install and Restart" button becomes available
- Update is automatically installed on next app quit

### 5. Installing Update

When user clicks "Install and Restart":
- App quits immediately
- Update is installed
- App restarts automatically with new version

## Configuration

### electron-builder (package.json)

```json
{
  "build": {
    "publish": [
      {
        "provider": "github",
        "owner": "aahepburn",
        "repo": "Zotero-RAG-Assistant",
        "releaseType": "release"
      }
    ]
  }
}
```

### Main Process Settings

```typescript
autoUpdater.autoDownload = false;      // Don't auto-download, let user decide
autoUpdater.autoInstallOnAppQuit = true; // Install on quit after download
```

## Publishing Updates

### Prerequisites

1. **GitHub Personal Access Token**
   - Required for publishing to GitHub Releases
   - Set as environment variable: `GH_TOKEN=your_token_here`
   - Token needs `repo` scope for private repos, or `public_repo` for public repos

2. **Version Bump**
   - Update version in `package.json`
   - Follow semantic versioning (MAJOR.MINOR.PATCH)

### Publishing Process

#### Option 1: Using npm scripts

```bash
# Publish for current platform
npm run publish

# Publish for specific platforms
npm run publish:mac
npm run publish:win
npm run publish:linux
```

#### Option 2: Manual electron-builder

```bash
# Build and publish for all platforms
npm run build
GH_TOKEN=your_token electron-builder -mwl --publish always

# Or for specific platform
GH_TOKEN=your_token electron-builder --mac --publish always
```

### What Gets Published

- Application installers (.dmg, .exe, .AppImage, etc.)
- Update metadata files (latest.yml, latest-mac.yml, etc.)
- Checksums for verification
- Release notes (from GitHub release or CHANGELOG.md)

## Release Best Practices

1. **Version Control**
   - Tag releases in git: `git tag v1.0.0 && git push origin v1.0.0`
   - Keep version in sync between package.json and git tags

2. **Release Notes**
   - Write clear, user-friendly release notes
   - List new features, improvements, and bug fixes
   - Mention any breaking changes or migration steps

3. **Testing**
   - Test the update process before publishing
   - Verify installers work on target platforms
   - Test update from previous version to new version

4. **Incremental Updates**
   - electron-updater supports differential updates on Windows
   - Users only download changed files, not entire app
   - Reduces download size and time

## Security

1. **Code Signing**
   - All releases should be code signed
   - Prevents "untrusted developer" warnings
   - Required for auto-updates on macOS

2. **HTTPS**
   - GitHub Releases uses HTTPS by default
   - Updates are verified with checksums

3. **Sandboxed API**
   - Update APIs are exposed via secure `contextBridge`
   - No direct access to Node.js or Electron APIs from renderer

## User Experience

### Update Notifications

- **Non-intrusive**: Updates don't interrupt the user
- **User Control**: User decides when to download and install
- **Progress Feedback**: Clear progress indicators during download
- **Graceful Handling**: Errors are displayed with clear messages

### Update States

1. **Idle** - No update check performed yet
2. **Checking** - Checking for updates with spinner
3. **Not Available** - Running latest version (green checkmark)
4. **Available** - Update available (orange, with version info)
5. **Downloading** - Download in progress (blue, with progress bar)
6. **Downloaded** - Ready to install (green, with install button)
7. **Error** - Something went wrong (red, with error message)

## Troubleshooting

### Updates Not Working

1. **Check GitHub Token**
   - Ensure `GH_TOKEN` is set when publishing
   - Verify token has correct permissions

2. **Check Release Visibility**
   - Releases must be marked as "releases" (not drafts or pre-releases)
   - For private repos, ensure token has access

3. **Check Build Artifacts**
   - Verify latest.yml (or platform-specific) is published
   - Check that artifact names match configuration

4. **Development Mode**
   - Updates are disabled in development mode
   - Test with packaged application

### Common Issues

**"No updates available" when update exists**
- Check that version in release is higher than current
- Verify update metadata files are published
- Check console for error messages

**Download fails**
- Check network connection
- Verify GitHub Release assets are accessible
- Check file permissions and disk space

**Install fails**
- On macOS: Check code signing and notarization
- On Windows: Check antivirus/firewall settings
- Verify update files are not corrupted (check checksums)

## API Reference

### Electron API (window.electron)

```typescript
interface ElectronAPI {
  // Check for updates manually
  checkForUpdates(): Promise<{ 
    success: boolean; 
    updateInfo?: any; 
    error?: string 
  }>;
  
  // Download available update
  downloadUpdate(): Promise<{ 
    success: boolean; 
    error?: string 
  }>;
  
  // Install downloaded update and restart
  installUpdate(): Promise<{ 
    success: boolean; 
    error?: string 
  }>;
  
  // Get current update status
  getUpdateStatus(): Promise<{
    updateAvailable: boolean;
    updateDownloaded: boolean;
    updateInfo: UpdateInfo | null;
    currentVersion: string;
  }>;
  
  // Event listeners
  onUpdateChecking(callback: () => void): void;
  onUpdateAvailable(callback: (info: UpdateInfo) => void): void;
  onUpdateNotAvailable(callback: (info: { version: string }) => void): void;
  onUpdateDownloadProgress(callback: (progress: DownloadProgress) => void): void;
  onUpdateDownloaded(callback: (info: UpdateInfo) => void): void;
  onUpdateError(callback: (error: { message: string }) => void): void;
}
```

### React Hook (useAppUpdater)

```typescript
const {
  status,              // Current update status
  updateInfo,          // Info about available/downloaded update
  downloadProgress,    // Download progress (percent, transferred, total)
  error,              // Error message if any
  currentVersion,      // Current app version
  checkForUpdates,     // Function to check for updates
  downloadUpdate,      // Function to download update
  installUpdate,       // Function to install and restart
} = useAppUpdater();
```

## Related Documentation

- [Electron Updater Documentation](https://www.electron.build/auto-update)
- [electron-builder Publishing](https://www.electron.build/configuration/publish)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
