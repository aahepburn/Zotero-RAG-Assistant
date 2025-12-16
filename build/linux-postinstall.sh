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

exit 0
