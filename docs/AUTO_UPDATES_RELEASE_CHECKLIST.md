# First Release with Auto-Updates Checklist

Use this checklist when publishing the first version with auto-update support.

## Pre-Release Preparation

### Version Management
- [ ] Update version in `package.json` (e.g., from 0.1.4 to 0.1.5)
- [ ] Update `CHANGELOG.md` with new features and changes
- [ ] Commit version changes: `git commit -am "Bump version to 0.1.5"`
- [ ] Create git tag: `git tag v0.1.5`
- [ ] Push commits and tag: `git push origin master && git push origin v0.1.5`

### GitHub Token Setup
- [ ] Create GitHub Personal Access Token if you don't have one:
  - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  - Generate new token with `repo` scope (or `public_repo` for public repos)
- [ ] Set token as environment variable:
  ```bash
  export GH_TOKEN=your_token_here
  ```
- [ ] (Optional) Add to shell config for persistence:
  ```bash
  echo 'export GH_TOKEN=your_token_here' >> ~/.zshrc
  source ~/.zshrc
  ```

### Code Signing (Recommended)
- [ ] **macOS**: Configure Apple Developer certificate
  - Set `CSC_LINK` or `CSC_NAME` environment variable
  - Add notarization credentials if needed
- [ ] **Windows**: Configure code signing certificate
  - Set certificate path and password
- [ ] **Linux**: Not required (but recommended for some distros)

## Build and Publish

### Test Build First (Optional but Recommended)
- [ ] Build locally without publishing:
  ```bash
  npm run package:mac
  ```
- [ ] Install and test the built application
- [ ] Verify app version shows correctly in Settings
- [ ] Test all major features work

### Publish Release
- [ ] Ensure GH_TOKEN is set: `echo $GH_TOKEN` (should output your token)
- [ ] Run publish command for your platform:
  ```bash
  npm run publish:mac     # For macOS
  # OR
  npm run publish:win     # For Windows
  # OR
  npm run publish:linux   # For Linux
  ```
- [ ] Wait for build to complete (may take several minutes)
- [ ] Check for any errors in console output

### Verify GitHub Release
- [ ] Go to GitHub repository → Releases
- [ ] Verify new release was created with correct version
- [ ] Check that installers were uploaded:
  - macOS: `.dmg` and `.zip` files
  - Windows: `.exe` installer
  - Linux: `.AppImage` file
- [ ] Verify update metadata files are present:
  - `latest-mac.yml` (macOS)
  - `latest.yml` (Windows)
  - `latest-linux.yml` (Linux)
- [ ] Check release notes are populated (from CHANGELOG or git commits)

## Post-Release Testing

### Fresh Install Test
- [ ] Download installer from GitHub Release
- [ ] Install on clean test machine or VM
- [ ] Launch application
- [ ] Verify version shows correctly (Settings → Application Updates)
- [ ] Test basic functionality

### Update Test (Important!)
- [ ] Install previous version (if available)
- [ ] Launch and go to Settings
- [ ] Click "Check for Updates"
- [ ] Verify new version is detected
- [ ] Click "Download Update"
- [ ] Wait for download to complete
- [ ] Click "Install and Restart"
- [ ] Verify app restarts with new version
- [ ] Test that data/settings are preserved

### Error Scenarios
- [ ] Test update check with no internet connection
- [ ] Verify error message is user-friendly
- [ ] Test "Check for Updates" when already on latest version
- [ ] Verify "up to date" message displays correctly

## Platform-Specific Checks

### macOS
- [ ] Test on both Intel and Apple Silicon Macs (if possible)
- [ ] Verify no "unidentified developer" warning (if code signed)
- [ ] Check app opens without right-click → Open (if notarized)
- [ ] Test update process on both architectures

### Windows
- [ ] Test installer on Windows 10 and Windows 11
- [ ] Verify no SmartScreen warning (if code signed)
- [ ] Check Start Menu shortcut is created
- [ ] Test update process

### Linux
- [ ] Test AppImage on Ubuntu/Debian-based distro
- [ ] Test on Fedora/RHEL-based distro (if possible)
- [ ] Verify AppImage is executable without chmod
- [ ] Test update process

## Communication

### User Announcement
- [ ] Draft release announcement
- [ ] Highlight new features (especially auto-updates!)
- [ ] Include installation/update instructions
- [ ] Post to relevant channels (Discord, forum, etc.)

### Documentation Updates
- [ ] Ensure README.md is up to date
- [ ] Verify installation instructions are clear
- [ ] Update screenshots if UI changed
- [ ] Check all documentation links work

## Troubleshooting Common Issues

### "Failed to publish" error
- ✅ Check GH_TOKEN is set correctly
- ✅ Verify token has `repo` or `public_repo` scope
- ✅ Ensure you have write access to repository
- ✅ Check repository owner/name in package.json matches GitHub

### "No updates available" when testing
- ✅ Ensure new version number is higher than old
- ✅ Check that GitHub release is not a draft
- ✅ Verify latest.yml files were uploaded
- ✅ Check console for error messages

### Download fails during update
- ✅ Verify GitHub release assets are public/accessible
- ✅ Check file sizes are reasonable (not corrupted)
- ✅ Test download manually from browser
- ✅ Check antivirus/firewall settings

### App won't restart after update
- ✅ Check file permissions on installed files
- ✅ Verify enough disk space
- ✅ Look for crash logs
- ✅ Test with fresh install

## Post-Release Monitoring

### First 24 Hours
- [ ] Monitor GitHub Issues for bug reports
- [ ] Check GitHub Releases download stats
- [ ] Test update from previous version yourself
- [ ] Watch for crash reports or error patterns

### First Week
- [ ] Collect user feedback
- [ ] Document any issues found
- [ ] Plan hotfix release if critical bugs found
- [ ] Update documentation based on user questions

## Next Release Preparation

### Lessons Learned
- [ ] Document what went well
- [ ] Note any problems encountered
- [ ] Update this checklist based on experience
- [ ] Improve automation if needed

### Process Improvements
- [ ] Consider setting up CI/CD for automatic builds
- [ ] Look into automatic release notes generation
- [ ] Explore beta/prerelease channels
- [ ] Consider automated testing

---

## Quick Commands Reference

```bash
# Set GitHub token
export GH_TOKEN=your_token_here

# Update version and create tag
npm version patch  # or minor, or major
git push origin master --follow-tags

# Publish release
npm run publish:mac     # macOS
npm run publish:win     # Windows
npm run publish:linux   # Linux

# Test local build (no publish)
npm run package:mac
```

## Support Resources

- [Auto-Updates Documentation](./AUTO_UPDATES.md)
- [Auto-Updates Quick Start](./AUTO_UPDATES_QUICKSTART.md)
- [electron-builder Publishing Docs](https://www.electron.build/configuration/publish)
- [GitHub Releases Guide](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

**Remember**: The first release with auto-updates is critical. Take time to test thoroughly before announcing to users!
