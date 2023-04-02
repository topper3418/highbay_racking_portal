CREATE TABLE IF NOT EXISTS internal_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL, -- Foreign key to departments table
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);