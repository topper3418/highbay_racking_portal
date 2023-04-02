CREATE TABLE IF NOT EXISTS ticket_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL, -- Foreign key to tickets table
    user_id INTEGER NOT NULL, -- Foreign key to users table
    field TEXT NOT NULL,
    old_value TEXT NOT NULL,
    new_value TEXT NOT NULL,
    timestamp INT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Unix timestamp
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);