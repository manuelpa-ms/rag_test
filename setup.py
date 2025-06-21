#!/usr/bin/env python3
"""
Setup script for the RAG application.
This script helps you set up the environment and check prerequisites.
"""

import subprocess
import sys
import os
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_virtual_env():
    """Check if we're in a virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        return True
    print("⚠️  Virtual environment not detected - consider using one")
    return True

def install_requirements():
    """Install required packages."""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def check_ollama():
    """Check if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
            models = response.json().get('models', [])
            if models:
                print(f"📋 Available models: {', '.join([m['name'] for m in models])}")
            else:
                print("⚠️  No models found. Consider running: ollama pull llama3.2")
            return True
        else:
            print("❌ Ollama is not responding properly")
            return False
    except requests.RequestException:
        print("❌ Ollama is not running. Please start it with: ollama serve")
        return False

def create_directories():
    """Create necessary directories."""
    dirs = ["cache", "chroma_db"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def main():
    """Main setup function."""
    print("🚀 Setting up RAG Application with Ollama")
    print("=" * 50)
    
    all_good = True
    
    # Check Python version
    if not check_python_version():
        all_good = False
    
    # Check virtual environment
    check_virtual_env()
    
    # Install requirements
    if not install_requirements():
        all_good = False
    
    # Create directories
    create_directories()
    
    # Check Ollama
    if not check_ollama():
        all_good = False
        print("\n📋 To install and setup Ollama:")
        print("1. Download from: https://ollama.ai/")
        print("2. Install and start: ollama serve")
        print("3. Pull a model: ollama pull llama3.2")
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 Setup complete! You can now run the application:")
        print("   streamlit run app.py")
    else:
        print("⚠️  Setup completed with some issues. Please resolve them before running the app.")
    
    print("\n📚 See README.md for detailed instructions")

if __name__ == "__main__":
    main()
