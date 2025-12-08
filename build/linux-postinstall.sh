#!/bin/bash
# Post-install script for Debian package
# Ensures chrome-sandbox has correct permissions for Electron/Chromium sandbox to work

set -e

# Find the chrome-sandbox helper
# electron-builder typically installs to /opt/{productName}
APP_DIR="/opt/Zotero RAG Assistant"
CHROME_SANDBOX="${APP_DIR}/chrome-sandbox"

if [ -f "$CHROME_SANDBOX" ]; then
    echo "Configuring Electron sandbox permissions..."
    
    # Set ownership to root:root
    chown root:root "$CHROME_SANDBOX" || true
    
    # Set setuid bit (mode 4755) so unprivileged users can use the sandbox
    chmod 4755 "$CHROME_SANDBOX" || true
    
    echo "✓ Chrome sandbox configured: ${CHROME_SANDBOX}"
else
    echo "Warning: chrome-sandbox not found at ${CHROME_SANDBOX}"
    echo "Sandbox may not work properly. App will attempt to run anyway."
fi

# Ensure the app binary is executable
APP_BINARY="${APP_DIR}/zotero-rag-assistant"
if [ -f "$APP_BINARY" ]; then
    chmod +x "$APP_BINARY" || true
fi

exit 0
