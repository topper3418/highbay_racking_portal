CREATE VIEW all_tickets_view AS
SELECT 
    t.id,
    tt.type as type,
    u1.username as submitter,
    strftime('%Y-%m-%d %H:%M:%S', t.submitted, 'unixepoch') as submitted,
    strftime('%Y-%m-%d', t.due_date, 'unixepoch') as due_date,
    r.reason as due_date_reason,
    ts.status as status,
    u2.username as owner,
    e.name as equipment
FROM tickets t
LEFT JOIN due_date_reasons r 
       ON r.id = t.due_date_reason_id
LEFT JOIN users u1 
       ON u1.id = t.submitter_id
LEFT JOIN ticket_types tt 
       ON tt.id = t.type_id
LEFT JOIN ticket_status ts 
       ON ts.id = t.status_id
LEFT JOIN users u2 
       ON u2.id = t.owner_id
LEFT JOIN equipment e 
       ON e.id = t.equipment_id
ORDER BY submitted DESC