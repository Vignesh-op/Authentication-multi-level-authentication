#!/usr/bin/env python3
"""
Authentication Database Backup & Restore Manager
Safely backup and restore MongoDB user data
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient
import argparse

# Configuration
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'authentication'
COLLECTION_NAME = 'users'
BACKUP_DIR = Path(__file__).parent / 'backups'

class BackupManager:
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
        
    def connect_db(self):
        """Connect to MongoDB"""
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            client.server_info()  # Check connection
            return client[DB_NAME][COLLECTION_NAME], client
        except Exception as e:
            print(f"❌ Error: Cannot connect to MongoDB at {MONGO_URI}")
            print(f"   Make sure MongoDB is running: net start MongoDB")
            sys.exit(1)
    
    def backup(self, name=None):
        """Backup all users to JSON file"""
        try:
            users_collection, client = self.connect_db()
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = name or f"authentication_backup_{timestamp}"
            backup_file = self.backup_dir / f"{backup_name}.json"
            
            # Get all users
            users = list(users_collection.find({}))
            
            if not users:
                print("⚠️  No users found in database")
                return
            
            # Convert ObjectId to string for JSON serialization
            for user in users:
                if '_id' in user:
                    user['_id'] = str(user['_id'])
                if 'face_encoding' in user and user['face_encoding']:
                    user['face_encoding'] = [float(x) for x in user['face_encoding']]
            
            # Save backup
            with open(backup_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            print(f"✅ Backup successful!")
            print(f"   Location: {backup_file}")
            print(f"   Users backed up: {len(users)}")
            print(f"   Timestamp: {timestamp}")
            
            client.close()
            return backup_file
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            sys.exit(1)
    
    def restore(self, backup_file, append=False):
        """Restore users from JSON file"""
        try:
            # Check if file exists
            if not os.path.exists(backup_file):
                print(f"❌ Error: Backup file not found: {backup_file}")
                sys.exit(1)
            
            # Load backup
            with open(backup_file, 'r') as f:
                users = json.load(f)
            
            users_collection, client = self.connect_db()
            
            if not append:
                # Confirm before clearing
                current_count = users_collection.count_documents({})
                if current_count > 0:
                    response = input(
                        f"\n⚠️  WARNING: Database has {current_count} user(s)\n"
                        "Replace mode will DELETE current users before restoring.\n"
                        "Type 'yes' to continue (or 'append' to add users): "
                    )
                    if response.lower() == 'yes':
                        users_collection.delete_many({})
                        print("   Cleared existing users")
                    elif response.lower() == 'append':
                        append = True
                    else:
                        print("Restore cancelled")
                        client.close()
                        return
            
            # Restore users
            restored = 0
            skipped = 0
            
            for user in users:
                try:
                    # Remove _id if it's a string to let MongoDB generate new one
                    if '_id' in user and isinstance(user['_id'], str):
                        if append:
                            del user['_id']
                    
                    if append:
                        # Check if user with same email exists
                        existing = users_collection.find_one({'email': user['email']})
                        if existing:
                            users_collection.replace_one({'email': user['email']}, user)
                        else:
                            if '_id' in user:
                                del user['_id']
                            users_collection.insert_one(user)
                    else:
                        if '_id' in user:
                            del user['_id']
                        users_collection.insert_one(user)
                    
                    restored += 1
                except Exception as e:
                    print(f"   ⚠️  Skipped user (error): {e}")
                    skipped += 1
            
            print(f"\n✅ Restore successful!")
            print(f"   File: {backup_file}")
            print(f"   Users restored: {restored}")
            if skipped > 0:
                print(f"   Users skipped: {skipped}")
            print(f"   Total in database: {users_collection.count_documents({})}")
            
            client.close()
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            sys.exit(1)
    
    def list_backups(self):
        """List all available backups"""
        backups = sorted(self.backup_dir.glob('*.json'))
        
        if not backups:
            print("ℹ️  No backups found")
            return
        
        print("\n📋 Available Backups:")
        for i, backup in enumerate(backups, 1):
            size = backup.stat().st_size / 1024  # KB
            modified = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"   {i}. {backup.name}")
            print(f"      Size: {size:.1f} KB")
            print(f"      Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def get_status(self):
        """Show current database status"""
        try:
            users_collection, client = self.connect_db()
            count = users_collection.count_documents({})
            
            print("\n📊 Database Status:")
            print(f"   MongoDB URI: {MONGO_URI}")
            print(f"   Database: {DB_NAME}")
            print(f"   Collection: {COLLECTION_NAME}")
            print(f"   Users in database: {count}")
            
            # Show sample user emails
            if count > 0:
                users = users_collection.find({}, {'email': 1, 'name': 1}).limit(5)
                print("\n   Sample users:")
                for user in users:
                    print(f"      • {user['name']} ({user['email']})")
            
            client.close()
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Authentication Database Backup & Restore Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backup_manager.py backup                  # Backup all users
  python backup_manager.py backup mybackup         # Backup with custom name
  python backup_manager.py restore backups/authentication_backup_20260518_123456.json
  python backup_manager.py restore backups/authentication_backup_20260518_123456.json --append
  python backup_manager.py list                    # List all backups
  python backup_manager.py status                  # Show database status
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup users to JSON file')
    backup_parser.add_argument('name', nargs='?', help='Custom backup name (optional)')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore users from JSON file')
    restore_parser.add_argument('file', help='Path to backup file')
    restore_parser.add_argument('--append', action='store_true', help='Append to existing users instead of replacing')
    
    # List command
    subparsers.add_parser('list', help='List all backups')
    
    # Status command
    subparsers.add_parser('status', help='Show database status')
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'backup':
        manager.backup(args.name)
    elif args.command == 'restore':
        append = getattr(args, 'append', False)
        manager.restore(args.file, append=append)
    elif args.command == 'list':
        manager.list_backups()
    elif args.command == 'status':
        manager.get_status()

if __name__ == '__main__':
    main()
