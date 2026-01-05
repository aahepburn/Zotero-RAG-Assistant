# Release 0.2.0 - Summary

**Status**: Ready for testing and release  
**Created**: January 5, 2026

## What Was Done

### 1. Fixed Profile-Specific Vector Databases ✅

**Problem**: All profiles were sharing the same vector database at `~/.zotero-llm/chroma/user-1`

**Solution**: 
- Removed hardcoded `CHROMA_PATH` with `user-1`
- Updated `load_settings()` to use `profile_manager.get_profile_chroma_path(profile_id)`
- Each profile now automatically gets: `~/.zotero-llm/profiles/{profile-id}/chroma`
- No reindexing required when switching profiles

**Files Changed**:
- `backend/main.py` - Fixed path management, removed global CHROMA_PATH dependency

### 2. Updated GitHub Actions CI/CD ✅

**Changes**:
- macOS now uses PyInstaller bundle (not venv)
- Windows now uses PyInstaller bundle (not venv)
- Linux continues using system Python + auto-setup venv
- Added YAML files to artifact uploads (for auto-updates)

**Files Changed**:
- `.github/workflows/build-all.yml` - Updated build steps for all platforms

### 3. Documentation ✅

**Created**:
- `docs/RELEASE_PLAN_v0.2.0.md` - Comprehensive release plan (200+ lines)
- `RELEASE_v0.2.0_QUICK_START.md` - Quick start guide for releasing

**Updated**:
- `CHANGELOG.md` - Added v0.2.0 section with all changes
- `docs/README.md` - Added link to release plan

## What's in 0.2.0

### Features

1. **Profile-Specific Vector Databases**
   - Each profile maintains its own ChromaDB instance
   - Automatic isolation between profiles
   - Support for different embedding models per profile
   - Path format: `~/.zotero-llm/profiles/{profile-id}/chroma`

2. **Full Windows Support**
   - PyInstaller build scripts (PowerShell + batch)
   - NSIS installer with shortcuts
   - Portable ZIP option
   - Complete build documentation

3. **Automated CI/CD**
   - GitHub Actions builds all platforms on tag push
   - Parallel builds (macOS, Windows, Linux)
   - Automatic release creation
   - ~15-25 minute build time

### Bug Fixes

- Vector database paths respect profile system
- No more shared database conflicts
- Settings UI shows correct profile-specific paths

## How to Release

### Quick Version

```bash
# 1. Update version in package.json to "0.2.0"
# 2. Commit
git commit -am "Release v0.2.0"

# 3. Create and push tag
git tag -a v0.2.0 -m "Release v0.2.0 - Profile-specific vector databases and Windows support"
git push origin v0.2.0

# 4. GitHub Actions automatically builds and creates release
# 5. Edit release notes and publish
```

### Detailed Version

See `RELEASE_v0.2.0_QUICK_START.md` or `docs/RELEASE_PLAN_v0.2.0.md`

## Testing Checklist

Before releasing, test:

- [ ] **Profile Isolation**
  - Create 2 profiles
  - Index different documents in each
  - Switch between profiles
  - Verify data doesn't mix

- [ ] **Different Embedding Models**
  - Profile 1: Use bge-base
  - Profile 2: Use all-MiniLM
  - Index in both
  - Switch and verify correct embeddings load

- [ ] **Path Display**
  - Check Settings UI shows: `/Users/{user}/.zotero-llm/profiles/{profile-id}/chroma`
  - Not the old: `/Users/{user}/.zotero-llm/chroma/user-1`

- [ ] **Platform Builds** (or rely on CI/CD)
  - macOS build succeeds
  - Windows build succeeds  
  - Linux build succeeds

## Migration Notes for Users

### For Existing Users

If you have data in the old `user-1` location:

**Option 1: Keep Old Data**
```bash
# Copy to default profile
cp -r ~/.zotero-llm/chroma/user-1/* ~/.zotero-llm/profiles/default/chroma/
```

**Option 2: Fresh Start**
- Just update and re-index your library
- Old data will be ignored

### For New Users

Everything works automatically - just create profiles and index!

## Expected Release Artifacts

After GitHub Actions completes:

**macOS** (5 files):
- ZoteroRAG-0.2.0-mac-arm64.dmg
- ZoteroRAG-0.2.0-mac-x64.dmg
- ZoteroRAG-0.2.0-mac-arm64.zip
- ZoteroRAG-0.2.0-mac-x64.zip
- latest-mac.yml

**Windows** (5 files):
- ZoteroRAG-0.2.0-win-x64.exe
- ZoteroRAG-0.2.0-win-ia32.exe
- ZoteroRAG-0.2.0-win-x64.zip
- ZoteroRAG-0.2.0-win-ia32.zip
- latest.yml

**Linux** (4 files):
- ZoteroRAG-0.2.0-linux-x64.AppImage
- zotero-rag-assistant_0.2.0_amd64.deb
- ZoteroRAG-0.2.0-linux-arm64.AppImage
- latest-linux.yml

## Post-Release

After release is published:

1. Test downloads on actual hardware
2. Verify auto-update from 0.1.11 works
3. Monitor GitHub Issues for bugs
4. Announce in Discussions
5. Update any external documentation

## Files to Review Before Release

Key files to check:

- [ ] `package.json` - Version is 0.2.0
- [ ] `CHANGELOG.md` - All changes documented
- [ ] `backend/main.py` - Profile paths working correctly
- [ ] `.github/workflows/build-all.yml` - CI/CD configured
- [ ] `docs/RELEASE_PLAN_v0.2.0.md` - Complete plan
- [ ] `RELEASE_v0.2.0_QUICK_START.md` - Quick start guide

## Known Issues

Document these in release notes:

1. **Windows SmartScreen Warning**
   - Expected for unsigned apps
   - Users click "More info" → "Run anyway"

2. **Migration Path**
   - Old `user-1` data not auto-migrated
   - Manual copy or re-index required

3. **Linux First Run**
   - May need to install Python venv dependencies
   - App auto-repairs if missing

## Success Criteria

Release is successful if:

- [ ] All platform builds complete without errors
- [ ] Installers download and launch on target platforms
- [ ] Profile switching works correctly
- [ ] Vector databases are isolated per profile
- [ ] Auto-update works from 0.1.11
- [ ] No critical bugs reported in first 48 hours

## Next Steps

After 0.2.0 is released:

1. Create milestone for 0.2.1 (hotfixes)
2. Create milestone for 0.3.0 (next features)
3. Monitor adoption and feedback
4. Plan next feature set

## Questions?

- **Detailed plan**: `docs/RELEASE_PLAN_v0.2.0.md`
- **Quick start**: `RELEASE_v0.2.0_QUICK_START.md`
- **General process**: `docs/RELEASE_PROCESS.md`
- **Build checklist**: `docs/BUILD_CHECKLIST.md`

---

**Ready to release?** Follow `RELEASE_v0.2.0_QUICK_START.md`! 🚀
