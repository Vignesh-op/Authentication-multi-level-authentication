# MongoDB Data Safety & Persistence Guide

## ✅ Data Preservation Confirmation

Your user data is **automatically preserved** when stopping MongoDB because:

### 1. **No Auto-Deletion Code**
- `app.py` has NO shutdown hooks that delete data
- `START.bat` and `start.sh` do NOT clear the database
- `clear_db.py` requires **manual execution** to delete users
- Session data is cleared, but database data persists

### 2. **MongoDB Data Persistence**
- Data is stored in: `C:\data\db\` (Windows) or system default location
- Data survives:
  - Flask server restart
  - Python process termination
  - MongoDB service stop/start
  - Computer restart

### 3. **Database Storage Locations**

**Windows:**
```
C:\data\db\
```

**Linux/Mac:**
```
/var/lib/mongodb/
```

## 📋 Backup & Recovery Procedures

### Backup Current Users

**Method 1: Export to JSON (Recommended)**
```bash
mongoexport --db authentication --collection users --out users_backup.json
```

**Method 2: Full Database Backup**
```bash
mongodump --db authentication --out ./backup_authentication
```

### Restore Users from Backup

**From JSON file:**
```bash
mongoimport --db authentication --collection users --file users_backup.json
```

**From mongodump backup:**
```bash
mongorestore --db authentication ./backup_authentication/authentication
```

## 🔐 Safe Cleanup Procedures

### Only Manual Cleanup Scripts Delete Data

The following require **explicit manual execution**:

- `clear_db.py` - Deletes ALL users (requires running script)
- `delete_users_now.py` - Deletes specific users (requires running script)
- `delete_all_users.py` - Deletes all users (requires running script)

**Never run these unless you intentionally want to clear users!**

### Safe Server Stop

**Windows:**
```powershell
# Stop Flask (Ctrl+C in Flask terminal)
# MongoDB data is automatically persisted
net stop MongoDB
```

**Linux/Mac:**
```bash
# Kill Flask
kill <flask_pid>
# MongoDB data is automatically persisted
sudo systemctl stop mongod
```

## 🛡️ Verification Checklist

To verify users are preserved:

### Check Users Exist Before Shutdown
```bash
python -c "from pymongo import MongoClient; c = MongoClient('mongodb://localhost:27017/'); print(f\"Users: {c['authentication']['users'].count_documents({})}\")"
```

### Check Users After Restart
```bash
# Stop MongoDB
net stop MongoDB

# Restart MongoDB
net start MongoDB

# Check users again
python -c "from pymongo import MongoClient; c = MongoClient('mongodb://localhost:27017/'); print(f\"Users: {c['authentication']['users'].count_documents({})}\"))"
```

## 📊 Database Schema

Each user record contains:
- `_id`: MongoDB unique identifier
- `name`: User full name
- `email`: User email (unique)
- `pin_hash`: Hashed PIN (never plain text)
- `unique_id`: AUTHENTICATION-XXXXXX format
- `face_encoding`: 160-dimensional face biometric vector
- `face_tolerance`: User-specific tolerance (0.82-0.88)
- `smartcard_path`: Path to QR code PNG
- `created_at`: Registration timestamp

## ⚠️ Important Notes

1. **Session Data ≠ Database Data**
   - Session data (in-memory) is cleared on server restart
   - Database data persists in MongoDB

2. **Data Only Deleted If You Explicitly Run:**
   - `python clear_db.py`
   - `python delete_users_now.py`
   - `python delete_all_users.py`

3. **MongoDB Configuration**
   - Default storage: `C:\data\db\` (Windows)
   - Data persists until explicitly deleted
   - No automatic cleanup on service stop

## 🆘 Emergency Recovery

If MongoDB file is corrupted:

```bash
# Stop MongoDB
net stop MongoDB

# Backup corrupted data
move C:\data\db C:\data\db_corrupted

# Recreate fresh data directory
mkdir C:\data\db

# Restart MongoDB
net start MongoDB

# Restore from backup
mongorestore --db authentication ./backup_authentication/authentication
```

---
**Last Updated:** 2026-05-18  
**Status:** ✅ All user data is safely persisted
