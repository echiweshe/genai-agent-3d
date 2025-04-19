#!/usr/bin/env python
"""
Check and install required dependencies for GenAI Agent 3D
"""
import os
import sys
import subprocess
import importlib.util
import pkg_resources

# Key dependencies that might be missing
REQUIRED_PACKAGES = [
    "fastapi",
    "uvicorn",
    "python-multipart",  # Required for file uploads
    "redis",
    "websockets",
    "pyyaml",
    "requests",
    "pillow",  # Commonly needed for image handling
    "aiofiles",  # Async file operations
    "python-dotenv"  # Environment variable management
]

def check_package(package_name):
    """Check if a package is installed"""
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def install_package(package_name):
    """Install a package using pip"""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}: {e}")
        return False

def main():
    """Check and install dependencies"""
    print("\n" + "="*80)
    print(" Checking GenAI Agent 3D Dependencies ".center(80, "="))
    print("="*80)
    
    missing_packages = []
    
    # Check required packages
    for package in REQUIRED_PACKAGES:
        if check_package(package):
            print(f"✅ {package} is installed")
        else:
            print(f"❌ {package} is NOT installed")
            missing_packages.append(package)
    
    # Install missing packages if any
    if missing_packages:
        print("\nMissing packages found. Installing...")
        
        # Ask for confirmation
        if input(f"Install missing packages ({', '.join(missing_packages)})? (y/n): ").lower() != 'y':
            print("Installation cancelled.")
            return 1
        
        # Install packages
        for package in missing_packages:
            if install_package(package):
                print(f"✅ Successfully installed {package}")
            else:
                print(f"❌ Failed to install {package}")
    else:
        print("\nAll required packages are installed! 🎉")
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"\nPython version: {python_version}")
    
    # Final message
    if missing_packages:
        print("\n⚠️ Please restart your backend services after installing dependencies.")
    else:
        print("\nYour system has all required dependencies.")
    
    print("="*80)
    return 0

if __name__ == "__main__":
    sys.exit(main())
