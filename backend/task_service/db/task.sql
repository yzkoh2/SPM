DROP TABLE IF EXISTS attachments CASCADE;
DROP TABLE IF EXISTS task_collaborators CASCADE;
DROP TABLE IF EXISTS project_collaborators CASCADE;
DROP TABLE IF EXISTS comment_mentions CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS comments CASCADE;


ALTER DATABASE task_db SET timezone TO 'UTC';

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    owner_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    status VARCHAR(50) DEFAULT 'UNASSIGNED',
    owner_id INT NOT NULL,
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    parent_task_id INT REFERENCES tasks(id) ON DELETE CASCADE, -- Self-referencing key for subtasks
    priority INT DEFAULT 5,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_interval VARCHAR(50),
    recurrence_days INT,
    recurrence_end_date TIMESTAMP
);

CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    author_id INT NOT NULL,
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parent_comment_id INT REFERENCES comments(id) ON DELETE CASCADE
);

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

CREATE TABLE comment_mentions (
    comment_id INT NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    user_id INT NOT NULL,
    PRIMARY KEY (comment_id, user_id)
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
('Week 04 Project Instructions', 'Week_04_Project_Instructions.pdf', 1);

-- Task 2: Backend API Setup (Standalone task, no project)
INSERT INTO tasks (title, description, deadline, status, owner_id)
VALUES ('Backend API Setup', 'Setup Flask API for task management', '2025-10-05', 'ONGOING', 2);

-- Subtasks for Task 2
INSERT INTO tasks (title, status, owner_id, parent_task_id) VALUES
('Define API endpoints', 'ONGOING', 2, 4),
('Setup database models', 'ONGOING', 2, 4);

-- Attachment for Task 2
INSERT INTO attachments (filename, url, task_id) VALUES
('Change Document', 'Change_Document_Week_6.pdf', 2);

-- Sample Collaborators
INSERT INTO project_collaborators (project_id, user_id) VALUES
(1, 1), (1, 2), (1, 3);

INSERT INTO task_collaborators (task_id, user_id) VALUES
(1, 1), (1, 2), (2, 2), (2, 3);

-- Comments for Task 1 ('Design Homepage')
INSERT INTO comments (body, author_id, task_id) VALUES
('I''ve uploaded a new mockup in the attachments. Let me know what you think!', 1, 1),
('Looks great! I think the call-to-action button could be a bit more prominent.', 2, 1);

-- Reply comment
INSERT INTO comments (body, author_id, task_id, parent_comment_id) VALUES
('Good point, I''ll make that adjustment.', 1, 1, 2);

INSERT INTO comments (body, author_id, task_id) VALUES
('Great work everyone. @john_staff can you check the final design and @jane_manager I will approve?', 2, 1);


-- The corresponding mention records for the comment above (id = 4)
INSERT INTO comment_mentions (comment_id, user_id) VALUES
(4, 1), -- Mentions user_id 1
(4, 2); -- Mentions user_id 3

-- Comment for Task 4 ('Backend API Setup')
INSERT INTO comments (body, author_id, task_id) VALUES
('I''ve defined the initial user and task endpoints in the attached markdown file.', 2, 4);

-- Comment for a subtask (task_id 5: 'Define API endpoints')
INSERT INTO comments (body, author_id, task_id) VALUES
('Should we include a route for collaborators or handle that within the main task endpoint?', 3, 5);