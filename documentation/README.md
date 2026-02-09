# MS Power Fitness - Retention-First Membership Management System

A comprehensive gym management system built with Flask and Vue.js 3, designed specifically for micro-enterprises in the Indian UPI/Cash economy.

## 🎯 Key Features

### Admin Dashboard
- **Priority Call List**: 7-day expiry tracking with WhatsApp integration
- **Digital Gatekeeper**: Quick approval system for expired members
- **Approval Queue**: Manual UTR verification against bank statements
- **Transaction Management**: Filter by period with revenue aggregation
- **Plan Management**: Create, edit, and soft-delete membership plans
- **Business Projections**: Revenue forecasting with scenario analysis

### Member Portal
- **Dignity Dashboard**: Visual access status (Green/Red screen)
- **Smart Payment Flow**: UPI with QR code + 12-digit UTR validation or Cash
- **Payment History**: Track all transactions and approval status

### Technical Highlights
- **Zero Gateway Fees**: Direct UPI/Cash tracking without payment processors
- **Mobile-First Design**: Optimized for smartphone admin access
- **Identity-First**: Name + Phone number on every record
- **RBAC Security**: Role-based access control (Admin/Member)

## 🛠️ Tech Stack

**Backend:**
- Flask (Python 3.10+)
- SQLAlchemy ORM
- Flask-Security-Too + Bcrypt
- SQLite Database

**Frontend:**
- Vue.js 3 (Composition API)
- Vite Build Tool
- Custom CSS (No framework dependencies for lightweight build)

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

1. **Clone the repository**
```bash
cd ms-power-fitness
```

2. **Create and activate virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY and SECURITY_PASSWORD_SALT
```

5. **Initialize the database**
```bash
python
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

6. **Create admin user**
```bash
# Run the Flask app first
python app.py

# In another terminal, make a POST request:
curl -X POST http://localhost:5000/api/init-admin \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin User",
    "phone": "9876543210",
    "email": "admin@mspowerfitness.com",
    "password": "admin123"
  }'
```

### Frontend Setup

1. **Install Node dependencies**
```bash
npm install
```

2. **Run development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
python app.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

Access the application at `http://localhost:3000`

### Production Build

**Build Frontend:**
```bash
npm run build
```

**Serve with Production WSGI Server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📊 Database Schema

### User
- name, phone (unique), email (unique)
- password (hashed), active status
- roles (admin/member via many-to-many)

### Plan
- name, price, duration_days
- is_active (soft delete)

### Membership
- user_id, plan_id
- start_date, end_date
- status (Active, Expiring, Expired)

### Payment
- user_id, amount, txn_ref (12-digit UTR)
- payment_method (UPI/Cash)
- status (Pending, Approved, Rejected)

## 🔐 Security Features

- **Password Hashing**: Bcrypt with configurable rounds
- **Token Authentication**: Flask-Security-Too session management
- **RBAC**: Role-based access control
- **CSRF Protection**: Configurable (disabled for API mode)
- **Input Validation**: 10-digit phone, 12-digit UTR enforcement

## 💰 Business Features

### Financial Forecasting
- **Expiry-Based Forecast**: Next 30 days expected revenue
- **Scenario Simulator**: 
  - Pessimistic (-5%)
  - Status Quo (0%)
  - Optimistic (+10%)
- Quarterly and Annual projections

### Retention Tools
- **7-Day Priority List**: Proactive renewal reminders
- **WhatsApp Integration**: Pre-filled renewal messages
- **Digital Gatekeeper**: Quick approval for walk-in renewals

## 📱 Mobile Optimization

- Responsive design tested on 360px - 1920px
- Touch-friendly buttons (min 44px height)
- Simplified navigation for one-handed use
- Fast load times (<2s on 3G)

## 🎨 Design Philosophy

**Distinctive Aesthetics:**
- **Typography**: Space Mono + Archivo Black for bold, modern look
- **Color Palette**: 
  - Primary: #FF6B35 (Vibrant Orange)
  - Secondary: #004E89 (Deep Blue)
  - Success: #06D6A0 (Mint Green)
  - Danger: #EF476F (Coral Red)
- **Motion**: Smooth transitions, hover states, loading animations
- **Accessibility**: High contrast, readable fonts, clear CTAs

## 🔄 Workflow Examples

### Member Renewal Flow
1. Member sees "Access Denied" (Red Screen)
2. Selects plan from dynamic list
3. Chooses UPI or Cash payment method
4. If UPI: Scans QR, enters 12-digit UTR
5. Submits for approval
6. Admin verifies UTR in Approval Queue
7. Admin approves → Membership auto-extends
8. Member sees "Access Granted" (Green Screen)

### Admin Daily Routine
1. Check Priority List for expiring members
2. Send WhatsApp reminders
3. Process Approval Queue payments
4. Manually approve walk-in renewals via Gatekeeper
5. Review transactions and projections

## 📈 API Endpoints

### Authentication
- `POST /api/register` - Member registration
- `POST /api/login` - Login (returns token)
- `GET /api/me` - Current user info

### Plans (Public)
- `GET /api/plans` - Active plans

### Plans (Admin)
- `GET /api/admin/plans` - All plans
- `POST /api/admin/plans` - Create plan
- `PUT /api/admin/plans/<id>` - Update plan
- `DELETE /api/admin/plans/<id>` - Soft delete plan

### Payments
- `POST /api/payments/submit` - Submit payment
- `GET /api/admin/payments/pending` - Pending approvals
- `POST /api/admin/payments/<id>/approve` - Approve
- `POST /api/admin/payments/<id>/reject` - Reject

### Memberships (Admin)
- `GET /api/admin/priority-list` - Expiring in 7 days
- `GET /api/admin/expired-members` - Expired members
- `POST /api/admin/memberships/<user_id>/renew` - Manual renewal

### Analytics (Admin)
- `GET /api/admin/transactions?filter=<type>` - Transactions
- `GET /api/admin/projections` - Business forecasting

## 🧪 Testing

### Manual Testing Checklist

**Member Flow:**
- [ ] Register new account
- [ ] Login successfully
- [ ] View access status
- [ ] Select plan and payment method
- [ ] Submit UPI payment with UTR
- [ ] Submit cash payment
- [ ] View payment history

**Admin Flow:**
- [ ] View priority call list
- [ ] Send WhatsApp reminder
- [ ] Approve pending payment
- [ ] Reject invalid payment
- [ ] Manually renew expired member
- [ ] View transactions with filters
- [ ] Create new plan
- [ ] Edit existing plan
- [ ] View business projections

### Load Testing
```bash
# Install locust
pip install locust

# Create locustfile.py with API tests
# Run: locust -f locustfile.py
```

## 🚢 Deployment

### Render.com (Recommended for Free Tier)

**Backend (Web Service):**
1. Connect GitHub repository
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app`
4. Add environment variables from `.env.example`

**Frontend (Static Site):**
1. Build Command: `npm install && npm run build`
2. Publish Directory: `dist`

### Heroku

```bash
# Install Heroku CLI
heroku login
heroku create ms-power-fitness

# Add buildpacks
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 heroku/nodejs

# Deploy
git push heroku main
```

### VPS (Ubuntu)

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx

# Clone and setup
git clone <repo-url>
cd ms-power-fitness
pip3 install -r requirements.txt
npm install
npm run build

# Configure nginx
sudo nano /etc/nginx/sites-available/ms-power-fitness

# Setup systemd service for Flask
sudo nano /etc/systemd/system/ms-power-fitness.service

# Start services
sudo systemctl start ms-power-fitness
sudo systemctl enable ms-power-fitness
sudo systemctl restart nginx
```

## 🔧 Maintenance

### Database Migrations
```bash
# Update membership statuses
flask update-statuses
```

### Backup
```bash
# SQLite backup
cp ms_power_fitness.db ms_power_fitness_backup_$(date +%Y%m%d).db
```

### Logs
```bash
# View Flask logs
tail -f app.log

# View nginx logs (production)
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📞 Support

For issues and questions:
- Email: support@mspowerfitness.com
- GitHub Issues: [Create an issue](https://github.com/yourusername/ms-power-fitness/issues)

## 🎯 Roadmap

- [ ] SMS notifications via Indian providers
- [ ] Attendance tracking with QR codes
- [ ] Automated WhatsApp integration via Business API
- [ ] Multi-gym support for franchises
- [ ] Equipment maintenance scheduling
- [ ] Member progress tracking
- [ ] Referral program management
- [ ] Mobile apps (iOS/Android)

## 💡 Best Practices

**For Admins:**
- Check Priority List daily
- Verify UTR against bank statement before approval
- Use Digital Gatekeeper for walk-in renewals
- Review projections weekly for business planning

**For Development:**
- Always use virtual environments
- Keep dependencies updated
- Test UTR validation thoroughly
- Maintain backup schedule
- Monitor server resources on free tiers

---

Built with ❤️ for Indian Micro-Enterprises | Zero Gateway Fees 🇮🇳
