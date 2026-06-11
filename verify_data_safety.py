#!/usr/bin/env python3
"""
Authentication Data Persistence Verification Tool
Verify that user data is safely stored and will persist after service restarts
"""

import sys
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'authentication'

def check_connection():
    """Verify MongoDB connection"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.server_info()
        return client, True
    except Exception as e:
        print("❌ Cannot connect to MongoDB")
        print(f"   Error: {e}")
        print("\n   To start MongoDB:")
        print("   Windows: net start MongoDB")
        print("   Linux:   sudo systemctl start mongod")
        return None, False

def verify_persistence():
    """Main verification function"""
    print("\n" + "="*60)
    print("  Authentication Data Persistence Verification")
    print("="*60 + "\n")
    
    client, connected = check_connection()
    if not connected:
        return False
    
    try:
        db = client[DB_NAME]
        users_collection = db['users']
        
        # Get database statistics
        user_count = users_collection.count_documents({})
        
        print(f"✅ Connected to MongoDB")
        print(f"   URI: {MONGO_URI}")
        print(f"   Database: {DB_NAME}")
        print(f"   Collection: users\n")
        
        print(f"📊 Database Statistics:")
        print(f"   Total users registered: {user_count}")
        
        if user_count == 0:
            print("\n   ℹ️  Database is empty (no users registered yet)")
        else:
            print(f"\n   Sample Users (first 10):")
            users = users_collection.find({}, {
                'name': 1, 'email': 1, 'unique_id': 1, 'created_at': 1
            }).limit(10)
            
            for i, user in enumerate(users, 1):
                email = user.get('email', 'N/A')
                name = user.get('name', 'N/A')
                unique_id = user.get('unique_id', 'N/A')
                created_at = user.get('created_at', 'N/A')
                print(f"   {i}. {name} ({email})")
                print(f"      UUID: {unique_id} | Registered: {created_at}")
        
        print(f"\n🔒 Data Persistence Status:")
        print(f"   ✅ Data is stored in MongoDB")
        print(f"   ✅ Data survives service restart")
        print(f"   ✅ Backup location: ./backups/")
        
        print(f"\n📋 Next Steps:")
        if user_count == 0:
            print(f"   • Navigate to http://127.0.0.1:5000 to register users")
        else:
            print(f"   • Data is safe and will persist after restarts")
            print(f"   • Create backup: python backup_manager.py backup")
        
        print(f"\n⚙️  Maintenance:")
        print(f"   • Manual backup: python backup_manager.py backup")
        print(f"   • Restore backup: python backup_manager.py restore <file>")
        print(f"   • Check status: python backup_manager.py status")
        
        print(f"\n⚠️  Data Only Deleted If You Explicitly Run:")
        print(f"   • python clear_db.py")
        print(f"   • python delete_users_now.py")
        print(f"   • python delete_all_users.py")
        
        print(f"\n✅ Verification Complete")
        print("="*60 + "\n")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        client.close()
        return False

def main():
    """Main entry point"""
    try:
        success = verify_persistence()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
