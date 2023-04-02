CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role INTEGER NOT NULL, -- Foreign key to roles table
    FOREIGN KEY (role) REFERENCES roles(id)
);