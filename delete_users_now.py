#!/usr/bin/env python3
"""Direct database deletion script"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_pymongo import PyMongo
from config import config

# Initialize Flask app
app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize MongoDB
try:
    mongo = PyMongo(app)
    
    with app.app_context():
        # Delete all users
        users_collection = mongo.db.users
        
        count_before = users_collection.count_documents({})
        print(f"Users before deletion: {count_before}")
        
        if count_before > 0:
            result = users_collection.delete_many({})
            print(f"✓ Deleted {result.deleted_count} user(s)")
        else:
            print("✓ No users found in database")
        
        count_after = users_collection.count_documents({})
        print(f"Users after deletion: {count_after}")
        print("✓ SUCCESS: All users have been removed from the database")
        
except Exception as e:
    print(f"✗ ERROR: {e}")
    print("Make sure MongoDB is running on localhost:27017")
    sys.exit(1)
