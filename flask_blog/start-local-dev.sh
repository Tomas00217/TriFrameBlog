#!/bin/bash

# Bash script for starting local development environment
set -e

echo -e "Starting Flask local development environment..."

# Check if .env file exists, create if it doesn't
if [ ! -f .env ]; then
    echo -e "Creating .env file for development..."
    cat > .env << EOL
FLASK_APP=flask_blog
SECRET_KEY=dev_secret_key_replace_in_production
DATABASE_URI=postgresql://postgres:postgres@db:5432/postgres

# Cloudinary settings (set for production)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
EOL
    echo -e "env file created with development defaults"
fi

# Build and start the containers
echo -e "Building and starting Docker containers..."
docker-compose -f docker-compose.yml up --build
