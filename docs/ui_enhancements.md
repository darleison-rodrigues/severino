# UI Enhancements

Severino leverages the `rich` Python library to provide a more engaging and informative user experience in the command-line interface. These enhancements include beautified logs, interactive loaders/spinners, and expressive emojis.

## Beautified Logs

Logging output is enhanced with colors, styling, and nerdy emojis to improve readability and quickly convey the severity or type of log message. This is configured in `src/config/logging_config.py`.

### Example Log Output (Conceptual):

```
🐛 [bold blue]Debugging[/bold blue] a cosmic ray... This is a debug message.
💡 [bold green]Insight[/bold green] unlocked! This is an info message.
⚠️ [bold yellow]Anomaly[/bold yellow] detected! This is a warning message.
🔥 [bold red]Critical failure[/bold red]! This is an error message.
💀 [bold magenta]System meltdown[/bold magenta]! This is a critical message.
```

## Loaders and Spinners

To provide immediate visual feedback during processing, especially when interacting with LLMs or performing computationally intensive tasks, Severino displays interactive loaders and spinners.

### Implementation:

*   **LLM Reasoning:** When the Gemini API is processing a request, a spinner is displayed to indicate that the system is actively thinking. This is implemented in `src/llm_inference/gemini_api.py`.

### Example:

```
[bold yellow]Thinking...[/bold yellow] (spinner animation)
```

## Emojis in Agent Responses

Agent responses in the interactive chat mode are prepended with a distinct emoji to visually differentiate them from user input and add a touch of personality.

### Implementation:

*   The emoji for agent responses is configured in `src/cli/commands.py`.

### Example:

```
You: What is the capital of France?
🐨 Severino: The capital of France is Paris.
```
