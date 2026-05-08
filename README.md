# AuthSafe - Multi-Factor Authentication System

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
   cd c:\Users\viggu\authsafe
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
   - You should see the AuthSafe homepage

---

## 📝 User Registration

### Step-by-Step Registration Guide

1. **Navigate to Registration Page:**
   - Click on **"CREATE ACCOUNT"** link on the login page
   - Or go directly to: `http://127.0.0.1:5000/register`

2. **Fill Registration Form:**
   - **Name:** Enter your full name (required)
   - **Email:** Enter a valid email address (required)
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
   - Your unique UUID will be generated (format: AUTHSAFE-XXXXXX)
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
   - **UUID:** Your unique identifier will appear with "AUTHSAFE-" prefix already filled
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
   - **Email:** `Vignesh423@authsafe.co.in`
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

## 📁 Project Structure

```
authsafe/
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
- **Connection String:** `mongodb://localhost:27017/authsafe`
- **Database:** `authsafe`
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

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify MongoDB is running
3. Ensure virtual environment is activated
4. Check browser console for error messages

---

## 📄 License

This project is part of the AuthSafe Multi-Factor Authentication System.

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

**AuthSafe v1.0 - Secure Multi-Factor Authentication System**
