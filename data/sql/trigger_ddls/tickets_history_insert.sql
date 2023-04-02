CREATE TRIGGER tickets_insert_history
AFTER INSERT ON tickets
FOR EACH ROW
BEGIN
    INSERT INTO ticket_history (ticket_id, user_id, field, old_value, new_value)
    VALUES (NEW.id, NEW.owner_id, 'INSERT', '', NEW.type_id || ',' || NEW.submitter_id || ',' || NEW.submitted || ',' || NEW.due_date || ',' || NEW.due_date_reason_id || ',' || NEW.status_id || ',' || NEW.owner_id);
END;