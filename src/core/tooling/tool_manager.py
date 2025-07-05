from typing import Any, Callable, Dict, List, Optional, Type
from src.perception.sensor_factory import SensorFactory
from src.ml_models.ml_model_factory import MLModelFactory
from src.llm_inference.llm_factory import LLMFactory
from src.actions.base_action import ActionInterface
from src.perception.sensors.base_sensor import SensorInterface
from src.ml_models.base_ml_model import MLModelInterface
from src.llm_inference.base_llm import LLMProviderInterface

class ToolManager:
    """
    Manages the registration, discovery, and orchestration of various tools.
    Ensures a secure mechanism for user confirmation for sensitive operations.
    Tools can be direct callables or instances of SensorInterface, MLModelInterface, LLMProviderInterface, or ActionInterface.
    """

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._tool_implementations: Dict[str, Callable] = {}
        self._tool_instances: Dict[str, Any] = {} # To store instantiated objects like sensors, models, llms

    def register_tool(self, tool_definition: Dict[str, Any], implementation: Optional[Callable] = None, 
                      factory_type: Optional[str] = None, factory_name: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Registers a new tool with the ToolManager.
        Args:
            tool_definition (Dict[str, Any]): A dictionary defining the tool (e.g., name, description, parameters, side_effects).
            implementation (Optional[Callable]): The callable function that executes the tool's logic for simple tools.
            factory_type (Optional[str]): The type of factory to use (e.g., 'sensor', 'ml_model', 'llm', 'action').
            factory_name (Optional[str]): The specific name within the factory (e.g., 'video', 'object_detector', 'llama_cpp').
            config (Optional[Dict[str, Any]]): Configuration for the factory-created instance.
        """
        tool_name = tool_definition.get("name")
        if not tool_name:
            raise ValueError("Tool definition must include a 'name'.")
        if tool_name in self._tools:
            print(f"Warning: Tool '{tool_name}' is already registered. Overwriting.")
        
        self._tools[tool_name] = tool_definition

        if factory_type:
            if factory_type == "sensor":
                if not (factory_name and config is not None):
                    raise ValueError(f"For factory_type 'sensor', 'factory_name' and 'config' must be provided.")
                self._tool_instances[tool_name] = SensorFactory.create_sensor(factory_name, tool_name, config)
            elif factory_type == "ml_model":
                if not (factory_name and config is not None):
                    raise ValueError(f"For factory_type 'ml_model', 'factory_name' and 'config' must be provided.")
                self._tool_instances[tool_name] = MLModelFactory.create_model(factory_name, tool_name, config)
            elif factory_type == "llm":
                if not (factory_name and config is not None):
                    raise ValueError(f"For factory_type 'llm', 'factory_name' and 'config' must be provided.")
                self._tool_instances[tool_name] = LLMFactory.create_provider(factory_name, tool_name, config)
            elif factory_type == "action":
                # For actions, 'implementation' is the class to be instantiated
                if not (isinstance(implementation, type) and issubclass(implementation, ActionInterface)):
                    raise ValueError(f"For factory_type 'action', 'implementation' must be an ActionInterface class.")
                # config is optional for actions, but if provided, pass it
                self._tool_instances[tool_name] = implementation(tool_name, config if config is not None else {})
                print(f"Tool '{tool_name}' registered as a factory-managed instance of type {factory_type}.") # No factory_name for actions
            else:
                raise ValueError(f"Unknown factory_type: {factory_type}")
        elif implementation:
            self._tool_implementations[tool_name] = implementation
            print(f"Tool '{tool_name}' registered as a direct callable.")
        else:
            raise ValueError("Either 'implementation' or ('factory_type', 'factory_name', 'config') must be provided.")

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
        Args:
            tool_name (str): The name of the tool to execute.
            args (Dict[str, Any]): A dictionary of arguments to pass to the tool's implementation.
            require_confirmation (bool): If True, prompts the user for confirmation for sensitive operations.
        """
        tool_definition = self._tools.get(tool_name)
        if not tool_definition:
            raise ValueError(f"Tool '{tool_name}' not found.")

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
        
        if tool_name in self._tool_instances:
            instance = self._tool_instances[tool_name]
            # Determine which method to call based on the instance type (using interfaces)
            if isinstance(instance, SensorInterface):
                operation = args.pop("operation", "read_data")
                if operation == "connect":
                    result = instance.connect()
                elif operation == "read_data":
                    result = instance.read_data()
                elif operation == "get_status":
                    result = instance.get_status()
                elif operation == "release":
                    result = instance.release()
                else:
                    raise ValueError(f"Unsupported sensor operation: {operation}")
            elif isinstance(instance, MLModelInterface):
                operation = args.pop("operation", "predict")
                if operation == "load_model":
                    result = instance.load_model()
                elif operation == "predict":
                    data = args.pop("data")
                    result = instance.predict(data)
                elif operation == "get_status":
                    result = instance.get_status()
                else:
                    raise ValueError(f"Unsupported ML model operation: {operation}")
            elif isinstance(instance, LLMProviderInterface):
                operation = args.pop("operation", "generate_response")
                if operation == "load_llm":
                    result = instance.load_llm()
                elif operation == "generate_response":
                    prompt_value = args.pop("prompt")
                    result = instance.generate_response(prompt_value, **args)
                elif operation == "get_status":
                    result = instance.get_status()
                else:
                    raise ValueError(f"Unsupported LLM provider operation: {operation}")
            elif isinstance(instance, ActionInterface):
                payload = args.pop("payload", {})
                result = instance.execute(payload)
            else:
                raise ValueError(f"Unsupported tool instance type: {type(instance)}")
        elif tool_name in self._tool_implementations:
            implementation = self._tool_implementations[tool_name]
            try:
                result = implementation(**args)
            except Exception as e:
                print(f"Error executing tool '{tool_name}': {e}")
                return {"status": "error", "message": str(e)}
        else:
            raise ValueError(f"Tool '{tool_name}' not found or not properly initialized.")

        print(f"Tool '{tool_name}' executed successfully.")
        return result

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

# Example Action Implementation
class NotificationAction(ActionInterface):
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        message = payload.get("message", "No message provided.")
        recipient = payload.get("recipient", "user")
        print(f"[NotificationAction] Sending message to {recipient}: {message}")
        return {"status": "success", "message_sent": message, "recipient": recipient}

    def get_status(self) -> Dict[str, Any]:
        return {"action_id": self.action_id, "type": "NotificationAction", "ready": True}

# Example Usage (for testing purposes)
if __name__ == "__main__":
    import logging
    import numpy as np
    import os
    from config.settings import PROJECT_ROOT # Assuming PROJECT_ROOT is still accessible

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    tool_manager = ToolManager()

    # Register a direct callable tool
    tool_manager.register_tool(
        tool_definition={
            "name": "read_file",
            "description": "Reads content from a specified file.",
            "parameters": {"absolute_path": {"type": "string"}},
            "side_effects": False
        },
        implementation=_read_file_impl
    )

    # Register a sensor tool via factory
    camera_config = {"rtsp_url": "rtsp://your.camera.url/stream"}
    tool_manager.register_tool(
        tool_definition={
            "name": "main_camera_sensor",
            "description": "Main video camera sensor.",
            "parameters": {"operation": {"type": "string", "enum": ["connect", "read_data", "get_status", "release"]}},
            "side_effects": True # Connecting/releasing has side effects
        },
        factory_type="sensor", factory_name="video", config=camera_config
    )

    # Register an ML model tool via factory
    detector_config = {"model_path": 'yolov8n.pt'}
    tool_manager.register_tool(
        tool_definition={
            "name": "object_detection_model",
            "description": "YOLOv8 object detection model.",
            "parameters": {"operation": {"type": "string", "enum": ["load_model", "predict", "get_status"]}, "data": {}},
            "side_effects": False # Prediction is generally side-effect free
        },
        factory_type="ml_model", factory_name="object_detector", config=detector_config
    )

    # Register an LLM provider tool via factory
    sample_model_path = os.path.join(PROJECT_ROOT, "data", "models", "gemma-2b-it.Q4_K_M.gguf")
    llm_config = {"model_path": sample_model_path, "n_gpu_layers": 0}
    tool_manager.register_tool(
        tool_definition={
            "name": "local_llm_provider",
            "description": "Local LLM inference provider.",
            "parameters": {"operation": {"type": "string", "enum": ["load_llm", "generate_response", "get_status"]}, "prompt": {"type": "string"}, "max_tokens": {"type": "integer"}, "temperature": {"type": "number"}, "chat_history": {"type": "array"}},
            "side_effects": False # Inference is generally side-effect free
        },
        factory_type="llm", factory_name="llama_cpp", config=llm_config
    )

    # Register an action tool
    notification_config = {"service_url": "https://api.notifications.com"}
    tool_manager.register_tool(
        tool_definition={
            "name": "send_alert_notification",
            "description": "Sends an alert notification.",
            "parameters": {"payload": {"type": "object"}},
            "side_effects": True
        },
        factory_type="action", implementation=NotificationAction, config=notification_config
    )

    print("\n--- Registered Tool Definitions ---")
    for tool_def in tool_manager.get_all_tool_definitions():
        print(tool_def)

    # --- Example Executions ---

    # Execute a direct callable tool
    print("\n--- Executing read_file ---")
    read_result = tool_manager.execute_tool("read_file", {"absolute_path": __file__}, require_confirmation=False)
    print(f"Read file status: {read_result.get("status")}")

    # Execute sensor operations
    print("\n--- Executing Sensor Operations ---")
    connect_result = tool_manager.execute_tool("main_camera_sensor", {"operation": "connect"})
    print(f"Camera connect status: {connect_result}")

    if connect_result:
        # Dummy frame for prediction since we don't have a live camera in this test block
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Execute ML model operations
        print("\n--- Executing ML Model Operations ---")
        load_model_result = tool_manager.execute_tool("object_detection_model", {"operation": "load_model"})
        print(f"Model load status: {load_model_result}")

        if load_model_result:
            detect_result = tool_manager.execute_tool("object_detection_model", {"operation": "predict", "data": dummy_frame})
            print(f"Detection result (dummy frame): {detect_result}")

        # Execute LLM operations
        print("\n--- Executing LLM Operations ---")
        load_llm_result = tool_manager.execute_tool("local_llm_provider", {"operation": "load_llm"})
        print(f"LLM load status: {load_llm_result}")

        if load_llm_result:
            llm_response = tool_manager.execute_tool("local_llm_provider", {"operation": "generate_response", "prompt": "What is the capital of France?", "max_tokens": 20})
            print(f"LLM response: {llm_response.get("generated_text")}")

        # Execute action
        print("\n--- Executing Action ---")
        alert_result = tool_manager.execute_tool("send_alert_notification", {"payload": {"message": "Test alert from Severino!", "recipient": "admin"}}, require_confirmation=True)
        print(f"Alert status: {alert_result}")

        # Release sensor
        release_result = tool_manager.execute_tool("main_camera_sensor", {"operation": "release"})
        print(f"Camera release status: {release_result}")
    else:
        print("Skipping further operations as camera connection failed.")