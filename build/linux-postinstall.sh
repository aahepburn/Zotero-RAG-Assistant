#!/bin/bash
# Post-install script for Linux .deb package
# Fixes permissions for chrome-sandbox to enable proper Electron functionality

set -e

# Set proper permissions on chrome-sandbox for security
# This is required for Electron to run properly on Linux
if [ -f "/opt/ZoteroRAG/chrome-sandbox" ]; then
    chmod 4755 "/opt/ZoteroRAG/chrome-sandbox"
    echo "Set chrome-sandbox permissions"
fi

# Ensure the application is executable
if [ -f "/opt/ZoteroRAG/zotero-rag-assistant" ]; then
    chmod +x "/opt/ZoteroRAG/zotero-rag-assistant"
    echo "Made application executable"
fi

# Make the backend launcher wrapper executable
if [ -f "/opt/ZoteroRAG/resources/start-backend.sh" ]; then
    chmod +x "/opt/ZoteroRAG/resources/start-backend.sh"
    echo "Made backend wrapper executable"
fi

# Update desktop launcher to include --disable-gpu-sandbox flag for Remote Desktop compatibility
DESKTOP_FILE="/usr/share/applications/zotero-rag-assistant.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    # Check if the Exec line already has the flag
    if ! grep -q "disable-gpu-sandbox" "$DESKTOP_FILE"; then
        # Add the flag to the Exec line
        sed -i 's|^Exec=/opt/ZoteroRAG/zotero-rag-assistant|Exec=/opt/ZoteroRAG/zotero-rag-assistant --disable-gpu-sandbox|g' "$DESKTOP_FILE"
        echo "Updated desktop launcher with --disable-gpu-sandbox flag"
    fi
fi

exit 0
