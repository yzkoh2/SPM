-- Task Service Database Schema with Subtasks
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
    created_by INTEGER NOT NULL,  -- Original creator (never changes)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,           -- Last person to update the task
    owner_id INTEGER NOT NULL,    -- Current owner (changes when task is reassigned)
    assigned_to INTEGER           -- Current assignee (can be null for unassigned tasks)
);

-- Create indexes for better performance
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_owner_id ON tasks(owner_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);

-- Subtasks table
CREATE TABLE subtasks (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) CHECK (status IN ('unassigned', 'ongoing', 'under_review', 'completed')) DEFAULT 'unassigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,  -- User ID from user service
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,           -- User ID from user service
    assigned_to INTEGER,          -- User ID from user service (can be null)
    order_index INTEGER DEFAULT 0, -- For ordering subtasks
    
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Create indexes for subtasks
CREATE INDEX idx_subtasks_task_id ON subtasks(task_id);
CREATE INDEX idx_subtasks_status ON subtasks(status);
CREATE INDEX idx_subtasks_assigned_to ON subtasks(assigned_to);
CREATE INDEX idx_subtasks_order ON subtasks(task_id, order_index);

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

-- Comments table (can be for tasks OR subtasks)
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER,              -- Can be null if comment is on subtask
    subtask_id INTEGER,           -- Can be null if comment is on task
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,  -- User ID from user service
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,           -- User ID from user service
    
    -- Constraint: comment must be on either task OR subtask, not both or neither
    CHECK ((task_id IS NOT NULL AND subtask_id IS NULL) OR (task_id IS NULL AND subtask_id IS NOT NULL)),
    
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (subtask_id) REFERENCES subtasks(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_comments_task_id ON comments(task_id);
CREATE INDEX idx_comments_subtask_id ON comments(subtask_id);
CREATE INDEX idx_comments_created_at ON comments(created_at);

-- Attachments table (can be for tasks OR subtasks)
CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER,              -- Can be null if attachment is on subtask
    subtask_id INTEGER,           -- Can be null if attachment is on task
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER NOT NULL, -- User ID from user service
    
    -- Constraint: attachment must be on either task OR subtask, not both or neither
    CHECK ((task_id IS NOT NULL AND subtask_id IS NULL) OR (task_id IS NULL AND subtask_id IS NOT NULL)),
    
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (subtask_id) REFERENCES subtasks(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_attachments_task_id ON attachments(task_id);
CREATE INDEX idx_attachments_subtask_id ON attachments(subtask_id);

-- Sample data demonstrating the relationships

-- Sample tasks
INSERT INTO tasks (title, description, deadline, status, created_by, owner_id, assigned_to) VALUES 
('Build User Authentication System', 'Implement complete user auth with JWT', '2024-12-31 17:00:00', 'ongoing', 1, 1, 2),
('Design Homepage', 'Create wireframes and mockups for homepage', '2024-11-30 15:00:00', 'unassigned', 1, 1, NULL),
('Database Optimization', 'Optimize queries and add proper indexing', '2024-10-30 12:00:00', 'ongoing', 2, 3, 3);

-- Sample subtasks for task 1 (User Authentication System)
INSERT INTO subtasks (task_id, title, description, status, created_by, assigned_to, order_index) VALUES 
(1, 'Design user schema', 'Create database schema for users table', 'completed', 1, 2, 1),
(1, 'Implement JWT middleware', 'Create middleware for JWT token validation', 'ongoing', 1, 2, 2),
(1, 'Create login endpoint', 'Build POST /auth/login endpoint', 'unassigned', 1, NULL, 3),
(1, 'Create registration endpoint', 'Build POST /auth/register endpoint', 'unassigned', 1, NULL, 4),
(1, 'Add password hashing', 'Implement bcrypt for password security', 'ongoing', 1, 2, 5);

-- Sample subtasks for task 2 (Design Homepage)
INSERT INTO subtasks (task_id, title, description, status, created_by, assigned_to, order_index) VALUES 
(2, 'Research competitor designs', 'Analyze 5 competitor homepages', 'unassigned', 1, NULL, 1),
(2, 'Create wireframes', 'Low-fidelity wireframes for desktop and mobile', 'unassigned', 1, NULL, 2),
(2, 'Design high-fidelity mockups', 'Create pixel-perfect designs in Figma', 'unassigned', 1, NULL, 3);

-- Sample comments on tasks and subtasks
INSERT INTO comments (task_id, content, created_by) VALUES 
(1, 'This is a critical feature for our MVP launch', 1),
(2, 'Make sure the design aligns with our brand guidelines', 1);

INSERT INTO comments (subtask_id, content, created_by) VALUES 
(1, 'Schema looks good, approved!', 1),
(2, 'Don''t forget to handle token expiration', 1),
(6, 'Check out Stripe''s homepage for inspiration', 1);

-- Sample collaborators
INSERT INTO task_collaborators (task_id, user_id, role, added_by) VALUES 
(1, 3, 'reviewer', 1),
(2, 2, 'designer', 1),
(3, 1, 'advisor', 3);

-- Sample attachments
INSERT INTO attachments (task_id, file_name, file_path, file_size, mime_type, uploaded_by) VALUES 
(1, 'auth_requirements.pdf', '/uploads/tasks/1/auth_requirements.pdf', 245760, 'application/pdf', 1),
(2, 'brand_guidelines.pdf', '/uploads/tasks/2/brand_guidelines.pdf', 1048576, 'application/pdf', 1);

INSERT INTO attachments (subtask_id, file_name, file_path, file_size, mime_type, uploaded_by) VALUES 
(1, 'user_schema.sql', '/uploads/subtasks/1/user_schema.sql', 2048, 'text/plain', 2),
(6, 'competitor_analysis.xlsx', '/uploads/subtasks/6/competitor_analysis.xlsx', 524288, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 1);