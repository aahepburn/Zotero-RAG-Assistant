# Linux AppImage - Python Requirements

## Quick Start

The Zotero LLM Assistant AppImage works in two ways:

### Option 1: Use Bundled Python (Recommended)
The AppImage includes Python and all dependencies. Just run it:

```bash
./Zotero-LLM-Assistant-*.AppImage --no-sandbox
```

No Python installation required! ✅

### Option 2: Use System Python (Fallback)
If the bundled Python fails, the app automatically uses your system Python 3.

**Install Python 3 on your system:**

```bash
# Ubuntu/Debian/Pop!_OS
sudo apt update
sudo apt install python3 python3-pip

# Fedora/RHEL/CentOS
sudo dnf install python3 python3-pip

# Arch/Manjaro
sudo pacman -S python python-pip

# OpenSUSE
sudo zypper install python3 python3-pip
```

Then run the AppImage:
```bash
./Zotero-LLM-Assistant-*.AppImage --no-sandbox
```

## Troubleshooting

### Error: "Python Not Found"

**Symptom**: AppImage shows dialog "The application requires Python 3 to run"

**Solution**: Install Python 3 using the commands above for your distro.

**Verify installation:**
```bash
python3 --version
# Should show: Python 3.x.x (any 3.8+ version works)
```

### Error: "Backend Failed to Start"

**Symptom**: App opens but shows connection errors

**Solution 1** - Install Python dependencies (if using system Python):
```bash
python3 -m pip install --user fastapi uvicorn chromadb sentence-transformers
```

**Solution 2** - Use the bundled Python by downloading a fresh AppImage

### Why `--no-sandbox`?

AppImages may need `--no-sandbox` on some Linux systems due to kernel security restrictions. This is normal and safe for desktop apps.

To make it permanent:
```bash
# Create a desktop launcher
cat > ~/.local/share/applications/zotero-llm.desktop <<EOF
[Desktop Entry]
Name=Zotero LLM Assistant
Exec=/path/to/Zotero-LLM-Assistant-*.AppImage --no-sandbox
Icon=/path/to/icon
Type=Application
Categories=Office;Education;
EOF
```

## Why Does This Work?

The app uses smart Python detection:

1. **First** tries bundled Python (in the AppImage)
2. **Then** tries system `python3` command
3. **Then** tries system `python` command (if you have python-is-python3)
4. **Then** tries absolute paths like `/usr/bin/python3`
5. **Finally** shows helpful error if none work

This means it "just works" on most Linux systems, even without Python installed!

## Check What Python the App Uses

Run the AppImage from terminal and look for these log messages:

```
Finding Python interpreter for production...
  Testing Python candidate: /tmp/.mount_Zotero.../python/bin/python3 (bundled)
  ✓ Found working Python 3.12.3 at /tmp/.mount_Zotero.../python/bin/python3
Using bundled Python
```

Or with system fallback:
```
Finding Python interpreter for production...
  Testing Python candidate: /tmp/.mount_Zotero.../python/bin/python3 (bundled)
  ✗ /tmp/.mount_Zotero.../python/bin/python3: Command not found
  Testing Python candidate: python3 (system)
  ✓ Found working Python 3.12.3 at python3
Using system Python: python3
```

## Still Having Issues?

1. **Check Python is installed:** `python3 --version`
2. **Check AppImage is executable:** `chmod +x Zotero-LLM-Assistant-*.AppImage`
3. **Try without sandbox:** Add `--no-sandbox` flag
4. **Check logs:** Run from terminal to see error messages
5. **File an issue:** https://github.com/aahepburn/zotero-llm-plugin/issues

Include the terminal output showing which Python the app tried to use.
