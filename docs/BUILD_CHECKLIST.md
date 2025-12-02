# Build & Release Checklist - Python Detection

Use this checklist when building and releasing new versions to ensure Python detection works correctly on all platforms.

## Pre-Build Checklist

### 1. Verify Code Compiles
```bash
npm run build:electron
```
- [ ] TypeScript compiles without errors
- [ ] No type errors in console

### 2. Test in Development Mode
```bash
npm run dev
```
- [ ] Backend starts successfully
- [ ] Frontend loads and connects
- [ ] Check console for Python detection logs
- [ ] Verify backend responds at http://localhost:8000/health

### 3. Bundle Python Environment
```bash
./scripts/bundle-python.sh
```
- [ ] Script completes without errors
- [ ] `python-dist/` directory created
- [ ] Verification passes (imports successful)
- [ ] Check bundle size is reasonable (~500MB-1GB)

### 4. Test Bundle Locally (Optional but Recommended)
```bash
# Test the bundled Python directly
python-dist/bin/python --version
python-dist/bin/python -c "import fastapi, uvicorn, chromadb"
```
- [ ] Bundled Python runs
- [ ] All imports work

## Build Checklist

### For Linux AppImage

```bash
npm run package:linux
```

- [ ] Build completes without errors
- [ ] AppImage file created in `release/`
- [ ] File size seems reasonable (>100MB with bundled Python)

### For macOS DMG

```bash
npm run package:mac
```

- [ ] Build completes without errors
- [ ] DMG file created in `release/`
- [ ] Both x64 and arm64 builds (if applicable)

### For Windows

```bash
npm run package:win
```

- [ ] Build completes without errors
- [ ] Installer created in `release/`

## Post-Build Testing

### Test Matrix

Test each build on the target platform:

#### Linux (Primary Focus)

**Test 1: With System Python 3**
```bash
# Ensure python3 is available
python3 --version

# Run AppImage
./release/Zotero-LLM-Assistant-*-linux-*.AppImage --no-sandbox
```
- [ ] App starts without errors
- [ ] Backend connects
- [ ] Check logs show Python detection
- [ ] Verify which Python was used (bundled or system)

**Test 2: Without System Python (if possible)**
```bash
# Simulate missing system Python by temporarily renaming
sudo mv /usr/bin/python3 /usr/bin/python3.bak

# Run AppImage
./release/Zotero-LLM-Assistant-*-linux-*.AppImage --no-sandbox

# Should use bundled Python or show clear error
```
- [ ] Uses bundled Python successfully OR
- [ ] Shows clear "Python Not Found" error with installation instructions

**Test 3: Run Diagnostic Script (Before Building)**
```bash
./scripts/test-linux-python.sh
```
- [ ] Script detects available Python interpreters
- [ ] Lists versions correctly

#### macOS

**Test 1: With Bundled Python**
```bash
# Open the DMG and install
open release/Zotero-LLM-Assistant-*.dmg

# Run from Applications
# Open Console.app to view logs
```
- [ ] App starts and runs
- [ ] Backend connects
- [ ] Check Console.app for Python detection logs

**Test 2: Check Resource Bundle**
```bash
# Verify bundled Python exists in .app
ls -la "/Applications/Zotero LLM Assistant.app/Contents/Resources/python/bin/"
```
- [ ] python3 exists
- [ ] python symlink exists

#### Windows

**Test 1: With Bundled Python**
```
# Install via installer
# Run app
# Check logs in: %APPDATA%\Zotero LLM Assistant\logs\
```
- [ ] App starts and runs
- [ ] Backend connects
- [ ] Python detection logs look correct

## Verification Checklist

### Log Output Verification

When the app starts, check console/logs for these messages:

**Expected (Bundled Python):**
```
Finding Python interpreter for production...
  Testing Python candidate: /path/to/resources/python/bin/python3 (bundled)
  ✓ Found working Python 3.12.3 at /path/to/resources/python/bin/python3
Using bundled Python: /path/to/resources/python/bin/python3
Version: 3.12.3
Source: bundled
```
- [ ] Shows "bundled" as source
- [ ] Python version is reasonable (3.8+)
- [ ] Backend starts successfully

**Expected (System Python Fallback):**
```
Finding Python interpreter for production...
  Testing Python candidate: /path/to/resources/python/bin/python3 (bundled)
  ✗ /path/to/resources/python/bin/python3: Command not found
  Testing Python candidate: python3 (system)
  ✓ Found working Python 3.12.3 at python3
Using system Python: python3
Version: 3.12.3
Source: system
```
- [ ] Shows "system" as source
- [ ] Tries bundled first, then system
- [ ] Backend starts successfully

**Expected (Error Case):**
```
Finding Python interpreter for production...
  Testing Python candidate: ... (bundled)
  ✗ ... Command not found
  Testing Python candidate: python3 (system)
  ✗ python3: Command not found
  Testing Python candidate: python (system)
  ✗ python: Command not found
✗ FATAL: Could not find Python interpreter
```
- [ ] Shows dialog: "Python Not Found"
- [ ] Dialog includes platform-specific installation instructions
- [ ] User can click "Continue Anyway" or "Exit"

### Backend Health Check

After app starts, verify backend:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "components": {
    "database": "healthy",
    "vector_db": "healthy",
    "llm": "healthy"
  }
}
```
- [ ] Returns 200 OK
- [ ] Status is "healthy" or "degraded"
- [ ] Components are listed

## Troubleshooting Common Issues

### Issue: "Python Not Found" on Linux with python3 installed

**Check:**
```bash
which python3
python3 --version
```

**Possible causes:**
- AppImage environment isolation issues
- Python not in standard locations
- Bundled Python missing and system Python not detected

**Fix:**
- Rebuild with bundled Python: `./scripts/bundle-python.sh && npm run package:linux`
- Or ensure python3 is in /usr/bin/

### Issue: Backend fails to start even with Python detected

**Check logs for:**
- Missing Python dependencies
- Port 8000 already in use
- Backend code errors

**Fix:**
- If using system Python: `python3 -m pip install -r requirements.txt`
- If using bundled Python: Rebuild bundle with `./scripts/bundle-python.sh`

### Issue: Bundled Python not found in packaged app

**Check:**
- `python-dist/` exists before build
- `package.json` extraResources includes python-dist → python
- Built app includes `resources/python/` directory

**Fix:**
- Run `./scripts/bundle-python.sh` before packaging
- Verify extraResources config in package.json

## Release Checklist

Before creating a GitHub release:

- [ ] All platform builds tested
- [ ] Python detection works (bundled and fallback)
- [ ] Error messages are helpful
- [ ] Update CHANGELOG.md
- [ ] Update version in package.json
- [ ] Tag release in git
- [ ] Upload all builds to GitHub Releases
- [ ] Write release notes mentioning Python detection improvements

## Quick Commands Summary

```bash
# Full build process (Linux example)
./scripts/bundle-python.sh           # Bundle Python
npm run build                         # Build frontend & electron
npm run package:linux                 # Create AppImage
./release/*.AppImage --no-sandbox    # Test

# Test Python detection
./scripts/test-linux-python.sh       # Diagnostic

# Clean rebuild
rm -rf python-dist/ release/ dist/   # Clean
./scripts/bundle-python.sh           # Re-bundle
npm run package:linux                # Re-package
```

## Notes

- Always bundle Python before packaging for best user experience
- Test on clean VMs/systems if possible
- Keep documentation updated when changing detection logic
- Monitor user reports of Python issues after release

## Files to Review

Before releasing, review these files:
- [ ] `electron/main.ts` - Python detection logic
- [ ] `scripts/bundle-python.sh` - Bundling script
- [ ] `docs/PYTHON_DETECTION.md` - Technical documentation
- [ ] `docs/LINUX_PYTHON_GUIDE.md` - User guide
- [ ] `README.md` - Installation instructions
