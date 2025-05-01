# Flask Blog

This is the implementation of the simple blog app using the [Flask](https://flask.palletsprojects.com/en/stable/) web framework.

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

When running the app for the first time, use the provided start script. This will:

- Create the necessary `.env` file
- Set up and start the database and web application containers
- Set up a super user
- Seed the database with blogs, tags, and users

Once started, you can access the website at:
**http://localhost:5000** or **http://127.0.0.1:5000**

---

### **Admin Interface**

The application includes an `/admin` interface where you can manage blog content and other entities.

**Admin Credentials (default):**

- **Email:** `admin@blog.com`
- **Password:** `admin`

Use these credentials to log in and create, update, or delete entities in the system.

---

### **Starting the Application**

#### **Windows**

Run the following PowerShell script:

```powershell
.\StartLocalDev.ps1
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

#### **Restarting the Application**

If the app has already been set up, start it again with:

```bash
docker-compose up
```

---

### **Running Tests**

**Make sure the app is running before running tests.**

Run tests inside the web container using:

```bash
docker-compose exec web pytest
```
