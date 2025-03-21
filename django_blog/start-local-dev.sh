#!/bin/bash

# Exit on error
set -e

echo "Starting local development environment..."

# Check if .env file exists, create if it doesn't
if [ ! -f .env ]; then
    echo "Creating .env file for development..."
    cat > .env << EOF
# Django settings
DEBUG=True
SECRET_KEY=dev_secret_key_replace_in_production

# Database settings (matching your development settings)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres

# Media storage
USE_CLOUDINARY=False
EOF
    echo ".env file created with development defaults"
fi

# Build and start the containers
echo "Building and starting Docker containers..."
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up

# This command will show logs in the terminal and can be stopped with Ctrl+C