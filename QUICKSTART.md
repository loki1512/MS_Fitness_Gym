# MS Power Fitness - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Install Prerequisites

**Python 3.10+**
```bash
python --version  # Should be 3.10 or higher
```

**Node.js 18+**
```bash
node --version  # Should be 18 or higher
```

### 2. Backend Setup (2 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate (choose your OS)
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 3. Create Admin User (1 minute)

```bash
# Start Flask
python app.py

# In another terminal, create admin
curl -X POST http://localhost:5000/api/init-admin \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin - Gangadhar",
    "phone": "9182834795",
    "email": "admin@msfitness.com",
    "password": "admin123"
  }'
```

### 4. Frontend Setup (2 minutes)

```bash
# Install Node dependencies
npm install

# Start development server
npm run dev
```

### 5. Access the Application

Open browser: `http://localhost:3000`

**Login with:**
- Email: `admin@gym.com`
- Password: `admin123`

---

## 🎯 First Steps After Login

### As Admin:
1. Go to **Plans** tab → Create your first membership plan
2. Go to **Gatekeeper** tab → Test manual member approval
3. Check **Projections** tab → See business forecasting

### Create Test Member:
1. Logout
2. Click **Register**
3. Fill details with test data
4. Login as member
5. Try payment flow

---

## 🚀 Production Deployment

### Option 1: Render.com (Free Tier)

**Backend:**
1. Push code to GitHub
2. Create new Web Service on Render
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app`

**Frontend:**
1. Create Static Site on Render
2. Build: `npm install && npm run build`
3. Publish: `dist`

### Option 2: Single VPS

```bash
# Install dependencies
sudo apt install python3 python3-pip nodejs npm nginx

# Setup project
git clone <your-repo>
cd ms-power-fitness
pip3 install -r requirements.txt
npm install && npm run build

# Configure nginx to serve frontend and proxy backend
# Setup systemd service for Flask app
```

---

## 📋 Common Commands

**Start Development:**
```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend
npm run dev
```

**Build for Production:**
```bash
npm run build
```

**Update Membership Statuses:**
```bash
flask update-statuses
```

**Database Backup:**
```bash
cp ms_power_fitness.db backup_$(date +%Y%m%d).db
```

---

## 🆘 Troubleshooting

**Port already in use:**
```bash
# Find and kill process
lsof -ti:5000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

**Database locked:**
```bash
# Close all Flask instances and restart
```

**Dependencies error:**
```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install

# For Python
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Review `PROJECT_STRUCTURE.md` for architecture
3. Open GitHub issue with error details
4. Email: support@mspowerfitness.com

---

**Built with ❤️ for Indian Micro-Enterprises**
