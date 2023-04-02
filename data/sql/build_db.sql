-- make the lookup tables first
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    role INTEGER NOT NULL, -- Foreign key to roles table
    FOREIGN KEY (role) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS ticket_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ticket_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS equipment_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS due_date_reasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reason TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vendor_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL, -- Foreign key to vendors table
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE TABLE IF NOT EXISTS departments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS internal_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL, -- Foreign key to departments table
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- now the main table
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id INTEGER NOT NULL, -- Foreign key to ticket_types table
    submitter_id NOT NULL, -- Foreign key to internal_contacts table
    submitted INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Unix timestamp
    due_date INTEGER NOT NULL, -- Unix timestamp
    due_date_reason_id INTEGER NOT NULL, -- Foreign key to due_date_reasons table
    status_id INTEGER NOT NULL, -- Foreign key to ticket_status table
    owner_id INTEGER NOT NULL, -- Foreign key to users table
    relevant_equipment INTEGER NOT NULL, -- Foreign key to equipment table
    FOREIGN KEY (type_id) REFERENCES ticket_types(id),
    FOREIGN KEY (submitter_id) REFERENCES internal_contacts(id),
    FOREIGN KEY (due_date_reason_id) REFERENCES due_date_reasons(id),
    FOREIGN KEY (status_id) REFERENCES ticket_status(id),
    FOREIGN KEY (owner_id) REFERENCES users(id),
    FOREIGN KEY (relevant_equipment) REFERENCES equipment(id)
);
-- now the comments table
CREATE TABLE IF NOT EXISTS ticket_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL, -- Foreign key to tickets table
    user_id INTEGER NOT NULL, -- Foreign key to users table
    comment TEXT NOT NULL,
    timestamp INT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Unix timestamp
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
-- now the attachments table
CREATE TABLE IF NOT EXISTS ticket_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL, -- Foreign key to tickets table
    user_id INTEGER NOT NULL, -- Foreign key to users table
    filename TEXT NOT NULL,
    timestamp INT NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Unix timestamp
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
-- now the history table
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
-- Trigger for INSERT
CREATE TRIGGER tickets_history_insert
AFTER INSERT ON tickets
FOR EACH ROW
BEGIN
    INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
    VALUES (NEW.id, NEW.owner_id, 'INSERT', '', NEW.type_id || ',' || NEW.submitter_id || ',' || NEW.submitted || ',' || NEW.due_date || ',' || NEW.due_date_reason_id || ',' || NEW.status_id || ',' || NEW.owner_id);
END;
-- Trigger for UPDATE
CREATE TRIGGER tickets_history_update
AFTER UPDATE ON tickets
FOR EACH ROW
BEGIN
    IF (OLD.type_id != NEW.type_id) THEN
        INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
        VALUES (NEW.id, NEW.owner_id, 'type_id', OLD.type_id, NEW.type_id);
    END IF;
    IF (OLD.submitter_id != NEW.submitter_id) THEN
        INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
        VALUES (NEW.id, NEW.owner_id, 'submitter_id', OLD.submitter_id, NEW.submitter_id);
    END IF;
    IF (OLD.due_date != NEW.due_date) THEN
        INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
        VALUES (NEW.id, NEW.owner_id, 'due_date', OLD.due_date, NEW.due_date);
    END IF;
    IF (OLD.due_date_reason_id != NEW.due_date_reason_id) THEN
        INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
        VALUES (NEW.id, NEW.owner_id, 'due_date_reason_id', OLD.due_date_reason_id, NEW.due_date_reason_id);
    END IF;
    IF (OLD.status_id != NEW.status_id) THEN
        INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
        VALUES (NEW.id, NEW.owner_id, 'status_id', OLD.status_id, NEW.status_id);
    END IF;
    IF (OLD.owner_id != NEW.owner_id) THEN
        INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
        VALUES (NEW.id, NEW.owner_id, 'owner_id', OLD.owner_id, NEW.owner_id);
    END IF;
END;
-- now an equipment table
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
-- now an equipment history table, all changes need a PO, vendor and comment
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
-- now create a trigger for equipment history
CREATE TRIGGER equipment_history_insert
AFTER INSERT ON equipment
FOR EACH ROW
BEGIN
    INSERT INTO equipment_history (equipment_id, user_id, vendor_id, po, comment)
    VALUES (NEW.id, NEW.created_by, NEW.created_vendor_id, NEW.original_po, 'Equipment created');
END;

CREATE TRIGGER equipment_history_update
AFTER UPDATE ON equipment
FOR EACH ROW
BEGIN
    IF (OLD.status_id != NEW.status_id) THEN
        INSERT INTO equipment_history (equipment_id, user_id, vendor_id, po, comment)
        VALUES (NEW.id, NEW.modified_by, NEW.modified_vendor_id, NEW.modified_po, 'Equipment status changed');
    END IF;
    IF (OLD.pc_owner_id != NEW.pc_owner_id) THEN
        INSERT INTO equipment_history (equipment_id, user_id, vendor_id, po, comment)
        VALUES (NEW.id, NEW.modified_by, NEW.modified_vendor_id, NEW.modified_po, 'Equipment owner changed');
    END IF;
    IF (OLD.external_owner_id != NEW.external_owner_id) THEN
        INSERT INTO equipment_history (equipment_id, user_id, vendor_id, po, comment)
        VALUES (NEW.id, NEW.modified_by, NEW.modified_vendor_id, NEW.modified_po, 'Equipment owner changed');
    END IF;
    IF (OLD.nearest_column != NEW.nearest_column) THEN
        INSERT INTO equipment_history (equipment_id, user_id, vendor_id, po, comment)
        VALUES (NEW.id, NEW.modified_by, NEW.modified_vendor_id, NEW.modified_po, 'Equipment location changed');
    END IF;
END;