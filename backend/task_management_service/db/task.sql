DROP TABLE IF EXISTS task_collaborators, attachments, comments, subtasks, tasks CASCADE;

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Unassigned',
    owner_id INT NOT NULL
);

CREATE TABLE subtasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Unassigned',
    assignee_id INTEGER,
    task_id INT REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT NOT NULL,
    author_id INT NOT NULL,
    task_id INT REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    task_id INT REFERENCES tasks(id) ON DELETE CASCADE
);

-- Create task_collaborators table for managing collaborators
CREATE TABLE task_collaborators (
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(50) DEFAULT 'collaborator',
    PRIMARY KEY (task_id, user_id)
);

-- Create indexes for better performance
CREATE INDEX idx_task_collaborators_task_id ON task_collaborators(task_id);
CREATE INDEX idx_task_collaborators_user_id ON task_collaborators(user_id);
CREATE INDEX idx_subtasks_assignee_id ON subtasks(assignee_id);

-- Sample Data
-- Task 1
INSERT INTO tasks (title, description, deadline, status, owner_id)
VALUES ('Design Homepage', 'Create wireframes and UI for homepage', '2025-10-01', 'Ongoing', 1);

INSERT INTO subtasks (title, description, status, task_id) VALUES
('Wireframe layout', 'Create initial wireframe structure', 'Ongoing', 1),
('Define color scheme', 'Choose brand colors', 'Ongoing', 1);

INSERT INTO comments (body, author_id, task_id) VALUES
('Remember to align with brand guidelines.', 2, 1),
('Wireframe draft is ready for review.', 3, 1);

INSERT INTO attachments (filename, url, task_id) VALUES
('homepage_mockup.png', 'http://example.com/homepage_mockup.png', 1);

-- Task 2
INSERT INTO tasks (title, description, deadline, status, owner_id)
VALUES ('Backend API Setup', 'Setup Flask API for task management', '2025-10-05', 'Ongoing', 2);

INSERT INTO subtasks (title, description, status, task_id) VALUES
('Define API endpoints', 'Document all REST endpoints', 'Ongoing', 2),
('Setup database models', 'Create SQLAlchemy models', 'Ongoing', 2);

INSERT INTO comments (body, author_id, task_id) VALUES
('Consider using JWT for auth.', 1, 2),
('Database schema looks fine.', 3, 2);

INSERT INTO attachments (filename, url, task_id) VALUES
('api_endpoints.md', 'http://example.com/api_endpoints.md', 2);