DROP TABLE IF EXISTS projects, project_tasks, project_collaborators CASCADE;
-- Projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    owner_id INT NOT NULL,                  -- stores the user.id of the project owner
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link table between projects and external tasks
CREATE TABLE project_tasks (
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    task_id INT NOT NULL,                   -- references tasks.id in the Task DB
    PRIMARY KEY (project_id, task_id)
);

-- Link table between projects and external users (collaborators)
CREATE TABLE project_collaborators (
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    user_id INT NOT NULL,                    -- references users.id in the User DB
    role VARCHAR(50),
    PRIMARY KEY (project_id, user_id)
);
