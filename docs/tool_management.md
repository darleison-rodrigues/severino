# Tool Management

Severino's extensibility is largely driven by its robust tool management system, which allows the AI agent to interact with the local environment and external services. The `ToolManager` within the `packages/core` is central to this functionality.

## `ToolManager`

The `ToolManager` is responsible for discovering, registering, and orchestrating the execution of various tools. It acts as an intermediary between the LLM's requests and the actual execution of operations.

### Key Responsibilities:

*   **Tool Discovery:** Identifies available tools within the system.
*   **Tool Registration:** Makes tools available for use by the LLM.
*   **Tool Orchestration:** Manages the sequence and execution of tool calls, especially for complex, multi-step tasks.
*   **Secure Execution:** Ensures that sensitive operations are handled with explicit user confirmation.

## Tool Definition

While a formal Tool Definition Language (TDL) is a future enhancement, tools are conceptually defined by their purpose, expected inputs, and potential side effects. This allows the LLM to understand how and when to use a tool.

## Secure User Confirmation

For any tool that can modify the file system, execute shell commands, or interact with sensitive external services, Severino implements a critical security measure: **explicit user confirmation**.

### How it Works:

1.  **LLM Request:** When the LLM determines that a tool with potential side effects needs to be executed, it communicates this to the `ToolManager`.
2.  **Details Presentation:** The `ToolManager` constructs a clear and concise summary of the proposed tool action, including the tool name, its arguments, and the potential impact.
3.  **User Prompt:** This summary is presented to the user in the CLI.
4.  **Confirmation:** The user is prompted to explicitly confirm or deny the execution of the tool. Severino will *not* proceed with the action without this confirmation.

### Examples of Tools Requiring Confirmation:

*   `run_shell_command`: Any command that modifies the system or executes external scripts.
*   `write_file`: Writing content to a file.
*   `replace`: Modifying existing file content.

### Read-Only Operations:

Tools that perform read-only operations (e.g., `read_file`, `list_directory`, `search_file_content`, `glob`, `web_fetch`) typically do not require explicit user confirmation, as they do not alter the system state.

## Tool Orchestration and Chaining

Severino aims for intelligent tool selection and chaining. The LLM, guided by the Core package, can:

*   **Intent Mapping:** Accurately map natural language commands to the correct tool and its parameters.
*   **Tool Chaining:** Automatically break down complex requests into a sequence of necessary tool calls, handling intermediate outputs as inputs for subsequent tools.
*   **Conditional Execution:** Use logic to decide which tool to call based on the results of a previous tool or the current system state.
