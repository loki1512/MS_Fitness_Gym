# MS Power Fitness - Deployment Guide

## 🎯 Deployment Options

### Option 1: Render.com (Recommended for Beginners)
- **Cost**: Free tier available
- **Pros**: Easy setup, automatic HTTPS, global CDN
- **Cons**: Cold starts on free tier, limited compute

### Option 2: Railway.app
- **Cost**: $5/month credit (free tier)
- **Pros**: No cold starts, simple deployment
- **Cons**: Credit-based pricing

### Option 3: VPS (DigitalOcean, Linode, AWS)
- **Cost**: $5-10/month
- **Pros**: Full control, no cold starts, scalable
- **Cons**: Requires server management skills

---

## 📦 Option 1: Render.com Deployment

### Backend Deployment

1. **Prepare Repository**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

2. **Create Web Service on Render**
- Go to https://dashboard.render.com
- Click "New +" → "Web Service"
- Connect GitHub repository
- Configure:
  ```
  Name: ms-power-fitness-api
  Environment: Python 3
  Build Command: pip install -r requirements.txt
  Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
  ```

3. **Add Environment Variables**
```
SECRET_KEY=<generate-random-32-char-string>
SECURITY_PASSWORD_SALT=<generate-random-32-char-string>
```

Generate secrets:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

4. **Deploy**
- Click "Create Web Service"
- Wait for deployment (5-10 minutes)
- Note your backend URL: `https://ms-power-fitness-api.onrender.com`

### Frontend Deployment

1. **Update API URL**
Create `.env.production`:
```
VITE_API_URL=https://ms-power-fitness-api.onrender.com
```

Update `vite.config.js`:
```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
});
```

2. **Create Static Site on Render**
- Click "New +" → "Static Site"
- Connect same GitHub repository
- Configure:
  ```
  Name: ms-power-fitness
  Build Command: npm install && npm run build
  Publish Directory: dist
  ```

3. **Deploy**
- Frontend URL: `https://ms-power-fitness.onrender.com`

### Initialize Admin User

```bash
curl -X POST https://ms-power-fitness-api.onrender.com/api/init-admin \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin User",
    "phone": "9876543210",
    "email": "admin@gym.com",
    "password": "YourSecurePassword123!"
  }'
```

---

## 🚂 Option 2: Railway.app Deployment

### One-Command Deployment

1. **Install Railway CLI**
```bash
npm i -g @railway/cli
railway login
```

2. **Deploy Backend**
```bash
railway init
railway up
```

3. **Add Environment Variables**
```bash
railway variables set SECRET_KEY=<your-secret>
railway variables set SECURITY_PASSWORD_SALT=<your-salt>
```

4. **Deploy Frontend**
```bash
cd frontend
railway init
railway up
```

Railway automatically detects Python and Node.js and configures appropriately.

---

## 🖥️ Option 3: VPS Deployment (Ubuntu 22.04)

### Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx nodejs npm git

# Install PM2 for process management
sudo npm install -g pm2

# Create application user
sudo adduser mspower
sudo usermod -aG sudo mspower
su - mspower
```

### Deploy Application

```bash
# Clone repository
cd /home/mspower
git clone <your-repo> ms-power-fitness
cd ms-power-fitness

# Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
SECURITY_PASSWORD_SALT=$(python -c "import secrets; print(secrets.token_hex(32))")
EOF

# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Frontend setup
npm install
npm run build
```

### Configure Gunicorn

Create `/home/mspower/ms-power-fitness/gunicorn_config.py`:
```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
timeout = 120
accesslog = "/home/mspower/ms-power-fitness/access.log"
errorlog = "/home/mspower/ms-power-fitness/error.log"
loglevel = "info"
```

### Setup PM2 Process Manager

```bash
# Start Flask app with PM2
cd /home/mspower/ms-power-fitness
source venv/bin/activate
pm2 start "gunicorn -c gunicorn_config.py app:app" --name ms-power-api

# Save PM2 configuration
pm2 save
pm2 startup
```

### Configure Nginx

Create `/etc/nginx/sites-available/ms-power-fitness`:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # Frontend
    location / {
        root /home/mspower/ms-power-fitness/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/ms-power-fitness /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Setup SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Setup Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 🔄 Continuous Deployment

### GitHub Actions (Automatic Deployment)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to VPS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /home/mspower/ms-power-fitness
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            npm install
            npm run build
            pm2 restart ms-power-api
```

Add secrets in GitHub repository settings:
- `VPS_HOST`: Your server IP
- `VPS_USER`: `mspower`
- `VPS_SSH_KEY`: Your private SSH key

---

## 📊 Monitoring & Maintenance

### Setup Monitoring

**PM2 Monitoring:**
```bash
pm2 monit
pm2 logs ms-power-api
```

**Nginx Logs:**
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Database Backup Script

Create `/home/mspower/backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/home/mspower/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="/home/mspower/ms-power-fitness/ms_power_fitness.db"

mkdir -p $BACKUP_DIR
cp $DB_PATH "$BACKUP_DIR/backup_$DATE.db"

# Keep only last 30 backups
ls -t $BACKUP_DIR/backup_*.db | tail -n +31 | xargs rm -f
```

Setup daily backup cron:
```bash
chmod +x /home/mspower/backup.sh
crontab -e

# Add this line
0 2 * * * /home/mspower/backup.sh
```

### Health Check Endpoint

The API includes `/api/health` endpoint. Setup monitoring with:
- UptimeRobot (free)
- Pingdom
- StatusCake

---

## 🔐 Security Checklist

- [ ] Change default admin credentials
- [ ] Set strong SECRET_KEY and SECURITY_PASSWORD_SALT
- [ ] Enable HTTPS (SSL certificate)
- [ ] Configure firewall (UFW)
- [ ] Disable password authentication for SSH
- [ ] Setup fail2ban for brute force protection
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`
- [ ] Database backups automated
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets (never commit .env)

---

## 🚨 Troubleshooting Production Issues

### High CPU Usage
```bash
# Check processes
top
pm2 monit

# Reduce Gunicorn workers
# Edit gunicorn_config.py: workers = 2
```

### Database Locked Errors
```bash
# Check for long-running queries
# Switch to PostgreSQL for production:
pip install psycopg2-binary
# Update DATABASE_URL in .env
```

### Application Crashes
```bash
# Check logs
pm2 logs ms-power-api --lines 100

# Restart application
pm2 restart ms-power-api
```

### Out of Memory
```bash
# Check memory usage
free -m

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📈 Scaling Strategies

### Vertical Scaling (Single Server)
- Upgrade VPS plan (more RAM, CPU)
- Optimize database queries
- Enable caching (Redis)

### Horizontal Scaling (Multiple Servers)
- Load balancer (Nginx)
- Separate database server (PostgreSQL)
- Redis for session storage
- CDN for static assets

### Database Migration (SQLite → PostgreSQL)

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE ms_power_fitness;
CREATE USER mspower WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ms_power_fitness TO mspower;
\q

# Update .env
DATABASE_URL=postgresql://mspower:secure_password@localhost/ms_power_fitness

# Update app.py
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
```

---

## 📞 Support & Resources

- **Documentation**: README.md
- **Issues**: GitHub Issues
- **Render Docs**: https://render.com/docs
- **Nginx Docs**: https://nginx.org/en/docs/
- **PM2 Docs**: https://pm2.keymetrics.io/docs/

---

**Deployment Complete! 🎉**

Your gym management system is now live and ready to help manage memberships efficiently!
