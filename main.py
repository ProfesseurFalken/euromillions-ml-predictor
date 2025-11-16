#!/usr/bin/env python3
"""
EuroMillions ML Prediction System - Main Launcher
================================================

Entry point for creating standalone executable with PyInstaller.
This script launches the Streamlit application.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path
import threading

def check_dependencies():
    """Check if all required packages are available."""
    try:
        import streamlit
        import pandas
        import numpy
        import lightgbm
        import sklearn
        import requests
        import bs4
        import lxml
        import loguru
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def setup_environment():
    """Setup the application environment."""
    # Get the directory of the executable/script
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        app_dir = Path(sys._MEIPASS)
        data_dir = Path(sys.executable).parent / "data"
        models_dir = Path(sys.executable).parent / "models"
    else:
        # Running as script
        app_dir = Path(__file__).parent
        data_dir = app_dir / "data"
        models_dir = app_dir / "models"
    
    # Create necessary directories
    data_dir.mkdir(exist_ok=True)
    (data_dir / "raw").mkdir(exist_ok=True)
    (data_dir / "processed").mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    (models_dir / "euromillions").mkdir(exist_ok=True)
    
    # Set working directory
    os.chdir(app_dir if not getattr(sys, 'frozen', False) else Path(sys.executable).parent)
    
    return app_dir

def open_browser(url, delay=3):
    """Open browser after a delay."""
    time.sleep(delay)
    webbrowser.open(url)

def main():
    """Main entry point."""
    print("EuroMillions ML Prediction System")
    print("=====================================")
    
    # Setup environment
    app_dir = setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("[ERROR] Missing dependencies. Please install requirements.")
        if sys.stdin.isatty():
            input("Press Enter to exit...")
        return
    
    print("[OK] Dependencies check passed")
    
    # Add current directory to Python path for imports
    sys.path.insert(0, str(app_dir))
    
    try:
        # Import and run Streamlit app
        print("Starting Streamlit server...")
        
        # Start browser opener in background
        browser_thread = threading.Thread(
            target=open_browser, 
            args=("http://localhost:8501",)
        )
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run Streamlit
        from streamlit.web import cli as stcli
        
        # Prepare Streamlit arguments
        streamlit_args = [
            "streamlit", "run", 
            str(app_dir / "ui" / "streamlit_app.py"),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "true"
        ]
        
        # Replace sys.argv to pass arguments to Streamlit
        sys.argv = streamlit_args
        
        # Launch Streamlit
        stcli.main()
        
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"[ERROR] {e}")
        if sys.stdin.isatty():
            input("Press Enter to exit...")

if __name__ == "__main__":
    main()
