# Use official lightweight Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (needed for pandas/openpyxl)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
