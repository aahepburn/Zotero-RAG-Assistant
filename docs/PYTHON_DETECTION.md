# Python Detection & Bundling

## Overview

The Zotero LLM Assistant uses a **hybrid approach** for Python detection that provides maximum compatibility across platforms:

1. **Bundled Python (Primary)**: Ships with a self-contained Python environment
2. **System Python (Fallback)**: Uses system-installed Python 3 if bundle is missing
3. **Clear Error Messages**: Guides users to install Python if neither option works

## Architecture

### Development Mode
- Uses system Python (prefers `python3` over `python`)
- Runs backend from source directory
- Requires Python 3.8+ and dependencies installed via `pip`

### Production Mode (Packaged App)
1. **First**: Checks for bundled Python in `app.asar.unpacked/resources/python/`
2. **Second**: Falls back to system Python (tries `python3`, then `python`)
3. **Third**: Shows user-friendly error with installation instructions

## Cross-Platform Behavior

### Linux (AppImage)
The AppImage includes a bundled Python environment, but if extraction fails or the bundle is incomplete:

- **Primary**: `resources/python/bin/python3` (bundled)
- **Fallback Order**:
  1. `python3` (from PATH)
  2. `python` (from PATH)
  3. `/usr/bin/python3` (absolute path)
  4. `/usr/local/bin/python3` (absolute path)

**Why both `python` and `python3`?**
- Most modern Linux distros only provide `python3` command
- Some have `python-is-python3` package that creates `python` symlink
- Our code handles both cases automatically

### macOS (DMG)
- **Primary**: `Resources/python/bin/python3` (bundled)
- **Fallback**: System Python (usually `/usr/bin/python3` or Homebrew's Python)

### Windows (NSIS Installer)
- **Primary**: `Resources\python\Scripts\python.exe` (bundled)
- **Fallback**: System Python from PATH or Python Launcher

## Building with Bundled Python

### 1. Create Python Bundle

Run the bundling script before packaging:

```bash
# Create bundled Python environment
./scripts/bundle-python.sh

# This creates python-dist/ with all dependencies
```

### 2. Package the App

The `electron-builder` configuration automatically includes the Python bundle:

```bash
# Package for your platform
npm run package:linux   # Creates AppImage with bundled Python
npm run package:mac     # Creates DMG with bundled Python
npm run package:win     # Creates installer with bundled Python

# Or package for all platforms
npm run package:all
```

### 3. What Gets Bundled

From `package.json` build config:

```json
{
  "extraResources": [
    {
      "from": "backend",
      "to": "backend"
    },
    {
      "from": "python-dist",
      "to": "python"
    }
  ]
}
```

This creates the following structure in the packaged app:

```
app.asar.unpacked/
  resources/
    backend/           # Python backend source code
      main.py
      *.py
    python/            # Bundled Python environment
      bin/
        python3        # Python interpreter
        python         # Symlink to python3 (Linux/macOS)
        pip
        uvicorn
      lib/
        python3.x/
          site-packages/
            fastapi/
            chromadb/
            sentence_transformers/
            ...
```

## Python Detection Logic (TypeScript)

The main detection logic in `electron/main.ts`:

```typescript
async function findPythonInterpreter(): Promise<{
  path: string;
  version?: string;
  source: string;
} | null> {
  const candidates: { path: string; source: string }[] = [];
  
  // In production, try bundled Python first
  if (!IS_DEV) {
    const bundledPaths = [
      path.join(process.resourcesPath, 'python', 'bin', 'python3'),
      path.join(process.resourcesPath, 'python', 'bin', 'python'),
      // ... platform-specific paths
    ];
    
    for (const pythonPath of bundledPaths) {
      if (fs.existsSync(pythonPath)) {
        candidates.push({ path: pythonPath, source: 'bundled' });
      }
    }
  }
  
  // Add system Python candidates
  if (process.platform !== 'win32') {
    candidates.push(
      { path: 'python3', source: 'system' },
      { path: 'python', source: 'system' },
      // ... more candidates
    );
  }
  
  // Test each candidate until one works
  for (const candidate of candidates) {
    const result = await checkPythonAvailability(candidate.path);
    if (result.available) {
      return {
        path: candidate.path,
        version: result.version,
        source: candidate.source
      };
    }
  }
  
  return null; // No working Python found
}
```

## Error Handling

### No Python Found
Shows platform-specific installation instructions:

**Linux:**
```
Python Not Found

The application requires Python 3 to run the backend service.

Please install Python 3:

Ubuntu/Debian: sudo apt install python3
Fedora/RHEL: sudo dnf install python3
Arch: sudo pacman -S python
```

**macOS:**
```
Please install Python 3:

Using Homebrew: brew install python3
Or download from: https://www.python.org/downloads/
```

**Windows:**
```
Please install Python 3 from:
https://www.python.org/downloads/

Make sure to check "Add Python to PATH" during installation.
```

## Testing

### Test on Linux (without bundled Python)
```bash
# Simulate AppImage environment
./scripts/test-linux-python.sh
```

### Test Python Detection
```bash
# Start app and check logs
npm run package:linux
./release/*.AppImage --no-sandbox

# Check console output for Python detection results
```

Expected log output:
```
Finding Python interpreter for production...
  Testing Python candidate: /app/resources/python/bin/python3 (bundled)
  ✓ Found working Python 3.12.3 at /app/resources/python/bin/python3
Using bundled Python: /app/resources/python/bin/python3
Version: 3.12.3
Source: bundled
```

Or with fallback:
```
Finding Python interpreter for production...
  Testing Python candidate: /app/resources/python/bin/python3 (bundled)
  ✗ /app/resources/python/bin/python3: Command not found
  Testing Python candidate: python3 (system)
  ✓ Found working Python 3.12.3 at python3
Using system Python: python3
Version: 3.12.3
Source: system
```

## Troubleshooting

### AppImage shows "Python Not Found"

**Cause**: Neither bundled nor system Python available

**Solutions**:
1. Install system Python 3: `sudo apt install python3`
2. Rebuild AppImage with bundled Python: `./scripts/bundle-python.sh && npm run package:linux`

### AppImage finds Python but backend fails to start

**Cause**: Missing Python dependencies

**Solutions**:
1. If using system Python, install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
2. Use bundled Python by rebuilding: `./scripts/bundle-python.sh && npm run package:linux`

### Bundled Python not found in AppImage

**Cause**: Bundle not created before packaging

**Solution**:
```bash
# Always run bundle script before packaging
./scripts/bundle-python.sh
npm run package:linux
```

### "python: command not found" on Linux

**This is normal!** Modern Linux distros only provide `python3`. Our code handles this automatically by trying `python3` first.

## Best Practices

1. **Always bundle Python for distribution**
   - Ensures consistent Python version across all user systems
   - Includes all dependencies
   - No user setup required

2. **Test fallback behavior**
   - Delete `python-dist/` and test with system Python
   - Verify error messages are helpful

3. **Keep bundle-python.sh updated**
   - Update when adding new Python dependencies
   - Test on all platforms after changes

4. **Document Python requirements**
   - Update README with minimum Python version
   - List required system packages (if any)

## Related Files

- `electron/main.ts` - Python detection and backend spawning logic
- `scripts/bundle-python.sh` - Creates bundled Python environment
- `scripts/test-linux-python.sh` - Tests Python detection on Linux
- `package.json` - Electron-builder configuration for bundling
- `requirements.txt` - Python dependencies to bundle

## Future Improvements

- [ ] Add automatic Python installer for Windows (download Python if missing)
- [ ] Support Python virtual environments in development
- [ ] Add Python version compatibility check (warn if <3.8)
- [ ] Create separate bundles for different architectures (x64, arm64)
- [ ] Add telemetry for Python detection failures
