# Severino CLI: The Indispensable Orchestrator for High-Performance Development

Severino is not just a command-line interface; it's a strategic imperative for organizations demanding peak efficiency, unparalleled insight, and scalable operations in their software and ML development lifecycles. We deliver immediate, measurable value by transforming complex workflows into streamlined, intelligent processes.

## IMPORTANT LICENSE NOTICE

This software is licensed under the **Severino Custom Non-Commercial License**. This means:

*   **Non-Commercial Use Only (Except by Creator):** The Software may be used, copied, modified, merged, published, distributed, sublicensed, and/or sold for **non-commercial purposes only**. Any commercial use, distribution, or sale of the Software is strictly prohibited, except when conducted directly by the original Creator (Your Name).
*   **Attribution:** The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*   **No Warranty:** The Software is provided "as is", without warranty of any kind, express or implied.

For commercial licensing inquiries or to obtain a commercial license, please contact the Creator at [your.email@example.com].

## Core Pillars of Unrivaled Value:

### 1. Command-Centric Intelligence: Accelerating Development Velocity

Severino translates natural language intent into precise, optimized sequences of tool commands. This isn't mere scripting; it's intelligent orchestration that anticipates needs, minimizes manual intervention, and drastically reduces development cycles. Our command-line driven interface ensures absolute control and transparency, eliminating the ambiguity of conversational AI while leveraging advanced intelligence (powered by Gemma) to select, configure, and execute the most efficient toolchains (file system, shell, custom scripts). A rich, terminal-native chat experience provides instant clarification and feedback, ensuring developers remain in their flow, maximizing productivity.

### 2. Cognitive ML Monitoring: Unlocking Actionable Insights & Mitigating Risk

Leveraging principles from cognitive architectures, Severino acts as an intelligent ML monitoring agent. It ingests raw monitoring data (e.g., drift reports, performance metrics from edge devices) and uses Gemma to process this data, providing human-readable, actionable insights and recommendations. This enables proactive oversight of ML systems, preventing costly failures and ensuring model integrity.

### 3. Targeted Multimodal Access with Lightweight UI: Enhancing Efficiency, Not Distraction

Severino's multimodal capabilities are focused and performant. The `severino listen` command is its primary multimodal entry point, activating a **minimal, non-intrusive UI element** that visually indicates active listening and provides real-time transcription preview. Once voice input is complete, the UI disappears, and the transcribed text is seamlessly fed into Severino's command processing pipeline. Other complex tooling or functions might trigger similarly lightweight, ephemeral UI components (e.g., for interactive configuration or brief visual summaries), preserving focus and maximizing developer flow.

### 4. Lightweight & Performant by Design: Maximizing ROI, Minimizing Overhead

Severino prioritizes local Gemma inference for core intelligence, ensuring data privacy, minimizing latency, and reducing reliance on costly cloud services. UI elements are designed to be ephemeral and consume negligible system resources, guaranteeing Severino remains responsive and never interferes with critical development workflows.

## Functional Features: Driving Tangible Results

### Core CLI Capabilities: Streamlining Your Workflow

*   **Intelligent Input Processing:** Understands and parses user commands, including natural language prompts, to determine intent and orchestrate actions, accelerating task completion.
*   **Conversational Context Management:** Maintains conversation history to provide context-aware responses and support long-running sessions, boosting efficiency and reducing rework.
*   **Dynamic Tool Execution:** Executes a wide range of tools, both local and remote, based on user requests or AI-driven decisions, expanding your operational reach.
*   **Secure Operations:** Implements a robust mechanism for user confirmation before executing sensitive commands that might modify the system or data, ensuring data integrity and peace of mind.
*   **Extensible Architecture:** Designed for easy integration of new tools and services, future-proofing your investment.

### AI Integration: Unleashing Advanced Intelligence

*   **Local LLM Inference (Gemma):** Supports local execution of large language models (e.g., Gemma GGUF models) for offline capabilities, enhanced data privacy, and reduced cloud dependency, optimizing costs and security.
*   **Prompt Construction & Management:** Dynamically builds and refines prompts for LLMs, incorporating conversational history and tool definitions, ensuring highly accurate and relevant AI responses.
*   **Text Processing & Feature Engineering:** Cleans and normalizes text inputs for consistent and high-quality LLM interactions, applying rules for robust data handling, maximizing AI effectiveness.

### Tool Management System: Orchestrating Your Development Ecosystem

The CLI features a `ToolManager` responsible for registering, discovering, and orchestrating the execution of various tools, transforming your development environment into a cohesive, intelligent ecosystem.

*   **Tool Registration:** Tools are defined with clear specifications (name, description, parameters, expected returns, side effects, security context), ensuring precise and predictable operations.
*   **Dynamic Discovery:** New tools can be registered at runtime, allowing for flexible expansion of CLI capabilities, adapting to your evolving needs.
*   **Intelligent Tool Selection & Chaining:** The AI can select the most appropriate tool(s) for a given task and chain multiple tool calls to achieve complex goals, automating intricate workflows.
*   **Tool Adapters:** Generic adapters enable seamless interaction with diverse environments, including local shell commands and remote APIs, unifying your toolchain.

## Command-Line Interface (CLI) Commands: Direct Control, Maximum Impact

The Severino CLI provides a set of commands for direct interaction and leverages natural language processing for more intuitive control, putting powerful capabilities at your fingertips.

### General Interaction: Intuitive and Powerful

*   `severino <your_natural_language_prompt>`: The primary way to interact. Describe what you want to achieve, and Severino will interpret your request, potentially executing tools or providing information, accelerating your workflow.
    *   **Example:** `severino "Summarize the main points of the file at /docs/project_plan.md"`
    *   **Example:** `severino "What is the current status of the 'core package foundations' task?"`

### Direct Tool Execution: Precision and Efficiency

For specific, direct actions, you can invoke tools explicitly, ensuring rapid execution of critical tasks.

*   `severino read <file_path>`: Reads and displays the content of a specified file, providing instant access to information.
    *   **Example:** `severino read /home/user/config.json`
*   `severino shell <command>`: Executes a shell command. **Requires user confirmation for potentially destructive commands, ensuring security and control.**
    *   **Example:** `severino shell "ls -la"`
    *   **Example:** `severino shell "git status"`

### Configuration Management: Streamlined Control

Manage Severino's settings and API keys with ease, ensuring optimal performance and security.

*   `severino config set <key> <value>`: Sets a configuration value (e.g., API keys, default model), enabling rapid customization.
    
*   `severino config show`: Displays the current configuration settings, providing transparency and control.

### Session & History Management: Contextual Awareness for Enhanced Productivity

Control conversational context, ensuring Severino always understands your needs.

*   `severino chat`: Enters an interactive chat mode for continuous conversation. This mode features:
    *   **Rich Terminal Output:** Colored text for user input, agent responses, and system messages, enhancing readability and comprehension.
    *   **Loading Spinners:** Visual feedback while the LLM is processing, keeping you informed.
    *   **Emoji Responses:** Agent responses are prepended with a distinctive emoji (e.g., :hatching-egg:), adding a touch of personality.
    
*   `severino history show [limit]`: Displays recent conversational history, providing valuable context.
*   `severino history clear`: Clears the current session's conversation history, allowing for fresh starts.

### UI Integration: Visualizing Insights

*   `severino code [path]`: Starts the UI and begins building a knowledge graph of the codebase at the specified path (defaults to current directory), providing visual insights into your project.

### Diagnostics & Health Checks: Ensuring Operational Excellence

*   `severino self-diagnose`: Checks the health and connectivity of internal components and integrated external services. Provides actionable insights for troubleshooting, minimizing downtime.
*   `severino status`: Displays the current status of the application, giving you real-time operational awareness.

## Getting Started: Unlock Severino's Power Today

To begin transforming your development workflow with Severino, ensure you have Python installed. You can then install the necessary dependencies and configure your API keys. Detailed installation instructions will be provided in the full documentation.

## Development: Contribute to the Future of Intelligent Development

This project uses `pyproject.toml` to manage dependencies. To install the dependencies, run:

```bash
pip install -e .
```

To run the tests, use:

```bash
python -m unittest discover tests
```