CREATE TRIGGER tickets_history_update_due_date_reason_id
AFTER UPDATE ON tickets
FOR EACH ROW
WHEN (OLD.due_date_reason_id != NEW.due_date_reason_id)
BEGIN
    INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
    VALUES (NEW.id, NEW.owner_id, 'due_date_reason_id', OLD.due_date_reason_id, NEW.due_date_reason_id);
END;