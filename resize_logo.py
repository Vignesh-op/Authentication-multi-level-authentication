"""
Resize Authentication Logo for navbar display
This script creates a smaller version of the main logo
"""
from PIL import Image
import os

def create_logo_variants():
    """Create logo variants for different uses"""
    
    images_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    main_logo_path = os.path.join(images_dir, 'authentication-logo.png')
    small_logo_path = os.path.join(images_dir, 'authentication-logo-small.png')
    
    if not os.path.exists(main_logo_path):
        print("✗ Main logo not found at:", main_logo_path)
        print("Please save your logo image to:", main_logo_path)
        return False
    
    try:
        # Open main logo
        main_logo = Image.open(main_logo_path)
        print(f"✓ Loaded main logo: {main_logo.size}")
        
        # Create small version (for navbar)
        main_logo.thumbnail((256, 300), Image.Resampling.LANCZOS)
        main_logo.save(small_logo_path, 'PNG')
        print(f"✓ Created navbar logo: {small_logo_path}")
        
        # Reload and save main logo in high quality
        main_logo_orig = Image.open(main_logo_path)
        main_logo_orig.save(main_logo_path, 'PNG', quality=95)
        print(f"✓ Optimized main logo")
        
        print("\n✓ All logo variants ready!")
        return True
        
    except Exception as e:
        print(f"✗ Error processing logo: {e}")
        return False

if __name__ == '__main__':
    create_logo_variants()
