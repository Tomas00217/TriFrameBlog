#!/bin/bash

# Bash script for starting local development environment
set -e

echo -e "Starting FastAPI local development environment..."

# Set environment to development
export FASTAPI_ENV=dev

# Check if .env file exists, create if it doesn't
if [ ! -f .env ]; then
    echo "Creating .env file for development..."
    cat > .env << EOL
DATABASE_URL="postgresql+asyncpg://postgres:postgres@db:5432/postgres"
SECRET_KEY=dev_secret_key_replace_in_production
CSRF_SECRET=dev_csrf_secret

# Cloudinary settings (set for production)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

EOL
    echo ".env file created with development defaults"
fi

# Build and start the containers
echo -e "Building and starting Docker containers..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build