

CREATE_LIBRARY_TABLE = """
    CREATE TABLE IF NOT EXISTS library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE NOT NULL,
        chunks_json TEXT,
        title TEXT,
        document_type TEXT,
        summary TEXT,
        metadata_title TEXT,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        last_modified TIMESTAMP NOT NULL
    )
"""

SAVE_DOCUMENT_IN_LIBRARY = """
    INSERT INTO library (
        file_path,
        chunks_json,
        title,
        document_type,
        summary,
        metadata_title,
        created_at,
        updated_at,
        last_modified
    ) VALUES (
        ?, ?, ?, ?, ?, ?,
        DATETIME('now'),  -- created_at
        DATETIME('now'),  -- updated_at
        DATETIME('now')   -- last_modified
    )
    ON CONFLICT(file_path) DO UPDATE SET
        chunks_json = excluded.chunks_json,
        title = excluded.title,
        document_type = excluded.document_type,
        summary = excluded.summary,
        metadata_title = excluded.metadata_title,
        updated_at = DATETIME('now')
"""