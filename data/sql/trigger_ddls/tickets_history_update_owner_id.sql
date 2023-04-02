CREATE TRIGGER tickets_history_update_owner_id
AFTER UPDATE ON tickets
FOR EACH ROW
WHEN (OLD.owner_id != NEW.owner_id)
BEGIN
    INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
    VALUES (NEW.id, NEW.owner_id, 'owner_id', OLD.owner_id, NEW.owner_id);
END;