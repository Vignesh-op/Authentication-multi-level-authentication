#!/usr/bin/env python3
"""
Quick MongoDB Atlas & Render Deployment Helper
This script helps you set up the connection string for MongoDB Atlas
"""

import secrets
import webbrowser
import time

print("\n" + "="*70)
print("🚀 AUTHENTICATION APP - DEPLOYMENT HELPER")
print("="*70)

# Generate Secret Key
secret_key = secrets.token_hex(32)
print("\n✅ GENERATED SECRET KEY (save this):")
print(f"   {secret_key}\n")

# Deployment URLs
print("\n📋 STEP-BY-STEP DEPLOYMENT GUIDE:")
print("="*70)

print("\n1️⃣ CREATE MONGODB ATLAS ACCOUNT (Free)")
print("   URL: https://www.mongodb.com/cloud/atlas")
print("   - Sign up with email")
print("   - Create free M0 cluster (512MB)")
print("   - Choose AWS/Google Cloud/Azure region")
print("\n2️⃣ CREATE DATABASE USER")
print("   - Go to Security → Database Access")
print("   - Add new user (username: 'admin' or similar)")
print("   - Use password authentication")
print("   - Set role to 'Atlas Admin'")
print("   - Save username and password!")
print("\n3️⃣ WHITELIST IPS")
print("   - Go to Security → Network Access")
print("   - Click 'Add IP Address'")
print("   - Select 'Allow Access from Anywhere' (0.0.0.0/0)")
print("\n4️⃣ GET CONNECTION STRING")
print("   - Go to Clusters → Connect")
print("   - Select 'Drivers' → Python 3.11+")
print("   - Copy connection string")
print("   - Replace <password> with your password")
print("   - Replace database name with 'authentication'")
print("   - Final format:")
print("   mongodb+srv://username:password@cluster0.xxx.mongodb.net/authentication?retryWrites=true&w=majority")

print("\n\n5️⃣ CREATE RENDER ACCOUNT (Free)")
print("   URL: https://render.com")
print("   - Sign up with GitHub account")
print("   - Authorize Render to access your repositories")

print("\n\n6️⃣ DEPLOY TO RENDER")
print("   - Click 'New +' → 'Web Service'")
print("   - Select your GitHub repository")
print("   - Configure:")
print("     • Name: authentication-app")
print("     • Environment: Python 3")
print("     • Build Command: pip install -r requirements.txt && python init_db.py")
print("     • Start Command: gunicorn app:app")

print("\n\n7️⃣ SET ENVIRONMENT VARIABLES IN RENDER")
print("   Add these environment variables:")
print(f"   • FLASK_ENV = production")
print(f"   • SECRET_KEY = {secret_key}")
print(f"   • MONGO_URI = [Your MongoDB connection string]")
print(f"   • ADMIN_EMAIL = Vignesh423@authentication.co.in")
print(f"   • ADMIN_PASSWORD = [Your secure password]")

print("\n\n" + "="*70)
print("✨ YOUR APP WILL BE LIVE AT: https://authentication-app.onrender.com")
print("="*70 + "\n")

# Ask to open links
try:
    response = input("Would you like me to open these websites? (y/n): ").lower().strip()
    if response == 'y':
        print("\nOpening websites...")
        time.sleep(1)
        webbrowser.open("https://www.mongodb.com/cloud/atlas")
        time.sleep(2)
        webbrowser.open("https://render.com")
except:
    pass

print("\n📧 Need help? Check DEPLOYMENT.md in your repository!")
print("\n")
