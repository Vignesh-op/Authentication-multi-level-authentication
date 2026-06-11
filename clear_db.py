#!/usr/bin/env python3
"""Quick script to delete all users from MongoDB"""

import sys
from pymongo import MongoClient

try:
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['authentication']
    users_collection = db['users']
    
    # Delete all users
    result = users_collection.delete_many({})
    
    print(f"✓ Successfully deleted {result.deleted_count} user(s) from the database")
    print("✓ The database is now ready for users with @authentication.in domain emails only")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
