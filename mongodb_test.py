#!/usr/bin/env python3
"""
MongoDB Atlas Connection Tester
Tests connection to MongoDB Atlas and creates database if needed
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_connection(mongo_uri):
    """Test MongoDB connection"""
    print("\n" + "="*70)
    print("🧪 MONGODB ATLAS CONNECTION TEST")
    print("="*70)
    
    try:
        print(f"\n📡 Testing connection to MongoDB...")
        print(f"   URI: {mongo_uri[:60]}...")
        
        # Connect with timeout
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Get server info
        server_info = client.server_info()
        print(f"\n📊 Server Information:")
        print(f"   Version: {server_info.get('version', 'Unknown')}")
        
        # Get database
        db = client['authentication']
        print(f"\n💾 Database: authentication")
        
        # List collections
        collections = db.list_collection_names()
        print(f"   Collections: {', '.join(collections) if collections else 'None (empty)'}")
        
        # Get collection stats
        if collections:
            for collection_name in collections:
                collection = db[collection_name]
                count = collection.count_documents({})
                print(f"   - {collection_name}: {count} documents")
        
        # Show database stats
        try:
            db_stats = db.command('dbStats')
            size_mb = db_stats.get('dataSize', 0) / (1024 * 1024)
            print(f"\n   Database Size: {size_mb:.2f} MB")
        except:
            pass
        
        print("\n✅ CONNECTION SUCCESSFUL!")
        print("="*70 + "\n")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError:
        print("\n❌ CONNECTION FAILED - Timeout")
        print("   Possible causes:")
        print("   1. IP not whitelisted in MongoDB Atlas")
        print("      → Go to Security → Network Access → Allow 0.0.0.0/0")
        print("   2. Incorrect password in connection string")
        print("   3. Cluster not running in MongoDB Atlas")
        print("   4. Network connectivity issue")
        print("="*70 + "\n")
        return False
        
    except ConnectionFailure as e:
        print(f"\n❌ CONNECTION FAILED: {str(e)}")
        print("   Check your MongoDB Atlas cluster and connection string")
        print("="*70 + "\n")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("="*70 + "\n")
        return False

def create_database(mongo_uri):
    """Create database collections if they don't exist"""
    try:
        print("\n📝 Creating database collections...")
        
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
        db = client['authentication']
        
        # Create users collection
        if 'users' not in db.list_collection_names():
            db.create_collection('users')
            print("✅ Created 'users' collection")
        else:
            print("ℹ️  'users' collection already exists")
        
        # Create admin_sessions collection
        if 'admin_sessions' not in db.list_collection_names():
            db.create_collection('admin_sessions')
            print("✅ Created 'admin_sessions' collection")
        else:
            print("ℹ️  'admin_sessions' collection already exists")
        
        # Create indexes
        print("\n🔑 Creating indexes...")
        users = db['users']
        
        try:
            users.create_index('email', unique=True)
            print("✅ Created unique index on 'email'")
        except:
            print("ℹ️  'email' index already exists")
        
        try:
            users.create_index('unique_id', unique=True)
            print("✅ Created unique index on 'unique_id'")
        except:
            print("ℹ️  'unique_id' index already exists")
        
        try:
            users.create_index('created_at')
            print("✅ Created index on 'created_at'")
        except:
            print("ℹ️  'created_at' index already exists")
        
        try:
            users.create_index('last_login')
            print("✅ Created index on 'last_login'")
        except:
            print("ℹ️  'last_login' index already exists")
        
        admin_sessions = db['admin_sessions']
        
        try:
            admin_sessions.create_index('email', unique=True)
            print("✅ Created unique index on admin 'email'")
        except:
            print("ℹ️  admin 'email' index already exists")
        
        try:
            admin_sessions.create_index('last_login')
            print("✅ Created index on admin 'last_login'")
        except:
            print("ℹ️  admin 'last_login' index already exists")
        
        print("\n✅ DATABASE READY!")
        print("="*70 + "\n")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    # Get MongoDB URI
    mongo_uri = os.environ.get('MONGO_URI')
    
    if not mongo_uri:
        print("\n❌ ERROR: MONGO_URI environment variable not set!")
        print("\nUsage:")
        print("  1. Set environment variable:")
        print("     export MONGO_URI='mongodb+srv://username:password@cluster.mongodb.net/authentication?retryWrites=true&w=majority'")
        print("\n  2. Run this script:")
        print("     python mongodb_test.py")
        print("\nExample:")
        print("  $env:MONGO_URI='mongodb+srv://vignesh_op:password@cluster0.vvcsmev.mongodb.net/authentication?retryWrites=true&w=majority'")
        print("  python mongodb_test.py")
        print()
        sys.exit(1)
    
    # Test connection
    if test_connection(mongo_uri):
        # Create database
        create_database(mongo_uri)
    else:
        print("⚠️  Connection failed. Please check your MongoDB Atlas setup.")
        sys.exit(1)
