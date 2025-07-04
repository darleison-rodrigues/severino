# Severino CLI: Intelligent Command-Line Interface

Severino is an intelligent command-line interface designed to empower developers with advanced AI capabilities, streamline workflows, and interact seamlessly with local tools and cloud services. It aims to provide a robust, secure, and intuitive experience for managing complex software engineering tasks.

## Functional Features

The Severino CLI is built around a modular architecture, enabling powerful interactions through natural language and direct commands.

### 1. Core CLI Capabilities

*   **Intelligent Input Processing:** Understands and parses user commands, including natural language prompts, to determine intent and orchestrate actions.
*   **Conversational Context Management:** Maintains conversation history to provide context-aware responses and support long-running sessions.
*   **Dynamic Tool Execution:** Executes a wide range of tools, both local and remote, based on user requests or AI-driven decisions.
*   **Secure Operations:** Implements a robust mechanism for user confirmation before executing sensitive commands that might modify the system or data.
*   **Extensible Architecture:** Designed for easy integration of new tools and services.

### 2. AI Integration

*   **Gemini API Client:** Communicates with the Google Gemini API for advanced language understanding, generation, and tool call orchestration.
*   **Local LLM Inference (Gemma):** Supports local execution of large language models (e.g., Gemma GGUF models) for offline capabilities and reduced cloud dependency.
*   **Prompt Construction & Management:** Dynamically builds and refines prompts for LLMs, incorporating conversational history and tool definitions.
*   **Text Processing & Feature Engineering:** Cleans and normalizes text inputs for consistent and high-quality LLM interactions, applying rules for robust data handling.

### 3. Tool Management System

The CLI features a `ToolManager` responsible for registering, discovering, and orchestrating the execution of various tools.

*   **Tool Registration:** Tools are defined with clear specifications (name, description, parameters, expected returns, side effects, security context).
*   **Dynamic Discovery:** New tools can be registered at runtime, allowing for flexible expansion of CLI capabilities.
*   **Intelligent Tool Selection & Chaining:** The AI can select the most appropriate tool(s) for a given task and chain multiple tool calls to achieve complex goals.
*   **Tool Adapters:** Generic adapters enable interaction with diverse environments, including local shell commands and remote APIs.

### 4. Cloud & RAG Integration Points

Severino is designed to integrate with robust cloud backends and secure knowledge management systems.

*   **Cloudflare Workers Backend:** The CLI can interact with Cloudflare Workers-based services for API key validation, business logic, data ingestion, and RAG orchestration.
*   **Secure RAG System:** Facilitates querying and integrating responses from Retrieval Augmented Generation (RAG) systems, ensuring context-aware and privacy-preserving access to knowledge bases.

## Command-Line Interface (CLI) Commands

The Severino CLI provides a set of commands for direct interaction and leverages natural language processing for more intuitive control.

### General Interaction

*   `severino <your_natural_language_prompt>`: The primary way to interact. Describe what you want to achieve, and Severino will interpret your request, potentially executing tools or providing information.
    *   **Example:** `severino "Summarize the main points of the file at /docs/project_plan.md"`
    *   **Example:** `severino "What is the current status of the 'core package foundations' task?"`

### Direct Tool Execution

For specific, direct actions, you can invoke tools explicitly.

*   `severino read <file_path>`: Reads and displays the content of a specified file.
    *   **Example:** `severino read /home/user/config.json`
*   `severino shell <command>`: Executes a shell command. **Requires user confirmation for potentially destructive commands.**
    *   **Example:** `severino shell "ls -la"`
    *   **Example:** `severino shell "git status"`

### Configuration Management

Manage Severino's settings and API keys.

*   `severino config set <key> <value>`: Sets a configuration value (e.g., API keys, default model).
    *   **Example:** `severino config set gemini_api_key YOUR_API_KEY`
*   `severino config show`: Displays the current configuration settings.

### Session & History Management

Control conversational context.

*   `severino chat`: Enters an interactive chat mode for continuous conversation.
*   `severino history show [limit]`: Displays recent conversational history.
*   `severino history clear`: Clears the current session's conversation history.

### Diagnostics & Health Checks

*   `severino self-diagnose`: Checks the health and connectivity of internal components and integrated external services. Provides actionable insights for troubleshooting.

## Getting Started

To begin using Severino, ensure you have Python installed. You can then install the necessary dependencies and configure your API keys. Detailed installation instructions will be provided in the full documentation.