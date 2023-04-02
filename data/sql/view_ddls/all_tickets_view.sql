CREATE VIEW all_tickets_vew AS
SELECT 
    id,
    tt.type as type,
    u1.name as submitter,
    strftime('%Y-%m-%d %H:%M:%S', submitted, 'unixepoch') as submitted,
    strftime('%Y-%m-%d', due_date, 'unixepoch') as due_date,
    r.reason as due_date_reason,
    ts.status as status,
    u2.name as owner,
    e.name as equipment
FROM tickets t
LEFT JOIN due_date_reasons r 
       ON r.id = t.due_date_reason_id
LEFT JOIN users u1 
       ON u1.id = t.submitter_id
LEFT JOIN ticket_types tt 
       ON tickttet_types.id = t.type_id
LEFT JOIN ticket_status ts 
       ON ts.id = t.status_id
LEFT JOIN users u2 
       ON u2.id = t.owner_id
LEFT JOIN equipment e 
       ON e.id = t.equipment_id
ORDER BY submitted DESC