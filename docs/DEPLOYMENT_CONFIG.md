# 🚀 Deployment Checklist & Configuration

## Your MongoDB Connection Details

**MongoDB Atlas Cluster:** `cluster0.vvcsmev.mongodb.net`
**Username:** `vignesh_op`

## ✅ MongoDB Connection String (Production)

Replace `<db_password>` with your actual MongoDB password:

```
mongodb+srv://vignesh_op:<db_password>@cluster0.vvcsmev.mongodb.net/authentication?retryWrites=true&w=majority
```

**Example (DO NOT use this - replace with your actual password):**
```
mongodb+srv://vignesh_op:MyActualPassword123@cluster0.vvcsmev.mongodb.net/authentication?retryWrites=true&w=majority
```

---

## 🎯 Environment Variables for Render

Copy and paste these into Render's environment variables section:

```
FLASK_ENV=production
SECRET_KEY=d1f554b2f19cacf7a711c3e014ccd0df7282b6d717e592d7177482c58caddd4a
MONGO_URI=mongodb+srv://vignesh_op:<YOUR_PASSWORD_HERE>@cluster0.vvcsmev.mongodb.net/authentication?retryWrites=true&w=majority
ADMIN_EMAIL=Vignesh423@authentication.co.in
ADMIN_PASSWORD=your-secure-admin-password-here
```

---

## 📋 Deployment Checklist

### MongoDB Atlas Setup ✅
- [x] Account created
- [x] M0 cluster created
- [x] Database user created (username: vignesh_op)
- [x] IPs whitelisted (0.0.0.0/0)
- [x] Connection string obtained

### Render Deployment Steps:

**Step 1:** Go to https://render.com

**Step 2:** Sign in with GitHub account (if not already signed in)

**Step 3:** Create New Web Service
- Click "New +" → "Web Service"
- Select repository: `Authentication-multi-level-authentication` (or your repo name)
- Click "Connect"

**Step 4:** Configure Service
```
Name:               authentication-app
Environment:        Python 3
Build Command:      pip install -r requirements.txt && python init_db.py
Start Command:      gunicorn app:app
```

**Step 5:** Add Environment Variables (IMPORTANT!)
Click "Add Environment Variable" and add each:

| Variable | Value |
|----------|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `d1f554b2f19cacf7a711c3e014ccd0df7282b6d717e592d7177482c58caddd4a` |
| `MONGO_URI` | `mongodb+srv://vignesh_op:YOUR_PASSWORD@cluster0.vvcsmev.mongodb.net/authentication?retryWrites=true&w=majority` |
| `ADMIN_EMAIL` | `Vignesh423@authentication.co.in` |
| `ADMIN_PASSWORD` | Your secure password |

**Step 6:** Deploy
- Click "Create Web Service"
- Wait 2-5 minutes for build and deployment
- Get your live URL: `https://authentication-app.onrender.com`

---

## 🔍 Verify Deployment

Once deployed, test:

1. **Homepage:** https://authentication-app.onrender.com/
2. **Register:** https://authentication-app.onrender.com/register
3. **Admin Login:** https://authentication-app.onrender.com/admin-login

Use credentials:
- **Email:** `Vignesh423@authentication.co.in`
- **Password:** (the one you set in `ADMIN_PASSWORD`)

---

## 🐛 Troubleshooting

### MongoDB Connection Fails
- ✅ Check password is correct in `MONGO_URI`
- ✅ Verify IP whitelist includes 0.0.0.0/0 in MongoDB Atlas
- ✅ Check database name is `authentication` in connection string

### Face Recognition Not Working
- ✅ This is normal - app will use Haar Cascade (no dlib required)
- ✅ Check server logs: Render → "Logs" tab

### Deployment Stuck
- ✅ Check build logs in Render → "Logs"
- ✅ Wait 5+ minutes (first deploy is slower)
- ✅ Restart deployment if needed

---

## 📊 Important Notes

- **Free Tier Limits:**
  - Render: 0.5GB RAM, limited compute
  - MongoDB: 512MB storage (sufficient for testing)

- **Automatic Updates:**
  - Push changes to GitHub → Render auto-deploys

- **Persistent Storage:**
  - Only MongoDB is persistent
  - Face images (in `/tmp/`) are temporary (reset on redeploy)

- **Monitoring:**
  - Render dashboard shows CPU, memory, disk
  - Check logs regularly for errors

---

## 🎉 Next Steps

1. **Complete MongoDB Connection:** Replace `<YOUR_PASSWORD>` with your actual password
2. **Go to Render:** https://render.com
3. **Create Web Service** with the configuration above
4. **Set Environment Variables** in Render dashboard
5. **Wait for deployment** (2-5 minutes)
6. **Test your live app!** 🚀

---

## 📱 Deployed Application URL
Once live: **https://authentication-app.onrender.com**

**Admin Dashboard:** https://authentication-app.onrender.com/admin-login

Good luck! 🎊
