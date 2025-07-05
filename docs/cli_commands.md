# CLI Commands

Severino provides a set of command-line interface (CLI) commands to interact with its AI capabilities. These commands are built using the `click` library.

## `severino gemma`

Runs local inference using the Gemma model. Ideal for quick insights, coding assistance, or general tasks where speed and privacy are key. Requires a Gemma GGUF model to be downloaded in `data/models/`.

### Usage

```bash
severino gemma <prompt> [OPTIONS]
```

### Arguments

*   `<prompt>`: The input prompt for the Gemma model.

### Options

*   `--max-tokens <INTEGER>`: Maximum number of tokens to generate locally by Gemma. (Default: 256)
*   `--temperature <FLOAT>`: Creativity of the Gemma model (0.0-1.0). Higher values are more creative. (Default: 0.7)

### Examples

```bash
severino gemma "Explain the concept of quantum entanglement in simple terms."
severino gemma "Write a Python function to calculate the Fibonacci sequence." --max-tokens 100 --temperature 0.5
```

## `severino gemini`

Generates content using the Gemini API. Best for high-quality, complex, or longer responses. Note: Usage of the Gemini API may incur charges based on Google Cloud billing.

### Usage

```bash
severino gemini <prompt> [OPTIONS]
```

### Arguments

*   `<prompt>`: The input prompt for the Gemini API.

### Options

*   `--max-tokens <INTEGER>`: Maximum number of tokens for Gemini API generation. (Default: 1000)

### Examples

```bash
severino gemini "Draft a marketing email for a new software product."
severino gemini "Summarize the key findings of the latest AI research paper." --max-tokens 500
```

## `severino chat`

Starts an interactive chat session with the chosen LLM. Type `exit` or `quit` to end the session.

### Usage

```bash
severino chat [OPTIONS]
```

### Options

*   `--model <gemma|gemini>`: Choose the LLM model for the chat session (gemma or gemini). (Default: gemma)
*   `--max-tokens <INTEGER>`: Maximum number of tokens for model generation in chat. (Default: 512)
*   `--temperature <FLOAT>`: Creativity of the Gemma model (0.0-1.0). Higher values are more creative. (Default: 0.7)

### In-Chat Commands

*   `/use gemini`: Enables the Gemini API for the current chat session. By default, Gemini API calls are not authorized at the start of a session, giving the user explicit control over cloud API usage.

### Examples

```bash
severino chat
# (Inside chat session)
You: Hello, Severino!
Severino: Hello! How can I assist you today?
You: /use gemini
Severino: Gemini API is now ENABLED for this session.
You: What's the weather like in London?
Severino: (Gemini response about London weather)

severino chat --model gemini --max-tokens 200
# (Starts chat directly with Gemini, assuming API is authorized)
```
