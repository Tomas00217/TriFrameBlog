# PowerShell script for starting local development environment

Write-Host "Starting local development environment..." -ForegroundColor Green

# Check if .env file exists, create if it doesn't
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file for development..." -ForegroundColor Yellow
    @"
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

# Change for production to (https://localhost:8443)
CSRF_TRUSTED_ORIGINS=http://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8
    Write-Host ".env file created with development defaults" -ForegroundColor Green
}

# Build and start the containers
Write-Host "Building and starting Docker containers..." -ForegroundColor Green
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build