# CLI Commands

Severino provides a set of command-line interface (CLI) commands to interact with its AI capabilities. These commands are built using the `click` library.

## `severino gemma`

Runs local inference using the Gemma model. Ideal for quick insights, coding assistance, or general tasks where speed and privacy are key.

### Usage

```bash
severino gemma <prompt> [OPTIONS]
```

### Arguments

*   `<prompt>`: The input prompt for the Gemma model.

### Options

*   `--model-path <PATH>`: Absolute path to the Gemma GGUF model file (e.g., `/path/to/data/models/gemma-2b-it.Q4_K_M.gguf`). **Required unless `--development` is used.**
*   `--max-tokens <INTEGER>`: Maximum number of tokens to generate locally by Gemma. (Default: 256)
*   `--temperature <FLOAT>`: Creativity of the Gemma model (0.0-1.0). Higher values are more creative. (Default: 0.7)
*   `--development`: Use default Gemma model path for development (`data/models/gemma-2b-it.Q4_K_M.gguf`).

### Examples

```bash
severino gemma "Explain the concept of quantum entanglement in simple terms." --model-path /path/to/data/models/gemma-2b-it.Q4_K_M.gguf
severino gemma "Write a Python function to calculate the Fibonacci sequence." --development
```

## `severino chat`

Starts an interactive chat session with the Gemma LLM. Type `exit` or `quit` to end the session.

### Usage

```bash
severino chat [OPTIONS]
```

### Options

*   `--model-path <PATH>`: Absolute path to the Gemma GGUF model file (e.g., `/path/to/data/models/gemma-2b-it.Q4_K_M.gguf`). **Required unless `--development` is used.**
*   `--max-tokens <INTEGER>`: Maximum number of tokens for model generation in chat. (Default: 512)
*   `--temperature <FLOAT>`: Creativity of the Gemma model (0.0-1.0). Higher values are more creative. (Default: 0.7)
*   `--development`: Use default Gemma model path for development (`data/models/gemma-2b-it.Q4_K_M.gguf`).

### Examples

```bash
severino chat --model-path /path/to/data/models/gemma-2b-it.Q4_K_M.gguf
severino chat --development
```