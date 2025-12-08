#!/bin/bash

# Post-install script for Debian package
# This sets the correct permissions for chrome-sandbox to enable sandboxing

INSTALL_DIR="/opt/zotero-rag-assistant"
SANDBOX="${INSTALL_DIR}/chrome-sandbox"

if [ -f "${SANDBOX}" ]; then
    echo "Setting chrome-sandbox permissions..."
    chown root:root "${SANDBOX}"
    chmod 4755 "${SANDBOX}"
    echo "chrome-sandbox permissions set successfully"
else
    echo "Warning: chrome-sandbox not found at ${SANDBOX}"
fi

exit 0
