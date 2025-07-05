import os
import sys
from contextlib import contextmanager
from llama_cpp import Llama, LlamaGrammar
from config.settings import GEMMA_MODEL_PATH, N_GPU_LAYERS, N_CTX, N_BATCH
from config.logging_config import logger
from utils.text_processor import TextProcessor

# Global instance of the Gemma LLM to ensure it's loaded only once.
_gemma_llm_instance = None
_text_processor_instance = TextProcessor() # Initialize TextProcessor globally

@contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(os.devnull, 'w') as fnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = fnull, fnull
        try:
            yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

def load_gemma_model():
    """
    Loads the Gemma GGUF model into memory and offloads layers to the GPU.
    This function uses a singleton pattern to ensure the model is loaded only once
    across multiple calls.
    """
    global _gemma_llm_instance
    if _gemma_llm_instance is None:
        if not os.path.exists(GEMMA_MODEL_PATH):
            raise FileNotFoundError(f"Gemma model not found at: {GEMMA_MODEL_PATH}. Please download it.")

        try:
            with suppress_stdout_stderr():
                _gemma_llm_instance = Llama(
                    model_path=GEMMA_MODEL_PATH,
                    n_gpu_layers=N_GPU_LAYERS, # Number of layers to offload to the GPU
                    n_ctx=N_CTX,               # Context window size
                    n_batch=N_BATCH,           # Batch size for prompt processing
                    verbose=False              # Set to True for more detailed loading output from llama.cpp
                )
        except Exception as e:
            _gemma_llm_instance = None # Reset instance on failure
            raise # Re-raise the exception to indicate failure

    return _gemma_llm_instance

def run_gemma_inference(prompt: str, max_tokens: int = 256, temperature: float = 0.7, chat_history: list[str] = None) -> str:
    """
    Runs inference with the locally loaded Gemma model.

    Args:
        prompt (str): The input prompt for the Gemma model.
        max_tokens (int): The maximum number of tokens to generate in the response.
        temperature (float): Controls the creativity/randomness of the output.
                             Higher values (e.g., 0.8) are more creative, lower (e.g., 0.2) are more deterministic.
        chat_history (list[str]): Optional. A list of previous conversational turns.

    Returns:
        str: The generated text from the Gemma model, or an error message.
    """
    llm = load_gemma_model()
    if llm is None:
        return "Error: Gemma model not loaded. Cannot perform inference."

    try:
        # Gemma instruction-tuned models typically expect a specific chat format.
        # This format helps the model understand its role in a conversation.
        # <bos> (beginning of sequence) is often added automatically by llama.cpp.
        # <start_of_turn> and <end_of_turn> are Gemma-specific tokens.
        
        processed_prompt = _text_processor_instance.process_text(prompt)

        full_prompt_parts = []
        if chat_history:
            for turn in chat_history:
                full_prompt_parts.append(turn)
        
        full_prompt_parts.append(f"<start_of_turn>user\n{processed_prompt}<end_of_turn>\n<start_of_turn>model\n")
        formatted_prompt = "".join(full_prompt_parts)

        with suppress_stdout_stderr():
            output = llm(
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<end_of_turn>", "<eos>"], # Gemma's stop tokens to prevent generating too much
                echo=False # Do not echo the input prompt in the output
            )

        # Extract the generated text from the model's output structure.
        generated_text = output["choices"][0]["text"]

        # Clean up any partial stop tokens that might appear at the end of the generation.
        for stop_token in ["<end_of_turn>", "<eos>"]:
            if generated_text.endswith(stop_token):
                generated_text = generated_text[:-len(stop_token)].strip()

        return generated_text
    except Exception as e:
        return f"Error during Gemma inference: {e}"

# Example usage for testing this module directly
if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    # This block will only run if you execute this file directly (e.g., python gemma_local.py)
    # It demonstrates how to load the model and run an inference.
    try:
        # Attempt to load the model (will raise FileNotFoundError if not present)
        model_instance = load_gemma_model()
        if model_instance:
            # Run a sample inference
            sample_prompt = "Tell me a short, funny story about a talking cat."
            response = run_gemma_inference(sample_prompt, max_tokens=150, temperature=0.8)
            console.print(f"\n[bold green]--- Gemma Sample Response ---[/bold green]\n[bold blue]Prompt:[/bold blue] {sample_prompt}\n[bold magenta]Response:[/bold magenta] {response}")

            sample_prompt_2 = "Write a simple Python function to reverse a string."
            response_2 = run_gemma_inference(sample_prompt_2, max_tokens=100, temperature=0.5)
            console.print(f"\n[bold green]--- Gemma Sample Response 2 ---[/bold green]\n[bold blue]Prompt:[/bold blue] {sample_prompt_2}\n[bold magenta]Response:[/bold magenta] {response_2}")

    except FileNotFoundError:
        console.print("\n[bold red]Skipping Gemma inference example: Model file not found. Please download it first.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred during example execution: {e}[/bold red]")
