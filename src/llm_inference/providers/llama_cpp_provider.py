import os
import sys
from contextlib import contextmanager
from llama_cpp import Llama
from typing import Any, Dict, List, Optional
from ..base_llm import LLMProviderInterface

# Assuming TextProcessor will be part of a Refactor step or passed in
# from utils.text_processor import TextProcessor

class LlamaCppProvider(LLMProviderInterface):
    """
    LLM provider for local GGUF models using llama-cpp-python.
    Implements the LLMProviderInterface.
    """

    def __init__(self, provider_id: str, config: Dict[str, Any]):
        super().__init__(provider_id, config)
        self.model_path = config.get("model_path")
        self.n_gpu_layers = config.get("n_gpu_layers", 0)
        self.n_ctx = config.get("n_ctx", 2048)
        self.n_batch = config.get("n_batch", 512)
        self.verbose = config.get("verbose", False)
        self.llm_instance: Optional[Llama] = None

        if not self.model_path:
            raise ValueError("Model path must be provided in LLM provider configuration.")

    @contextmanager
    def _suppress_stdout_stderr(self):
        """A context manager that redirects stdout and stderr to devnull"""
        with open(os.devnull, 'w') as fnull:
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = fnull, fnull
            try:
                yield
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr

    def load_llm(self) -> bool:
        """
        Loads a local GGUF model into memory and offloads layers to the GPU.
        Returns True if model is loaded successfully, False otherwise.
        """
        if self.llm_instance is not None:
            print(f"LLM '{self.provider_id}' already loaded.")
            return True

        if not os.path.exists(self.model_path):
            print(f"Error: Local LLM model not found at: {self.model_path}. Please download it.")
            return False

        try:
            with self._suppress_stdout_stderr():
                self.llm_instance = Llama(
                    model_path=self.model_path,
                    n_gpu_layers=self.n_gpu_layers,
                    n_ctx=self.n_ctx,
                    n_batch=self.n_batch,
                    verbose=self.verbose
                )
            print(f"LLM '{self.provider_id}' loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading LLM '{self.provider_id}': {e}")
            self.llm_instance = None
            return False

    def generate_response(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Runs inference with the locally loaded LLM.
        """
        if self.llm_instance is None:
            return {"generated_text": "Error: Local LLM model not loaded. Cannot perform inference.", "tokens_generated": 0}

        try:
            # Instruction-tuned models typically expect a specific chat format.
            # This format helps the model understand its role in a conversation.
            # <bos> (beginning of sequence) is often added automatically by llama.cpp.
            # <start_of_turn> and <end_of_turn> are common tokens for instruction-tuned models.
            
            # Assuming prompt is already processed or will be processed by a higher layer (Refactor)
            processed_prompt = prompt # Placeholder for now

            full_prompt_parts = []
            if chat_history:
                for turn in chat_history:
                    # Assuming chat_history is a list of {'role': 'user'/'assistant', 'content': '...'}
                    full_prompt_parts.append(f"<start_of_turn>{turn['role']}\n{turn['content']}<end_of_turn>\n")
            
            full_prompt_parts.append(f"<start_of_turn>user\n{processed_prompt}<end_of_turn>\n<start_of_turn>model\n")
            formatted_prompt = "".join(full_prompt_parts)

            with self._suppress_stdout_stderr():
                output = self.llm_instance(
                    prompt=formatted_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=["<end_of_turn>", "<eos>"], # Common stop tokens to prevent generating too much
                    echo=False # Do not echo the input prompt in the output
                )

            generated_text = output["choices"][0]["text"]
            tokens_generated = output["usage"]["completion_tokens"]

            # Clean up any partial stop tokens that might appear at the end of the generation.
            for stop_token in ["<end_of_turn>", "<eos>"]:
                if generated_text.endswith(stop_token):
                    generated_text = generated_text[:-len(stop_token)].strip()

            return {"generated_text": generated_text, "tokens_generated": tokens_generated}
        except Exception as e:
            return {"generated_text": f"Error during LLM inference: {e}", "tokens_generated": 0}

    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the LLM provider.
        """
        return {
            "provider_id": self.provider_id,
            "type": "LlamaCppProvider",
            "model_loaded": self.llm_instance is not None,
            "model_path": self.model_path,
            "n_gpu_layers": self.n_gpu_layers,
            "n_ctx": self.n_ctx
        }

# Example Usage (for testing purposes)
if __name__ == "__main__":
    from config.settings import PROJECT_ROOT # Assuming PROJECT_ROOT is still accessible for example
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Define a sample model path for testing
    sample_model_path = os.path.join(PROJECT_ROOT, "data", "models", "gemma-2b-it.Q4_K_M.gguf")

    # Example configuration for the LLM provider
    llm_config = {
        "model_path": sample_model_path,
        "n_gpu_layers": 0, # Adjust based on your GPU
        "n_ctx": 2048,
        "n_batch": 512
    }

    llm_provider = LlamaCppProvider(provider_id="gemma_local", config=llm_config)

    if llm_provider.load_llm():
        sample_prompt = "Tell me a short, funny story about a talking cat."
        response = llm_provider.generate_response(sample_prompt, max_tokens=150, temperature=0.8)
        print(f"\n--- Local LLM Sample Response ---")
        print(f"Prompt: {sample_prompt}")
        print(f"Response: {response['generated_text']}")
        print(f"Tokens generated: {response['tokens_generated']}")

        sample_prompt_2 = "Write a simple Python function to reverse a string."
        chat_history = [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I am doing well, thank you!"}
        ]
        response_2 = llm_provider.generate_response(sample_prompt_2, max_tokens=100, temperature=0.5, chat_history=chat_history)
        print(f"\n--- Local LLM Sample Response 2 ---")
        print(f"Prompt: {sample_prompt_2}")
        print(f"Chat History: {chat_history}")
        print(f"Response: {response_2['generated_text']}")
        print(f"Tokens generated: {response_2['tokens_generated']}")

        print(f"\nLLM Status: {llm_provider.get_status()}")
    else:
        print("Failed to load LLM. Check model path and configuration.")
