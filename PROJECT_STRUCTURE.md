# MS Power Fitness - Project Structure

```
ms-power-fitness/
├── Backend (Flask)
│   ├── app.py                      # Main Flask application with all API endpoints
│   ├── models.py                   # SQLAlchemy database models
│   ├── requirements.txt            # Python dependencies
│   └── ms_power_fitness.db        # SQLite database (created on first run)
│
├── Frontend (Vue.js 3 + Vite)
│   ├── index.html                  # HTML entry point
│   ├── main.js                     # Vue app initialization
│   ├── App.vue                     # Root Vue component with routing logic
│   ├── components/
│   │   ├── LoginView.vue          # Login/Register component
│   │   ├── AdminDashboard.vue     # Admin dashboard with all features
│   │   └── MemberPortal.vue       # Member portal with payment flow
│   ├── package.json               # Node dependencies
│   └── vite.config.js             # Vite configuration
│
├── Configuration
│   ├── .env.example               # Environment variables template
│   ├── .gitignore                # Git ignore rules
│   └── setup.sh                  # Quick setup script
│
└── Documentation
    └── README.md                  # Comprehensive setup and usage guide
```

## File Descriptions

### Backend Files

**app.py** (Main Application)
- Flask application configuration
- Flask-Security-Too setup with User/Role management
- Complete REST API with endpoints for:
  - Authentication (login, register, current user)
  - Plan management (CRUD operations)
  - Payment processing (submit, approve, reject)
  - Membership management (renewals, status updates)
  - Admin features (priority list, expired members, projections)
  - Transaction reporting with filters

**models.py** (Database Models)
- User: Member/Admin accounts with phone+email identity
- Role: RBAC roles (admin, member)
- Plan: Membership plans with pricing and duration
- Membership: Active membership records with status tracking
- Payment: Payment records with UPI UTR or Cash tracking

### Frontend Files

**App.vue** (Main Component)
- Application-level routing logic
- Loading screen for cold starts
- Navigation bar
- User authentication state management
- Component switching (Login/Admin/Member)

**LoginView.vue**
- Dual-tab interface (Login/Register)
- Form validation for phone (10 digits) and email
- Error/success message display
- Token-based authentication

**AdminDashboard.vue**
- 6 major tabs:
  1. Priority List - 7-day expiry tracking with WhatsApp links
  2. Digital Gatekeeper - Expired member approval
  3. Approval Queue - Payment verification
  4. Transactions - Revenue reporting with filters
  5. Plan Management - CRUD for membership plans
  6. Business Projections - Revenue forecasting
- Real-time data fetching
- Mobile-responsive design

**MemberPortal.vue**
- Dynamic status card (Green/Yellow/Red based on membership)
- Plan selection interface
- Payment method selector (UPI/Cash)
- UPI payment flow with QR code and 12-digit UTR validation
- Cash payment instructions
- Payment history display

## Component Interaction Flow

```
User Login
    ↓
App.vue (Check role)
    ↓
    ├─→ Admin → AdminDashboard.vue
    │              ↓
    │          Tab Navigation
    │              ↓
    │          API Calls to Backend
    │
    └─→ Member → MemberPortal.vue
                   ↓
               Status Check
                   ↓
               Payment Flow (if needed)
                   ↓
               Submit Payment
                   ↓
               Backend Processing
```

## API Integration

All components use the `Authentication-Token` header for authenticated requests:

```javascript
fetch('/api/endpoint', {
  headers: {
    'Content-Type': 'application/json',
    'Authentication-Token': token
  }
})
```

## State Management

- **No Vuex/Pinia**: Lightweight approach using Vue 3 Composition API
- **Local Storage**: Token persistence for sessions
- **Props/Emits**: Parent-child communication
- **Reactive Refs**: Component-level state

## Styling Approach

- **No CSS Framework**: Custom CSS for production-grade aesthetics
- **CSS Variables**: Consistent color palette
- **Mobile-First**: Responsive breakpoints at 768px
- **Animations**: Smooth transitions and loading states
- **Typography**: Google Fonts (Space Mono + Archivo Black)

## Build Process

**Development:**
```bash
# Backend: Flask development server
python app.py

# Frontend: Vite HMR dev server
npm run dev
```

**Production:**
```bash
# Frontend build
npm run build  # Creates dist/ folder

# Backend production server
gunicorn -w 4 app:app
```

## Database Initialization

On first run, Flask creates tables automatically via:
```python
db.create_all()
```

No migrations needed for initial setup. For production, consider Flask-Migrate.

## Security Considerations

1. **Password Hashing**: Bcrypt with configurable rounds
2. **Token Auth**: Flask-Security-Too session tokens
3. **Input Validation**: 
   - Phone: Exactly 10 digits
   - UTR: Exactly 12 digits, numeric only
   - Email: Standard email format
4. **RBAC**: Decorator-based access control
5. **CORS**: Configured for API access

## Deployment Checklist

- [ ] Set strong SECRET_KEY in production
- [ ] Set strong SECURITY_PASSWORD_SALT
- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Monitor logs for errors
- [ ] Set up health check endpoints
- [ ] Configure rate limiting
- [ ] Enable application monitoring (e.g., Sentry)

## Performance Optimization

1. **Frontend**:
   - Lazy loading for heavy components
   - Image optimization for QR codes
   - Code splitting via Vite
   - Minimal dependencies

2. **Backend**:
   - Database indexing on phone, email, dates
   - Query optimization with proper filters
   - Connection pooling for production DB
   - Caching for frequently accessed data

3. **Network**:
   - API response compression
   - CDN for static assets
   - Browser caching headers

## Future Enhancements

- WebSocket support for real-time notifications
- Progressive Web App (PWA) capabilities
- Offline mode for member access status
- Advanced analytics dashboard
- Automated report generation
- Integration with WhatsApp Business API
- Biometric attendance tracking
- Mobile apps (React Native/Flutter)
