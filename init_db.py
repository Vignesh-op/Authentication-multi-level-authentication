#!/usr/bin/env python3
"""
Database Initialization Script
Creates MongoDB collections and indexes for the Authentication system
"""

import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def initialize_database():
    """Initialize the authentication database with collections and indexes"""
    try:
        # Connect to MongoDB
        print("📡 Connecting to MongoDB...")
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB at localhost:27017")
        
        # Get database
        db = client['authentication']
        print(f"✓ Using database: authentication")
        
        # Create users collection
        print("\n📋 Creating collections...")
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
            print("✓ Created 'users' collection")
        else:
            print("✓ 'users' collection already exists")
        
        # Create admin_sessions collection
        if 'admin_sessions' not in db.list_collection_names():
            db.create_collection('admin_sessions')
            print("✓ Created 'admin_sessions' collection")
        else:
            print("✓ 'admin_sessions' collection already exists")
        
        # Create indexes for users collection
        print("\n🔑 Creating indexes...")
        users = db['users']
        
        # Email index (unique)
        try:
            users.create_index('email', unique=True)
            print("✓ Created unique index on 'email'")
        except Exception as e:
            print(f"⚠ Email index: {str(e)[:60]}")
        
        # Unique ID index (unique)
        try:
            users.create_index('unique_id', unique=True)
            print("✓ Created unique index on 'unique_id'")
        except Exception as e:
            print(f"⚠ Unique ID index: {str(e)[:60]}")
        
        # Created at index (for sorting)
        try:
            users.create_index('created_at')
            print("✓ Created index on 'created_at'")
        except Exception as e:
            print(f"⚠ Created at index: {str(e)[:60]}")
        
        # Last login index (for tracking)
        try:
            users.create_index('last_login')
            print("✓ Created index on 'last_login'")
        except Exception as e:
            print(f"⚠ Last login index: {str(e)[:60]}")
        
        # Create indexes for admin_sessions collection
        admin_sessions = db['admin_sessions']
        
        try:
            admin_sessions.create_index('email', unique=True)
            print("✓ Created unique index on admin_sessions 'email'")
        except Exception as e:
            print(f"⚠ Admin email index: {str(e)[:60]}")
        
        try:
            admin_sessions.create_index('last_login')
            print("✓ Created index on admin_sessions 'last_login'")
        except Exception as e:
            print(f"⚠ Admin last_login index: {str(e)[:60]}")
        
        # Print summary
        print("\n" + "="*60)
        print("✓ DATABASE INITIALIZATION COMPLETE")
        print("="*60)
        print(f"Database: authentication")
        print(f"Collections: {', '.join(db.list_collection_names())}")
        print(f"Users count: {users.count_documents({})}")
        print(f"Admin sessions count: {admin_sessions.count_documents({})}")
        print("\nThe database is ready for use!")
        print("="*60)
        
        client.close()
        return True
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ MongoDB Connection Error: {str(e)[:100]}")
        print("\n⚠️  Make sure MongoDB is running:")
        print("   • Start MongoDB service on Windows: net start MongoDB")
        print("   • Or run: mongod")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    success = initialize_database()
    sys.exit(0 if success else 1)
