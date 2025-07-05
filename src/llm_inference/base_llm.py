from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class LLMProviderInterface(ABC):
    """
    Abstract base class for all Large Language Model providers.
    Defines the common interface for loading an LLM and performing inference.
    """

    def __init__(self, provider_id: str, config: Dict[str, Any]):
        self.provider_id = provider_id
        self.config = config
        self.llm_instance: Optional[Any] = None

    @abstractmethod
    def load_llm(self) -> bool:
        """
        Loads the LLM into memory.
        Returns True if LLM is loaded successfully, False otherwise.
        """
        pass

    @abstractmethod
    def generate_response(self, prompt: str, max_tokens: int, temperature: float, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Generates a response from the LLM.
        Args:
            prompt (str): The input prompt for the LLM.
            max_tokens (int): The maximum number of tokens to generate.
            temperature (float): Controls creativity/randomness.
            chat_history (Optional[List[Dict[str, str]]]): List of previous messages.
        Returns:
            Dict[str, Any]: A dictionary containing 'generated_text' (str) and 'tokens_generated' (int).
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the LLM provider.
        """
        pass
