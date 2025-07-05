# Architecture

Severino's architecture is modular and designed for extensibility, separating concerns into distinct packages and leveraging local resources.

## Core Components

### CLI Package (`packages/cli`)

*   **Purpose:** This is the user-facing component of Severino. It handles all direct interactions with the user through the command-line interface.
*   **Key Functions:**
    *   **Input Processing:** Manages user commands and prompts.
    *   **Output Presentation:** Formats and displays responses to the user, leveraging `rich` for enhanced visual experience.
    *   **History Management:** Manages command history and conversational context for the CLI session.
    *   **User Experience:** Overall management of the interactive terminal experience.

### Core Package (`packages/core`)

*   **Purpose:** Acts as the central backend for Severino, orchestrating interactions between LLMs, tools, and managing the application's state.
*   **Key Functions:**
    *   **LLM Communication:** Handles requests to local (Gemma) LLMs.
    *   **Prompt Construction:** Dynamically builds prompts for LLMs, incorporating conversational history and tool definitions.
    *   **Tool Management:** Registers, discovers, and executes various tools.
    *   **State Management:** Maintains conversational context and session-specific data.

### Tooling (`packages/core/src/tools/`)

*   **Purpose:** Individual modules that extend Severino's capabilities, allowing it to interact with the local environment.
*   **Examples:** File system operations, shell command execution, and custom AI tools.
*   **Interaction:** The Core package invokes these tools based on LLM requests, often requiring user confirmation for sensitive operations.

## LLM Integration

*   **Gemma (Local):** Utilizes `src/llm_inference/gemma_local.py` for local, privacy-preserving inference. Ideal for quick insights and tasks where data remains on the local machine.