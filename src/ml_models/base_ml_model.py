from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class MLModelInterface(ABC):
    """
    Abstract base class for all Machine Learning model types.
    Defines the common interface for loading a model and performing inference.
    """

    def __init__(self, model_id: str, config: Dict[str, Any]):
        self.model_id = model_id
        self.config = config
        self.model: Optional[Any] = None

    @abstractmethod
    def load_model(self) -> bool:
        """
        Loads the ML model into memory.
        Returns True if model is loaded successfully, False otherwise.
        """
        pass

    @abstractmethod
    def predict(self, data: Any) -> Any:
        """
        Performs inference using the loaded ML model.
        Args:
            data (Any): The input data for prediction. Type depends on the specific model.
        Returns:
            Any: The prediction result. Type depends on the specific model.
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the ML model.
        """
        pass
