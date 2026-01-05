#!/bin/bash
# test-linux-python.sh - Test Python detection on Linux systems
# This script simulates the Python detection logic from the Electron app

set -e

echo " Testing Python detection on Linux..."
echo ""

# Function to check if a Python command works
check_python() {
    local cmd=$1
    local source=$2
    
    echo -n "  Testing '$cmd' ($source)... "
    
    if command -v "$cmd" &> /dev/null; then
        version=$("$cmd" --version 2>&1 | grep -oP 'Python \K[\d.]+' || echo "unknown")
        if [[ $version == 3.* ]]; then
            echo " Found Python $version"
            return 0
        else
            echo " Found Python $version (need 3.x)"
            return 1
        fi
    else
        echo " Not found"
        return 1
    fi
}

echo "System Python candidates:"
check_python "python3" "system" && FOUND_PYTHON3=1 || FOUND_PYTHON3=0
check_python "python" "system" && FOUND_PYTHON=1 || FOUND_PYTHON=0
check_python "/usr/bin/python3" "system" && FOUND_USR_PYTHON3=1 || FOUND_USR_PYTHON3=0
check_python "/usr/local/bin/python3" "system" && FOUND_LOCAL_PYTHON3=1 || FOUND_LOCAL_PYTHON3=0

echo ""

if [ $FOUND_PYTHON3 -eq 1 ] || [ $FOUND_PYTHON -eq 1 ] || [ $FOUND_USR_PYTHON3 -eq 1 ] || [ $FOUND_LOCAL_PYTHON3 -eq 1 ]; then
    echo " At least one working Python 3 interpreter found!"
    echo ""
    echo "The Zotero LLM Assistant AppImage should work on this system."
else
    echo " No Python 3 interpreter found!"
    echo ""
    echo "To fix this, install Python 3:"
    echo ""
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  Fedora/RHEL:   sudo dnf install python3"
    echo "  Arch:          sudo pacman -S python"
    echo ""
    echo "After installation, the AppImage should work."
fi

echo ""
echo " Note: The app first tries bundled Python, then falls back to system Python."
