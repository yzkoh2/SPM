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
(3, 'Senior Management');


INSERT INTO teams (id, name, department_id) VALUES 
(1, 'Finance Team 1', 1),
(2, 'Finance Team 2', 1),
(3, 'Tech Team 1', 2),
(4, 'Tech Leadership Team', 2),
(5, 'Executive', 3);

-- Insert a user with the 'staff' role
INSERT INTO users (username, name, password_hash, email, role, team_id) VALUES
-- finance team 1
('john_staff', 'John', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'john.spm.g3@gmail.com', 'STAFF',1),
('jane_manager', 'Jane', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'jane.spm.g3@gmail.com', 'MANAGER',1),
('susan_director', 'Susan', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'c@c.com', 'DIRECTOR', 1),
-- finance team 2
('d_staff', 'D', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'd@d.com', 'STAFF', 2),
('e_manager', 'E', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'e@e.com', 'MANAGER', 2),
('f_staff', 'F', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'f@f.com', 'STAFF', 3),
('g_director', 'G', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'g@g.com', 'DIRECTOR', 4),
('jack_ceo', 'Jack', 'scrypt:32768:8:1$dCPdgoTqcJd1S7lY$5cc719af753d37f8c64580c227d4ce985fe2e1aaf7f8a204293d48d0e45e41479f819d62652d24a477fa65b4f34bb1667641b80bdc697b837e90d2c283bb2b74', 'sm@sm.com', 'SM', 5);


-- password is "a"
