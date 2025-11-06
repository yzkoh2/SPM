# Task Management System

A comprehensive microservices-based task management system built with Flask (backend), Vue.js (frontend), and deployed using Docker. The system includes user management, task tracking, project collaboration, file attachments, real-time notifications, and PDF report generation.

## 🚀 Quick Start Guide

### Step 1: Prerequisites
- Install Docker Desktop (includes Docker & Docker Compose)
- Download link: https://www.docker.com/products/docker-desktop

### Step 2: Setup Environment Variables
Create a `.env` file in the project root directory:

```env
# Database Configurations
DATABASE_URL=postgresql://user:user@user_db:5432/user_db
TASK_DATABASE_URL=postgresql://user:user@task_db:5432/task_db
NOTIFICATION_DATABASE_URL=postgresql://user:user@notification_db:5432/notification_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# AWS S3 Configuration
S3_BUCKET_NAME=your-s3-bucket-name
S3_ACCESS_KEY=your-aws-access-key
S3_SECRET_KEY=your-aws-secret-key
S3_REGION=ap-southeast-1

# Email Configuration (Brevo SMTP)
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=your-brevo-username
SMTP_PASSWORD=your-brevo-api-key
SMTP_FROM_EMAIL=noreply@yourdomain.com

# RabbitMQ Configuration
RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
```

### Step 3: Start the Application

```bash
# Navigate to project directory
cd <project-directory>

# Start all services
docker-compose up -d

# Wait for services to initialize (about 30-60 seconds)
# Check if all services are running
docker-compose ps
```

### Step 4: Access the Application

Open your browser and navigate to:
- **Frontend Application**: http://localhost:5173
- **API Documentation (Swagger)**: http://localhost:6008/api-docs/documentation
- **API Gateway**: http://localhost:8000

### Step 5: Login to the System

Use one of the pre-configured test accounts:

| Role | Email | Password | Department |
|------|-------|----------|------------|
| **Staff** | spmg8t3+john@gmail.com | a | Finance Department |
| **Manager** | spmg8t3+jane@gmail.com | a | Finance Department |
| **Director** | spmg8t3+susan@gmail.com | a | Finance Department |
| **HR** | spmg8t3+harry@gmail.com | a | HR |
| **Senior Manager** | spmg8t3+tom@gmail.com | a | Senior Management |

**How to Login:**
1. Go to http://localhost:5173
2. Click on "Login" or you'll be redirected to the login page
3. Enter the email and password from the table above
4. Click "Login"
5. You'll be redirected to the dashboard

### Step 6: Reset Database (If Needed)

To reset all databases to their initial state with test data:

```bash
# On Linux/Mac
chmod +x reset-db.sh
./reset-db.sh

# On Windows
reset-db.bat
```

After resetting, all test users and sample data will be restored.

### Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (WARNING: This deletes all data)
docker-compose down -v
```

---

## ✅ First-Time Setup Checklist

- [ ] **Docker is installed and running**
  ```bash
  docker --version
  docker-compose --version
  ```

- [ ] **All Docker containers are running**
  ```bash
  docker-compose up -d
  docker-compose ps  # All services should show "Up"
  ```

- [ ] **Frontend is accessible**
  - Open http://localhost:5173
  - Should see login page

- [ ] **API documentation is accessible**
  - Open http://localhost:6008/api-docs/documentation
  - Should see Swagger UI

- [ ] **Can login successfully**
  - Email: spmg8t3+john@gmail.com
  - Password: a
  - Should redirect to dashboard

- [ ] **Database reset script works**
  ```bash
  ./reset-db.sh  # Should complete without errors
  ```

---

## ✨ Features

### User Management
- User authentication with JWT tokens
- Role-based access control (Staff, Manager, Director, HR, Senior Management)
- Team and department organization
- User profile management

### Task Management
- Create, read, update, and delete tasks
- Task prioritization (1-10 scale)
- Task status tracking (Unassigned, Ongoing, Under Review, Completed)
- Subtask support with parent-child relationships
- Task collaborator management
- Deadline tracking with overdue notifications

### Project Management
- Project creation and management
- Project-based task organization
- Project collaborators
- Project progress tracking

### Collaboration Features
- Task comments with @mentions
- Reply to comments (threaded discussions)
- Email notifications for mentions
- Task activity logging
- Real-time updates via RabbitMQ

### File Management
- File attachment to tasks
- S3 cloud storage integration
- Secure file upload and download
- Support for multiple file types

### Reporting
- PDF report generation for projects
- Individual user performance reports
- Report history tracking
- Charts and visualizations (task status, priority distribution)

### Notifications
- Email notifications for:
  - Task assignments
  - @mentions in comments
  - Deadline reminders
  - Task status changes
- Beautiful HTML email templates

---

## 🏗 System Architecture

The system consists of the following microservices:

1. **User Service** (Port 6000)
   - User authentication and management
   - Team and department management
   - JWT token generation and verification

2. **Task Service** (Port 6001)
   - Task and project management
   - Comments and attachments
   - Activity logging
   - Report generation

3. **Notification Service** (Port 6003)
   - Email notifications via Brevo SMTP
   - RabbitMQ message consumer
   - Template-based email generation

4. **Frontend** (Port 5173)
   - Vue.js single-page application
   - Responsive UI with Tailwind CSS
   - Real-time updates

5. **Kong API Gateway** (Port 8000)
   - API routing and management
   - CORS handling
   - Load balancing

6. **Swagger Documentation** (Port 6008)
   - Interactive API documentation
   - API testing interface

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (v20.10 or higher)
- **Docker Compose** (v2.0 or higher)
- **Git**

Optional (for local development without Docker):
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

---

## 📚 API Documentation

### Access Swagger Documentation

Once the system is running, access the interactive API documentation at:

**http://localhost:6008/api-docs/documentation**

### API Gateway Endpoints

All API requests should go through the Kong gateway at `http://localhost:8000`:

**User Service:**
- `POST /user/create` - Create a new user
- `POST /user/login` - User login
- `GET /user/verifyJWT` - Verify JWT token
- `GET /user/{user_id}` - Get user by ID
- `GET /user` - Get all users
- `GET /user/teams` - Get all teams
- `GET /user/team/{team_id}` - Get users in a team
- `GET /user/departments` - Get all departments
- `GET /user/department/{dept_id}` - Get users in a department

**Task Service:**
- `GET /tasks` - Get all tasks
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get task by ID
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task
- `GET /tasks/{task_id}/subtasks` - Get subtasks
- `GET /tasks/{task_id}/collaborators` - Get task collaborators
- `GET /tasks/{task_id}/comments` - Get task comments
- `POST /tasks/{task_id}/comments` - Add a comment
- `DELETE /tasks/deletecomment/{comment_id}` - Delete a comment
- `GET /tasks/{task_id}/attachments` - Get task attachments
- `POST /tasks/{task_id}/attachments` - Upload an attachment
- `GET /tasks/{task_id}/attachments/{attachment_id}` - Get attachment
- `DELETE /tasks/{task_id}/attachments/{attachment_id}` - Delete attachment

**Project Service:**
- `GET /projects` - Get all projects
- `POST /projects` - Create a new project
- `GET /projects/{project_id}` - Get project by ID
- `PUT /projects/{project_id}` - Update a project
- `DELETE /projects/{project_id}` - Delete a project
- `GET /projects/user/{user_id}` - Get user's projects
- `POST /projects/{project_id}/collaborators` - Add project collaborator
- `DELETE /projects/{project_id}/collaborators/{collaborator_id}` - Remove collaborator

**Report Service:**
- `GET /reports/project/{project_id}?user_id={user_id}` - Generate project report
- `GET /reports/individual?user_id={user_id}&target_user_id={target_user_id}` - Generate user report
- `GET /reports/history/{user_id}` - Get report history
- `GET /reports/retrieve/{report_id}?user_id={user_id}` - Retrieve a report
- `DELETE /reports/delete/{report_id}?user_id={user_id}` - Delete a report

---

## 📁 Project Structure

```
.
├── backend/
│   ├── user_service/          # User management microservice
│   │   ├── app/
│   │   │   ├── models.py      # Database models
│   │   │   ├── routes.py      # API endpoints
│   │   │   ├── service.py     # Business logic
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   └── user.sql       # Database initialization
│   │   ├── test/
│   │   │   └── test.py        # Unit tests
│   │   ├── config.py
│   │   ├── requirements.txt
│   │   ├── wsgi.py
│   │   └── Dockerfile
│   │
│   ├── task_service/          # Task management microservice
│   │   ├── app/
│   │   │   ├── models.py
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   ├── report/        # Report generation
│   │   │   │   ├── generator_service.py
│   │   │   │   ├── routes.py
│   │   │   │   └── templates/
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   └── task.sql
│   │   ├── test/
│   │   ├── config.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── notification_service/  # Email notification microservice
│       ├── app/
│       │   ├── models.py
│       │   ├── email_service.py
│       │   ├── email_templates.py
│       │   ├── rabbitmq_consumer.py
│       │   └── __init__.py
│       ├── db/
│       │   └── notification.sql
│       ├── config.py
│       ├── requirements.txt
│       ├── run.py
│       └── Dockerfile
│
├── frontend/                  # Vue.js frontend
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/
│   │   ├── stores/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── documentation/             # Swagger API documentation
│   ├── swaggerJson/
│   │   └── documentation.json
│   ├── swagger.js
│   ├── package.json
│   └── Dockerfile
│
├── kong.yml                   # Kong API Gateway configuration
├── docker-compose.yml         # Docker orchestration
├── reset-db.sh               # Database reset script (Linux/Mac)
├── reset-db.bat              # Database reset script (Windows)
├── .env                      # Environment variables (create this)
└── README.md                 # This file
```

---

## 🗄 Database Management

### Quick Database Reset

**On Linux/Mac:**
```bash
chmod +x reset-db.sh
./reset-db.sh
```

**On Windows:**
```cmd
reset-db.bat
```



**After reset, you can login with:**
- spmg8t3+john@gmail.com / a
- spmg8t3+jane@gmail.com / a
- spmg8t3+susan@gmail.com / a
- spmg8t3+harry@gmail.com / a
- spmg8t3+tom@gmail.com / a

### Access PgAdmin

1. Open http://localhost:5434
2. Login with:
   - Email: admin@admin.com
   - Password: admin

### Database Schema

**User Database (user_db):**
- `users` - User accounts and authentication
- `teams` - Team organization
- `departments` - Department structure

**Task Database (task_db):**
- `tasks` - Tasks and subtasks
- `projects` - Project management
- `task_collaborators` - Task-user relationships
- `project_collaborators` - Project-user relationships
- `comments` - Task comments
- `comment_mentions` - @mention tracking
- `attachments` - File attachments
- `task_activity_log` - Task change history
- `reports` - Generated report metadata

**Notification Database (notification_db):**
- `notification_log` - Email notification history
- `notification_preferences` - User notification settings

---

## 🔐 User Roles and Permissions

### Testing Different Roles

**1. Staff (spmg8t3+john@gmail.com / a)**
- Create personal tasks
- View only assigned tasks
- Cannot access Department Schedule

**2. Manager (spmg8t3+jane@gmail.com / a)**
- Access Team Schedule
- Create projects
- Assign tasks to team members

**3. Director (spmg8t3+susan@gmail.com / a)**
- Access Department Schedule
- View multiple teams
- Generate department reports

**4. HR (spmg8t3+harry@gmail.com / a)**
- Access Company Schedule
- View all users
- Generate employee reports

**5. Senior Manager (spmg8t3+tom@gmail.com / a)**
- Full system access
- Executive dashboard
- All reports and analytics

### Login Process

**Web Interface:**
1. Go to http://localhost:5173
2. Enter email and password
3. Click "Login"



