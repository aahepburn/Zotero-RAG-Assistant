#!/bin/bash
# Shell wrapper to fully detach Python backend from Electron process tree
# This avoids Chromium sandbox restrictions that can kill child Python processes

# Log file for debugging
LOG="/tmp/backend-shell-wrapper.log"

{
    echo "=== Shell wrapper started ===" 
    echo "PID: $$"
    echo "PPID: $PPID"
    echo "Args: $@"
    date
    
    # Fully detach using setsid and nohup
    # This creates a new session and process group completely independent of Electron
    setsid nohup "$@" > /tmp/backend-stdout.log 2> /tmp/backend-stderr.log &
    BACKEND_PID=$!
    
    echo "Backend launched with PID: $BACKEND_PID"
    echo "Check logs:"
    echo "  /tmp/backend-stdout.log"
    echo "  /tmp/backend-stderr.log"
    
    # Write PID file so Electron can track it
    echo "$BACKEND_PID" > /tmp/backend.pid
    
} >> "$LOG" 2>&1

# Exit immediately - backend is fully detached
exit 0
