-- Task Service Database Schema
-- Independent microservice - no direct foreign key constraints to user service
-- User validation will be handled via API calls to the user service

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    deadline TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('unassigned', 'ongoing', 'under_review', 'completed')) DEFAULT 'unassigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,  -- User ID from user service
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,           -- User ID from user service
    assigned_to INTEGER           -- User ID from user service
);

-- Create indexes for better performance
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);

-- Task collaborators junction table (many-to-many relationship)
CREATE TABLE task_collaborators (
    task_id INTEGER,
    user_id INTEGER,              -- User ID from user service
    role VARCHAR(50) DEFAULT 'collaborator',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by INTEGER,             -- User ID from user service
    
    PRIMARY KEY (task_id, user_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,  -- User ID from user service
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,           -- User ID from user service
    
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_comments_task_id ON comments(task_id);
CREATE INDEX idx_comments_created_at ON comments(created_at);

-- Attachments table
CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER NOT NULL, -- User ID from user service
    
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Create index for better performance
CREATE INDEX idx_attachments_task_id ON attachments(task_id);

-- Sample task (using user IDs that should exist in user service)
INSERT INTO tasks (title, description, deadline, status, created_by, assigned_to) VALUES 
('Complete project documentation', 'Write comprehensive documentation for the new feature', '2024-12-31 17:00:00', 'ongoing', 1, 2);

-- Sample comment
INSERT INTO comments (task_id, content, created_by) VALUES 
(1, 'Started working on the introduction section', 2);

-- Sample collaborator
INSERT INTO task_collaborators (task_id, user_id, added_by) VALUES 
(1, 3, 1);