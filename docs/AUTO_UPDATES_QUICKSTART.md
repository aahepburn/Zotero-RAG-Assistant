# Auto-Update Quick Start Guide

## For End Users

### Checking for Updates

1. Open the application
2. Navigate to **Settings** (gear icon or menu)
3. Scroll to the **Application Updates** section
4. Click **Check for Updates**

### Installing Updates

When an update is available:

1. You'll see the new version number displayed
2. Click **Download Update** to begin downloading
3. Wait for the download to complete (you can use the app while downloading)
4. Once ready, click **Install and Restart**
5. The app will close and reopen with the new version

### Automatic Checks

The app automatically checks for updates:
- 10 seconds after startup
- Every 4 hours while running

You'll be notified in Settings when updates are available, but they won't download or install without your permission.

## For Developers/Maintainers

### Prerequisites

1. **Set GitHub Token**
   ```bash
   export GH_TOKEN=your_github_personal_access_token
   ```
   
   Or add to `.bashrc`/`.zshrc`:
   ```bash
   echo 'export GH_TOKEN=your_token_here' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **Update Version**
   ```bash
   # In package.json, bump the version
   # Example: "version": "0.1.5"
   ```

3. **Create Git Tag**
   ```bash
   git tag v0.1.5
   git push origin v0.1.5
   ```

### Publishing a Release

#### Method 1: Using npm scripts (Recommended)

```bash
# For macOS
npm run publish:mac

# For Windows
npm run publish:win

# For Linux
npm run publish:linux

# For all platforms (if on appropriate build machine)
npm run publish
```

#### Method 2: Manual with electron-builder

```bash
# Build first
npm run build

# Then publish
GH_TOKEN=your_token electron-builder --mac --publish always
```

### What Happens When You Publish

1. Application is built and packaged
2. Installers are created (.dmg, .exe, .AppImage, etc.)
3. A GitHub Release is created (or updated)
4. Update metadata files are uploaded (latest.yml, etc.)
5. Users running older versions will be notified of the update

### Release Checklist

- [ ] Update version in `package.json`
- [ ] Update `CHANGELOG.md` with changes
- [ ] Create git tag matching version
- [ ] Set `GH_TOKEN` environment variable
- [ ] Run publish script for target platform(s)
- [ ] Verify release appears on GitHub
- [ ] Test update process from previous version
- [ ] Announce release to users

### Testing Updates

#### Test Without Publishing

1. Build locally: `npm run package:mac`
2. Install the built app
3. Manually create a GitHub Release with higher version
4. Check if app detects the update

#### Test Full Flow

1. Publish version X to GitHub
2. Install version X on test machine
3. Publish version X+1 to GitHub
4. Open app, go to Settings
5. Click "Check for Updates"
6. Verify update is detected
7. Download and install update
8. Verify app restarts with new version

### Troubleshooting

**"Updates not working in development"**
- Updates are disabled in dev mode by design
- Test with packaged application

**"No updates found" when one exists**
- Check version numbers (new must be > old)
- Verify GitHub release is not a draft
- Check that latest.yml was uploaded
- Look for errors in Developer Console

**"Download fails"**
- Check network connectivity
- Verify GitHub release assets are public/accessible
- Check antivirus/firewall settings

**"Permission denied" during publish**
- Verify GH_TOKEN is set correctly
- Check token has `repo` or `public_repo` scope
- Ensure you have write access to repository

### Platform-Specific Notes

#### macOS
- Code signing required for updates to work properly
- Set signing identity in electron-builder config
- Notarize for macOS 10.15+

#### Windows
- Code signing recommended (otherwise users get warnings)
- NSIS installer supports delta updates (smaller downloads)

#### Linux
- AppImage works without installation
- No code signing required
- Auto-update should work on most distributions

## Configuration Files

### package.json (relevant sections)

```json
{
  "version": "0.1.4",
  "build": {
    "publish": [
      {
        "provider": "github",
        "owner": "aahepburn",
        "repo": "Zotero-RAG-Assistant",
        "releaseType": "release"
      }
    ]
  },
  "scripts": {
    "publish": "npm run build && electron-builder --publish always",
    "publish:mac": "npm run build && electron-builder --mac --publish always"
  }
}
```

### Environment Variables

```bash
# Required for publishing
GH_TOKEN=your_github_token

# Optional: specify GitHub API URL (for GitHub Enterprise)
GH_API_URL=https://api.github.com

# Optional: specify release type (default: release)
EP_RELEASE_TYPE=release  # or draft, prerelease
```

## Support

For issues with auto-updates:
1. Check the [AUTO_UPDATES.md](./AUTO_UPDATES.md) documentation
2. Look at console logs (Help > Toggle Developer Tools)
3. Check GitHub Issues for similar problems
4. Create a new issue with logs and system info
