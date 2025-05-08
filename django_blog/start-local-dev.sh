#!/bin/bash

# Exit on error
set -e

echo "Starting local development environment..."

# Check if .env file exists, create if it doesn't
if [ ! -f .env ]; then
    echo "Creating .env file for development..."
    cat > .env << EOF
# Django settings
SECRET_KEY=dev_secret_key_replace_in_production

# Database settings
DB_HOST=db
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres

# Cloudinary settings (set for production)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Change for production (https://localhost:8443)
CSRF_TRUSTED_ORIGINS=http://localhost:8000
EOF
    echo ".env file created with development defaults"
fi

# Build and start the containers
echo "Building and starting Docker containers..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build