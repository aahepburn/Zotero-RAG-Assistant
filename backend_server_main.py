#!/usr/bin/env python3
"""
Backend server wrapper for PyInstaller bundle
This script starts the FastAPI backend server with uvicorn
Accepts port as a command-line argument to match Electron's expectations
"""
import sys
import uvicorn

def main():
    # Parse command line arguments
    port = 8000  # default port
    host = "127.0.0.1"
    
    # Simple argument parsing
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == '--port' and i + 1 < len(args):
            port = int(args[i + 1])
        elif arg == '--host' and i + 1 < len(args):
            host = args[i + 1]
    
    print(f"Starting Zotero RAG Assistant backend server on {host}:{port}")
    print(f"PyInstaller bundle - Python {sys.version}")
    
    # Import the app directly (not as a string) so PyInstaller can find it
    from backend.main import app
    
    # Run uvicorn with the FastAPI app object
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
