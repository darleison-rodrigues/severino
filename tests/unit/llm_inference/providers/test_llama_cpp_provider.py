import unittest
import os
from unittest.mock import MagicMock, patch, mock_open

from src.llm_inference.base_llm import LLMProviderInterface
from src.llm_inference.providers.llama_cpp_provider import LlamaCppProvider

class TestLlamaCppProvider(unittest.TestCase):

    def setUp(self):
        self.provider_id = "test_llama_provider"
        self.model_path = "/fake/path/to/model.gguf"
        self.config = {
            "model_path": self.model_path,
            "n_gpu_layers": 0,
            "n_ctx": 2048,
            "n_batch": 512,
            "verbose": False
        }

    def test_llama_cpp_provider_initialization(self):
        provider = LlamaCppProvider(self.provider_id, self.config)
        self.assertIsInstance(provider, LlamaCppProvider)
        self.assertIsInstance(provider, LLMProviderInterface)
        self.assertEqual(provider.provider_id, self.provider_id)
        self.assertEqual(provider.model_path, self.model_path)
        self.assertIsNone(provider.llm_instance)

    def test_llama_cpp_provider_initialization_no_model_path(self):
        with self.assertRaises(ValueError) as cm:
            LlamaCppProvider(self.provider_id, {})
        self.assertIn("Model path must be provided", str(cm.exception))

    @patch('os.path.exists', return_value=True)
    @patch('src.llm_inference.providers.llama_cpp_provider.Llama')
    @patch('src.llm_inference.providers.llama_cpp_provider.open', new_callable=mock_open)
    def test_load_llm_success(self, mock_file_open, mock_llama_class, mock_exists):
        mock_llama_instance = MagicMock()
        mock_llama_class.return_value = mock_llama_instance

        provider = LlamaCppProvider(self.provider_id, self.config)
        self.assertTrue(provider.load_llm())
        self.assertIsNotNone(provider.llm_instance)
        mock_llama_class.assert_called_once_with(
            model_path=self.model_path,
            n_gpu_layers=self.config["n_gpu_layers"],
            n_ctx=self.config["n_ctx"],
            n_batch=self.config["n_batch"],
            verbose=self.config["verbose"]
        )

    @patch('os.path.exists', return_value=False)
    @patch('src.llm_inference.providers.llama_cpp_provider.open', new_callable=mock_open)
    def test_load_llm_model_not_found(self, mock_file_open, mock_exists):
        provider = LlamaCppProvider(self.provider_id, self.config)
        self.assertFalse(provider.load_llm())
        self.assertIsNone(provider.llm_instance)

    @patch('os.path.exists', return_value=True)
    @patch('src.llm_inference.providers.llama_cpp_provider.Llama', side_effect=Exception("LLM init error"))
    @patch('src.llm_inference.providers.llama_cpp_provider.open', new_callable=mock_open)
    def test_load_llm_failure(self, mock_file_open, mock_llama_class, mock_exists):
        provider = LlamaCppProvider(self.provider_id, self.config)
        self.assertFalse(provider.load_llm())
        self.assertIsNone(provider.llm_instance)

    @patch('os.path.exists', return_value=True)
    @patch('src.llm_inference.providers.llama_cpp_provider.Llama')
    @patch('src.llm_inference.providers.llama_cpp_provider.open', new_callable=mock_open)
    def test_generate_response_success(self, mock_file_open, mock_llama_class, mock_exists):
        mock_llama_instance = MagicMock()
        mock_llama_instance.return_value = {
            "choices": [{"text": "Generated response."}] ,
            "usage": {"completion_tokens": 2}
        }
        mock_llama_class.return_value = mock_llama_instance

        provider = LlamaCppProvider(self.provider_id, self.config)
        provider.load_llm()

        prompt = "Hello LLM"
        response = provider.generate_response(prompt, max_tokens=10, temperature=0.7)

        self.assertEqual(response["generated_text"], "Generated response.")
        self.assertEqual(response["tokens_generated"], 2)
        mock_llama_instance.assert_called_once()

    def test_generate_response_llm_not_loaded(self):
        provider = LlamaCppProvider(self.provider_id, self.config)
        response = provider.generate_response("Prompt", max_tokens=10)
        self.assertIn("Error: Local LLM model not loaded", response["generated_text"])
        self.assertEqual(response["tokens_generated"], 0)

    @patch('os.path.exists', return_value=True)
    @patch('src.llm_inference.providers.llama_cpp_provider.Llama')
    @patch('src.llm_inference.providers.llama_cpp_provider.open', new_callable=mock_open)
    def test_get_status_loaded(self, mock_file_open, mock_llama_class, mock_exists):
        mock_llama_instance = MagicMock()
        mock_llama_class.return_value = mock_llama_instance

        provider = LlamaCppProvider(self.provider_id, self.config)
        provider.load_llm()
        status = provider.get_status()

        self.assertEqual(status["provider_id"], self.provider_id)
        self.assertEqual(status["type"], "LlamaCppProvider")
        self.assertTrue(status["model_loaded"])
        self.assertEqual(status["model_path"], self.model_path)
        self.assertEqual(status["n_gpu_layers"], self.config["n_gpu_layers"])
        self.assertEqual(status["n_ctx"], self.config["n_ctx"])

    def test_get_status_not_loaded(self):
        provider = LlamaCppProvider(self.provider_id, self.config)
        status = provider.get_status()

        self.assertEqual(status["provider_id"], self.provider_id)
        self.assertEqual(status["type"], "LlamaCppProvider")
        self.assertFalse(status["model_loaded"])
        self.assertEqual(status["model_path"], self.model_path)
        self.assertEqual(status["n_gpu_layers"], self.config["n_gpu_layers"])
        self.assertEqual(status["n_ctx"], self.config["n_ctx"])

if __name__ == '__main__':
    unittest.main()
