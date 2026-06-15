# ✅ Authentication Data Safety Checklist

## 🔐 Data Preservation Verification

Use this checklist to verify that your user data is safe and will persist after restarts.

### Step 1: Verify Current Users

Run this command to check how many users are registered:

```bash
python verify_data_safety.py
```

**Expected Output:**
```
✅ Connected to MongoDB
   Database: authentication
   Total users registered: X
   
✅ Verification Complete
```

### Step 2: Create Backup Before Major Changes

Before stopping MongoDB or the server:

```bash
# Create backup with timestamp
python backup_manager.py backup

# List backups
python backup_manager.py list
```

**Result:** Your users are now backed up to `./backups/` directory

---

## 📋 Daily Safety Routine

### Recommended Schedule

- **Weekly:** Create a backup
- **Before Updates:** Always create a backup first
- **After Registration:** Verify users were saved

### Quick Safety Check

```bash
# Check data is still there
python verify_data_safety.py

# Should show all registered users
```

---

## 🛡️ Safe Server Shutdown

### Windows

```powershell
# Stop Flask server
# Press Ctrl+C in the Flask terminal

# Stop MongoDB (optional - data persists)
net stop MongoDB

# Verify data still exists
python verify_data_safety.py
```

### Linux/macOS

```bash
# Stop Flask server
kill <flask_pid>

# Stop MongoDB (optional)
sudo systemctl stop mongod

# Verify data
python verify_data_safety.py
```

**Result:** All user data remains in database

---

## 🔄 Safe Server Restart

### Step 1: Stop Server

```bash
# Stop Flask (Ctrl+C)
# MongoDB data is automatically saved
```

### Step 2: Restart Services

```bash
# Windows
net start MongoDB
python app.py

# Linux/macOS
sudo systemctl start mongod
python app.py
```

### Step 3: Verify Data

```bash
python verify_data_safety.py
```

**Result:** All users are restored and accessible

---

## 📤 Backup Management

### Create Regular Backups

```bash
# Automatic timestamp backup
python backup_manager.py backup

# Named backup
python backup_manager.py backup production_backup
```

### Restore If Needed

```bash
# Interactive restore (will confirm before replacing)
python backup_manager.py restore backups/authentication_backup_20260518_123456.json

# Append backup to existing users
python backup_manager.py restore backups/authentication_backup_20260518_123456.json --append
```

### View All Backups

```bash
python backup_manager.py list
```

---

## ⚠️ Critical: Data Only Deleted If You Explicitly Run

| Script | Action | Recoverable |
|--------|--------|-------------|
| `clear_db.py` | Deletes ALL users | Yes (from backup) |
| `delete_users_now.py` | Deletes specific users | Yes (from backup) |
| `delete_all_users.py` | Deletes all users | Yes (from backup) |
| Server stop | **NOTHING** | N/A |
| MongoDB stop | **NOTHING** | N/A |
| Server crash | **NOTHING** | N/A |

**Important:** These cleanup scripts will NEVER run automatically

---

## 🆘 Emergency Recovery

### If Data Seems Lost

**Step 1: Check MongoDB is Running**
```bash
python verify_data_safety.py
```

**Step 2: Restore from Backup**
```bash
python backup_manager.py restore backups/authentication_backup_20260518_123456.json
```

**Step 3: Verify Restoration**
```bash
python verify_data_safety.py
```

**Step 4: Check Database Directly**
```powershell
mongosh
use authentication
db.users.countDocuments()
db.users.find().limit(1).pretty()
```

---

## 📊 Data Location

**MongoDB stores user data at:**

- **Windows:** `C:\data\db\`
- **Linux:** `/var/lib/mongodb/`
- **macOS:** `/usr/local/var/mongodb/`

**Backups stored at:**
- `./backups/` (relative to project root)

---

## ✅ Verification Checklist

- [ ] Users are registered in system
- [ ] `python verify_data_safety.py` shows correct user count
- [ ] Recent backup exists in `./backups/`
- [ ] Can view users: `python backup_manager.py status`
- [ ] Server can be stopped and restarted without data loss
- [ ] Users still exist after restart
- [ ] Can successfully login with registered credentials

---

## 🚨 Common Concerns Addressed

### Q: Will my data be deleted if I stop the server?
**A:** ❌ NO. Stopping Flask or MongoDB does NOT delete user data. Data persists in MongoDB database files.

### Q: What happens if the power goes out?
**A:** Data is safely stored in MongoDB. Once power returns and MongoDB restarts, all data is recovered.

### Q: Can I safely restart the computer?
**A:** ✅ YES. MongoDB automatically persists data to disk. Restart as needed - users remain.

### Q: How do I prevent accidental data loss?
**A:** Create regular backups using `python backup_manager.py backup`

### Q: Is my data automatically backed up?
**A:** ❌ NO. Use `backup_manager.py` to manually create backups.

### Q: Can I restore deleted users?
**A:** ✅ YES, if you have a backup file created before deletion.

---

## 📞 Need Help?

1. Run: `python verify_data_safety.py` to check status
2. Check: [MONGODB_DATA_SAFETY.md](MONGODB_DATA_SAFETY.md) for detailed info
3. Review: Backup management section above
4. Run: `python backup_manager.py status` for database info

---

**Last Updated:** 2026-05-18  
**Status:** ✅ All safety procedures verified and working
