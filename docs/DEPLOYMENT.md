# Deployment Guide - Multi-Factor Authentication System

This guide will help you deploy the Authentication application to **Render** (free tier) with **MongoDB Atlas** (free tier cloud database).

## Prerequisites

- GitHub account (repository already set up)
- MongoDB Atlas account (free)
- Render account (free)

## Step 1: Set Up MongoDB Atlas (Free Cloud Database)

### 1.1 Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Click "Try Free" and sign up with your email
3. Create a new organization and project

### 1.2 Create a Free Cluster
1. Click "Create" to build a new cluster
2. Select **M0 Sandbox** (free tier)
3. Choose your preferred cloud provider (AWS/Google Cloud/Azure)
4. Choose a region closest to you
5. Click "Create Cluster" (takes 5-10 minutes)

### 1.3 Create Database User
1. Go to "Security" → "Database Access"
2. Click "Add New Database User"
3. Enter username (e.g., `admin`)
4. Choose "Password" and enter a strong password (save this!)
5. Set "Database User Privileges" to "Atlas Admin"
6. Click "Add User"

### 1.4 Whitelist IP & Get Connection String
1. Go to "Security" → "Network Access"
2. Click "Add IP Address"
3. Select "Allow Access from Anywhere" (or add your IP)
4. Go back to "Clusters" → Click "Connect"
5. Select "Drivers" and choose "Python" → "3.11 or later"
6. Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/database`)
7. Replace `password` with your actual password, `database` with `authentication`

**Example:**
```
mongodb+srv://admin:mypassword@cluster0.abc123.mongodb.net/authentication?retryWrites=true&w=majority
```

## Step 2: Prepare Application for Deployment

Files already created:
- ✅ `Procfile` - Tells Render how to run the app
- ✅ `runtime.txt` - Specifies Python version
- ✅ `.env.example` - Environment variables template

Verify all files exist in your repository.

## Step 3: Deploy to Render

### 3.1 Create Render Account
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub account
3. Authorize Render to access your GitHub repositories

### 3.2 Create a New Web Service
1. Click "New +" → "Web Service"
2. Select your GitHub repository (`Authentication` or similar)
3. Click "Connect"

### 3.3 Configure Deployment Settings

**Name:** `authentication-app` (or any name)

**Environment:** `Python 3`

**Build Command:**
```bash
pip install -r requirements.txt && python init_db.py
```

**Start Command:**
```bash
gunicorn app:app
```

### 3.4 Set Environment Variables
1. Scroll down to "Environment" section
2. Click "Add Environment Variable" and add these:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Generate a random string (use: `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `MONGO_URI` | Your MongoDB Atlas connection string from Step 1.4 |
| `ADMIN_EMAIL` | `Vignesh423@authentication.co.in` |
| `ADMIN_PASSWORD` | Set a secure password |

**Important:** Never commit `.env` file to Git - use environment variables in Render dashboard!

### 3.5 Deploy
1. Click "Create Web Service"
2. Render will start building (takes 2-5 minutes)
3. Once deployed, you'll get a URL like: `https://authentication-app.onrender.com`
4. Check deployment status in the "Deploy" section

## Step 4: Post-Deployment Verification

1. **Check MongoDB Connection:**
   - Visit your deployed app URL
   - Try registering a new user
   - Check MongoDB Atlas dashboard → "Browse Collections" to verify data is being saved

2. **Test Application Flow:**
   - ✅ Register with email and PIN
   - ✅ Capture face biometric
   - ✅ Verify face authentication
   - ✅ Download smart card (QR code)
   - ✅ Login with multi-factor auth
   - ✅ Check admin dashboard

3. **View Logs:**
   - In Render dashboard, click "Logs" to debug any issues

## Step 5: Common Issues & Fixes

### Issue: "Connection timeout to MongoDB"
**Solution:** 
- Check MongoDB Atlas Network Access whitelist includes "0.0.0.0/0" (Allow Access from Anywhere)
- Verify MONGO_URI is correct (includes password without special URL encoding issues)

### Issue: "ModuleNotFoundError: No module named 'dlib'"
**Solution:**
- This is expected! The app falls back to Haar Cascade geometry extraction
- Check app logs - should show: `⚠ dlib not available - using cascade-based geometry extraction`

### Issue: "Face recognition not working"
**Solution:**
- Face capture requires HTTPS in production
- Render provides free HTTPS automatically
- Check browser console for webcam permission errors
- Allow camera access when prompted

### Issue: "Face images not saving"
**Solution:**
- Render's filesystem is ephemeral (resets on redeploy)
- Images are in `/tmp/` and will be lost
- For persistent storage, implement AWS S3 or Render Disk storage (paid feature)
- Currently acceptable for development/testing

## Step 6: Update Code on Deployment

To update the deployed app:
```bash
# Make changes locally
git add .
git commit -m "Your update message"
git push origin main
```

Render automatically redeploys when you push to GitHub!

## Step 7: Optional Enhancements

### Add Custom Domain
1. In Render dashboard → "Settings"
2. Click "Add Custom Domain"
3. Point your domain's DNS to Render's provided address

### Enable Auto-Deploy
1. Settings → "Auto-Deploy"
2. Select "Yes" (already enabled by default)

### Database Backups
1. MongoDB Atlas → "Backup" tab
2. Enable automated backups (free tier has limited backup options)

## Monitoring & Maintenance

1. **Monitor Performance:**
   - Render dashboard shows CPU, memory, disk usage
   - Free tier: 0.5GB RAM (sufficient for small-medium load)

2. **View Logs:**
   - Render → "Logs" tab
   - Check for errors and application output

3. **Update Dependencies:**
   - Update `requirements.txt`
   - Push to GitHub
   - Render automatically redeploys

## Production Checklist

- ✅ MongoDB Atlas configured and tested
- ✅ Render deployment created
- ✅ Environment variables set securely
- ✅ HTTPS enabled (automatic with Render)
- ✅ Admin credentials changed from defaults
- ✅ Database backups configured (if using paid MongoDB)
- ✅ Application tested end-to-end
- ✅ Logs monitored for errors

## Support & Resources

- **Render Docs:** https://render.com/docs
- **MongoDB Atlas Docs:** https://docs.atlas.mongodb.com/
- **Flask Deployment:** https://flask.palletsprojects.com/deployment/
- **GitHub Integration:** Check Render's GitHub integration dashboard

---

**Deployed URL:** [Will be provided by Render after deployment]

**MongoDB Atlas Cluster:** [Saved in Render environment variables]

**Admin Access:** Use credentials set in environment variables
