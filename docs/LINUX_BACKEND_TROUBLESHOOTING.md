# Linux Backend Troubleshooting Guide

## Problem: Backend Fails to Start (ERR_CONNECTION_REFUSED)

When you see errors like:
```
Failed to load resource: net::ERR_CONNECTION_REFUSED
localhost:8000/api/ollama_status:1
```

This means the backend server is not running. On Linux, the app needs to set up a Python virtual environment on first run.

## Quick Fixes

### 1. Check Python Installation

The app requires Python 3.8 or later with venv support:

```bash
# Check Python version
python3 --version

# Should show Python 3.8.x or higher
```

### 2. Install Required Python Packages

If Python is missing or incomplete, install it:

```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv

# Fedora/RHEL/CentOS
sudo dnf install python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

### 3. Reset the Virtual Environment

If the venv is corrupted or partially installed:

```bash
# Remove the existing virtual environment
rm -rf ~/.config/zotero-rag-assistant/venv

# Restart the application - it will recreate the venv
```

### 4. Check Build Tools (if dependency installation fails)

Some Python packages need compilation:

```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# Fedora/RHEL
sudo dnf install gcc gcc-c++ python3-devel

# Arch Linux
sudo pacman -S base-devel
```

## How It Works (Linux)

Unlike macOS/Windows which bundle Python, the Linux version:

1. **First Run**: Creates a virtual environment at `~/.config/zotero-rag-assistant/venv`
2. **Installs Dependencies**: Downloads and installs all required Python packages (takes 2-5 minutes)
3. **Subsequent Runs**: Uses the existing venv (starts quickly)

## What Changed in v0.2.5

The recent update improves the Linux experience:

### Before
- No visual feedback during setup
- Generic error messages
- Users didn't know what was happening

### After
- **Loading window** shows progress during venv setup
- **Detailed error messages** explain what went wrong
- **Specific guidance** for different failure types
- **Better logging** in the console

## Common Error Scenarios

### "Python venv module is missing"
```bash
sudo apt install python3-venv
```

### "Failed to install required Python packages"
**Possible causes:**
- No internet connection
- Missing build tools
- PyPI server issues

**Solutions:**
```bash
# Install build tools
sudo apt install build-essential python3-dev

# Check internet connection
ping pypi.org

# Try again with reset venv
rm -rf ~/.config/zotero-rag-assistant/venv
```

### "Permission denied"
```bash
# Fix permissions
chmod -R u+rwX ~/.config/zotero-rag-assistant

# Or recreate with correct permissions
rm -rf ~/.config/zotero-rag-assistant
```

### "Port 8000 already in use"
```bash
# Find what's using the port
sudo lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

## Viewing Console Output

To see detailed error messages:

1. **Run from terminal** to see stdout/stderr:
   ```bash
   /path/to/ZoteroRAG.AppImage
   # or
   zotero-rag-assistant  # if installed via deb/rpm
   ```

2. **Open DevTools** in the app:
   - Press `Ctrl+Shift+I`
   - Go to Console tab
   - Look for `[Backend Error]` messages

3. **Check application logs** (if available):
   ```bash
   cat ~/.config/zotero-rag-assistant/logs/*.log
   ```

## Still Having Issues?

1. **Collect diagnostic info:**
   ```bash
   # System info
   uname -a
   python3 --version
   
   # Check venv
   ls -la ~/.config/zotero-rag-assistant/venv/
   
   # Try manual venv creation
   python3 -m venv /tmp/test-venv
   source /tmp/test-venv/bin/activate
   pip install uvicorn
   ```

2. **Run the backend manually** (for advanced troubleshooting):
   ```bash
   # Activate the venv
   source ~/.config/zotero-rag-assistant/venv/bin/activate
   
   # Navigate to the app resources
   cd /path/to/app/resources
   
   # Run the backend
   python3 -m uvicorn backend.main:app --port 8000
   ```

3. **Report the issue** with:
   - Linux distribution and version
   - Python version
   - Console output
   - Error messages from the dialog boxes

## For Developers

If you're running from source:

```bash
# Create a development environment
cd /path/to/zotero-rag-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run backend manually
python3 -m uvicorn backend.main:app --port 8000 --reload

# In another terminal, run frontend
npm run dev
```
