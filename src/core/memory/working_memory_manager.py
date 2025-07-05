from typing import Any, Dict, List, Optional
import logging
import os
from .long_term_memory_manager import LongTermMemoryManager

logger = logging.getLogger(__name__)

class WorkingMemoryManager:
    """
    Manages conversational context and long-running sessions using a SQLite backend.
    """

    def __init__(self, session_id: str = "default_session", project_root: str = None):
        self.session_id = session_id
        # Determine the project root for the database path
        if project_root is None:
            # Fallback if not provided, assuming current working directory for DB location
            # In a real scenario, this should be passed from the CLI command
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

        db_dir = os.path.join(project_root, ".severino", "knowledge")
        db_path = os.path.join(db_dir, "mnemonic.db")
        self.long_term_memory_manager = LongTermMemoryManager(db_path)

        # Ensure the session exists in the database
        if not self.long_term_memory_manager.get_session(self.session_id):
            self.long_term_memory_manager.create_session(self.session_id, project_root)
            logger.info(f"New session '{self.session_id}' created in LongTermMemoryManager.")
        else:
            logger.info(f"Session '{self.session_id}' loaded from LongTermMemoryManager.")

    def add_message(self, role: str, content: str):
        """
        Adds a message to the conversation history.
        """
        self.long_term_memory_manager.add_message(self.session_id, role, content)
        logger.info(f"Message added to session '{self.session_id}'.")

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves the conversation history.
        limit: Optional maximum number of messages to retrieve (most recent).
        """
        return self.long_term_memory_manager.get_messages(self.session_id, limit)

    def update_session_data(self, key: str, value: Any):
        """
        Updates a specific piece of data in the session.
        """
        # SQLite stores text, so convert complex types to JSON string
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.long_term_memory_manager.set_session_data(self.session_id, key, str(value))
        logger.info(f"Session data '{key}' updated for session '{self.session_id}'.")

    def get_session_data(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a specific piece of data from the session.
        """
        value = self.long_term_memory_manager.get_session_data(self.session_id, key)
        if value is None:
            return default
        # Attempt to parse JSON if it looks like one
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def clear_session(self):
        """
        Clears the conversation history and session data.
        """
        self.long_term_memory_manager.clear_session_data(self.session_id)
        logger.info(f"Session '{self.session_id}' cleared in LongTermMemoryManager.")

    # New methods for code entities and relationships (facade for MnemonicManager)
    def add_code_entity(self, path: str, type: str, name: str, checksum: str, last_modified: str, embedding: Optional[List[float]] = None) -> int:
        return self.long_term_memory_manager.add_code_entity(self.session_id, path, type, name, checksum, last_modified, embedding)

    def get_code_entity(self, path: str) -> Optional[Dict[str, Any]]:
        return self.long_term_memory_manager.get_code_entity(path)

    def update_code_entity_checksum(self, path: str, new_checksum: str, new_last_modified: str):
        self.long_term_memory_manager.update_code_entity_checksum(path, new_checksum, new_last_modified)

    def add_relationship(self, source_entity_id: int, target_entity_id: int, type: str):
        self.long_term_memory_manager.add_relationship(self.session_id, source_entity_id, target_entity_id, type)

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Configure basic logging for standalone execution
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a WorkingMemoryManager for a specific session
    session_manager = WorkingMemoryManager(session_id="dev_workflow_123", project_root=os.getcwd())

    # Add some messages to the history
    session_manager.add_message("user", "What is the current project status?")
    session_manager.add_message("assistant", "The project is in the planning phase.")

    # Update some session-specific data
    session_manager.update_session_data("project_name", "Severino CLI")
    session_manager.update_session_data("current_task", "Implement Mnemonic Manager")

    # Retrieve history and data
    logger.info("\n--- Conversation History ---")
    for msg in session_manager.get_history():
        logger.info(f"{msg['role']}: {msg['content']}")

    logger.info("\n--- Session Data ---")
    logger.info(f"Project Name: {session_manager.get_session_data("project_name")}")
    logger.info(f"Current Task: {session_manager.get_session_data("current_task")}")
    logger.info(f"Non-existent Key: {session_manager.get_session_data("non_existent", "Default Value")}")

    # Simulate another interaction in the same session
    logger.info("\n--- Another Interaction ---")
    session_manager.add_message("user", "Can you remind me of the current task?")
    logger.info(f"Current task from session data: {session_manager.get_session_data("current_task")}")

    # Clear the session
    # session_manager.clear_session()

    # Verify state is cleared (if clear_session was uncommented)
    # new_session_manager = WorkingMemoryManager(session_id="dev_workflow_123")
    # logger.info("--- History after clearing (should be empty) ---")
    # logger.info(new_session_manager.get_history())