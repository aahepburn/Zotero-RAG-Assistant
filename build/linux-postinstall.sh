#!/bin/bash
# Post-installation script for Linux .deb package
# This runs after the package is installed via apt/dpkg

# Set up chrome-sandbox permissions
# The chrome-sandbox binary needs to be owned by root with setuid bit
# to properly sandbox the Chromium renderer processes

INSTALL_DIR="/opt/ZoteroRAG"
SANDBOX_PATH="$INSTALL_DIR/chrome-sandbox"

if [ -f "$SANDBOX_PATH" ]; then
    echo "Setting up chrome-sandbox permissions..."
    chown root:root "$SANDBOX_PATH"
    chmod 4755 "$SANDBOX_PATH"
    echo "✓ chrome-sandbox configured"
fi

exit 0
