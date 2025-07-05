import unittest
from typing import Any
import unittest
from unittest.mock import MagicMock, patch

from src.ml_models.base_ml_model import MLModelInterface
from src.ml_models.ml_model_factory import MLModelFactory

# Mock a concrete MLModel for testing the factory
class MockMLModel(MLModelInterface):
    def load_model(self) -> bool:
        return True

    def predict(self, data: Any) -> Any:
        return "mock_prediction"

    def get_status(self) -> dict:
        return {"status": "mocked"}

class TestMLModelFactory(unittest.TestCase):

    def setUp(self):
        # Clear registered models before each test to ensure isolation
        MLModelFactory._models = {}

    def test_register_model_success(self):
        MLModelFactory.register_model("mock_model", MockMLModel)
        self.assertIn("mock_model", MLModelFactory._models)
        self.assertEqual(MLModelFactory._models["mock_model"], MockMLModel)

    def test_register_model_invalid_class(self):
        with self.assertRaises(ValueError) as cm:
            MLModelFactory.register_model("invalid_model", MagicMock)
        self.assertIn("Model class must inherit from MLModelInterface", str(cm.exception))

    def test_create_model_success(self):
        MLModelFactory.register_model("mock_model", MockMLModel)
        config = {"param": "value"}
        model = MLModelFactory.create_model("mock_model", "test_instance", config)
        self.assertIsInstance(model, MockMLModel)
        self.assertEqual(model.model_id, "test_instance")
        self.assertEqual(model.config, config)

    def test_create_model_not_registered(self):
        config = {"param": "value"}
        with self.assertRaises(ValueError) as cm:
            MLModelFactory.create_model("non_existent_model", "test_instance", config)
        self.assertIn("ML model type 'non_existent_model' not registered.", str(cm.exception))

    def test_create_model_with_actual_object_detector(self):
        # This test requires ObjectDetector to be importable and its dependencies mocked
        from src.ml_models.vision.object_detector import ObjectDetector
        MLModelFactory.register_model("object_detector", ObjectDetector)
        
        # Mock ultralytics.YOLO for ObjectDetector's internal workings
        with patch('src.ml_models.vision.object_detector.YOLO'):
            config = {"model_path": "yolov8n.pt"}
            model = MLModelFactory.create_model("object_detector", "real_detector", config)
            self.assertIsInstance(model, ObjectDetector)
            self.assertEqual(model.model_id, "real_detector")
            self.assertEqual(model.config, config)
            self.assertTrue(model.load_model()) # Test that load_model can be called

if __name__ == '__main__':
    unittest.main()
