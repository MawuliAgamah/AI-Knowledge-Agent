import os
from rich.console import Console
console = Console()
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from .sql_queries import (
    CREATE_DOCUMENT_TABLE,
    CREATE_CHUNK_TABLE,
    SAVE_DOCUMENT,
    SAVE_CHUNK,
    DOCUMENT_EXISTS_QUERY,
    GET_DOCUMENT_WITH_CHUNKS
)

class SqlLite:
    """Handles SQL operations for documents and chunks"""

    def __init__(self, db_path=None):
        # Set default path in project's data directory
        if db_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            db_path = project_root / "data" / "document_db.db"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = str(db_path)
        console.print(f"[bold blue]Using database at: {self.db_path}[/bold blue]")
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(CREATE_DOCUMENT_TABLE)
                cursor.execute(CREATE_CHUNK_TABLE)
                conn.commit()
                console.print("[bold green]✓[/bold green] Database initialized successfully")
        except Exception as e:
            console.print(f"[red]Error initializing database: {e}[/red]")
            raise

    def doc_exists(self, document_path: str) -> bool:  
        """Check if the document exists"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(DOCUMENT_EXISTS_QUERY, (document_path,))  
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            console.print(f"[red]Error checking if document exists: {e}[/red]")
            return False

    def save_document(self, document: Any) -> bool:
        """Save document and its chunks to the database"""
        try:
            timestamp = datetime.now()
            
            # Debug information
            self._print_debug_info(document, timestamp)
            console.print(f"[yellow]Attempting to save document: {document.file_path}[/yellow]")
            console.print(f"[blue]Using database at: {self.db_path}[/blue]")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                try:
                    # Start transaction
                    cursor.execute("BEGIN TRANSACTION")
                    console.print("[yellow]Started database transaction[/yellow]")
                    
                    # Save document and get its ID
                    doc_values = (
                        document.file_path,
                        document.hash if hasattr(document, 'hash') else None,
                        document.file_type,
                        document.title,
                        document.metadata.summary if hasattr(document.metadata, 'summary') else None,
                        timestamp,
                        timestamp,
                        timestamp
                    )
                    
                    console.print(f"[yellow]Saving document with values: {doc_values}[/yellow]")
                    cursor.execute(SAVE_DOCUMENT, doc_values)
                    document_id = cursor.fetchone()[0]  # Get the returned ID
                    console.print(f"[green]Saved document with ID: {document_id}[/green]")
                    
                    # Delete existing chunks for this document
                    cursor.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
                    console.print(f"[yellow]Deleted existing chunks for document {document_id}[/yellow]")
                    
                    # Save chunks
                    chunk_ids = []  # Store chunk IDs for linking
                    if hasattr(document, 'textChunks') and document.textChunks:
                        console.print(f"[yellow]Saving {len(document.textChunks)} chunks[/yellow]")
                        for i, chunk in enumerate(document.textChunks):
                            chunk_values = (
                                document_id,
                                chunk.content,
                                i,  # chunk_index
                                chunk.metadata.word_count,
                                chunk.metadata.token_count if hasattr(chunk.metadata, 'token_count') else None,
                                chunk.metadata.language,
                                json.dumps(chunk.metadata.topics) if chunk.metadata.topics else None,
                                json.dumps(chunk.metadata.keywords) if chunk.metadata.keywords else None,
                                chunk.metadata.start_index,
                                chunk.metadata.end_index,
                                None,  # previous_chunk_id - will be updated
                                None   # next_chunk_id - will be updated
                            )
                            console.print(f"[yellow]Saving chunk {i} with values: {chunk_values}[/yellow]")
                            cursor.execute(SAVE_CHUNK, chunk_values)
                            chunk_ids.append(cursor.lastrowid)
                            console.print(f"[green]Saved chunk with ID: {cursor.lastrowid}[/green]")
                    else:
                        console.print("[red]No chunks found in document[/red]")
                    
                    # Update chunk links
                    if len(chunk_ids) > 1:
                        console.print("[yellow]Updating chunk links[/yellow]")
                        for i, chunk_id in enumerate(chunk_ids):
                            prev_id = chunk_ids[i-1] if i > 0 else None
                            next_id = chunk_ids[i+1] if i < len(chunk_ids)-1 else None
                            
                            cursor.execute("""
                                UPDATE chunks 
                                SET previous_chunk_id = ?, next_chunk_id = ?
                                WHERE id = ?
                            """, (prev_id, next_id, chunk_id))
                    
                    # Commit transaction
                    conn.commit()
                    console.print("[bold green]✓[/bold green] Document and chunks saved successfully")
                    return True
                    
                except Exception as e:
                    # Rollback on error
                    conn.rollback()
                    console.print(f"[red]Error during save, rolling back: {e}[/red]")
                    raise e
                
        except sqlite3.Error as e:
            console.print(f"[red]SQLite error: {str(e)}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Unexpected error: {str(e)}[/red]")
            raise

    def get_document_with_chunks(self, document_path: str) -> Optional[Dict]:
        """Get document and its chunks from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(GET_DOCUMENT_WITH_CHUNKS, (document_path,))
                results = cursor.fetchall()
                
                if not results:
                    return None
                
                # First row contains document info
                doc_data = results[0]
                document = {
                    "id": doc_data[0],
                    "file_path": doc_data[1],
                    "hash": doc_data[2],
                    "document_type": doc_data[3],
                    "title": doc_data[4],
                    "summary": doc_data[5],
                    "created_at": doc_data[6],
                    "updated_at": doc_data[7],
                    "last_modified": doc_data[8],
                    "chunks": []
                }
                
                # Process chunks
                for row in results:
                    if row[9]:  # Check if chunk data exists
                        chunk = {
                            "id": row[9],
                            "document_id": row[10],
                            "content": row[11],
                            "chunk_index": row[12],
                            "word_count": row[13],
                            "token_count": row[14],
                            "language": row[15],
                            "topics": json.loads(row[16]) if row[16] else [],
                            "keywords": json.loads(row[17]) if row[17] else [],
                            "start_index": row[18],
                            "end_index": row[19],
                            "previous_chunk_id": row[20],
                            "next_chunk_id": row[21]
                        }
                        document["chunks"].append(chunk)
                return document
                
        except Exception as e:
            console.print(f"[red]Error retrieving document: {e}[/red]")
            return None

    def _print_debug_info(self, document: Any, timestamp: datetime) -> None:
        """Print debug information about the document"""
        from rich.table import Table
        
        table = Table(title="--Debug - Saving Document", show_header=True)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Type", style="green")
        
        # Document info
        table.add_row("Path", repr(document.file_path), str(type(document.file_path)))
        table.add_row("Type", repr(document.file_type), str(type(document.file_type)))
        table.add_row("Title", repr(document.title), str(type(document.title)))
        table.add_row("Chunks", str(len(document.textChunks)), str(type(document.textChunks)))
        
        # Timestamps
        table.add_row("Created At", str(timestamp), str(type(timestamp)))
        table.add_row("Updated At", str(timestamp), str(type(timestamp)))
        table.add_row("Last Modified", str(timestamp), str(type(timestamp)))
        
        console.print()
        console.print(table)
        console.print()

    def query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Execute a custom query"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                results = cursor.fetchall()
                return results
        except Exception as e:
            console.print(f"[red]Error executing query: {e}[/red]")
            raise
