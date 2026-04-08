"""
Setup and Installation Script for Resume Screening System

This script helps set up the project environment and install dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.9 or higher."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required. You have Python {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} OK")

def install_requirements():
    """Install project requirements."""
    print("\n📦 Installing requirements...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ requirements.txt not found at {requirements_file}")
        sys.exit(1)
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        sys.exit(1)

def download_nltk_data():
    """Download required NLTK data."""
    print("\n📚 Downloading NLTK data...")
    
    import nltk
    
    data_packages = [
        'punkt',
        'stopwords',
        'wordnet',
        'averaged_perceptron_tagger'
    ]
    
    for package in data_packages:
        try:
            nltk.download(package, quiet=True)
            print(f"  ✅ Downloaded {package}")
        except Exception as e:
            print(f"  ⚠️ Warning: Could not download {package}: {e}")
    
    print("✅ NLTK data downloaded")

def setup_directories():
    """Create necessary project directories."""
    print("\n📁 Creating project directories...")
    
    directories = [
        'data',
        'outputs',
        'docs',
        'src'
    ]
    
    for dirname in directories:
        dir_path = Path(__file__).parent / dirname
        dir_path.mkdir(exist_ok=True)
        print(f"  ✅ {dirname}/")
    
    print("✅ Directories created")

def verify_installation():
    """Verify that all modules can be imported."""
    print("\n🧪 Verifying installation...")
    
    modules = [
        'nltk',
        'pandas',
        'numpy',
        'sklearn',
        'streamlit',
        'kagglehub'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - Not installed")
            return False
    
    print("✅ All modules verified")
    return True

def main():
    """Run setup process."""
    print("=" * 60)
    print("  Resume Screening System - Setup & Installation")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Install requirements
    install_requirements()
    
    # Download NLTK data
    download_nltk_data()
    
    # Create directories
    setup_directories()
    
    # Verify installation
    if verify_installation():
        print("\n" + "=" * 60)
        print("✅ Setup completed successfully!")
        print("=" * 60)
        print("\n📖 Next steps:")
        print("  1. Run demo: python main.py")
        print("  2. Launch web app: streamlit run src/app.py")
        print("  3. Read documentation: docs/DOCUMENTATION.md")
        print("=" * 60)
    else:
        print("\n❌ Setup completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
