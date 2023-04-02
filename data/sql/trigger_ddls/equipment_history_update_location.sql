CREATE TRIGGER equipment_history_update_location
AFTER UPDATE ON equipment
FOR EACH ROW
WHEN (OLD.nearest_column != NEW.nearest_column)
BEGIN
    INSERT INTO equipment_history (equipment_id, user_id, vendor_id, po, comment)
    VALUES (NEW.id, NEW.modified_by, NEW.modified_vendor_id, NEW.modified_po, 'Equipment location changed');
END;