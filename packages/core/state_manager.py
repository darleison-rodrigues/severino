from typing import Any, Dict, List, Optional
import json
import os

class StateManager:
    """
    Manages conversational context and long-running sessions.
    This can be extended to persist state to a database or file system.
    """

    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self._conversation_history: List[Dict[str, Any]] = []
        self._session_data: Dict[str, Any] = {}
        # In a real application, you might load state from a persistent store here
        self._load_state()

    def _load_state(self):
        """
        Loads the session state from a persistent store (e.g., a JSON file).
        For simplicity, this example uses a local file. In production, consider
        Cloudflare D1 or another suitable database.
        """
        file_path = self._get_state_file_path()
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    state = json.load(f)
                    self._conversation_history = state.get("history", [])
                    self._session_data = state.get("data", {})
                print(f"State loaded for session '{self.session_id}' from {file_path}")
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from state file {file_path}. Starting with empty state.")
            except Exception as e:
                print(f"Error loading state: {e}")

    def _save_state(self):
        """
        Saves the current session state to a persistent store.
        """
        file_path = self._get_state_file_path()
        state = {
            "history": self._conversation_history,
            "data": self._session_data
        }
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"State saved for session '{self.session_id}' to {file_path}")

    def _get_state_file_path(self) -> str:
        """
        Returns the file path for the session state.
        """
        # Using a simple 'data' directory for state files
        # In a real project, this path should be configurable and secure
        return os.path.join("data", "sessions", f"{self.session_id}.json")

    def add_message(self, role: str, content: str):
        """
        Adds a message to the conversation history.
        """
        self._conversation_history.append({"role": role, "content": content})
        self._save_state()

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves the conversation history.
        limit: Optional maximum number of messages to retrieve (most recent).
        """
        if limit is None:
            return self._conversation_history
        return self._conversation_history[-limit:]

    def update_session_data(self, key: str, value: Any):
        """
        Updates a specific piece of data in the session.
        """
        self._session_data[key] = value
        self._save_state()

    def get_session_data(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a specific piece of data from the session.
        """
        return self._session_data.get(key, default)

    def clear_session(self):
        """
        Clears the conversation history and session data.
        """
        self._conversation_history = []
        self._session_data = {}
        self._save_state()
        print(f"Session '{self.session_id}' cleared.")

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Create a StateManager for a specific session
    session_manager = StateManager(session_id="dev_workflow_123")

    # Add some messages to the history
    session_manager.add_message("user", "What is the current project status?")
    session_manager.add_message("assistant", "The project is in the planning phase.")

    # Update some session-specific data
    session_manager.update_session_data("project_name", "Severino CLI")
    session_manager.update_session_data("current_task", "Implement Core Package Foundations")

    # Retrieve history and data
    print("\n--- Conversation History ---")
    for msg in session_manager.get_history():
        print(f"{msg['role']}: {msg['content']}")

    print("\n--- Session Data ---")
    print(f"Project Name: {session_manager.get_session_data("project_name")}")
    print(f"Current Task: {session_manager.get_session_data("current_task")}")
    print(f"Non-existent Key: {session_manager.get_session_data("non_existent", "Default Value")}")

    # Simulate another interaction in the same session
    print("\n--- Another Interaction ---")
    session_manager.add_message("user", "Can you remind me of the current task?")
    print(f"Current task from session data: {session_manager.get_session_data("current_task")}")

    # Clear the session
    # session_manager.clear_session()

    # Verify state is cleared (if clear_session was uncommented)
    # new_session_manager = StateManager(session_id="dev_workflow_123")
    # print("\n--- History after clearing (should be empty) ---")
    # print(new_session_manager.get_history())
