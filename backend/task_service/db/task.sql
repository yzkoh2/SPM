DROP TABLE IF EXISTS attachments;
DROP TABLE IF EXISTS task_collaborators;
DROP TABLE IF EXISTS project_collaborators;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS projects;

-- 1. Create Projects Table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    owner_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Tasks Table (Handles both tasks and subtasks)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Unassigned',
    owner_id INT NOT NULL,
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    parent_task_id INT REFERENCES tasks(id) ON DELETE CASCADE -- Self-referencing key for subtasks
);

-- 3. Create Attachments Table
CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE
);

-- 4. Create Collaborator Junction Tables
CREATE TABLE project_collaborators (
    project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id INT NOT NULL,
    PRIMARY KEY (project_id, user_id)
);

CREATE TABLE task_collaborators (
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INT NOT NULL,
    PRIMARY KEY (task_id, user_id)
);

------------------------------------------------------------------
-- SAMPLE DATA MIGRATION
------------------------------------------------------------------

-- Project 1 (Assuming a project context for the first task)
INSERT INTO projects (title, description, deadline, owner_id)
VALUES ('Website Redesign', 'A project to overhaul the company homepage.', '2025-10-15', 2);

-- Task 1: Design Homepage (and its subtasks)
INSERT INTO tasks (title, description, deadline, status, owner_id, project_id)
VALUES ('Design Homepage', 'Create wireframes and UI for homepage', '2025-10-01', 'ONGOING', 1, 1);

-- Subtasks for Task 1
INSERT INTO tasks (title, description, status, owner_id, project_id, parent_task_id) VALUES
('Wireframe layout', 'Create wireframes', 'ONGOING', 1, 1, 1),
('Define color scheme', 'Design UI', 'ONGOING', 1, 1, 1);

-- Attachment for Task 1
INSERT INTO attachments (filename, url, task_id) VALUES
('homepage_mockup.png', 'http://example.com/homepage_mockup.png', 1);

-- Task 2: Backend API Setup (Standalone task, no project)
INSERT INTO tasks (title, description, deadline, status, owner_id)
VALUES ('Backend API Setup', 'Setup Flask API for task management', '2025-10-05', 'ONGOING', 2);

-- Subtasks for Task 2
INSERT INTO tasks (title, status, owner_id, parent_task_id) VALUES
('Define API endpoints', 'ONGOING', 2, 4),
('Setup database models', 'ONGOING', 2, 4);

-- Attachment for Task 2
INSERT INTO attachments (filename, url, task_id) VALUES
('api_endpoints.md', 'http://example.com/api_endpoints.md', 2);

-- Sample Collaborators
INSERT INTO project_collaborators (project_id, user_id) VALUES
(1, 1), (1, 2), (1, 3);

INSERT INTO task_collaborators (task_id, user_id) VALUES
(1, 1), (1, 2), (2, 2), (2, 3);