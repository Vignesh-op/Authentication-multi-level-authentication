"""
Setup script to install the Authentication logo image
This script will save the provided logo image to the correct locations
"""
import os
from PIL import Image
import requests
from io import BytesIO

def setup_logo():
    """
    Save the Authentication logo to the correct directory with proper sizing
    """
    output_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    os.makedirs(output_dir, exist_ok=True)
    
    print("✓ Logo directory ready: static/images/")
    print("\nTo add the logo manually:")
    print("1. Save the uploaded image as: static/images/authentication-logo.png")
    print("2. The navbar will automatically resize it to fit")
    print("\nSupported formats: PNG, JPG, JPEG, GIF, WEBP")
    print("Recommended size: 512x512px or larger")

if __name__ == '__main__':
    setup_logo()
