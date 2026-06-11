#!/usr/bin/env python3
"""
Authentication Requirements Verification Script
Verifies that all required packages are installed correctly
"""

import sys
import subprocess

def check_requirement(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        __import__(import_name)
        return True, f"✓ {package_name}"
    except ImportError:
        return False, f"✗ {package_name} (NOT INSTALLED)"

def main():
    print("\n" + "="*60)
    print("Authentication - Requirements Verification")
    print("="*60 + "\n")
    
    requirements = [
        ("flask", "flask"),
        ("pymongo", "pymongo"),
        ("bcrypt", "bcrypt"),
        ("opencv-python", "cv2"),
        ("face-recognition", "face_recognition"),
        ("qrcode", "qrcode"),
        ("pyzbar", "pyzbar"),
        ("pillow", "PIL"),
        ("numpy", "numpy"),
    ]
    
    print("Checking required packages...\n")
    
    all_passed = True
    for package_name, import_name in requirements:
        passed, message = check_requirement(package_name, import_name)
        print(f"  {message}")
        if not passed:
            all_passed = False
    
    print("\n" + "-"*60)
    
    if all_passed:
        print("\n✓ All requirements are satisfied!")
        print("\nYou can now run: python app.py\n")
        return 0
    else:
        print("\n✗ Some requirements are missing!")
        print("\nRun this command to install missing packages:")
        print("  pip install -r requirements.txt\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
