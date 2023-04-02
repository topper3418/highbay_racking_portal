CREATE TRIGGER tickets_history_update_status_id
AFTER UPDATE ON tickets
FOR EACH ROW
WHEN (OLD.status_id != NEW.status_id)
BEGIN
    INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
    VALUES (NEW.id, NEW.owner_id, 'status_id', OLD.status_id, NEW.status_id);
END;