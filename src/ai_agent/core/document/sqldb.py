
import os
from rich.console import Console
console = Console()
import sqlite3
from ai_agent.core.document.sql_queries import (CREATE_LIBRARY_TABLE,
                                                SAVE_DOCUMENT_IN_LIBRARY,DOCUMENT_EXISTS_QUERY)

class DocumentSQL:
    """Handles SQL operations for documents"""

    def __init__(self):
        self.db_path = "/Users/mawuliagamah/gitprojects/aiModule/databases/sql_lite/document_db.db"
    

    def doc_exists(self, document):  
        """check if the document exits"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(DOCUMENT_EXISTS_QUERY, (document.path,))  
                result = cursor.fetchone()
                return result is not None  # Returns True if document exists, False if not
        except Exception as e:
            console.print(f"[red]Error checking if document exists in database: {e}[/red]")
            return False

    def save_document(self, document):
        from rich.table import Table
        from rich import print as rprint
        import datetime
        import json
        """Persist a fully constructed document to the database"""
        try:
            # Create a table for debug values
            timestamp = datetime.datetime.now()
            table = Table(title="--Debug - Saving Document ", show_header=True)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_column("Type", style="green")
            
            # Add rows with debug information
            table.add_row(
                "Path",
                repr(document.path),
                str(type(document.path))
            )
            table.add_row(
                "Hash",
                repr(document.hash),
                str(type(document.hash))
            )
            table.add_row(
                "Chunks",
                "Content too long to display",
                str(type(document.contents['chunks']))
            )
            table.add_row(
                "No of chunks",
                repr(document.contents['no_of_chunks']),
                str(type(document.contents['no_of_chunks']))
            )
            table.add_row(
                "Doc type",
                repr(document.doc_type),
                str(type(document.doc_type))
            )
            table.add_row(
                "Title",
                repr(document.title),
                str(type(document.title))
            )
            table.add_row(
                "Summary",
                "Content too long to display",
                str(type(document.contents['summary']))
            )
            
            # Add timestamp information to the same table
            table.add_row(
                "Created At",
                str(timestamp),
                str(type(timestamp))
            )
            table.add_row(
                "Updated At",
                str(timestamp),
                str(type(timestamp))
            )
            table.add_row(
                "Last Modified",
                str(timestamp),
                str(type(timestamp))
            )

            # Print the combined table
            console.print()
            console.print(table)
            console.print()

            print(document.contents['chunks'])
            values = (
                document.path,
                document.hash,
                document.contents['number_of_chunks'],
                document.doc_type,
                document.title,
                document.contents['summary'],
                timestamp,
                timestamp,
                timestamp
            )

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(SAVE_DOCUMENT_IN_LIBRARY, values)
            console.print("[bold green]✓[/bold green] DOCUMENT SAVED ")
                
        except sqlite3.Error as e:
            console.print(f"[red]SQLite error: {str(e)}[/red]")
            console.print(f"[red]Error details: {type(e)}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Unexpected error: {str(e)}[/red]")
            console.print(f"[red]Error type: {type(e)}[/red]")
            raise

    def check_document_exists(self):
        """Query DB to check if a document exists"""