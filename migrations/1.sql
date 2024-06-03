-- 1.sql
-- "todos" table
BEGIN;

CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_finished BOOLEAN DEFAULT FALSE
);

-- "schema_version" table
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

-- Setting schema version to 1
INSERT INTO schema_version (version) VALUES (1);

COMMIT;