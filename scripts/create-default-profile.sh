#!/bin/bash
# Create a default profile for Zotero RAG Assistant
# This script creates the minimal directory structure and files needed for a profile

set -e

PROFILE_DIR="$HOME/.zotero-llm/profiles/default"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S")

echo "Creating default profile at: $PROFILE_DIR"

# Create directory structure
mkdir -p "$PROFILE_DIR/chroma"

# Create profile.json metadata
cat > "$PROFILE_DIR/profile.json" << EOF
{
  "id": "default",
  "name": "Default Profile",
  "description": "",
  "createdAt": "${TIMESTAMP}Z",
  "updatedAt": "${TIMESTAMP}Z",
  "version": "1.0"
}
EOF

# Create settings.json (empty, will use app defaults)
cat > "$PROFILE_DIR/settings.json" << EOF
{}
EOF

# Create sessions.json
cat > "$PROFILE_DIR/sessions.json" << EOF
{
  "sessions": {},
  "currentSessionId": null
}
EOF

# Create active_profile.json to set default as active
cat > "$HOME/.zotero-llm/active_profile.json" << EOF
{
  "activeProfileId": "default"
}
EOF

echo "✓ Default profile created successfully"
echo "  Profile directory: $PROFILE_DIR"
echo "  Active profile set to: default"
