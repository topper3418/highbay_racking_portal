CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id INTEGER NOT NULL, -- Foreign key to ticket_types table
    submitter_id NOT NULL, -- Foreign key to internal_contacts table
    submitted INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Unix timestamp
    due_date INTEGER NOT NULL, -- Unix timestamp
    due_date_reason_id INTEGER NOT NULL, -- Foreign key to due_date_reasons table
    status_id INTEGER NOT NULL, -- Foreign key to ticket_status table
    owner_id INTEGER NOT NULL, -- Foreign key to users table
    equipment_id INTEGER, -- Foreign key to equipment table
    FOREIGN KEY (type_id) REFERENCES ticket_types(id),
    FOREIGN KEY (submitter_id) REFERENCES internal_contacts(id),
    FOREIGN KEY (due_date_reason_id) REFERENCES due_date_reasons(id),
    FOREIGN KEY (status_id) REFERENCES ticket_status(id),
    FOREIGN KEY (owner_id) REFERENCES users(id),
    FOREIGN KEY (equipment_id) REFERENCES equipment(id)
);