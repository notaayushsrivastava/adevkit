"""
Aayush's DevKit - Main Entry Point.
Run directly via `python app.py` or install globally via `pip install -e .` and use `devkit`.
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from devkit.cli import main

if __name__ == "__main__":
    main()
