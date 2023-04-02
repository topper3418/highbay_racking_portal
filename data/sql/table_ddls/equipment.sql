CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    business_case INTEGER NOT NULL, -- Foreign key to attachments table
    pc_owner_id INTEGER NOT NULL, -- Foreign key to internal_contacts table
    external_owner_id INTEGER NOT NULL, -- Foreign key to external_contacts table
    created_vendor_id INTEGER NOT NULL, -- Foreign key to vendors table
    created_date INTEGER NOT NULL, -- Unix timestamp
    created_by INTEGER NOT NULL, -- Foreign key to users table
    original_po INTEGER NOT NULL, -- Foreign key to attachments table
    status_id INTEGER NOT NULL, -- Foreign key to equipment_status table
    modified_vendor_id INTEGER, -- Foreign key to vendors table
    modified_date INTEGER, -- Unix timestamp
    modified_by INTEGER, -- Foreign key to users table
    modified_po INTEGER, -- Foreign key to attachments table
    primary_image INTEGER NOT NULL, -- Foreign key to attachments table
    nearest_column TEXT NOT NULL, -- column number
    FOREIGN KEY (business_case) REFERENCES ticket_attachments(id),
    FOREIGN KEY (pc_owner_id) REFERENCES internal_contacts(id),
    FOREIGN KEY (external_owner_id) REFERENCES external_contacts(id),
    FOREIGN KEY (created_vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (original_po) REFERENCES ticket_attachments(id),
    FOREIGN KEY (status_id) REFERENCES equipment_status(id),
    FOREIGN KEY (modified_vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (modified_by) REFERENCES users(id),
    FOREIGN KEY (modified_po) REFERENCES ticket_attachments(id),
    FOREIGN KEY (primary_image) REFERENCES ticket_attachments(id)
);