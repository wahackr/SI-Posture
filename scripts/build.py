#!/usr/bin/env python3
"""Build SI-Posture for distribution."""

import subprocess
import sys

def main():
    print("Building SI-Posture...")
    
    # Build with PyInstaller
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "SI-Posture",
        "--add-data", "src/si_posture/resources:.",
        "src/si_posture/main.py"
    ], check=True)
    
    print("Build complete!")

if __name__ == "__main__":
    main()
