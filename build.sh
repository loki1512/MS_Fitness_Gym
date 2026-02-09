# Render.com Build Script
#!/usr/bin/env bash
# This script runs during deployment on Render

set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Initialize database
python - <<EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("Database tables created successfully")
EOF

echo "Build completed successfully!"
