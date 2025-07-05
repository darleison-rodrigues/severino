from typing import Any, Dict, List, Optional
import os
import json
import subprocess

from src.core.tooling.tool_manager import ToolManager
from src.core.memory.working_memory_manager import WorkingMemoryManager
from src.core.memory.long_term_memory_manager import LongTermMemoryManager
from src.core.memory.thought_process_manager import ThoughtProcessManager
from src.llm_inference.llm_factory import LLMFactory
from src.ml_models.ml_model_factory import MLModelFactory
from src.perception.sensor_factory import SensorFactory

class Agent:
    """
    The core cognitive agent responsible for interpreting directives, planning, and executing actions.
    It orchestrates the Refactor, Break Down, and Compile steps using various managers and tools.
    """

    def __init__(
        self, 
        session_id: str,
        project_root: str,
        llm_provider_name: str,
        llm_config: Dict[str, Any]
    ):
        self.session_id = session_id
        self.project_root = project_root

        self.long_term_memory = LongTermMemoryManager(os.path.join(project_root, ".severino", "knowledge", "mnemonic.db"))
        self.working_memory = WorkingMemoryManager(session_id=session_id, project_root=project_root)
        self.thought_process_manager = ThoughtProcessManager(session_id=session_id)
        self.tool_manager = ToolManager()

        # Initialize LLM Provider
        self.llm_provider = LLMFactory.create_provider(llm_provider_name, "agent_llm", llm_config)
        if not self.llm_provider.load_llm():
            raise RuntimeError("Failed to load LLM provider for the agent.")

        # Register core tools (can be expanded dynamically)
        self._register_core_tools()

    def _register_core_tools(self):
        # Example: Registering a generic shell command tool
        self.tool_manager.register_tool(
            tool_definition={
                "name": "run_shell_command",
                "description": "Executes a shell command.",
                "parameters": {"command": {"type": "string"}},
                "side_effects": True
            },
            implementation=self._run_shell_command_impl
        )

        # Register the LLM provider itself as a tool for the agent to use
        self.tool_manager.register_tool(
            tool_definition={
                "name": "agent_llm_inference",
                "description": """Performs inference using the agent's primary LLM.""",
                "parameters": {
                    "operation": {"type": "string", "enum": ["generate_response"]},
                    "prompt": {"type": "string"},
                    "max_tokens": {"type": "integer"},
                    "temperature": {"type": "number"},
                    "chat_history": {"type": "array"}
                },
                "side_effects": False
            },
            factory_type="llm", factory_name=self.llm_provider.config.get("provider_name", "llama_cpp"), config=self.llm_provider.config
        )

    def _run_shell_command_impl(self, command: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "stdout": e.stdout, "stderr": e.stderr, "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Error running command: {e}"}

    def process_directive(self, directive: str) -> Dict[str, Any]:
        """
        Processes a high-level user directive through the CAMA Refactor, Break Down, and Compile steps.
        """
        self.thought_process_manager.clear_thought_log() # Clear log for new directive
        self.thought_process_manager.log_thought("Directive Received", directive, {"directive": directive})

        # --- Refactor Step ---
        refactored_data = self._refactor_directive(directive)
        self.thought_process_manager.log_thought("Refactor Step", "Directive interpreted and initial data structured.", {"refactored_data": refactored_data})

        # --- Break Down Step ---
        plan = self._break_down_task(refactored_data)
        self.thought_process_manager.log_thought("Break Down Step", "Task decomposed into a plan.", {"plan": plan})

        # --- Execute Plan ---
        execution_results = self._execute_plan(plan)
        self.thought_process_manager.log_thought("Execution Step", "Plan executed.", {"results": execution_results})

        # --- Compile Step ---
        final_insight = self._compile_results(execution_results)
        self.thought_process_manager.log_thought("Compile Step", "Results compiled into final insight.", {"insight": final_insight})

        # Store final insight in working memory or long-term memory if significant
        self.working_memory.update_session_data("last_insight", final_insight)

        return {"insight": final_insight, "thought_log": self.thought_process_manager.get_thought_log()}

    def _refactor_directive(self, directive: str) -> Dict[str, Any]:
        """
        Refactors the user directive into a structured format, identifying goal, entities, context, and required capabilities.
        """
        llm_prompt = f"""Analyze the following user directive and extract the primary goal, key entities, relevant context, and the types of capabilities (sensors, ML models, actions) that would be needed to fulfill it. 
        Output in JSON format with the following keys:
        - 'goal': (str) The main objective.
        - 'entities': (List[str]) List of key objects or subjects.
        - 'context': (str) Any specific conditions or environmental factors.
        - 'required_capabilities': (Dict[str, List[str]]) Dictionary where keys are capability types (e.g., 'sensors', 'ml_models', 'actions') and values are lists of specific capabilities (e.g., 'video_camera', 'object_detection', 'send_alert').

        Directive: '{directive}'
        """
        response = self.llm_provider.generate_response(llm_prompt, max_tokens=300, temperature=0.2)
        try:
            refactored_data = json.loads(response.get("generated_text", "{}"))
        except json.JSONDecodeError:
            refactored_data = {"raw_directive": directive, "interpretation_error": response.get("generated_text")}
        return refactored_data

    def _break_down_task(self, refactored_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decomposes the refactored data into a sequence of concrete steps and tool calls.
        This involves LLM-driven planning based on identified goals and capabilities.
        """
        # Example: If goal is child safety, plan involves camera, object detection, and alert
        goal = refactored_data.get("goal", "")
        entities = refactored_data.get("entities", [])
        required_capabilities = refactored_data.get("required_capabilities", {})

        plan_steps = []

        # Step 1: Connect to relevant sensors
        if "sensors" in required_capabilities:
            for sensor_type in required_capabilities["sensors"]:
                if sensor_type == "video_camera": # Assuming a specific sensor type
                    # This would ideally come from long-term memory or a discovery process
                    # For now, hardcode a generic camera tool name
                    plan_steps.append({
                        "description": f"Connect to {sensor_type}",
                        "tool_call": {"tool_name": "main_camera_sensor", "args": {"operation": "connect"}}
                    })
                    plan_steps.append({
                        "description": f"Read frame from {sensor_type}",
                        "tool_call": {"tool_name": "main_camera_sensor", "args": {"operation": "read_data"}}
                    })

        # Step 2: Perform ML inference
        if "ml_models" in required_capabilities:
            for ml_model_type in required_capabilities["ml_models"]:
                if ml_model_type == "object_detection": # Assuming a specific ML model type
                    plan_steps.append({
                        "description": f"Load {ml_model_type} model",
                        "tool_call": {"tool_name": "object_detection_model", "args": {"operation": "load_model"}}
                    })
                    plan_steps.append({
                        "description": f"Perform {ml_model_type} on frame",
                        "tool_call": {"tool_name": "object_detection_model", "args": {"operation": "predict", "data": "<frame_placeholder>"}} # Placeholder for actual frame
                    })

        # Step 3: LLM-driven analysis (more detailed breakdown)
        llm_prompt = f"""Given the goal: '{goal}', entities: {entities}, and initial plan steps: {plan_steps},
        refine this plan to include detailed analysis steps and conditional logic. 
        For example, if 'child safety' is the goal and 'object_detection' is a capability, 
        include steps to analyze child's position relative to a 'balcony' and trigger 'send_alert' if dangerous.
        Output as a JSON list of refined steps, each with 'description' and optional 'tool_call'.
        """
        response = self.llm_provider.generate_response(llm_prompt, max_tokens=700, temperature=0.5)
        try:
            refined_plan = json.loads(response.get("generated_text", "[]"))
        except json.JSONDecodeError:
            refined_plan = [{
                "description": "Failed to generate refined plan from LLM.",
                "error": response.get("generated_text")
            }]
        return refined_plan

    def _execute_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executes the generated plan, calling tools and managing intermediate results.
        """
        results = []
        current_frame = None # To hold the frame read from camera
        loaded_models = {} # To keep track of loaded models

        for step in plan:
            step_result = {"step": step.get("description", "Unknown Step"), "status": "executed"}
            tool_call = step.get("tool_call")

            if tool_call:
                tool_name = tool_call.get("tool_name")
                args = tool_call.get("args", {})

                # Handle specific tool operations and pass data between steps
                if tool_name == "main_camera_sensor":
                    if args.get("operation") == "read_data":
                        # Execute the tool to get the frame
                        frame_result = self.tool_manager.execute_tool(tool_name, args, require_confirmation=False)
                        if frame_result and frame_result is not None: # Assuming frame_result is the frame itself
                            current_frame = frame_result
                            step_result["result"] = "Frame captured."
                        else:
                            step_result["status"] = "failed"
                            step_result["error"] = "Failed to capture frame."
                    else:
                        # For connect, release, get_status
                        result = self.tool_manager.execute_tool(tool_name, args, require_confirmation=False)
                        step_result["result"] = result

                elif tool_name == "object_detection_model":
                    if args.get("operation") == "load_model":
                        load_result = self.tool_manager.execute_tool(tool_name, args, require_confirmation=False)
                        if load_result: # Assuming load_model returns True on success
                            loaded_models["object_detection_model"] = True
                            step_result["result"] = "Model loaded."
                        else:
                            step_result["status"] = "failed"
                            step_result["error"] = "Failed to load model."
                    elif args.get("operation") == "predict":
                        if current_frame is not None and loaded_models.get("object_detection_model"):
                            # Replace placeholder with actual frame
                            predict_args = args.copy()
                            predict_args["data"] = current_frame
                            detections = self.tool_manager.execute_tool(tool_name, predict_args, require_confirmation=False)
                            step_result["result"] = {"detections": detections}
                        else:
                            step_result["status"] = "skipped"
                            step_result["error"] = "No frame or model not loaded for prediction."

                elif tool_name == "send_alert_notification": # Example action tool
                    payload = args.get("payload", {})
                    alert_result = self.tool_manager.execute_tool(tool_name, {"payload": payload}, require_confirmation=True)
                    step_result["result"] = alert_result

                elif tool_name == "run_shell_command": # Generic shell command
                    command = args.get("command")
                    shell_result = self.tool_manager.execute_tool(tool_name, {"command": command}, require_confirmation=True)
                    step_result["result"] = shell_result

                else:
                    # Fallback for other tools
                    try:
                        generic_result = self.tool_manager.execute_tool(tool_name, args, require_confirmation=False)
                        step_result["result"] = generic_result
                    except Exception as e:
                        step_result["status"] = "error"
                        step_result["error"] = str(e)
            else:
                step_result["status"] = "no_tool_call"

            results.append(step_result)
        return results

    def _compile_results(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesizes the execution results into a concise and actionable insight.
        """
        llm_prompt = f"""Given the following execution results from a task: {json.dumps(execution_results, indent=2)}
        
        Synthesize a concise and actionable insight. Focus on:
        - A brief summary of what was achieved.
        - Key findings or important observations.
        - Concrete recommendations or next steps based on the findings.
        
        Output in JSON format with the following keys:
        - 'summary': (str) A brief overview.
        - 'key_findings': (List[str]) Important observations.
        - 'recommendations': (List[str]) Actionable suggestions.
        """
        response = self.llm_provider.generate_response(llm_prompt, max_tokens=500, temperature=0.3)
        try:
            insight = json.loads(response.get("generated_text", "{}"))
        except json.JSONDecodeError:
            insight = {"raw_results": execution_results, "compilation_error": response.get("generated_text")}
        return insight