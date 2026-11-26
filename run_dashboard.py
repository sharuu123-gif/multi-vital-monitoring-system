"""
Launcher for Multi-Vital Early Warning System (MVEWS) Web Dashboard
===================================================================
Launches Streamlit application in default web browser.

Usage:
    python run_dashboard.py
"""

import sys
import os
import subprocess

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(project_root, "web", "app.py")

    print("=" * 70)
    print("  LAUNCHING MULTI-VITAL EARLY WARNING SYSTEM (MVEWS)")
    print("  Smart Healthcare Decision Support & Telemetry Dashboard")
    print("=" * 70)
    print(f"Target App: {app_path}\n")

    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nDashboard closed by user.")

if __name__ == "__main__":
    main()
