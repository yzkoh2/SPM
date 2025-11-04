DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    name VARCHAR(80) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Staff',
    team_id INTEGER REFERENCES teams(id)
);

INSERT INTO departments (id, name) VALUES 
(1, 'Finance Department'),
(2, 'Tech Department'),
(3, 'HR'),
(4, 'Senior Management');


INSERT INTO teams (id, name, department_id) VALUES 
(1, 'Finance Team 1', 1),
(2, 'Finance Team 2', 1),
(3, 'Finance Leadership Team', 1),
(4, 'Tech Team 1', 2),
(5, 'Tech Team 2', 2),
(6, 'Tech Leadership Team', 2),
(7, 'HR Team', 3),
(8, 'Senior Management Team', 4);

-- Insert a user with the 'staff' role
INSERT INTO users (username, name, password_hash, email, role, team_id) VALUES
-- finance team 1
('john_staff', 'John', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+john@gmail.com', 'STAFF',1),
('jane_manager', 'Jane', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+jane@gmail.com', 'MANAGER',1),
('susan_director', 'Susan', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+susan@gmail.com', 'DIRECTOR', 3),
('toby_staff', 'Toby', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+toby@gmail.com', 'STAFF',1),

-- finance team 2
('paul_staff', 'Paul', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+paul@gmail.com', 'STAFF',2),
('lily_staff', 'Lily', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+lily@gmail.com', 'STAFF',2),
('sam_manager', 'Sam', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+sam@gmail.com', 'MANAGER',2),
-- finance leadership team

-- tech team 1
('alice_staff', 'Alice', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+alice@gmail.com', 'STAFF',4),
('bob_staff', 'Bob', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+bob@gmail.com', 'STAFF',4),
('carol_manager', 'Carol', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+carol@gmail.com', 'MANAGER',4),
-- tech team 2
('dave_staff', 'Dave', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+dave@gmail.com', 'STAFF',5),
('eva_staff', 'Eva', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+eva@gmail.com', 'STAFF',5),
('frank_manager', 'Frank', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+frank@gmail.com', 'MANAGER',5),
-- tech leadership team
('grace_director', 'Grace', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+grace@gmail.com', 'DIRECTOR', 6),

-- hr team
('harry_hr', 'Harry', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+harry@gmail.com', 'HR', 7),
-- senior management team
('tom_sm', 'Tom', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'spmg8t3+tom@gmail.com', 'SM', 8);


-- password is "a"
