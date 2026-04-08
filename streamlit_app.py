"""
Streamlit entrypoint for Streamlit Community Cloud.
"""

import sys
from pathlib import Path

# Ensure the src directory is in the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app import main

if __name__ == "__main__":
    main()
