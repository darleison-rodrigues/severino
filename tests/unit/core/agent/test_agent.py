import unittest
import os
import json
from unittest.mock import MagicMock, patch, ANY
from typing import Any

from src.core.agent.agent import Agent
from src.core.memory.long_term_memory_manager import LongTermMemoryManager
from src.core.memory.working_memory_manager import WorkingMemoryManager
from src.core.memory.thought_process_manager import ThoughtProcessManager
from src.core.tooling.tool_manager import ToolManager
from src.llm_inference.base_llm import LLMProviderInterface

class TestAgent(unittest.TestCase):

    def setUp(self):
        self.session_id = "test_session_agent"
        self.project_root = "/tmp/test_project" # Use a temporary path for testing
        os.makedirs(os.path.join(self.project_root, ".severino", "knowledge"), exist_ok=True)

        self.llm_provider_name = "mock_llm"
        self.llm_config = {"model_path": "/fake/llm/model.gguf"}

        # Mock dependencies
        self.mock_long_term_memory = MagicMock(spec=LongTermMemoryManager)
        self.mock_working_memory = MagicMock(spec=WorkingMemoryManager)
        self.mock_thought_process_manager = MagicMock(spec=ThoughtProcessManager)
        self.mock_tool_manager = MagicMock(spec=ToolManager)
        self.mock_llm_provider = MagicMock(spec=LLMProviderInterface)
        self.mock_llm_provider.config = self.llm_config # Add config attribute to mock

        # Patch constructors and methods that Agent calls
        patcher_ltm_class = patch('src.core.agent.agent.LongTermMemoryManager', return_value=self.mock_long_term_memory)
        patcher_wm_class = patch('src.core.agent.agent.WorkingMemoryManager', return_value=self.mock_working_memory)
        patcher_tpm_class = patch('src.core.agent.agent.ThoughtProcessManager', return_value=self.mock_thought_process_manager)
        patcher_tm_class = patch('src.core.agent.agent.ToolManager', return_value=self.mock_tool_manager)
        patcher_llm_factory = patch('src.core.agent.agent.LLMFactory.create_provider', return_value=self.mock_llm_provider)

        self.mock_ltm_class = patcher_ltm_class.start()
        self.mock_wm_class = patcher_wm_class.start()
        self.mock_tpm_class = patcher_tpm_class.start()
        self.mock_tm_class = patcher_tm_class.start()
        self.mock_llm_factory = patcher_llm_factory.start()

        self.addCleanup(patcher_ltm_class.stop)
        self.addCleanup(patcher_wm_class.stop)
        self.addCleanup(patcher_tpm_class.stop)
        self.addCleanup(patcher_tm_class.stop)
        self.addCleanup(patcher_llm_factory.stop)

    def tearDown(self):
        # Clean up created directories
        if os.path.exists(self.project_root):
            import shutil
            shutil.rmtree(self.project_root)

    def test_agent_initialization(self):
        agent = Agent(self.session_id, self.project_root, self.llm_provider_name, self.llm_config)

        # Verify managers are instantiated with correct arguments
        expected_db_path = os.path.join(self.project_root, ".severino", "knowledge", "mnemonic.db")
        self.mock_ltm_class.assert_called_once_with(expected_db_path)
        self.mock_wm_class.assert_called_once_with(session_id=self.session_id, project_root=self.project_root)
        self.mock_tpm_class.assert_called_once_with(session_id=self.session_id)
        self.mock_tm_class.assert_called_once()

        # Verify LLM provider is created and loaded
        self.mock_llm_provider.load_llm.assert_called_once()
        self.mock_tool_manager.register_tool.assert_any_call(
            tool_definition={'name': 'run_shell_command', 'description': 'Executes a shell command.', 'parameters': {'command': {'type': 'string'}}, 'side_effects': True},
            implementation=agent._run_shell_command_impl
        )
        self.mock_tool_manager.register_tool.assert_any_call(
            tool_definition={
                'name': 'agent_llm_inference',
                'description': """Performs inference using the agent's primary LLM.""",
                'parameters': {
                    'operation': {'type': 'string', 'enum': ['generate_response']},
                    'prompt': {'type': 'string'},
                    'max_tokens': {'type': 'integer'},
                    'temperature': {'type': 'number'},
                    'chat_history': {'type': 'array'}
                },
                'side_effects': False
            },
            factory_type="llm", factory_name=self.llm_config.get("provider_name", "llama_cpp"), config=self.llm_config
        )

    def test_agent_initialization_llm_load_failure(self):
        self.mock_llm_provider.load_llm.return_value = False
        with self.assertRaises(RuntimeError) as cm:
            Agent(self.session_id, self.project_root, self.llm_provider_name, self.llm_config)
        self.assertIn("Failed to load LLM provider for the agent.", str(cm.exception))

    def test_process_directive_flow(self):
        agent = Agent(self.session_id, self.project_root, self.llm_provider_name, self.llm_config)

        # Mock LLM responses for each step (these are now internal to Agent's methods)
        # self.mock_llm_provider.generate_response.side_effect = [
        #     # Refactor response
        #     {"generated_text": json.dumps({"entities": ["child", "balcony"], "actions": ["monitor"], "sensors": ["camera"]})},
        #     # Break Down response
        #     {"generated_text": json.dumps([{"description": "Detect child", "tool_call": {"tool_name": "object_detection_model", "args": {"operation": "predict", "data": "frame"}}}] )},
        #     # Compile response
        #     {"generated_text": json.dumps({"summary": "Child monitored", "key_findings": ["Child detected near balcony"], "recommendations": ["Continue monitoring"]})}
        # ]

        # Mock tool execution for the plan step (if _execute_plan is called)
        self.mock_tool_manager.execute_tool.return_value = {"status": "success", "detections": [{"class_name": "child"}]}

        # Patch Agent's internal methods to control their behavior
        with patch.object(agent, '_refactor_directive', return_value={'goal': 'child_safety', 'entities': ['child', 'balcony'], 'required_capabilities': {'sensors': ['video_camera'], 'ml_models': ['object_detection']}}) as mock_refactor,
             patch.object(agent, '_break_down_task', return_value=[{'description': 'Connect camera', 'tool_call': {'tool_name': 'main_camera_sensor', 'args': {'operation': 'connect'}}},
                                                                 {'description': 'Read frame', 'tool_call': {'tool_name': 'main_camera_sensor', 'args': {'operation': 'read_data'}}},
                                                                 {'description': 'Load object detector', 'tool_call': {'tool_name': 'object_detection_model', 'args': {'operation': 'load_model'}}},
                                                                 {'description': 'Predict objects', 'tool_call': {'tool_name': 'object_detection_model', 'args': {'operation': 'predict', 'data': 'frame_placeholder'}}},
                                                                 {'description': 'Analyze child position', 'tool_call': {'tool_name': 'agent_llm_inference', 'args': {'operation': 'generate_response', 'prompt': 'analyze_child_position', 'max_tokens': 100}}},
                                                                 {'description': 'Send alert', 'tool_call': {'tool_name': 'send_alert_notification', 'args': {'payload': {'message': 'Child in danger!'}}}}] ) as mock_break_down,
             patch.object(agent, '_execute_plan', return_value=[{'step': 'Connect camera', 'result': True},
                                                              {'step': 'Read frame', 'result': np.zeros((100,100,3))},
                                                              {'step': 'Load object detector', 'result': True},
                                                              {'step': 'Predict objects', 'result': [{'class_name': 'child', 'box': [1,2,3,4]}]},
                                                              {'step': 'Analyze child position', 'result': {'generated_text': 'Child is near edge.'}},
                                                              {'step': 'Send alert', 'result': {'status': 'success'}}]) as mock_execute_plan,
             patch.object(agent, '_compile_results', return_value={'summary': 'Child monitored', 'key_findings': ['Child detected near balcony'], 'recommendations': ['Continue monitoring']}) as mock_compile:

            directive = "Watch my child on the balcony."
            result = agent.process_directive(directive)

            # Verify thought process logging
            self.mock_thought_process_manager.clear_thought_log.assert_called_once()
            self.mock_thought_process_manager.log_thought.assert_any_call("Directive Received", directive, {"directive": directive})
            self.mock_thought_process_manager.log_thought.assert_any_call("Refactor Step", "Directive interpreted and initial data structured.", ANY)
            self.mock_thought_process_manager.log_thought.assert_any_call("Break Down Step", "Task decomposed into a plan.", ANY)
            self.mock_thought_process_manager.log_thought.assert_any_call("Execution Step", "Plan executed.", ANY)
            self.mock_thought_process_manager.log_thought.assert_any_call("Compile Step", "Results compiled into final insight.", ANY)

            # Verify LLM calls for each step (now internal to patched methods)
            # The LLM is called by _refactor_directive, _break_down_task, _compile_results
            # We are patching these methods, so we don't assert on llm_provider.generate_response directly here.
            # Instead, we assert that the patched methods were called.
            mock_refactor.assert_called_once_with(directive)
            mock_break_down.assert_called_once_with(mock_refactor.return_value)
            mock_execute_plan.assert_called_once_with(mock_break_down.return_value)
            mock_compile.assert_called_once_with(mock_execute_plan.return_value)

            # Verify working memory update
            self.mock_working_memory.update_session_data.assert_called_once_with("last_insight", ANY)

            # Verify final result structure
            self.assertIn("insight", result)
            self.assertIn("thought_log", result)
            self.assertIsInstance(result["insight"], dict)
            self.assertIsInstance(result["thought_log"], list)

if __name__ == '__main__':
    unittest.main()