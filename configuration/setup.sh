#!/bin/bash

echo "🏋️ MS Power Fitness - Quick Setup Script"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Backend setup
echo "📦 Setting up Python backend..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "🗄️ Initializing database..."
python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database initialized")
EOF

echo ""
echo "👤 Creating admin user..."
echo "Please enter admin details:"
read -p "Name: " admin_name
read -p "Phone (10 digits): " admin_phone
read -p "Email: " admin_email
read -sp "Password: " admin_password
echo ""

# Start Flask in background
python3 app.py &
FLASK_PID=$!
sleep 3

# Create admin user
curl -X POST http://localhost:5000/api/init-admin \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$admin_name\",
    \"phone\": \"$admin_phone\",
    \"email\": \"$admin_email\",
    \"password\": \"$admin_password\"
  }"

echo ""
echo ""

# Frontend setup
echo "📦 Setting up Vue.js frontend..."
npm install

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  python app.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  npm run dev"
echo ""
echo "Then open http://localhost:3000 in your browser"
echo ""
echo "Admin Login:"
echo "  Email: $admin_email"
echo "  Password: [your password]"
echo ""

# Kill background Flask process
kill $FLASK_PID
