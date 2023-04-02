CREATE TRIGGER tickets_history_update_type_id
AFTER UPDATE ON tickets
FOR EACH ROW
WHEN (OLD.type_id != NEW.type_id)
BEGIN
    INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
    VALUES (NEW.id, NEW.owner_id, 'type_id', OLD.type_id, NEW.type_id);
END;
