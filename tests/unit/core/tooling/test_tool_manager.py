import unittest
from unittest.mock import MagicMock, patch
from typing import Any, Dict

from src.core.tooling.tool_manager import ToolManager
from src.perception.sensors.base_sensor import SensorInterface
from src.ml_models.base_ml_model import MLModelInterface
from src.llm_inference.base_llm import LLMProviderInterface
from src.actions.base_action import ActionInterface

# Example Action Implementation (moved here for test scope)
class NotificationAction(ActionInterface):
    def __init__(self, action_id: str, config: Dict[str, Any]):
        super().__init__(action_id, config)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        message = payload.get("message", "No message provided.")
        recipient = payload.get("recipient", "user")
        # print(f"[NotificationAction] Sending message to {recipient}: {message}") # Suppress print in test
        return {"status": "success", "message_sent": message, "recipient": recipient}

    def get_status(self) -> Dict[str, Any]:
        return {"action_id": self.action_id, "type": "NotificationAction", "ready": True}

class TestToolManager(unittest.TestCase):

    def setUp(self):
        self.tool_manager = ToolManager()

    def test_register_tool_direct_callable(self):
        def mock_func(arg1: str): return f"Called with {arg1}"
        self.tool_manager.register_tool(
            tool_definition={"name": "test_func", "description": "A test function"},
            implementation=mock_func
        )
        self.assertIn("test_func", self.tool_manager._tools)
        self.assertIn("test_func", self.tool_manager._tool_implementations)
        self.assertEqual(self.tool_manager._tool_implementations["test_func"], mock_func)

    @patch('src.perception.sensor_factory.SensorFactory.create_sensor')
    def test_register_tool_sensor_factory(self, mock_create_sensor):
        mock_sensor_instance = MagicMock(spec=SensorInterface)
        mock_create_sensor.return_value = mock_sensor_instance

        config = {"rtsp_url": "test_url"}
        self.tool_manager.register_tool(
            tool_definition={"name": "test_sensor", "description": "A test sensor"},
            factory_type="sensor", factory_name="video", config=config
        )
        self.assertIn("test_sensor", self.tool_manager._tools)
        self.assertIn("test_sensor", self.tool_manager._tool_instances)
        self.assertEqual(self.tool_manager._tool_instances["test_sensor"], mock_sensor_instance)
        mock_create_sensor.assert_called_once_with("video", "test_sensor", config)

    @patch('src.ml_models.ml_model_factory.MLModelFactory.create_model')
    def test_register_tool_ml_model_factory(self, mock_create_model):
        mock_model_instance = MagicMock(spec=MLModelInterface)
        mock_create_model.return_value = mock_model_instance

        config = {"model_path": "test_path"}
        self.tool_manager.register_tool(
            tool_definition={"name": "test_model", "description": "A test model"},
            factory_type="ml_model", factory_name="object_detector", config=config
        )
        self.assertIn("test_model", self.tool_manager._tools)
        self.assertIn("test_model", self.tool_manager._tool_instances)
        self.assertEqual(self.tool_manager._tool_instances["test_model"], mock_model_instance)
        mock_create_model.assert_called_once_with("object_detector", "test_model", config)

    @patch('src.llm_inference.llm_factory.LLMFactory.create_provider')
    def test_register_tool_llm_factory(self, mock_create_provider):
        mock_llm_instance = MagicMock(spec=LLMProviderInterface)
        mock_create_provider.return_value = mock_llm_instance

        config = {"llm_param": "value"}
        self.tool_manager.register_tool(
            tool_definition={"name": "test_llm", "description": "A test LLM"},
            factory_type="llm", factory_name="llama_cpp", config=config
        )
        self.assertIn("test_llm", self.tool_manager._tools)
        self.assertIn("test_llm", self.tool_manager._tool_instances)
        self.assertEqual(self.tool_manager._tool_instances["test_llm"], mock_llm_instance)
        mock_create_provider.assert_called_once_with("llama_cpp", "test_llm", config)

    def test_register_tool_action_factory(self):
        config = {"action_param": "value"}
        self.tool_manager.register_tool(
            tool_definition={"name": "test_action", "description": "A test action"},
            factory_type="action", implementation=NotificationAction, config=config
        )
        self.assertIn("test_action", self.tool_manager._tools)
        self.assertIn("test_action", self.tool_manager._tool_instances)
        self.assertIsInstance(self.tool_manager._tool_instances["test_action"], NotificationAction)

    def test_register_tool_invalid_factory_type(self):
        with self.assertRaises(ValueError) as cm:
            self.tool_manager.register_tool(
                tool_definition={"name": "invalid_tool"},
                factory_type="unknown_type", factory_name="name", config={}
            )
        self.assertIn("Unknown factory_type: unknown_type", str(cm.exception))

    def test_get_tool_definition(self):
        tool_def = {"name": "get_def_test", "description": "Get definition test"}
        self.tool_manager.register_tool(tool_def, lambda: None)
        retrieved_def = self.tool_manager.get_tool_definition("get_def_test")
        self.assertEqual(retrieved_def, tool_def)

    def test_get_all_tool_definitions(self):
        self.tool_manager.register_tool({"name": "tool1"}, lambda: None)
        self.tool_manager.register_tool({"name": "tool2"}, lambda: None)
        all_defs = self.tool_manager.get_all_tool_definitions()
        self.assertEqual(len(all_defs), 2)
        self.assertIn({"name": "tool1"}, all_defs)
        self.assertIn({"name": "tool2"}, all_defs)

    def test_execute_tool_not_found(self):
        with self.assertRaises(ValueError) as cm:
            self.tool_manager.execute_tool("non_existent_tool", {})
        self.assertIn("Tool 'non_existent_tool' not found.", str(cm.exception))

    @patch('builtins.input', return_value='yes')
    def test_execute_tool_direct_callable_with_confirmation_yes(self, mock_input):
        mock_func = MagicMock(return_value="Executed")
        self.tool_manager.register_tool(
            tool_definition={"name": "sensitive_func", "side_effects": True},
            implementation=mock_func
        )
        result = self.tool_manager.execute_tool("sensitive_func", {"arg": "value"})
        self.assertEqual(result, "Executed")
        mock_func.assert_called_once_with(arg="value")
        mock_input.assert_called_once()

    @patch('builtins.input', return_value='no')
    def test_execute_tool_direct_callable_with_confirmation_no(self, mock_input):
        mock_func = MagicMock()
        self.tool_manager.register_tool(
            tool_definition={"name": "sensitive_func", "side_effects": True},
            implementation=mock_func
        )
        result = self.tool_manager.execute_tool("sensitive_func", {"arg": "value"})
        self.assertEqual(result, {"status": "cancelled", "message": "Tool execution cancelled by user."})
        mock_func.assert_not_called()
        mock_input.assert_called_once()

    @patch('builtins.input', return_value='yes')
    @patch('src.perception.sensor_factory.SensorFactory.create_sensor')
    def test_execute_tool_sensor_instance_connect(self, mock_create_sensor, mock_input):
        mock_sensor_instance = MagicMock(spec=SensorInterface)
        mock_sensor_instance.connect.return_value = True
        mock_create_sensor.return_value = mock_sensor_instance

        config = {"rtsp_url": "test_url"}
        self.tool_manager.register_tool(
            tool_definition={"name": "test_sensor", "side_effects": True},
            factory_type="sensor", factory_name="video", config=config
        )
        result = self.tool_manager.execute_tool("test_sensor", {"operation": "connect"})
        self.assertTrue(result)
        mock_sensor_instance.connect.assert_called_once()

    @patch('builtins.input', return_value='yes')
    @patch('src.ml_models.ml_model_factory.MLModelFactory.create_model')
    def test_execute_tool_ml_model_instance_predict(self, mock_create_model, mock_input):
        mock_model_instance = MagicMock(spec=MLModelInterface)
        mock_model_instance.predict.return_value = [{"class": "person"}]
        mock_create_model.return_value = mock_model_instance

        config = {"model_path": "test_path"}
        self.tool_manager.register_tool(
            tool_definition={"name": "test_model", "side_effects": False},
            factory_type="ml_model", factory_name="object_detector", config=config
        )
        dummy_data = MagicMock()
        result = self.tool_manager.execute_tool("test_model", {"operation": "predict", "data": dummy_data})
        self.assertEqual(result, [{"class": "person"}])
        mock_model_instance.predict.assert_called_once_with(dummy_data)

    @patch('builtins.input', return_value='yes')
    @patch('src.llm_inference.llm_factory.LLMFactory.create_provider')
    def test_execute_tool_llm_instance_generate_response(self, mock_create_provider, mock_input):
        mock_llm_instance = MagicMock(spec=LLMProviderInterface)
        mock_llm_instance.generate_response.return_value = {"generated_text": "LLM response"}
        mock_create_provider.return_value = mock_llm_instance

        config = {"llm_param": "value"}
        self.tool_manager.register_tool(
            tool_definition={"name": "test_llm", "side_effects": False},
            factory_type="llm", factory_name="llama_cpp", config=config
        )
        prompt_args = {"prompt": "test prompt", "max_tokens": 50, "temperature": 0.7}
        result = self.tool_manager.execute_tool("test_llm", {"operation": "generate_response", **prompt_args})
        self.assertEqual(result, {"generated_text": "LLM response"})
        mock_llm_instance.generate_response.assert_called_once_with(prompt_args["prompt"], max_tokens=prompt_args["max_tokens"], temperature=prompt_args["temperature"])

    @patch('builtins.input', return_value='yes')
    def test_execute_tool_action_instance_execute(self, mock_input):
        config = {"action_param": "value"}
        self.tool_manager.register_tool(
            tool_definition={"name": "test_action", "side_effects": True},
            factory_type="action", implementation=NotificationAction, config=config
        )
        payload = {"message": "Hello"}
        result = self.tool_manager.execute_tool("test_action", {"payload": payload})
        self.assertEqual(result, {"status": "success", "message_sent": "Hello", "recipient": "user"})

if __name__ == '__main__':
    unittest.main()