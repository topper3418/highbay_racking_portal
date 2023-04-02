CREATE TRIGGER tickets_history_update_due_date
AFTER UPDATE ON tickets
FOR EACH ROW
WHEN (OLD.due_date != NEW.due_date)
BEGIN
    INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
    VALUES (NEW.id, NEW.owner_id, 'due_date', OLD.due_date, NEW.due_date);
END;