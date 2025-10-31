DROP TRIGGER IF EXISTS set_timestamp_projects ON projects;
DROP TRIGGER IF EXISTS set_timestamp_tasks ON tasks;
DROP FUNCTION IF EXISTS trigger_set_timestamp();
DROP TABLE IF EXISTS task_activity_log CASCADE;
DROP TABLE IF EXISTS attachments CASCADE;
DROP TABLE IF EXISTS task_collaborators CASCADE;
DROP TABLE IF EXISTS project_collaborators CASCADE;
DROP TABLE IF EXISTS comment_mentions CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS report_history CASCADE;


ALTER DATABASE task_db SET timezone TO 'UTC';

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    owner_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    recurrence_end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_activity_log (
    id SERIAL PRIMARY KEY,
    task_id INT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INT NOT NULL,
    "timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT
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

CREATE TABLE report_history (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    user_id INT NOT NULL,
    target_user_id INT,
    project_id INT,
    report_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp_projects
BEFORE UPDATE ON projects
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- This tells PostgreSQL to run the function before any UPDATE on 'tasks'
CREATE TRIGGER set_timestamp_tasks
BEFORE UPDATE ON tasks
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

------------------------------------------------------------------
-- SAMPLE DATA MIGRATION
------------------------------------------------------------------

-- Project 1 (Assuming a project context for the first task)
-- Project 1: Owner (2) is auto-added as collaborator
------------------------------------------------------------------
-- STANDARDIZED SAMPLE DATA MIGRATION (Base Time: 2025-10-01 08:00:00 UTC)
------------------------------------------------------------------

-- Project 1 (ID=1)
WITH inserted_project AS (
  INSERT INTO projects (title, description, deadline, owner_id, created_at, updated_at)
  VALUES ('Website Redesign', 'A project to overhaul the company homepage.', '2025-11-15', 2, '2025-10-01 08:00:00', '2025-10-01 08:00:00')
  RETURNING id, owner_id
)
INSERT INTO project_collaborators (project_id, user_id)
SELECT id, owner_id FROM inserted_project;
INSERT INTO project_collaborators (project_id, user_id) VALUES (1, 1), (1, 3);


-- Task 1: Design Homepage (ID=1, Initial Status: ONGOING, P5)
WITH inserted_task AS (
  INSERT INTO tasks (title, description, deadline, status, owner_id, project_id, created_at, updated_at)
  VALUES ('Design Homepage', 'Create wireframes and UI for homepage', '2025-11-02', 'ONGOING', 1, 1, '2025-10-01 08:00:00', '2025-10-01 08:00:00')
  RETURNING id, owner_id
)
INSERT INTO task_collaborators (task_id, user_id)
SELECT id, owner_id FROM inserted_task;
INSERT INTO task_collaborators (task_id, user_id) VALUES (1, 2);


-- Subtasks for Task 1 (ID=2, 3)
WITH inserted_task AS (
  INSERT INTO tasks (title, description, deadline, status, owner_id, project_id, parent_task_id, created_at, updated_at) 
  VALUES ('Wireframe layout', 'Create wireframes', '2025-10-01', 'ONGOING', 1, 1, 1, '2025-10-01 08:00:00', '2025-10-01 08:00:00'),
  ('Define color scheme', 'Design UI', '2025-11-01', 'ONGOING', 1, 1, 1, '2025-10-01 08:00:00', '2025-10-01 08:00:00')
  RETURNING id, owner_id
)
INSERT INTO task_collaborators (task_id, user_id)
SELECT id, owner_id FROM inserted_task;
INSERT INTO task_collaborators (task_id, user_id) VALUES (2, 2);

-- Attachment for Task 1
INSERT INTO attachments (filename, url, task_id) VALUES
('Week 04 Project Instructions', 'Week_04_Project_Instructions.pdf', 1);


-- Task 4: Backend API Setup (ID=4, NO Project ID)
WITH inserted_task AS (
  INSERT INTO tasks (title, description, deadline, status, owner_id, created_at, updated_at)
  VALUES ('Backend API Setup', 'Setup Flask API for task management', '2025-10-05', 'ONGOING', 2, '2025-10-01 08:00:00', '2025-10-01 08:00:00')
  RETURNING id, owner_id
)
INSERT INTO task_collaborators (task_id, user_id)
SELECT id, owner_id FROM inserted_task;
INSERT INTO task_collaborators (task_id, user_id) VALUES (4, 3);

-- Subtasks for Task 4 (ID=5, 6)
WITH inserted_task AS (
  INSERT INTO tasks (title, status, owner_id, parent_task_id, created_at, updated_at) VALUES
  ('Define API endpoints', 'ONGOING', 2, 4, '2025-10-01 08:00:00', '2025-10-01 08:00:00'),
  ('Setup database models', 'UNASSIGNED', 2, 4, '2025-10-01 08:00:00', '2025-10-01 08:00:00'), 
  ('Add in proxy data', 'UNDER_REVIEW', 2, 4, '2025-10-01 08:00:00', '2025-10-01 08:00:00')
  RETURNING id, owner_id
)
INSERT INTO task_collaborators (task_id, user_id)
SELECT id, owner_id FROM inserted_task;
INSERT INTO task_collaborators (task_id, user_id) VALUES (5, 1);
INSERT INTO task_collaborators (task_id, user_id) VALUES (5, 2);
INSERT INTO task_collaborators (task_id, user_id) VALUES (5, 3);
INSERT INTO task_collaborators (task_id, user_id) VALUES (6, 1);
INSERT INTO task_collaborators (task_id, user_id) VALUES (6, 2);
INSERT INTO task_collaborators (task_id, user_id) VALUES (6, 3);
INSERT INTO task_collaborators (task_id, user_id) VALUES (7, 1);
INSERT INTO task_collaborators (task_id, user_id) VALUES (7, 2);
INSERT INTO task_collaborators (task_id, user_id) VALUES (7, 3);

-- Attachment for Task 4
INSERT INTO attachments (filename, url, task_id) VALUES
('Change Document', 'Change_Document_Week_6.pdf', 4);


-- Task 8: Frontend Development (ID=8, Project 1, Initial Status: UNASSIGNED, P5, Owner 3)
WITH inserted_task AS (
  INSERT INTO tasks (title, description, deadline, status, owner_id, project_id, created_at, updated_at)
  VALUES ('Frontend Development', 'Develop the frontend using Vue.js', '2025-11-13', 'UNASSIGNED', 3, 1, '2025-10-01 08:00:00', '2025-10-01 08:00:00')
  RETURNING id, owner_id
)
INSERT INTO task_collaborators (task_id, user_id)
SELECT id, owner_id FROM inserted_task;
INSERT INTO task_collaborators (task_id, user_id) VALUES (8, 1);

-- Noti_004 test (ID=9)
WITH inserted_task AS (
  INSERT INTO tasks (title, description, deadline, status, owner_id, project_id, created_at, updated_at)
  VALUES ('Test 4', 'Unassigned to Ongoing', '2026-11-11', 'UNASSIGNED', 1, 1, '2025-10-01 08:00:00', '2025-10-01 08:00:00')
  RETURNING id, owner_id
)
INSERT INTO task_collaborators (task_id, user_id)
SELECT id, owner_id FROM inserted_task;
INSERT INTO task_collaborators (task_id, user_id) VALUES (9, 1);
INSERT INTO task_collaborators (task_id, user_id) VALUES (9, 2);

-- Subtasks for Task 9 (ID=10)
WITH inserted_task AS (
  INSERT INTO tasks (title, status, owner_id, parent_task_id, created_at, updated_at) VALUES
  ('Testing Subtask', 'ONGOING', 1, 9, '2025-10-01 08:00:00', '2025-10-01 08:00:00')
  RETURNING id, owner_id
)
INSERT INTO task_collaborators (task_id, user_id)
SELECT id, owner_id FROM inserted_task;
INSERT INTO task_collaborators (task_id, user_id) VALUES (10, 1);
INSERT INTO task_collaborators (task_id, user_id) VALUES (10, 2);

-- Noti_006 test (ID=11)
INSERT INTO tasks (title, description, deadline, status, owner_id, project_id, created_at, updated_at)
VALUES ('Test 6', 'Under Review to Completed', '2026-11-11', 'UNDER_REVIEW', 1, 1, '2025-10-01 08:00:00', '2025-10-01 08:00:00');

-- Project 2 (ID=2)
WITH inserted_project AS (
  INSERT INTO projects (title, description, deadline, owner_id, created_at, updated_at)
  VALUES ('Marketing Campaign', 'Plan and execute the fall marketing campaign.', '2025-12-01', 3, '2025-10-01 08:00:00', '2025-10-01 08:00:00')
  RETURNING id, owner_id
)
INSERT INTO project_collaborators (project_id, user_id)
SELECT id, owner_id FROM inserted_project
UNION
SELECT id, 2 FROM inserted_project;


-- Comments (IDs 1-6 assumed sequentially)
INSERT INTO comments (body, author_id, task_id) VALUES
('I''ve uploaded a new mockup in the attachments. Let me know what you think!', 1, 1),
('Looks great! I think the call-to-action button could be a bit more prominent.', 2, 1);
INSERT INTO comments (body, author_id, task_id, parent_comment_id) VALUES
('Good point, I''ll make that adjustment.', 1, 1, 2);
INSERT INTO comments (body, author_id, task_id) VALUES
('Great work everyone. @john_staff can you check the final design and @jane_manager I will approve?', 2, 1);
INSERT INTO comments (body, author_id, task_id) VALUES
('I''ve defined the initial user and task endpoints in the attached markdown file.', 2, 4);
INSERT INTO comments (body, author_id, task_id) VALUES
('Should we include a route for collaborators or handle that within the main task endpoint?', 3, 5);

-- The corresponding mention records for the comment ID 4
INSERT INTO comment_mentions (comment_id, user_id) VALUES
(4, 1),
(4, 3);

-- Task Activity Log (Reflects sequential updates in October 2025, using correct old_values)
INSERT INTO task_activity_log (task_id, user_id, "timestamp", field_changed, old_value, new_value)
VALUES
-- SGT Date: 2025-10-26 (Sunday)
(1, 1, '2025-10-25 16:00:00', 'priority', '5', '8'),               -- Task 1: P5 -> P8
(8, 3, '2025-10-26 12:00:00', 'owner_id', '3', '1'),               -- Task 8: Owner 3 -> 1
-- SGT Date: 2025-10-27 (Monday)
(8, 1, '2025-10-27 15:59:59', 'status', 'Unassigned', 'Ongoing'),  -- Task 8: Unassigned -> Ongoing
-- SGT Date: 2025-10-28 (Tuesday)
(1, 2, '2025-10-27 16:00:00', 'status', 'Ongoing', 'Under Review'), -- Task 1: Ongoing -> Under Review (Correctly follows initial state)
-- SGT Date: 2025-10-29 (Wednesday)
(1, 1, '2025-10-29 07:00:00', 'status', 'Under Review', 'Completed'),-- Task 1: Under Review -> Completed
-- SGT Date: 2025-10-30 (Thursday)
(8, 1, '2025-10-30 08:00:00', 'priority', '5', '6');               -- Task 8: P5 -> P6