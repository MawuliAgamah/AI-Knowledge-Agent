

CREATE_LIBRARY_TABLE = """CREATE TABLE IF NOT EXISTS library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    hash TEXT,
    no_of_chunks INTEGER,
    document_type TEXT,
    title TEXT,
    summary TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)"""

SAVE_DOCUMENT_IN_LIBRARY = """
    INSERT INTO library (
        file_path,
        hash,
        no_of_chunks,
        document_type,
        title,
        summary,
        created_at,
        updated_at,
        last_modified
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    ON CONFLICT(file_path) DO UPDATE SET
        hash = excluded.hash,
        no_of_chunks = excluded.no_of_chunks,
        title = excluded.title,
        document_type = excluded.document_type,
        summary = excluded.summary,
        updated_at = DATETIME('now')
"""

DOCUMENT_EXISTS_QUERY = """
    SELECT rowid 
    FROM library 
    WHERE file_path = ?
"""