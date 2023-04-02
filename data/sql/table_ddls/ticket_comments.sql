CREATE TABLE IF NOT EXISTS ticket_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL, -- Foreign key to tickets table
    user_id INTEGER NOT NULL, -- Foreign key to users table
    comment TEXT NOT NULL,
    timestamp INT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Unix timestamp
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);