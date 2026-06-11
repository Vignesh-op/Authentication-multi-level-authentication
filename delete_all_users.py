"""
Database management script to delete all users from MongoDB.
Run this script to clear all registered users from the authentication database.

Usage:
    python delete_all_users.py
"""

from flask import Flask
from flask_pymongo import PyMongo
from config import config
import os
import sys

# Initialize Flask app and MongoDB
app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize MongoDB
mongo = PyMongo(app)

def delete_all_users():
    """Delete all users from the database"""
    with app.app_context():
        try:
            # Get the users collection
            users_collection = mongo.db.users
            
            # Count users before deletion
            user_count_before = users_collection.count_documents({})
            
            if user_count_before == 0:
                print("✓ No users found in the database. Database is already clean.")
                return True
            
            # Delete all users
            result = users_collection.delete_many({})
            
            print(f"✓ Successfully deleted {result.deleted_count} user(s) from the database.")
            
            # Verify deletion
            user_count_after = users_collection.count_documents({})
            if user_count_after == 0:
                print("✓ Database verification: All users have been removed.")
                return True
            else:
                print(f"⚠ Warning: {user_count_after} user(s) still exist in the database.")
                return False
                
        except Exception as e:
            print(f"✗ Error deleting users: {e}")
            return False

def verify_email_domain():
    """Verify that email validation now enforces @authentication.in domain"""
    from utils.auth_utils import validate_email
    
    print("\n=== Email Validation Test ===")
    test_emails = [
        ("user@authentication.in", True),
        ("test.user@authentication.in", True),
        ("admin123@authentication.in", True),
        ("user@gmail.com", False),
        ("user@example.com", False),
        ("user@authentication.com", False),
        ("random.email@domain.co.uk", False),
    ]
    
    all_passed = True
    for email, expected in test_emails:
        result = validate_email(email)
        status = "✓" if result == expected else "✗"
        all_passed = all_passed and (result == expected)
        print(f"{status} {email}: {result} (expected: {expected})")
    
    return all_passed

if __name__ == '__main__':
    print("=" * 50)
    print("Authentication Database Cleanup Tool")
    print("=" * 50)
    print("\n⚠ WARNING: This will delete ALL registered users from the database!")
    print("This action cannot be undone.\n")
    
    # Check for --force flag
    force_delete = '--force' in sys.argv
    
    if force_delete:
        confirmation = 'yes'
    else:
        confirmation = input("Are you sure you want to delete all users? (yes/no): ").strip().lower()
    
    if confirmation == 'yes':
        print("\nProceeding with user deletion...\n")
        success = delete_all_users()
        
        # Verify email validation
        email_validation_ok = verify_email_domain()
        
        print("\n" + "=" * 50)
        if success and email_validation_ok:
            print("✓ All tasks completed successfully!")
            print("  - All users have been deleted from the database")
            print("  - Email validation now enforces @authentication.in domain")
        else:
            print("✗ Some tasks may not have completed successfully.")
            sys.exit(1)
        print("=" * 50)
    else:
        print("✗ Deletion cancelled. No users were deleted.")
        sys.exit(0)
