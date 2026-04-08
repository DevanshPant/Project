"""
Resume Screening System - Main Application
Streamlit Community Cloud Entry Point
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to path for Streamlit Cloud
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the main application
from app import main

if __name__ == "__main__":
    main()