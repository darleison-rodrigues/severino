from typing import Any, Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ThoughtProcessManager:
    """
    Manages the logging and retrieval of the agent's internal thought processes.
    This includes LLM reasoning steps, tool calls, and intermediate results
    during the Refactor, Break Down, and Compile phases.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._thought_log: List[Dict[str, Any]] = []

    def log_thought(self, step_name: str, description: str, details: Dict[str, Any] = None):
        """
        Logs a step in the agent's thought process.
        Args:
            step_name (str): A concise name for the thought step (e.g., "Refactor: Prompt Interpretation", "Break Down: Sub-task Planning").
            description (str): A brief description of what happened in this step.
            details (Dict[str, Any], optional): Any relevant data or results from this step. Defaults to None.
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "session_id": self.session_id,
            "step_name": step_name,
            "description": description,
            "details": details if details is not None else {}
        }
        self._thought_log.append(log_entry)
        logger.debug(f"Thought logged for session {self.session_id}: {step_name} - {description}")

    def get_thought_log(self) -> List[Dict[str, Any]]:
        """
        Retrieves the entire thought process log for the current session.
        """
        return self._thought_log

    def clear_thought_log(self):
        """
        Clears the thought process log for the current session.
        """
        self._thought_log = []
        logger.debug(f"Thought log cleared for session {self.session_id}.")

# Example Usage (for testing purposes)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    session_id = "test_session_123"
    thought_manager = ThoughtProcessManager(session_id)

    print("\n--- Logging Thoughts ---")
    thought_manager.log_thought("Refactor: Initial Prompt", "User asked to monitor child on balcony.", {"prompt": "Watch child on balcony"})
    thought_manager.log_thought("Break Down: Identify Sub-goals", "Decomposed task into object detection and proximity analysis.", {"sub_goals": ["detect_child", "detect_balcony", "evaluate_proximity"]})
    thought_manager.log_thought("Tool Call: Camera Connect", "Attempting to connect to RTSP stream.", {"tool": "connect_iot_camera", "url": "rtsp://..."})
    thought_manager.log_thought("Compile: Generate Alert", "Child detected near balcony edge, generating alert.", {"alert_type": "SMS", "message": "Child in danger!"})

    print("\n--- Retrieving Thought Log ---")
    for entry in thought_manager.get_thought_log():
        print(f"[{entry["timestamp"]}] {entry["step_name"]}: {entry["description"]} - Details: {entry["details"]}")

    print("\n--- Clearing Thought Log ---")
    thought_manager.clear_thought_log()
    print(f"Log after clearing: {thought_manager.get_thought_log()}")
