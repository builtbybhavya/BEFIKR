"""Befikr Desktop Application Launcher.

Runs the local offline FastAPI backend and opens an interactive desktop window.
Zero external network APIs required. 100% offline.
"""

import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess
from pathlib import Path

# Explicit imports so PyInstaller bundles all required submodules
import fastapi
import fastapi.middleware
import fastapi.middleware.cors
import fastapi.staticfiles
import fastapi.responses
import starlette
import starlette.middleware
import starlette.middleware.cors
import starlette.staticfiles
import starlette.responses
import starlette.routing
import pydantic
import uvicorn
import networkx
import sqlite3

# Base directory for assets (supports PyInstaller --onedir / --onefile)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
else:
    BASE_DIR = Path(__file__).resolve().parent

# Check if backend is directly in BASE_DIR or in _internal
if not (BASE_DIR / "backend").exists() and (BASE_DIR / "_internal" / "backend").exists():
    BASE_DIR = BASE_DIR / "_internal"

BACKEND_DIR = BASE_DIR / "backend"
WEB_DIR = BASE_DIR / "web"
FIXTURES_DIR = BACKEND_DIR / "fixtures"

# User persistent data directory
APPDATA_DIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / "Befikr"
APPDATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = APPDATA_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

os.environ["BEFIKR_DATA_DIR"] = str(DATA_DIR)
os.environ["BEFIKR_WEB_DIR"] = str(WEB_DIR)
os.environ["BEFIKR_FIXTURES_DIR"] = str(FIXTURES_DIR)
os.environ["BEFIKR_MAPPING_PROVIDER"] = "offline_ai_decider"

# Add backend directory to sys.path
sys.path.insert(0, str(BACKEND_DIR))


def find_free_port(start_port=8000):
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port


def run_server(port):
    import uvicorn
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def open_window(url):
    time.sleep(1.2)
    # Check for Edge or Chrome to run in frameless standalone app mode
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe")
    ]
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    browser_exe = None
    for p in edge_paths + chrome_paths:
        if os.path.exists(p):
            browser_exe = p
            break

    if browser_exe:
        try:
            subprocess.Popen([browser_exe, f"--app={url}", "--new-window"])
            return
        except Exception:
            pass

    webbrowser.open(url)


def main():
    print("=" * 60)
    print("  BEFIKR - Offline AI Safe Route & Safety System")
    print("  Zero Network Dependencies. Running 100% Locally.")
    print("=" * 60)
    
    port = find_free_port(8000)
    print(f"Starting local offline server on http://127.0.0.1:{port}...")
    
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    url = f"http://127.0.0.1:{port}/"
    print(f"Opening Befikr application: {url}")
    open_window(url)
    
    print("\nBefikr is running. Close the application window or press Ctrl+C here to stop.")
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\nStopping Befikr...")
        sys.exit(0)


if __name__ == "__main__":
    main()
