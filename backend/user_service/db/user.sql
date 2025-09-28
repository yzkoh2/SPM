DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(80) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'staff'
);

-- Insert a user with the 'staff' role
INSERT INTO users (username, name, password, email, role) VALUES
('john_staff', 'John', '$2b$12$L5e3VZsUYTJ5p9g6rBRZf.GBy/FHxg/CLnSdvfAVmOy9RslkUz/LC', 'a@a.com', 'staff');

-- Insert a user with the 'manager' role
INSERT INTO users (username, name, password, email, role) VALUES
('jane_manager', 'Jane', '$2b$12$L5e3VZsUYTJ5p9g6rBRZf.GBy/FHxg/CLnSdvfAVmOy9RslkUz/LC', 'b@b.com', 'manager');

-- Insert a user with the 'director' role
INSERT INTO users (username, name, password, email, role) VALUES
('susan_director', 'Susan', '$2b$12$L5e3VZsUYTJ5p9g6rBRZf.GBy/FHxg/CLnSdvfAVmOy9RslkUz/LC', 'c@c.com', 'director');

-- password is "a"