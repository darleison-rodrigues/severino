import unittest
from unittest.mock import MagicMock, patch

from src.llm_inference.base_llm import LLMProviderInterface
from src.llm_inference.llm_factory import LLMFactory

# Mock a concrete LLMProvider for testing the factory
class MockLLMProvider(LLMProviderInterface):
    def load_llm(self) -> bool:
        return True

    def generate_response(self, prompt: str, max_tokens: int, temperature: float, chat_history=None) -> dict:
        return {"generated_text": f"Mock response to {prompt}", "tokens_generated": 5}

    def get_status(self) -> dict:
        return {"status": "mocked"}

class TestLLMFactory(unittest.TestCase):

    def setUp(self):
        # Clear registered providers before each test to ensure isolation
        LLMFactory._providers = {}

    def test_register_provider_success(self):
        LLMFactory.register_provider("mock_llm", MockLLMProvider)
        self.assertIn("mock_llm", LLMFactory._providers)
        self.assertEqual(LLMFactory._providers["mock_llm"], MockLLMProvider)

    def test_register_provider_invalid_class(self):
        with self.assertRaises(ValueError) as cm:
            LLMFactory.register_provider("invalid_llm", MagicMock)
        self.assertIn("Provider class must inherit from LLMProviderInterface", str(cm.exception))

    def test_create_provider_success(self):
        LLMFactory.register_provider("mock_llm", MockLLMProvider)
        config = {"model_path": "/path/to/model"}
        provider = LLMFactory.create_provider("mock_llm", "test_instance", config)
        self.assertIsInstance(provider, MockLLMProvider)
        self.assertEqual(provider.provider_id, "test_instance")
        self.assertEqual(provider.config, config)

    def test_create_provider_not_registered(self):
        config = {"model_path": "/path/to/model"}
        with self.assertRaises(ValueError) as cm:
            LLMFactory.create_provider("non_existent_llm", "test_instance", config)
        self.assertIn("LLM provider 'non_existent_llm' not registered.", str(cm.exception))

    def test_create_provider_with_actual_llama_cpp_provider(self):
        # This test requires llama_cpp_provider to be importable and its dependencies mocked
        from src.llm_inference.providers.llama_cpp_provider import LlamaCppProvider
        LLMFactory.register_provider("llama_cpp", LlamaCppProvider)
        
        # Mock Llama class and os.path.exists for LlamaCppProvider's internal workings
        with patch('src.llm_inference.providers.llama_cpp_provider.Llama'), \
             patch('os.path.exists', return_value=True), \
             patch('src.llm_inference.providers.llama_cpp_provider.open'):
            
            config = {"model_path": "/fake/path/to/model.gguf"}
            provider = LLMFactory.create_provider("llama_cpp", "real_llama_instance", config)
            self.assertIsInstance(provider, LlamaCppProvider)
            self.assertEqual(provider.provider_id, "real_llama_instance")
            self.assertEqual(provider.config, config)
            self.assertTrue(provider.load_llm()) # Test that load_llm can be called

if __name__ == '__main__':
    unittest.main()
