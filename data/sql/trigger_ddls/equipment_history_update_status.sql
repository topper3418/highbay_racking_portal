CREATE TRIGGER equipment_history_update_status
AFTER UPDATE ON equipment
FOR EACH ROW
WHEN (OLD.status_id != NEW.status_id)
BEGIN
    INSERT INTO equipment_history (equipment_id, user_id, vendor_id, po, comment)
    VALUES (NEW.id, NEW.modified_by, NEW.modified_vendor_id, NEW.modified_po, 'Equipment status changed');
END;
