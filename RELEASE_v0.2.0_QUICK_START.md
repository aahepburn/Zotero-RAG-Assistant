# Quick Start: Release v0.2.0

**Read this first before releasing!**

Complete details in: [docs/RELEASE_PLAN_v0.2.0.md](docs/RELEASE_PLAN_v0.2.0.md)

## Pre-Flight Checklist

Before creating the release tag, ensure:

1. **Testing Complete**
   - [ ] Profile switching works with different embedding models
   - [ ] Vector databases are isolated per profile
   - [ ] Tested on macOS, Windows, Linux (or rely on CI/CD)
   - [ ] Migration path documented for existing users

2. **Documentation Updated**
   - [ ] `CHANGELOG.md` reviewed (already updated)
   - [ ] Version numbers correct
   - [ ] No placeholder "TBD" dates remain

3. **Version Bumped**
   - [ ] Update `package.json`: `"version": "0.2.0"`
   - [ ] Commit: `git commit -am "Release v0.2.0"`

## Release Command

```bash
# 1. Ensure you're on master branch with latest changes
git checkout master
git pull origin master

# 2. Create annotated tag
git tag -a v0.2.0 -m "Release v0.2.0 - Profile-specific vector databases and Windows support"

# 3. Push tag (this triggers GitHub Actions CI/CD)
git push origin v0.2.0
```

## What Happens Next

1. **GitHub Actions starts** (~15-25 minutes)
   - Builds macOS (arm64 + x64)
   - Builds Windows (x64 + ia32)
   - Builds Linux (x64 + arm64)
   - Creates GitHub Release
   - Uploads all artifacts

2. **Monitor Build**: https://github.com/aahepburn/Zotero-RAG-Assistant/actions

3. **Release Created**: https://github.com/aahepburn/Zotero-RAG-Assistant/releases/tag/v0.2.0

## After Build Completes

1. **Edit Release Notes** - Enhance auto-generated notes with:
   - Clear feature descriptions
   - Installation instructions per platform
   - Known issues (Windows SmartScreen warning)
   - Migration notes for existing users

2. **Test Downloads** - Download and test installers on actual hardware

3. **Publish** - If created as draft, click "Publish release"

## Quick Commands Reference

```bash
# Verify current version
grep '"version"' package.json

# Create tag
git tag -a v0.2.0 -m "Release v0.2.0"

# Push tag (triggers build)
git push origin v0.2.0

# If you need to delete and recreate tag
git tag -d v0.2.0              # Delete local
git push origin :refs/tags/v0.2.0  # Delete remote
# Then recreate and push again
```

## Rollback

If something goes wrong:

```bash
# Delete the release on GitHub UI
# Delete the tag
git tag -d v0.2.0
git push origin :refs/tags/v0.2.0

# Fix issues, then retry
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

## Key Features in v0.2.0

Highlight these in release notes:

- ✅ **Profile-Specific Vector Databases** - Each profile gets its own isolated ChromaDB
- ✅ **Full Windows Support** - Native installers with desktop shortcuts
- ✅ **Improved Profile Isolation** - No more shared `user-1` paths
- ✅ **Multi-Model Support** - Different embedding models per profile

## Expected Artifacts

After build completes, verify these files exist in the release:

**macOS** (4 files):
- `ZoteroRAG-0.2.0-mac-arm64.dmg`
- `ZoteroRAG-0.2.0-mac-x64.dmg`
- `ZoteroRAG-0.2.0-mac-arm64.zip`
- `ZoteroRAG-0.2.0-mac-x64.zip`
- `latest-mac.yml`

**Windows** (4 files):
- `ZoteroRAG-0.2.0-win-x64.exe`
- `ZoteroRAG-0.2.0-win-ia32.exe`
- `ZoteroRAG-0.2.0-win-x64.zip`
- `ZoteroRAG-0.2.0-win-ia32.zip`
- `latest.yml`

**Linux** (3 files):
- `ZoteroRAG-0.2.0-linux-x64.AppImage`
- `zotero-rag-assistant_0.2.0_amd64.deb`
- `ZoteroRAG-0.2.0-linux-arm64.AppImage`
- `latest-linux.yml`

## Post-Release

- [ ] Announce in GitHub Discussions
- [ ] Monitor issues for bug reports
- [ ] Test auto-update from v0.1.11
- [ ] Update README badges if needed

---

**Ready?** Run the release commands above! 🚀

For complete details, see [docs/RELEASE_PLAN_v0.2.0.md](docs/RELEASE_PLAN_v0.2.0.md)
