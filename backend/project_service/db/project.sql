-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS project_tasks CASCADE;
DROP TABLE IF EXISTS project_collaborators CASCADE;
DROP TABLE IF EXISTS projects CASCADE;

-- Projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    owner_id INT NOT NULL,                  -- stores the user.id of the project owner (no FK constraint)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link table between projects and external tasks
CREATE TABLE project_tasks (
    project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_id INT NOT NULL,                   -- references tasks.id in the Task DB (no FK constraint)
    PRIMARY KEY (project_id, task_id)
);

-- Link table between projects and external users (collaborators)
CREATE TABLE project_collaborators (
    project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id INT NOT NULL,                   -- references users.id in the User DB (no FK constraint)
    role VARCHAR(50),
    PRIMARY KEY (project_id, user_id)
);

-- Indexes for better query performance on external IDs
CREATE INDEX idx_project_tasks_task_id ON project_tasks(task_id);
CREATE INDEX idx_project_collaborators_user_id ON project_collaborators(user_id);
CREATE INDEX idx_projects_owner_id ON projects(owner_id);