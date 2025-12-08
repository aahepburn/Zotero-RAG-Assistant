#!/bin/bash

# Post-install script for Debian package
# This sets the correct permissions for chrome-sandbox to enable sandboxing

INSTALL_DIR="/opt/zotero-rag-assistant"
SANDBOX_PATH="$INSTALL_DIR/chrome-sandbox"

if [ -f "$SANDBOX_PATH" ]; then
    echo "Setting chrome-sandbox permissions..."
    chown root:root "$SANDBOX_PATH"
    chmod 4755 "$SANDBOX_PATH"
    echo "chrome-sandbox permissions set successfully"
else
    echo "Warning: chrome-sandbox not found at $SANDBOX_PATH"
fi

exit 0
