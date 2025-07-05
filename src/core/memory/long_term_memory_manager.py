import sqlite3
import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

class LongTermMemoryManager:
    """
    Manages the SQLite database for mnemonic files (enhanced knowledge graph).
    Stores session data, conversation history, and code entity information.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """
        Initializes the SQLite database and creates necessary tables if they don't exist.
        """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time TEXT,
                    end_time TEXT,
                    current_project_path TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    timestamp TEXT,
                    role TEXT,
                    content TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS code_entities (
                    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    path TEXT UNIQUE,
                    type TEXT,
                    name TEXT,
                    checksum TEXT,
                    last_modified TEXT,
                    embedding TEXT, -- New column for storing embeddings as JSON string
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    source_entity_id INTEGER,
                    target_entity_id INTEGER,
                    type TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                    FOREIGN KEY (source_entity_id) REFERENCES code_entities(entity_id),
                    FOREIGN KEY (target_entity_id) REFERENCES code_entities(entity_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_data (
                    session_id TEXT,
                    key TEXT,
                    value TEXT,
                    PRIMARY KEY (session_id, key),
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            conn.commit()

    def _execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """
        Helper to execute a query and return results.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()

    # --- Session Management ---
    def create_session(self, session_id: str, project_path: str):
        now = datetime.now().isoformat()
        self._execute_query(
            "INSERT INTO sessions (session_id, start_time, current_project_path) VALUES (?, ?, ?)",
            (session_id, now, project_path)
        )

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        rows = self._execute_query("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        if rows:
            # Assuming order: session_id, start_time, end_time, current_project_path
            return {
                "session_id": rows[0][0],
                "start_time": rows[0][1],
                "end_time": rows[0][2],
                "current_project_path": rows[0][3]
            }
        return None

    def update_session_end_time(self, session_id: str):
        now = datetime.now().isoformat()
        self._execute_query("UPDATE sessions SET end_time = ? WHERE session_id = ?", (now, session_id))

    # --- Message Management ---
    def add_message(self, session_id: str, role: str, content: str):
        now = datetime.now().isoformat()
        self._execute_query(
            "INSERT INTO messages (session_id, timestamp, role, content) VALUES (?, ?, ?, ?)",
            (session_id, now, role, content)
        )

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT timestamp, role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC"
        params = (session_id,)
        if limit:
            query += f" LIMIT ?"
            params = (session_id, limit)
        rows = self._execute_query(query, params)
        return [{"timestamp": r[0], "role": r[1], "content": r[2]} for r in rows]

    # --- Code Entity Management ---
    def add_code_entity(self, session_id: str, path: str, type: str, name: str, checksum: str, last_modified: str, embedding: Optional[List[float]] = None) -> int:
        embedding_str = json.dumps(embedding) if embedding is not None else None
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO code_entities (session_id, path, type, name, checksum, last_modified, embedding) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (session_id, path, type, name, checksum, last_modified, embedding_str)
            )
            return cursor.lastrowid

    def get_code_entity(self, path: str) -> Optional[Dict[str, Any]]:
        rows = self._execute_query("SELECT entity_id, session_id, path, type, name, checksum, last_modified, embedding FROM code_entities WHERE path = ?", (path,))
        if rows:
            # Assuming order: entity_id, session_id, path, type, name, checksum, last_modified, embedding
            embedding_data = rows[0][7]
            embedding_list = json.loads(embedding_data) if embedding_data else None
            return {
                "entity_id": rows[0][0],
                "session_id": rows[0][1],
                "path": rows[0][2],
                "type": rows[0][3],
                "name": rows[0][4],
                "checksum": rows[0][5],
                "last_modified": rows[0][6],
                "embedding": embedding_list
            }
        return None

    def update_code_entity_checksum(self, path: str, new_checksum: str, new_last_modified: str):
        self._execute_query(
            "UPDATE code_entities SET checksum = ?, last_modified = ? WHERE path = ?",
            (new_checksum, new_last_modified, path)
        )

    # --- Relationship Management ---
    def add_relationship(self, session_id: str, source_entity_id: int, target_entity_id: int, type: str):
        self._execute_query(
            "INSERT INTO relationships (session_id, source_entity_id, target_entity_id, type) VALUES (?, ?, ?, ?)",
            (session_id, source_entity_id, target_entity_id, type)
        )

    # --- Generic Session Data ---
    def set_session_data(self, session_id: str, key: str, value: str):
        self._execute_query(
            "INSERT OR REPLACE INTO session_data (session_id, key, value) VALUES (?, ?, ?)",
            (session_id, key, value)
        )

    def get_session_data(self, session_id: str, key: str) -> Optional[str]:
        rows = self._execute_query("SELECT value FROM session_data WHERE session_id = ? AND key = ?", (session_id, key))
        if rows:
            return rows[0][0]
        return None

    def clear_session_data(self, session_id: str):
        self._execute_query("DELETE FROM messages WHERE session_id = ?", (session_id,))
        self._execute_query("DELETE FROM code_entities WHERE session_id = ?", (session_id,))
        self._execute_query("DELETE FROM relationships WHERE session_id = ?", (session_id,))
        self._execute_query("DELETE FROM session_data WHERE session_id = ?", (session_id,))
        self._execute_query("DELETE FROM sessions WHERE session_id = ?", (session_id,))

# Example Usage (for testing purposes)
if __name__ == "__main__":
    db_file = os.path.join(os.getcwd(), ".severino", "test_mnemonic.db")
    manager = MnemonicManager(db_file)

    # Clear previous test data
    if os.path.exists(db_file):
        os.remove(db_file)
        manager = MnemonicManager(db_file) # Re-initialize after deletion

    session_id = "test_session_123"
    project_path = "/path/to/my/project"

    print(f"\n--- Creating Session {session_id} ---")
    manager.create_session(session_id, project_path)
    session = manager.get_session(session_id)
    print(f"Session created: {session}")

    print("\n--- Adding Messages ---")
    manager.add_message(session_id, "user", "Hello, Severino!")
    manager.add_message(session_id, "assistant", "How can I help you?")
    messages = manager.get_messages(session_id)
    print(f"Messages: {messages}")

    print("\n--- Adding Code Entities ---")
    entity1_id = manager.add_code_entity(session_id, "/path/to/my/project/main.py", "file", "main.py", "abc123def", datetime.now().isoformat())
    entity2_id = manager.add_code_entity(session_id, "/path/to/my/project/utils.py", "file", "utils.py", "xyz456uvw", datetime.now().isoformat())
    print(f"Entity 1 ID: {entity1_id}, Entity 2 ID: {entity2_id}")

    entity = manager.get_code_entity("/path/to/my/project/main.py")
    print(f"Retrieved Entity: {entity}")

    print("\n--- Adding Relationships ---")
    if entity1_id and entity2_id:
        manager.add_relationship(session_id, entity1_id, entity2_id, "imports")
        print("Relationship added: main.py imports utils.py")

    print("\n--- Setting Session Data ---")
    manager.set_session_data(session_id, "current_task", "Implement Mnemonic Manager")
    task = manager.get_session_data(session_id, "current_task")
    print(f"Current Task: {task}")

    print("\n--- Clearing Session Data ---")
    manager.clear_session_data(session_id)
    session_after_clear = manager.get_session(session_id)
    messages_after_clear = manager.get_messages(session_id)
    print(f"Session after clear: {session_after_clear}")
    print(f"Messages after clear: {messages_after_clear}")
    print("Mnemonic Manager test complete.")