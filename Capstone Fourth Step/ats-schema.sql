CREATE TABLE recruiters (
  id SERIAL PRIMARY KEY,
  username VARCHAR(25),
  password TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL CHECK (POSITION('@' IN email) > 1)

);

CREATE TABLE companies (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  industry TEXT NOT NULL,
  location TEXT NOT NULL
);

CREATE TABLE applicants (
  id SERIAL PRIMARY KEY,
  username VARCHAR(25),
  password TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone VARCHAR(20),
  email TEXT NOT NULL CHECK (POSITION('@' IN email) > 1),
  job_title TEXT NOT NULL,
  company_id INTEGER,
  FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE jobs (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  salary INTEGER CHECK (salary >= 0),
  company_id INTEGER,
  company_name TEXT UNIQUE NOT NULL,
  FOREIGN KEY (company_name) REFERENCES companies(name),
  FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE interviews ( 
  id SERIAL PRIMARY KEY,
  application_id INTEGER,
  company_id INTEGER,
  notes VARCHAR(150),
  FOREIGN KEY (application_id) REFERENCES applicants(id),
  FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE applied ( 
  id SERIAL PRIMARY KEY,
  application_id INTEGER,
  job_id INTEGER,
  applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (application_id) REFERENCES applicants(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id)
);


CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  notes VARCHAR(150) NOT NULL,
  applicant_id INTEGER,
  recruiter_id INTEGER,
  FOREIGN KEY (applicant_id) REFERENCES applicants(id),
  FOREIGN KEY (recruiter_id) REFERENCES recruiters(id)
);



/* Database */


INSERT INTO recruiters (username, password, first_name, last_name, email)
VALUES ('testuser',
        '$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q',
        'Test',
        'User',
        'joel@joelburton.com');


INSERT INTO companies (name, industry, location)
VALUES ('Bauer-Gallagher', 'Law', 'RI'),
        ('Jones Agency', 'Marketing', 'RI'),
        ('Bill Construction', 'Construction', 'RI');


INSERT INTO applicants (username, password, first_name, last_name, phone, email, job_title)
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


INSERT INTO jobs (title, salary, company_id, company_name)
VALUES ( 'Marketing Specialist', 110000, 2, 'Jones Agency'),
        ( 'Laborer', 90000, 3, 'Bill Construction');


INSERT INTO interviews (application_id, company_id, notes)
VALUES ( 1, 2, 'Sam interviewed with Greg from Jones Agency for the Marketing role' ),
        ( 4, 2, 'Jon with Edwin from Jones Agency for the Marketing role' );


INSERT INTO applied (application_id, job_id, applied_at)
VALUES (4, 2, CURRENT_TIMESTAMP);

INSERT INTO tasks (notes, applicant_id)
VALUES ('my task is first', 11 );