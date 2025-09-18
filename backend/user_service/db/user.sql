DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(80) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'staff'
);

-- Insert a user with the 'staff' role
INSERT INTO users (username, password, email, role) VALUES
('john_staff', 'password123', 'john@example.com', 'staff');

-- Insert a user with the 'manager' role
INSERT INTO users (username, password, email, role) VALUES
('jane_manager', 'password123', 'jane@example.com', 'manager');

-- Insert a user with the 'director' role
INSERT INTO users (username, password, email, role) VALUES
('susan_director', 'password123', 'susan@example.com', 'director');