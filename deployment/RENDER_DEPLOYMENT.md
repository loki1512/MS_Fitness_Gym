# MS Power Fitness - Render.com Deployment Guide

## 🚀 Quick Deployment (10 minutes)

### Prerequisites
- GitHub account
- Render.com account (sign up at https://render.com)
- Your code pushed to a GitHub repository

---

## Method 1: Automatic Deployment (Recommended)

### Step 1: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - MS Power Fitness v2.0"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/ms-power-fitness.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy on Render using Blueprint

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Click "New +" button
   - Select "Blueprint"

2. **Connect Repository**
   - Connect your GitHub account if not already connected
   - Select your `ms-power-fitness` repository
   - Click "Connect"

3. **Render will automatically detect `render.yaml`**
   - Review the services to be created:
     - ✅ Backend API (Python web service)
     - ✅ Frontend (Static site)
     - ✅ PostgreSQL Database (optional, for production)
   - Click "Apply"

4. **Wait for deployment** (5-10 minutes)
   - Render will build and deploy both services
   - You'll get URLs like:
     - Backend: `https://ms-power-fitness-api.onrender.com`
     - Frontend: `https://ms-power-fitness-frontend.onrender.com`

### Step 3: Initialize Admin User

Once deployed, create your first admin user:

```bash
curl -X POST https://ms-power-fitness-api.onrender.com/api/init-admin \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Super Admin",
    "phone": "9876543210",
    "email": "admin@mspowerfitness.com",
    "password": "ChangeThisPassword123!",
    "date_of_birth": "1990-01-01",
    "gender": "Male"
  }'
```

**🎉 Done! Your app is live!**

---

## Method 2: Manual Deployment (Step by Step)

### Part A: Deploy Backend

1. **Create Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Backend Service**
   ```
   Name: ms-power-fitness-api
   Region: Choose closest to your users (e.g., Singapore for India)
   Branch: main
   Runtime: Python 3
   Build Command: chmod +x build.sh && ./build.sh
   Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   Plan: Free
   ```

3. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable"
   
   **Required Variables:**
   ```
   SECRET_KEY = [Click "Generate" button]
   SECURITY_PASSWORD_SALT = [Click "Generate" button]
   PYTHON_VERSION = 3.11.0
   ```

4. **Create Service**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Note the URL (e.g., `https://ms-power-fitness-api.onrender.com`)

### Part B: Deploy Frontend

1. **Update API URL in Frontend**
   
   Create `.env.production` file in your project root:
   ```
   VITE_API_URL=https://ms-power-fitness-api.onrender.com
   ```

2. **Update `vite.config.js`**
   
   Modify to use environment variable:
   ```javascript
   export default defineConfig({
     plugins: [vue()],
     server: {
       port: 3000,
       proxy: {
         '/api': {
           target: process.env.VITE_API_URL || 'http://localhost:5000',
           changeOrigin: true
         }
       }
     },
     build: {
       outDir: 'dist',
       assetsDir: 'assets'
     }
   });
   ```

3. **Commit and push changes**
   ```bash
   git add .env.production vite.config.js
   git commit -m "Add production API URL"
   git push
   ```

4. **Create Static Site on Render**
   - Click "New +" → "Static Site"
   - Connect same GitHub repository
   
   **Configure:**
   ```
   Name: ms-power-fitness-frontend
   Branch: main
   Build Command: npm install && npm run build
   Publish Directory: dist
   ```

5. **Add Environment Variables**
   ```
   NODE_VERSION = 18.17.0
   VITE_API_URL = https://ms-power-fitness-api.onrender.com
   ```

6. **Add Rewrite Rules**
   
   In "Redirects/Rewrites" section:
   ```
   Source: /api/*
   Destination: https://ms-power-fitness-api.onrender.com/api/*
   Action: Rewrite
   ```

7. **Deploy**
   - Click "Create Static Site"
   - Wait 3-5 minutes
   - Note the URL (e.g., `https://ms-power-fitness.onrender.com`)

---

## 🔧 Post-Deployment Configuration

### 1. Test the Deployment

Visit your frontend URL and test:
- ✅ Registration works
- ✅ Login works
- ✅ Admin can access dashboard
- ✅ Members can access portal

### 2. Set Up Custom Domain (Optional)

#### For Frontend:
1. Go to your Static Site settings
2. Click "Custom Domains"
3. Add your domain (e.g., `app.yourgym.com`)
4. Update DNS settings as instructed by Render

#### For Backend API:
1. Go to your Web Service settings
2. Click "Custom Domains"
3. Add API subdomain (e.g., `api.yourgym.com`)
4. Update DNS settings

### 3. Configure CORS for Custom Domain

If using custom domain, update `app.py`:

```python
# Find this line
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Replace with
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://yourdomain.com",
            "https://ms-power-fitness.onrender.com"
        ]
    }
})
```

### 4. Set Up Database Backups

**For SQLite (Free Tier):**

Create a cron job service on Render:

1. Create `backup_cron.py`:
```python
import os
import shutil
from datetime import datetime

def backup_database():
    db_path = 'ms_power_fitness.db'
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{backup_dir}/backup_{timestamp}.db'
    
    shutil.copy2(db_path, backup_path)
    print(f'Backup created: {backup_path}')

if __name__ == '__main__':
    backup_database()
```

**For PostgreSQL (Recommended for Production):**

Render automatically backs up PostgreSQL databases.

---

## 📊 Monitoring & Maintenance

### 1. View Logs

**Backend Logs:**
- Go to your Web Service
- Click "Logs" tab
- Monitor for errors

**Frontend Logs:**
- Go to your Static Site
- Click "Logs" tab

### 2. Set Up Notifications

1. Go to Service Settings
2. Click "Notifications"
3. Add email or Slack webhook for:
   - Deploy failures
   - Service crashes
   - Health check failures

### 3. Health Checks

Render automatically monitors `/api/health` endpoint.

To view health status:
- Go to your Web Service
- Click "Health" tab

---

## 🔄 Updating Your App

### Option 1: Git Push (Automatic)

```bash
# Make changes to your code
git add .
git commit -m "Update feature X"
git push

# Render automatically detects and deploys!
```

### Option 2: Manual Deploy

1. Go to your service dashboard
2. Click "Manual Deploy"
3. Select branch
4. Click "Deploy"

---

## 💰 Free Tier Limitations

Render Free Tier includes:
- ✅ 750 hours/month (enough for 1 service running 24/7)
- ✅ Automatic HTTPS
- ✅ 100GB bandwidth/month
- ⚠️ **Services spin down after 15 minutes of inactivity**
- ⚠️ **Cold start time: 30-60 seconds**

### Handling Cold Starts

Your app already has a loading screen! But you can also:

**Option 1: Keep-Alive Service (External)**

Use a free service like UptimeRobot or Cron-Job.org to ping your API every 14 minutes:
```
https://ms-power-fitness-api.onrender.com/api/health
```

**Option 2: Upgrade to Paid Plan ($7/month)**
- No sleep/spin down
- Instant response times
- More resources

---

## 🔐 Security Checklist

After deployment:

- [ ] Change admin password immediately
- [ ] Verify SECRET_KEY and SECURITY_PASSWORD_SALT are random
- [ ] Enable HTTPS only (Render does this automatically)
- [ ] Set up custom domain with SSL
- [ ] Configure CORS properly for your domain
- [ ] Review and limit API rate limits
- [ ] Set up monitoring alerts
- [ ] Regular database backups (if using PostgreSQL)

---

## 🐛 Troubleshooting

### Issue: "Build Failed"

**Solution:**
1. Check build logs in Render dashboard
2. Verify `requirements.txt` has all dependencies
3. Ensure Python version is correct (3.10+)
4. Try manual build locally:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

### Issue: "Frontend shows blank page"

**Solution:**
1. Check browser console for errors
2. Verify API URL is correct in `.env.production`
3. Check CORS settings in backend
4. Clear browser cache

### Issue: "Database error on first run"

**Solution:**
1. SSH into your service (Render Shell)
2. Run database initialization:
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   >>>     db.create_all()
   >>> exit()
   ```

### Issue: "Admin creation fails"

**Solution:**
Check if admin already exists:
```bash
curl https://ms-power-fitness-api.onrender.com/api/stats
```

If stats work, admin might exist. Try logging in with credentials.

### Issue: "Cold start is too slow"

**Solutions:**
1. **Keep-alive ping** (free): Use UptimeRobot
2. **Upgrade to paid plan** ($7/month): No cold starts
3. **Show loading screen** (already implemented in your app)

---

## 📈 Scaling Options

### When to Upgrade?

Consider paid plan ($7-$25/month) when:
- More than 50 active members
- Need instant response times
- Want custom domain
- Need guaranteed uptime

### Render Plans:

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0 | 750 hrs/month, sleeps after 15min |
| **Starter** | $7/mo | No sleep, 1GB RAM, faster CPU |
| **Standard** | $25/mo | 4GB RAM, auto-scaling |
| **Pro** | $85/mo | 16GB RAM, priority support |

---

## 🎯 Production Checklist

Before going live with real members:

- [ ] Deploy both backend and frontend
- [ ] Initialize admin user
- [ ] Test all features (registration, login, payments)
- [ ] Create at least 3 membership plans
- [ ] Add 1-2 test members
- [ ] Test payment approval workflow
- [ ] Test WhatsApp links
- [ ] Verify member management works
- [ ] Test profile editing
- [ ] Set up database backups
- [ ] Configure monitoring/alerts
- [ ] Add custom domain (optional)
- [ ] Update CORS for production domain
- [ ] Change all default passwords
- [ ] Train gym staff on admin interface

---

## 📞 Support Resources

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Status Page**: https://status.render.com

---

## 🔗 Quick Links After Deployment

Once deployed, save these URLs:

```
Frontend: https://ms-power-fitness.onrender.com
Backend API: https://ms-power-fitness-api.onrender.com
Admin Login: https://ms-power-fitness.onrender.com (use admin credentials)
API Health: https://ms-power-fitness-api.onrender.com/api/health
```

---

**🎉 Congratulations! Your gym management system is now live on Render!**

For questions or issues, refer to the troubleshooting section or check Render's documentation.
