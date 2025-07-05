# Severino CLI: The Intelligent Developer's Orchestrator

Severino is a specialized, intelligent command-line interface designed for developers. It augments your terminal experience with targeted multimodal interactions and a cognitive architecture for interpretable ML monitoring. Severino's core value lies in its ability to execute complex tasks through intelligent tool chaining, provide real-time insights into ML systems, and offer a seamless, performant user experience without feature bloat.

## IMPORTANT LICENSE NOTICE

This software is licensed under the **Severino Custom Non-Commercial License**. This means:

*   **Non-Commercial Use Only (Except by Creator):** The Software may be used, copied, modified, merged, published, distributed, sublicensed, and/or sold for **non-commercial purposes only**. Any commercial use, distribution, or sale of the Software is strictly prohibited, except when conducted directly by the original Creator (Your Name).
*   **Attribution:** The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*   **No Warranty:** The Software is provided "as is", without warranty of any kind, express or implied.

For commercial licensing inquiries or to obtain a commercial license, please contact the Creator at [your.email@example.com].

## Core Pillars of Severino

### 1. Command-Centric Intelligence

Severino interprets natural language requests and translates them into precise sequences of tool commands. It understands context, anticipates needs, and proactively suggests or executes the most efficient toolchain to achieve the user's goal. The primary mode of interaction remains command-line driven, where users issue commands, and Severino leverages its internal intelligence (powered by Gemma) to select, configure, and execute the appropriate tools (file system operations, shell commands, custom scripts, etc.). For conversational clarification or general queries, Severino maintains a rich, text-based chat experience directly within the terminal, leveraging `rich` for enhanced readability and feedback.

### 2. Targeted Multimodal Access with Lightweight UI

Severino's multimodal capabilities are focused and performant. The `severino listen` command is its primary multimodal entry point, activating a **minimal, non-intrusive UI element** that visually indicates active listening and provides real-time transcription preview. Once voice input is complete, the UI disappears, and the transcribed text is seamlessly fed into Severino's command processing pipeline. Other complex tooling or functions might trigger similarly lightweight, ephemeral UI components (e.g., for interactive configuration or brief visual summaries).

### 3. Cognitive ML Monitoring (Future Integration)

Leveraging principles from cognitive architectures, Severino aims to act as an intelligent ML monitoring agent. It will ingest raw monitoring data (e.g., drift reports, performance metrics from edge devices) and use Gemma to process this data, providing human-readable, actionable insights and recommendations. This enables proactive oversight of ML systems.

### 4. Lightweight & Performant by Design

Severino prioritizes local Gemma inference for core intelligence, ensuring privacy and minimizing latency. UI elements are designed to be ephemeral and consume minimal system resources, ensuring Severino remains responsive and doesn't interfere with the developer's primary workflow.

## Functional Features

### Core CLI Capabilities

*   **Intelligent Input Processing:** Understands and parses user commands, including natural language prompts, to determine intent and orchestrate actions.
*   **Conversational Context Management:** Maintains conversation history to provide context-aware responses and support long-running sessions.
*   **Dynamic Tool Execution:** Executes a wide range of tools, both local and remote, based on user requests or AI-driven decisions.
*   **Secure Operations:** Implements a robust mechanism for user confirmation before executing sensitive commands that might modify the system or data.
*   **Extensible Architecture:** Designed for easy integration of new tools and services.

### AI Integration

*   **Local LLM Inference (Gemma):** Supports local execution of large language models (e.g., Gemma GGUF models) for offline capabilities and reduced cloud dependency.
*   **Prompt Construction & Management:** Dynamically builds and refines prompts for LLMs, incorporating conversational history and tool definitions.
*   **Text Processing & Feature Engineering:** Cleans and normalizes text inputs for consistent and high-quality LLM interactions, applying rules for robust data handling.

### Tool Management System

The CLI features a `ToolManager` responsible for registering, discovering, and orchestrating the execution of various tools.

*   **Tool Registration:** Tools are defined with clear specifications (name, description, parameters, expected returns, side effects, security context).
*   **Dynamic Discovery:** New tools can be registered at runtime, allowing for flexible expansion of CLI capabilities.
*   **Intelligent Tool Selection & Chaining:** The AI can select the most appropriate tool(s) for a given task and chain multiple tool calls to achieve complex goals.
*   **Tool Adapters:** Generic adapters enable interaction with diverse environments, including local shell commands and remote APIs.

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
    
*   `severino config show`: Displays the current configuration settings.

### Session & History Management

Control conversational context.

*   `severino chat`: Enters an interactive chat mode for continuous conversation. This mode features:
    *   **Rich Terminal Output:** Colored text for user input, agent responses, and system messages.
    *   **Loading Spinners:** Visual feedback while the LLM is processing.
    *   **Emoji Responses:** Agent responses are prepended with a distinctive emoji (e.g., :hatching-egg:).
    
*   `severino history show [limit]`: Displays recent conversational history.
*   `severino history clear`: Clears the current session's conversation history.

### Diagnostics & Health Checks

*   `severino self-diagnose`: Checks the health and connectivity of internal components and integrated external services. Provides actionable insights for troubleshooting.

## Getting Started

To begin using Severino, ensure you have Python installed. You can then install the necessary dependencies and configure your API keys. Detailed installation instructions will be provided in the full documentation.