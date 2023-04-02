CREATE TABLE IF NOT EXISTS equipment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL, -- Foreign key to equipment table
    user_id INTEGER NOT NULL, -- Foreign key to users table
    vendor_id INTEGER NOT NULL, -- Foreign key to vendors table
    po INTEGER NOT NULL, -- Foreign key to attachments table
    comment TEXT NOT NULL,
    timestamp INT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Unix timestamp
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (po) REFERENCES ticket_attachments(id)
);