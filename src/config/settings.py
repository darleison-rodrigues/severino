import os
from dotenv import load_dotenv

# Load environment variables from a .env file at the project root
# This allows for easy management of sensitive information like API keys
load_dotenv()

# --- API Keys ---
# Retrieve Gemini API key from environment variables.
# It's crucial not to hardcode API keys directly in your code.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please create a .env file or set the variable.")

# --- Local Model Paths ---
# Construct the absolute path to the Gemma GGUF model file.
# This assumes the model is downloaded into the 'data/models/' directory.
# Adjust the filename if you download a different Gemma model version or quantization.
GEMMA_MODEL_FILENAME = "gemma-2b-it.Q4_K_M.gguf"
GEMMA_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), # Go up to the project root (severino/)
    "data", "models", GEMMA_MODEL_FILENAME
)

# Optional: Check if the model file exists (useful for warnings)
if not os.path.exists(GEMMA_MODEL_PATH):
    print(f"Warning: Gemma model not found at {GEMMA_MODEL_PATH}. Local inference might fail until downloaded.")

# --- LLM Settings ---
# Default Gemini model to use for API calls.
# 'gemini-1.5-pro' offers high quality, 'gemini-1.5-flash' is faster and cheaper.
GEMINI_MODEL_NAME = "gemini-1.5-pro"

# Default maximum output tokens for Gemini API generation.
# This helps control cost and response length.
MAX_GEMINI_OUTPUT_TOKENS = 1000

# Cost warning threshold for Gemini API calls in USD.
# If an estimated request cost exceeds this, the user will be warned.
# Adjust this based on your budget and Gemini API pricing (check official docs for current rates).
GEMINI_COST_WARNING_THRESHOLD_USD = 0.05 # Example: $0.05 per request

# --- llama-cpp-python specific settings for Gemma local inference ---
# N_GPU_LAYERS: Number of layers to offload to the GPU.
# -1 means all layers (if they fit). Adjust based on your GPU VRAM (RTX 4070 has 12GB).
# For Gemma 7B Q4_K_M, a value like 30-32 is a good starting point for 12GB VRAM.
N_GPU_LAYERS = 30

# N_CTX: Context window size for the local Gemma model (number of tokens it can process).
# Larger context requires more VRAM. 8192 is a common and good value for Gemma 7B.
N_CTX = 8192

# N_BATCH: Batch size for prompt processing.
# Larger batches can improve throughput but use more VRAM.
N_BATCH = 512

# --- Logging Settings ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "CRITICAL").upper() # Default to CRITICAL to suppress most logs
LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "logs", "severino.log"
)
