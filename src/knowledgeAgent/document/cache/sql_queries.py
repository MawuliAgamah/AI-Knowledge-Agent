CREATE_DOCUMENT_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    hash TEXT,
    document_type TEXT,
    title TEXT,
    summary TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_modified TIMESTAMP
)
"""

CREATE_CHUNK_TABLE = """
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    word_count INTEGER,
    token_count INTEGER,
    language TEXT,
    topics TEXT,
    keywords TEXT,
    start_index INTEGER,
    end_index INTEGER,
    previous_chunk_id INTEGER,
    next_chunk_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (previous_chunk_id) REFERENCES chunks(id),
    FOREIGN KEY (next_chunk_id) REFERENCES chunks(id)
)
"""

SAVE_DOCUMENT = """
INSERT INTO documents (
    file_path, hash, document_type, title, summary, 
    created_at, updated_at, last_modified
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(file_path) DO UPDATE SET
    hash = excluded.hash,
    document_type = excluded.document_type,
    title = excluded.title,
    summary = excluded.summary,
    updated_at = excluded.updated_at,
    last_modified = excluded.last_modified
RETURNING id
"""

SAVE_CHUNK = """
INSERT INTO chunks (
    document_id, content, chunk_index, word_count, token_count,
    language, topics, keywords, start_index, end_index,
    previous_chunk_id, next_chunk_id
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

DOCUMENT_EXISTS_QUERY = """
SELECT id FROM documents WHERE file_path = ?
"""

GET_DOCUMENT_WITH_CHUNKS = """
SELECT 
    d.*,
    c.id as chunk_id,
    c.document_id,
    c.content,
    c.chunk_index,
    c.word_count,
    c.token_count,
    c.language,
    c.topics,
    c.keywords,
    c.start_index,
    c.end_index,
    c.previous_chunk_id,
    c.next_chunk_id,
    c.created_at as chunk_created_at
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
WHERE d.file_path = ?
ORDER BY c.chunk_index
"""