CREATE TRIGGER equipment_history_insert
AFTER INSERT ON equipment
FOR EACH ROW
BEGIN
    INSERT INTO equipment_history (equipment_id, user_id, vendor_id, po, comment)
    VALUES (NEW.id, NEW.created_by, NEW.created_vendor_id, NEW.original_po, 'Equipment created');
END;