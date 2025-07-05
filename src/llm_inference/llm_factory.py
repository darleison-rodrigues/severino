from typing import Dict, Type, Any
from src.llm_inference.base_llm import LLMProviderInterface
from src.llm_inference.providers.llama_cpp_provider import LlamaCppProvider

class LLMFactory:
    """
    Factory class to create and manage LLM provider instances.
    """
    _providers: Dict[str, Type[LLMProviderInterface]] = {
        "llama_cpp": LlamaCppProvider,
        # Add other LLM providers here (e.g., "openai": OpenAIProvider)
    }

    @staticmethod
    def register_provider(name: str, provider_class: Type[LLMProviderInterface]):
        """
        Registers a new LLM provider class with the factory.
        """
        if not issubclass(provider_class, LLMProviderInterface):
            raise ValueError("Provider class must inherit from LLMProviderInterface")
        LLMFactory._providers[name] = provider_class

    @staticmethod
    def create_provider(name: str, provider_id: str, config: Dict[str, Any]) -> LLMProviderInterface:
        """
        Creates an instance of the specified LLM provider.
        Args:
            name (str): The name of the provider (e.g., "llama_cpp").
            provider_id (str): A unique ID for this provider instance.
            config (Dict[str, Any]): Configuration dictionary for the provider.
        Returns:
            LLMProviderInterface: An instance of the requested LLM provider.
        Raises:
            ValueError: If the provider name is not registered.
        """
        provider_class = LLMFactory._providers.get(name)
        if not provider_class:
            raise ValueError(f"LLM provider '{name}' not registered.")
        return provider_class(provider_id, config)

# Example Usage (for testing purposes)
if __name__ == "__main__":
    from config.settings import PROJECT_ROOT # Assuming PROJECT_ROOT is still accessible
    import logging
    import os

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Example of creating a LlamaCppProvider
    sample_model_path = os.path.join(PROJECT_ROOT, "data", "models", "gemma-2b-it.Q4_K_M.gguf")
    llm_config = {"model_path": sample_model_path, "n_gpu_layers": 0}

    try:
        llama_provider = LLMFactory.create_provider("llama_cpp", "my_llama_model", llm_config)
        if llama_provider.load_llm():
            response = llama_provider.generate_response("Hello, how are you?", max_tokens=50)
            print(f"\nLLM Response: {response['generated_text']}")
            print(f"LLM Status: {llama_provider.get_status()}")
        else:
            print("Failed to load LLM via factory.")
    except ValueError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("Skipping LLM example: Model file not found. Please download it first.")
