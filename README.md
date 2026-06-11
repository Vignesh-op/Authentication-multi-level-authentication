# Authentication - Multi-Factor Authentication System

A comprehensive multi-factor authentication (MFA) system built with Flask and MongoDB, featuring email/UUID authentication, facial recognition, and smart card verification.

---

## 🚀 Project Initialization

### Prerequisites
- Python 3.8 or higher
- MongoDB 8.0 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

1. **Navigate to the project directory:**
   ```bash
   cd c:\Users\viggu\authentication
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment (Windows)
   venv\Scripts\activate
   
   # Or on macOS/Linux
   source venv/bin/activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Start MongoDB

1. **Create MongoDB data directory (if not exists):**
   ```bash
   New-Item -ItemType Directory -Path "C:\data\db" -Force
   ```

2. **Start MongoDB server:**
   ```bash
   & "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath "C:\data\db"
   ```
   
   Or use the MongoDB service:
   ```bash
   net start MongoDB
   ```

### Step 3: Run the Flask Application

1. **Start the Flask development server:**
   ```bash
   python app.py
   ```

2. **Access the application:**
   - Open your browser and navigate to: `http://127.0.0.1:5000`
   - You should see the Authentication homepage

---

## 📝 User Registration

### Step-by-Step Registration Guide

1. **Navigate to Registration Page:**
   - Click on **"CREATE ACCOUNT"** link on the login page
   - Or go directly to: `http://127.0.0.1:5000/register`

2. **Fill Registration Form:**
   - **Name:** Enter your full name (required)
   - **Email:** Enter a valid email address (Ex: user@authentication.in)
   - **PIN:** Choose a 4-6 digit numeric PIN (required)
   - **Confirm PIN:** Re-enter your PIN to confirm (required)

3. **Submit Registration:**
   - Click **"REGISTER"** button
   - You will be redirected to capture your face image

4. **Face Capture:**
   - Allow camera access when prompted
   - Position your face clearly in front of the camera
   - Click **"CAPTURE FACE"** to take a snapshot
   - Click **"VERIFY & SAVE"** to confirm the face image

5. **Smart Card Generation:**
   - Your unique UUID will be generated (format: AUTHENTICATION-XXXXXX)
   - A smart card (QR code) will be automatically generated
   - Click **"DOWNLOAD SMART CARD"** to save the card image
   - Keep this card safe - you'll need it for authentication

6. **Registration Complete:**
   - You will be redirected to the dashboard
   - Your account is now ready to use

---

## 🔐 User Login

### Step-by-Step Login Guide

#### **Option 1: Login with Email**

1. **Navigate to Login Page:**
   - Go to: `http://127.0.0.1:5000/login`

2. **Select Email Authentication:**
   - Click the **"EMAIL"** button (cyan colored)
   - The button will turn green when selected

3. **Enter Credentials:**
   - **Email:** Enter your registered email address
   - **PIN:** Enter your 4-6 digit PIN

4. **Authenticate:**
   - Click **"AUTHENTICATE"** button
   - A "VERIFYING PIN" modal will appear briefly

5. **Face Verification:**
   - Allow camera access when prompted
   - Position your face in front of the camera
   - Your registered face will be compared with live capture
   - Click **"VERIFY FACE"** when ready

6. **Smart Card QR Verification:**
   - Hold your downloaded smart card in front of the camera
   - The QR code will be scanned and verified
   - Click **"VERIFY QR CODE"** when ready

7. **Login Successful:**
   - You will be redirected to your personal dashboard
   - Your authentication is complete

#### **Option 2: Login with Smart Card UUID**

1. **Navigate to Login Page:**
   - Go to: `http://127.0.0.1:5000/login`

2. **Select Smart Card UUID:**
   - Click the **"SMART CARD UUID"** button (cyan colored)
   - The button will turn green when selected

3. **Enter Credentials:**
   - **UUID:** Your unique identifier will appear with "AUTHENTICATION-" prefix already filled
   - Type only the 6-character ID after the dash (e.g., `ABC123`)
   - **PIN:** Enter your 4-6 digit PIN

4. **Authenticate:**
   - Click **"AUTHENTICATE"** button
   - Follow the same face and QR verification steps as Option 1

---

## 👤 Admin Dashboard

### Admin Login

1. **Navigate to Admin Login:**
   - Go to: `http://127.0.0.1:5000/admin-login`

2. **Enter Admin Credentials:**
   - **Email:** `Vignesh423@authentication.co.in`
   - **Password:** `100305`

3. **Access Admin Panel:**
   - View all registered users
   - Download user smart cards
   - Manage authentication records

### Admin Logout

- Click **"LOGOUT"** button in the admin dashboard to exit

---

## 🔑 Key Features

### Authentication Methods
- ✅ **Email & PIN** - Primary authentication method
- ✅ **Smart Card UUID & PIN** - Alternative authentication
- ✅ **Facial Recognition** - 3-factor verification
- ✅ **QR Code Verification** - Smart card validation

### Security Features
- 🔒 Rate limiting (5 attempts per 5 minutes)
- 🔒 Account lockout (5-minute lockdown after max attempts)
- 🔒 Password hashing with PIN verification
- 🔒 Face encoding storage and comparison
- 🔒 Unique smart card generation per user

### User Management
- 📊 Personal dashboard with authentication status
- 📥 Smart card download capability
- 🔑 PIN and face data management
- 📧 Email-based registration and authentication

---

## 🎯 Authentication Technology Explained

### 1️⃣ Face Authentication (Facial Recognition)

#### **How It Works:**

**Registration Phase:**
1. User provides their name, email, and PIN
2. User captures their face using the webcam during registration
3. The system extracts unique facial features from the captured image using advanced image processing:
   - **Histogram Equalization** - Normalizes lighting and contrast for consistency
   - **Local Binary Patterns (LBP)** - Analyzes texture patterns around the face
   - **Sobel Gradient Features** - Detects edges and structural patterns
4. These features are combined into a 160-dimensional encoding (mathematical representation of face)
5. The face encoding is securely stored in MongoDB

**Authentication Phase:**
1. During login, user captures their face again via webcam
2. The system extracts face encoding from the captured image using the same method
3. The new encoding is compared with the stored encoding using **Cosine Similarity**:
   - Calculates the angle/distance between the two face encodings
   - If distance is below the tolerance threshold (0.85) = **Face Matched** ✅
   - If distance exceeds threshold = **Face Not Matched** ❌
4. If no face is detected in the captured image = **No Face Detected** error message

**Error Messages:**
- ⚠️ **"No face detected"** - Camera didn't capture any face or face is unclear
- ⚠️ **"Face not matched"** - Face was captured but doesn't match the registered face (different person or poor lighting/angle)

**Key Benefits:**
- 🔐 Highly secure - extremely difficult to forge facial features
- 📱 User-friendly - no password to remember beyond PIN
- 🚫 Prevents unauthorized access - even if PIN is compromised, attacker still needs matching face

---

### 2️⃣ Smart Card Authentication (QR Code Verification)

#### **How It Works:**

**Registration Phase:**
1. During registration, a unique UUID is generated for each user (format: `AUTHENTICATION-XXXXXX`)
2. The system generates a smart card image containing:
   - **QR Code** - Encoded with the user's unique UUID and registration details
   - **User Information** - Name and unique identifier printed on the card
   - **Branding** - Authentication logo and security features
3. User downloads and saves this smart card image (typically as a PNG file)
4. User should print the card or keep it digital for authentication

**Authentication Phase:**
1. During login (after face verification), user is prompted to verify their smart card
2. User presents the smart card in front of the camera
3. The system:
   - Detects and reads the QR code from the smart card
   - Extracts the UUID encoded in the QR code
   - Compares extracted UUID with the UUID stored in user's database profile
   - Verifies that UUID matches the current login session
4. If QR code is valid and UUID matches = **Smart Card Verified** ✅
5. If QR code cannot be read or UUID doesn't match = **Invalid Smart Card** ❌

**Key Benefits:**
- 🎫 Physical/Digital possession factor - proves user has the card
- 🔄 Cannot be easily duplicated - QR code is unique per user
- 🛡️ Additional security layer - even with face and PIN, attacker needs the actual card
- 📲 Flexible - can be printed, saved digitally, or displayed on mobile device

---

### 3️⃣ Complete 3-Factor Authentication Flow

#### **Registration Flow:**
```
1. User Registration
   ↓
2. PIN Setup
   ↓
3. Face Capture & Encoding
   ↓
4. Smart Card Generation & Download
   ↓
5. Account Created ✅
```

#### **Login Flow (3-Factor Authentication):**
```
1. Email/UUID + PIN Verification
   ↓ (If correct)
2. Face Verification
   ↓ (If face matched)
3. Smart Card QR Verification
   ↓ (If QR code valid)
4. Login Successful → Dashboard Access ✅
```

#### **Security Layers:**

| Factor | Type | Purpose |
|--------|------|---------|
| **Factor 1: PIN** | Knowledge | Something you know (memorized) |
| **Factor 2: Face** | Biometric | Something you are (unique biological features) |
| **Factor 3: Smart Card** | Possession | Something you have (physical/digital artifact) |

**Why This Is Secure:**
- 🔐 **Redundant Security** - All three factors must pass for successful login
- 🔐 **Diverse Methods** - Different authentication types prevent single point of failure
- 🔐 **Difficult to Compromise** - Attacker would need: correct PIN + matching face + physical card
- 🔐 **Rate Limiting** - System locks account after 5 failed attempts in 5 minutes

---

### 4️⃣ Technical Implementation Details

#### **Face Encoding Algorithm:**
- **Detection Method:** Haar Cascade Classifier (OpenCV) - Fast, reliable face detection
- **Feature Extraction:** Multi-method approach combining:
  - Histogram features (64 values) - Lighting invariant characteristics
  - Texture features (64 values) - Surface pattern analysis
  - Gradient features (32 values) - Edge and structure information
- **Total Encoding Size:** 160-dimensional vector
- **Comparison Method:** Cosine similarity with configurable tolerance

#### **Smart Card QR Code:**
- **Content:** User UUID and registration metadata
- **Format:** Standard QR code (2D barcode)
- **Recovery Ability:** QR code includes error correction up to 30% damage
- **Uniqueness:** Each user gets a unique QR code generated at registration
- **Verification:** UUID extracted from QR code is matched against database record

#### **Database Storage:**
- **Face Encoding:** Stored as JSON array of 160 float values
- **Smart Card UUID:** Stored as unique string identifier
- **PIN:** Stored as hashed value (never stored in plain text)
- **Session Data:** Temporarily stored during authentication process

---

## 📁 Project Structure

```
authentication/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── homepage.html     # Homepage
│   ├── register.html     # Registration page
│   ├── login.html        # Login page
│   ├── dashboard.html    # User dashboard
│   ├── face_auth.html    # Face authentication
│   ├── face_register.html # Face registration
│   └── admin_dashboard.html
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   ├── images/          # Images
│   ├── uploads/         # User uploads
│   └── cards/           # Generated smart cards
└── utils/               # Utility modules
    ├── auth_utils.py    # Authentication utilities
    ├── face_utils.py    # Face recognition utilities
    ├── qr_utils.py      # QR code utilities
    └── card_generator.py # Smart card generation
```

---

## ⚙️ Configuration

### Database Configuration
The application uses MongoDB for data storage. Default configuration:
- **Connection String:** `mongodb://localhost:27017/authentication`
- **Database:** `authentication`
- **Collections:** users, sessions

### Security Configuration
- **Session Timeout:** 1 hour (3600 seconds)
- **Max Login Attempts:** 5 per 5 minutes
- **Account Lockout Duration:** 5 minutes
- **Face Recognition Tolerance:** 0.85

---

## 🐛 Troubleshooting

### MongoDB Connection Timeout
**Problem:** "PyMongo server timed out" error

**Solution:**
```bash
# Verify MongoDB is running
Get-Service MongoDB

# Start MongoDB manually
& "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath "C:\data\db"
```

### Camera Access Issues
**Problem:** Camera is not accessible or not working

**Solution:**
- Check browser camera permissions
- Allow camera access in browser settings
- Use a different browser if issue persists

### Face Recognition Failures
**Problem:** Face not being detected during authentication

**Solution:**
- Ensure good lighting
- Position face clearly in frame
- Avoid wearing sunglasses or masks
- Try registering face again with better conditions

---

## � Data Safety & Preservation

### ✅ Your User Data is Protected

**Important:** User data is **automatically persisted** in MongoDB and is **never automatically deleted** when:
- Stopping the Flask server (Ctrl+C)
- Stopping the MongoDB service
- Restarting your computer
- Updating the application

### Data Persistence Guarantee

- ✅ User registrations persist after server restart
- ✅ Face encodings survive database service stop
- ✅ Smart cards remain accessible
- ✅ Account information is never lost

### Backup Your Users

**Authentication includes a backup manager to safely protect your user database:**

```bash
# Backup all users to JSON file
python backup_manager.py backup

# Backup with custom name
python backup_manager.py backup my_backup

# List all available backups
python backup_manager.py list

# Restore from backup (interactive)
python backup_manager.py restore backups/authentication_backup_20260518_123456.json

# Restore and append to existing users
python backup_manager.py restore backups/authentication_backup_20260518_123456.json --append

# Check current database status
python backup_manager.py status
```

### ⚠️ Manual Cleanup Scripts

The following scripts **require manual execution** and will only delete users if you explicitly run them:

- `clear_db.py` - Clears all users from database
- `delete_users_now.py` - Deletes specific users
- `delete_all_users.py` - Deletes all users

**These scripts will NEVER run automatically on server stop or restart.**

### Database Storage Locations

**Windows:**
```
C:\data\db\
```

**Linux/macOS:**
```
/var/lib/mongodb/
```

### Emergency Recovery

If MongoDB data becomes corrupted:

```powershell
# Stop MongoDB
net stop MongoDB

# Restore from backup
python backup_manager.py restore backups/authentication_backup_20260518_123456.json

# Restart MongoDB
net start MongoDB
```

### For Complete Data Safety Information

See: [MONGODB_DATA_SAFETY.md](MONGODB_DATA_SAFETY.md)

---

## �📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify MongoDB is running
3. Ensure virtual environment is activated
4. Check browser console for error messages

---

## 📄 License

This project is part of the Authentication Multi-Factor Authentication System.

---

## 🎯 Quick Start Summary

```bash
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Start MongoDB (in a separate terminal)
& "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath "C:\data\db"

# 3. Run Flask application
python app.py

# 4. Open browser and navigate to
# http://127.0.0.1:5000
```

---

**Authentication v1.0 - Secure Multi-Factor Authentication System**
