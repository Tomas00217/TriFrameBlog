# TriFrameBlog

This project serves as aid for Diploma thesis: Comparison of Python Web Frameworks.

## Compared Frameworks

There are three python web frameworks used. Each of them implements the same [application](#blog-app) in their own respective sub-project. The following frameworks are used:

- Django - code is located in django_blog
- Flask - code is located in flask_blog
- FastAPI - code is located in fastapi_blog

Shared functionality is found under the shared folder.

## Blog App

A simple blog web application implemented by the three frameworks.

### Functional requirements

- Users can register with an email, and password.
- Users can set their username on their profile.
- Users can log in using their email and password.
- All users can view list of blogs.
- All users can view the detail page of a blog.
- Authenticated users can create, update, and delete blogs.
- Blogs can have various tags.
- Blogs can be filtered by tags or searched by title.

---

### Non-functional requirements

- The application should have a straightforward navigation for operations.
- The application should validate inputs.
- Passwords must be hashed and securely stored.
- Code should be modular and well-documented.

---

### Admin Interface

Each implementation also includes an **`/admin` interface**, where an admin user can manage blog content and other entities.

**Admin Credentials (default):**

- **Email:** `admin@blog.com`
- **Password:** `admin`

## Running the app locally

### Prerequisites

#### **Docker**

Docker is required to containerize and run this application.

Installation: Follow the official Docker installation guide for your operating system.

- **Install Docker**: [Docker Installation Guide](https://docs.docker.com/get-started/get-docker/)

To verify Docker is installed, run the following command in your terminal:

```bash
docker --version
```

---

### Running the App

You can choose from three implementations. Follow the instructions below based on the implementation you'd like to run:

- **Django Implementation**
  Navigate to the `/django_blog` directory and follow the instructions in the [README](./django_blog/README.md).

- **Flask Implementation**
  Navigate to the `/flask_blog` directory and follow the instructions in the [README](./flask_blog/README.md).

- **FastAPI Implementation**
  Navigate to the `/fastapi_blog` directory and follow the instructions in the [README](./fastapi_blog/README.md).

---

### Design

This is the base ER diagram that all implementations should fulfill. However, tables related to authentication might vary based on the framework.

![er-diagram](docs/erd.png)

#### Wireframes

![wireframes](docs/triframeblog_wireframes.png)
