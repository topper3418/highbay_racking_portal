CREATE TABLE IF NOT EXISTS orgs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    internal INTEGER NOT NULL -- 0 = external, 1 = internal
);