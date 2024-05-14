/// Schema //

CREATE TABLE Recruiter (
id SERIAL PRIMARY KEY,
  username VARCHAR(25),
  password TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL
    CHECK (position('@' IN email) > 1)
);

CREATE TABLE Companies (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  industry TEXT NOT NULL,
  location TEXT NOT NULL
);

CREATE TABLE Applicants (
  id SERIAL PRIMARY KEY,
  username VARCHAR(25),
  password TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone VARCHAR(20),
  email TEXT NOT NULL
    CHECK (position('@' IN email) > 1),
  job_title TEXT NOT NULL,
  company_id INTEGER,
  FOREIGN KEY (company_id) REFERENCES Companies(id)
);

CREATE TABLE Jobs (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  salary INTEGER CHECK (salary >= 0),
  company_id INTEGER,
  FOREIGN KEY (company_id) REFERENCES Companies(id)
);

CREATE TABLE Interviews (
  id SERIAL PRIMARY KEY,
  application_id INTEGER,
  company_id INTEGER,
  notes TEXT NOT NULL,
  FOREIGN KEY (application_id) REFERENCES Applicants(id),
  FOREIGN KEY (company_id) REFERENCES Companies(id)
);


/// Database ///


INSERT INTO Recruiter (username, password, first_name, last_name, email)
VALUES ('testuser',
        '$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q',
        'Test',
        'User',
        'joel@joelburton.com');


INSERT INTO Companies (name, industry, location)
VALUES ('Bauer-Gallagher', 'Law', 'RI'),
        ('Jones Agency', 'Marketing', 'RI'),
        ('Bill Construction', 'Construction', 'RI');


INSERT INTO Applicants (username, password, first_name, last_name, phone, email, job_title)
VALUES ('applicant1',
        '$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q',
        'Sam',
        'Lang',
        '508-234-2343',
        'sam@joelburton.com',
        'Marketing'), ('applicant2',
        '$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q',
        'Lam',
        'Sang',
        '508-234-9876',
        'lam@joelburton.com',
        'Assembler'), ('applicant3',
        '$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q',
        'Mo',
        'Lang',
        '860-345-2354',
        'mo@joelburton.com',
        'Accountant');


INSERT INTO Jobs (title, salary, company_id)
VALUES ( 'Marketing Specialist', 110000, 2),
        ( 'Laborer', 90000, 3);


INSERT INTO Interviews (application_id, company_id, notes)
VALUES ( 1, 2, 'Sam interviewed with Greg from Jones Agency for the Marketing role' );


