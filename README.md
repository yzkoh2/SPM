# Task Management System

A comprehensive microservices-based task management system built with Flask (backend), Vue.js (frontend), and deployed using Docker.

## 🚀 Quick Start Guide

This guide will get you up and running in a few minutes.

### Step 1: Prerequisites

- **Docker Desktop**: Make sure Docker is installed and running on your system.
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

### Step 2: Setup Environment Variables

Create a `.env` file in the root of the project directory by copying the example below.

```sh
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
EOL
```

### Step 3: Start the Application

```bash
# Start all services in detached mode
docker-compose up --build -d

# Wait for services to initialize (about 30-60 seconds)
# Check if all services are running
docker-compose ps
```

### Step 4: Access the Application

- **Frontend Application**: [http://localhost:5173](http://localhost:5173)
- **API Documentation**: [http://localhost:6008/api-docs/documentation](http://localhost:6008/api-docs/documentation)
- **API Gateway**: `http://localhost:8000`

### Step 5: Login Credentials

Use one of the pre-configured test accounts to log in. The password for all accounts is `a`.

| Role | Email | Department |
| :--- | :--- | :--- |
| **Staff** | `spmg8t3+john@gmail.com` | Finance Department |
| **Manager** | `spmg8t3+jane@gmail.com` | Finance Department |
| **Director** | `spmg8t3+susan@gmail.com` | Finance Department |
| **HR** | `spmg8t3+harry@gmail.com` | HR |
| **Senior Manager** | `spmg8t3+tom@gmail.com` | Senior Management |

### Step 6: Reset Database (If Needed)

To reset all databases to their initial state with test data:

```bash
# On Linux/Mac
chmod +x reset-db.sh
./reset-db.sh

# On Windows
reset-db.bat
```

### Step 7: Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (WARNING: This deletes all data)
docker-compose down -v
```

---

<details>
<summary>✅ First-Time Setup Checklist</summary>

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
</details>

<details>
<summary>✨ Features</summary>

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
</details>

<details>
<summary>🏗 System Architecture</summary>

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
</details>

<details>
<summary>📁 Project Structure</summary>

```
.
├── backend/
│   ├── user_service/
│   ├── task_service/
│   └── notification_service/
├── frontend/
├── documentation/
├── kong.yml
├── docker-compose.yml
├── reset-db.sh
├── reset-db.bat
└── README.md
```
</details>


<details>
<summary>📚 API Documentation</summary>

Access the interactive API documentation at:
**[http://localhost:6008/api-docs/documentation](http://localhost:6008/api-docs/documentation)**

All API requests are routed through the Kong gateway at `http://localhost:8000`.
</details>

<details>
<summary>🗄 Database Management</summary>

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

### Access PgAdmin

1. Open http://localhost:5434
2. Login with:
   - **Email**: `admin@admin.com`
   - **Password**: `admin`
</details>
