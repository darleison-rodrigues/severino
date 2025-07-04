from typing import Any, Callable, Dict, List, Optional

class ToolManager:
    """
    Manages the registration, discovery, and orchestration of various tools.
    Ensures a secure mechanism for user confirmation for sensitive operations.
    """

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._tool_implementations: Dict[str, Callable] = {}

    def register_tool(self, tool_definition: Dict[str, Any], implementation: Callable):
        """
        Registers a new tool with the ToolManager.
        tool_definition: A dictionary defining the tool (e.g., name, description, parameters, side_effects).
        implementation: The callable function that executes the tool's logic.
        """
        tool_name = tool_definition.get("name")
        if not tool_name:
            raise ValueError("Tool definition must include a 'name'.")
        if tool_name in self._tools:
            print(f"Warning: Tool '{tool_name}' is already registered. Overwriting.")
        
        self._tools[tool_name] = tool_definition
        self._tool_implementations[tool_name] = implementation
        print(f"Tool '{tool_name}' registered successfully.")

    def get_tool_definition(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the definition of a registered tool.
        """
        return self._tools.get(tool_name)

    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all registered tool definitions.
        """
        return list(self._tools.values())

    def execute_tool(self, tool_name: str, args: Dict[str, Any], require_confirmation: bool = True) -> Any:
        """
        Executes a registered tool.
        tool_name: The name of the tool to execute.
        args: A dictionary of arguments to pass to the tool's implementation.
        require_confirmation: If True, prompts the user for confirmation for sensitive operations.
        """
        if tool_name not in self._tool_implementations:
            raise ValueError(f"Tool '{tool_name}' not found.")

        tool_definition = self._tools[tool_name]
        has_side_effects = tool_definition.get("side_effects", False)

        if require_confirmation and has_side_effects:
            print(f"\n--- Tool Execution Confirmation ---")
            print(f"Tool: {tool_name}")
            print(f"Description: {tool_definition.get('description', 'No description provided.')}")
            print(f"Arguments: {args}")
            print(f"WARNING: This tool may modify the system or data.")
            confirmation = input("Do you want to proceed? (yes/no): ").lower()
            if confirmation != 'yes':
                print("Tool execution cancelled by user.")
                return {"status": "cancelled", "message": "Tool execution cancelled by user."}

        print(f"Executing tool '{tool_name}' with arguments: {args}")
        implementation = self._tool_implementations[tool_name]
        try:
            result = implementation(**args)
            print(f"Tool '{tool_name}' executed successfully.")
            return result
        except Exception as e:
            print(f"Error executing tool '{tool_name}': {e}")
            return {"status": "error", "message": str(e)}

# Example Tool Implementations (for demonstration)
def _read_file_impl(absolute_path: str) -> Dict[str, Any]:
    try:
        with open(absolute_path, 'r') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except FileNotFoundError:
        return {"status": "error", "message": f"File not found: {absolute_path}"}
    except Exception as e:
        return {"status": "error", "message": f"Error reading file: {e}"}

def _run_shell_command_impl(command: str) -> Dict[str, Any]:
    import subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "stdout": e.stdout, "stderr": e.stderr, "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Error running command: {e}"}

# Example Usage (for testing purposes)
if __name__ == "__main__":
    tool_manager = ToolManager()

    # Register a read_file tool
    tool_manager.register_tool(
        tool_definition={
            "name": "read_file",
            "description": "Reads content from a specified file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "absolute_path": {"type": "string", "description": "The absolute path to the file."}
                },
                "required": ["absolute_path"]
            },
            "side_effects": False
        },
        implementation=_read_file_impl
    )

    # Register a run_shell_command tool
    tool_manager.register_tool(
        tool_definition={
            "name": "run_shell_command",
            "description": "Executes a shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to execute."}
                },
                "required": ["command"]
            },
            "side_effects": True # This tool has side effects
        },
        implementation=_run_shell_command_impl
    )

    # Get all tool definitions
    print("\n--- Registered Tool Definitions ---")
    for tool_def in tool_manager.get_all_tool_definitions():
        print(tool_def)

    # Execute a read-only tool (no confirmation needed)
    print("\n--- Executing read_file (no confirmation) ---")
    read_result = tool_manager.execute_tool("read_file", {"absolute_path": "./tool_manager.py"}, require_confirmation=False)
    print(read_result.get("status"))
    # print(read_result.get("content")) # Uncomment to see file content

    # Execute a sensitive tool (confirmation needed)
    print("\n--- Executing run_shell_command (confirmation needed) ---")
    # This will prompt for user confirmation in the console
    shell_result = tool_manager.execute_tool("run_shell_command", {"command": "echo Hello from shell!"})
    print(shell_result.get("status"))
    print(shell_result.get("stdout"))

    # Example of a tool call that would be cancelled
    print("\n--- Executing run_shell_command (user cancels) ---")
    # Simulate user typing 'no' when prompted
    # You would need to manually type 'no' in the console for this test
    # shell_cancel_result = tool_manager.execute_tool("run_shell_command", {"command": "rm -rf /"})
    # print(shell_cancel_result.get("status"))
