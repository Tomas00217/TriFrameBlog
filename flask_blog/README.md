# Flask Blog

This is the implementation of the simple blog app using the [Flask](https://flask.palletsprojects.com/en/stable/) web framework.

---

### **Admin Interface**

The application includes an `/admin` interface where you can manage blog content and other entities.

**Admin Credentials (default):**

- **Email:** `admin@blog.com`
- **Password:** `admin`

Use these credentials to log in and create, update, or delete entities in the system.

---

## Prerequisites

### **Docker**

Docker is required to containerize and run this application.

Installation: Follow the official Docker installation guide for your operating system.

- **Install Docker**: [Docker Installation Guide](https://docs.docker.com/get-started/get-docker/)

To verify Docker is installed, run the following command in your terminal:

```bash
docker --version
```

## **Running the Application**

**Working Directory:** `/flask_blog`

### **Initial Setup**

> This initial setup runs the application in development mode and is recommended for exploring the app.

When running the app for the first time, use the provided start script. This will:

- Create the necessary `.env` file
- Set up and start the database and web application containers
- Set up a super user
- Seed the database with blogs, tags, and users

#### **Windows**

Run the following PowerShell script:

```powershell
.\StartLocalDev.ps1
```

In case you run into an issue with permissions for the script, try adding temporary bypass:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

#### **Linux / macOS**

Use the Bash script:

```bash
bash start-local-dev.sh
```

In case you run into an errors related to invalid commands such as "\r", try running the following command which will replace DOS newlines:

```bash
sed -i 's/\r$//' start-local-dev.sh
```

Once started, you can access the website at:
**http://localhost:5000** or **http://127.0.0.1:5000**

---

#### **Restarting the Application**

If the app has already been set up, start it again with:

```bash
docker-compose up
```

#### **Stop the Application**

Stopping the application can be done using

```bash
docker-compose down
```

---

### **Running Tests**

**Make sure the app is running before running tests.**

Run tests inside the web container using:

```bash
docker-compose exec web pytest
```

## Production Mode

Production mode runs the app using **Gunicorn** behind **Nginx**, with HTTPS enabled.

> Development mode is easier to get started with and is recommended for exploring the app. See the dev instructions for automatic `.env` setup and a simpler workflow.

---

### Prerequisites

Before running in production mode, make sure you have:

- A **Cloudinary account** for media storage ([sign up here](https://cloudinary.com/))
- An `.env.production` file with production environment variables (you can use the `.env` generated by the dev script as a reference)
- A valid **SSL certificate** for `localhost`
  You can generate a self-signed certificate for local testing

---

### Setup

1. **Create `env.production`**

   This file should include environment variables like:

   ```ini
    FLASK_APP=flask_blog
    SECRET_KEY=dev_secret_key_replace_in_production
    DATABASE_URI=postgresql://postgres:postgres@db:5432/postgres

    # Cloudinary settings (set for production)
    CLOUDINARY_CLOUD_NAME=your_cloud_name
    CLOUDINARY_API_KEY=your_api_key
    CLOUDINARY_API_SECRET=your_api_secret
   ```

2. **Generate SSL certificates**

Place them under `nginx/certs/`:

- localhost.crt

- localhost.key

You can generate self-signed certs for local use with OpenSSL like so (on windows it might require installing OpenSSL or using git bash if git is installed or WSL):

```bash
mkdir nginx/certs

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/certs/localhost.key \
  -out nginx/certs/localhost.crt \
  -subj "/C=US/ST=Dev/L=Local/O=Dev/OU=Dev/CN=localhost"
```

3. **Starting in production mode**

Production mode can be started by running the following command:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

After successfully running the app it should now be available on **https://localhost:5443**.
