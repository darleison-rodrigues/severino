# Architecture

Severino's architecture is modular and designed for extensibility, separating concerns into distinct packages and leveraging both local and cloud resources.

## Core Components

### CLI Package (`packages/cli`)

*   **Purpose:** This is the user-facing component of Severino. It handles all direct interactions with the user through the command-line interface.
*   **Key Functions:**
    *   **Input Processing:** Manages user commands and prompts.
    *   **Output Presentation:** Formats and displays responses to the user, leveraging `rich` for enhanced visual experience.
    *   **History Management:** (Planned) Manages command history and conversational context for the CLI session.
    *   **User Experience:** Overall management of the interactive terminal experience.

### Core Package (`packages/core`)

*   **Purpose:** Acts as the central backend for Severino, orchestrating interactions between LLMs, tools, and managing the application's state.
*   **Key Functions:**
    *   **LLM Communication:** Handles requests to both local (Gemma) and cloud (Gemini) LLMs.
    *   **Prompt Construction:** Dynamically builds prompts for LLMs, incorporating conversational history and tool definitions.
    *   **Tool Management:** Registers, discovers, and executes various tools.
    *   **State Management:** Maintains conversational context and session-specific data.

### Tooling (`packages/core/src/tools/`)

*   **Purpose:** Individual modules that extend Severino's capabilities, allowing it to interact with the local environment and external services.
*   **Examples:** File system operations, shell command execution, web fetching, and custom AI tools.
*   **Interaction:** The Core package invokes these tools based on LLM requests, often requiring user confirmation for sensitive operations.

## LLM Integration

*   **Gemma (Local):** Utilizes `src/llm_inference/gemma_local.py` for local, privacy-preserving inference. Ideal for quick insights and tasks where data remains on the edge device.
*   **Gemini (Cloud):** Integrates with the Google Gemini API via `src/llm_inference/gemini_api.py`. Used for more complex tasks, larger context windows, and when higher quality responses are required. Cost warnings are implemented for API usage.

## Cloud Backend (Conceptual - `api.rdltechworks.com`)

Severino is designed to integrate with a robust cloud backend, primarily leveraging Cloudflare's developer platform for scalability, security, and performance.

*   **API Gateway Worker:** Acts as the public-facing entry point for all API requests.
*   **Auth Service Worker:** Handles authentication and authorization, including API key validation and tenant management using a D1 database.
*   **Intelligent Services Worker:** Hosts various AI-powered microservices.
*   **Data Ingress Service Worker:** Manages secure and efficient data transfer into the cloud.
*   **RAG Service Worker:** Orchestrates Retrieval Augmented Generation, interacting with knowledge bases.

## Edge AI Hub Integration (Conceptual - NVIDIA Jetson Xavier NX)

Severino is built to manage and interact with edge AI devices, such as the NVIDIA Jetson Xavier NX, for real-time monitoring and local data processing.

*   **Data Ingestion:** Receives real-time alerts, metrics, and raw data streams from edge devices.
*   **Alert Management:** Relays alerts to the CLI and integrates with external notification systems.
*   **Remote Control:** Allows the CLI to send commands and update configurations on the edge device.

## Data Storage and Knowledge Management

*   **Memory Palace:** A local, privacy-centric knowledge graph (SQLite-based) designed to store extracted entities, intents, and SPO triples from conversations. This enables sophisticated recall and reasoning directly on the edge device.
*   **Secure RAG System:** Integration with a secure RAG system (potentially on Azure Confidential VMs) for querying internal documentation and codebase knowledge, ensuring data privacy and adherence to Confidential AI principles.
