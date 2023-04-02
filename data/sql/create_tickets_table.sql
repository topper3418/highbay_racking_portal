CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    submitter TEXT NOT NULL,
    submitted INT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Unix timestamp
    due_date INT NOT NULL, -- Unix timestamp
    due_date_reason TEXT NOT NULL
);