from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class ActionInterface(ABC):
    """
    Abstract base class for all action types.
    Defines the common interface for executing an action.
    """

    def __init__(self, action_id: str, config: Dict[str, Any]):
        self.action_id = action_id
        self.config = config

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the action with the given payload.
        Args:
            payload (Dict[str, Any]): Data required to execute the action.
        Returns:
            Dict[str, Any]: A dictionary containing the result of the action execution.
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the action.
        """
        pass
