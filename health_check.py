#!/usr/bin/env python3
"""
Authentication Health Check Script
Verifies database connectivity and basic functionality
"""

import sys
import os

def check_flask():
    """Check if Flask is installed and can run"""
    try:
        import flask
        print("✓ Flask:", flask.__version__)
        return True
    except ImportError:
        print("✗ Flask not installed")
        return False

def check_mongodb_connection():
    """Check MongoDB connection"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        # Force connection attempt
        client.admin.command('ping')
        print("✓ MongoDB:  Connected to localhost:27017")
        return True
    except Exception as e:
        print("✗ MongoDB:  Connection failed")
        print(f"  Error: {str(e)[:100]}")
        return False

def check_database_setup():
    """Check if authentication database is set up"""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/')
        db = client['authentication']
        
        # Check if users collection exists
        if 'users' in db.list_collection_names():
            user_count = db.users.count_documents({})
            print(f"✓ Database:  authentication.users collection ({user_count} users)")
            return True
        else:
            print("✓ Database:  authentication database exists (users collection will be created on first registration)")
            return True
    except Exception as e:
        print("✗ Database:  Cannot access authentication database")
        return False

def check_dependencies():
    """Check all required packages"""
    packages = {
        'flask': 'Flask',
        'flask_pymongo': 'Flask-PyMongo',
        'pymongo': 'PyMongo',
        'bcrypt': 'bcrypt',
        'cv2': 'OpenCV',
        'face_recognition': 'face_recognition',
        'qrcode': 'qrcode',
        'pyzbar': 'pyzbar',
        'PIL': 'Pillow',
        'numpy': 'NumPy'
    }
    
    print("\nDependencies:")
    all_good = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name}")
            all_good = False
    
    return all_good

def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'config.py',
        'requirements.txt',
        'templates/homepage.html',
        'templates/login.html',
        'templates/register.html',
        'static/css/style.css',
        'static/js/main.js',
        'utils/auth_utils.py',
        'utils/face_utils.py',
        'utils/qr_utils.py',
        'utils/card_generator.py'
    ]
    
    print("\nProject Files:")
    all_good = True
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"  ✓ {filepath}")
        else:
            print(f"  ✗ {filepath} (MISSING)")
            all_good = False
    
    return all_good

def main():
    print("\n" + "="*60)
    print("Authentication - Health Check")
    print("="*60 + "\n")
    
    checks = [
        ("Flask Installation", check_flask),
        ("MongoDB Connection", check_mongodb_connection),
        ("Database Setup", check_database_setup),
        ("File Structure", check_file_structure),
        ("Dependencies", check_dependencies),
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\nError checking {name}: {e}")
            results[name] = False
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    for name, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "-"*60)
    if all_passed:
        print("\n✓ All checks passed! You can start Authentication:\n")
        print("  1. Ensure MongoDB is running:")
        print("     Windows: net start MongoDB")
        print("     macOS:   brew services start mongodb-community")
        print("     Linux:   sudo systemctl start mongod")
        print("\n  2. Run Flask:")
        print("     python app.py")
        print("\n  3. Open browser:")
        print("     http://127.0.0.1:5000")
        print()
        return 0
    else:
        print("\n✗ Some checks failed!")
        print("\nNext Steps:")
        print("  1. Review the failures above")
        print("  2. Run: pip install -r requirements.txt")
        print("  3. Start MongoDB service")
        print("  4. Run this script again")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
