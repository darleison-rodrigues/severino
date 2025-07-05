import unittest
import numpy as np
from unittest.mock import MagicMock, patch

from src.ml_models.base_ml_model import MLModelInterface
from src.ml_models.vision.object_detector import ObjectDetector

class TestObjectDetector(unittest.TestCase):

    def setUp(self):
        self.model_id = "test_object_detector"
        self.model_path = "yolov8n.pt" # A dummy path for testing
        self.config = {"model_path": self.model_path}

    def test_object_detector_initialization(self):
        detector = ObjectDetector(self.model_id, self.config)
        self.assertIsInstance(detector, ObjectDetector)
        self.assertIsInstance(detector, MLModelInterface)
        self.assertEqual(detector.model_id, self.model_id)
        self.assertEqual(detector.model_path, self.model_path)
        self.assertIsNone(detector.model)

    @patch('src.ml_models.vision.object_detector.YOLO')
    def test_load_model_success(self, mock_yolo_class):
        mock_yolo_instance = MagicMock()
        mock_yolo_class.return_value = mock_yolo_instance

        detector = ObjectDetector(self.model_id, self.config)
        self.assertTrue(detector.load_model())
        self.assertIsNotNone(detector.model)
        mock_yolo_class.assert_called_once_with(self.model_path)

    @patch('src.ml_models.vision.object_detector.YOLO', side_effect=Exception("Model load error"))
    def test_load_model_failure(self, mock_yolo_class):
        detector = ObjectDetector(self.model_id, self.config)
        self.assertFalse(detector.load_model())
        self.assertIsNone(detector.model)

    @patch('src.ml_models.vision.object_detector.YOLO')
    def test_predict_success(self, mock_yolo_class):
        mock_yolo_instance = MagicMock()
        # Mock the return value of the YOLO model's __call__ method
        mock_results = MagicMock()
        
        # Create a mock for a single box
        mock_single_box = MagicMock()
        mock_single_box.xyxy = np.array([[10, 10, 50, 50]])
        mock_single_box.conf = np.array([0.9])
        mock_single_box.cls = np.array([0])

        # Make mock_results.boxes iterable and yield mock_single_box
        mock_results.boxes = [mock_single_box]

        mock_yolo_instance.names = {0: "person"}
        mock_yolo_instance.return_value = [mock_results]
        mock_yolo_class.return_value = mock_yolo_instance

        detector = ObjectDetector(self.model_id, self.config)
        detector.load_model()

        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        detections = detector.predict(dummy_frame)

        self.assertIsInstance(detections, list)
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0]["class_name"], "person")
        self.assertAlmostEqual(detections[0]["confidence"], 0.9)
        self.assertEqual(detections[0]["box"], [10, 10, 50, 50])
        mock_yolo_instance.assert_called_once_with(dummy_frame, verbose=False)

    def test_predict_model_not_loaded(self):
        detector = ObjectDetector(self.model_id, self.config)
        dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        detections = detector.predict(dummy_frame)
        self.assertEqual(detections, [])

    @patch('src.ml_models.vision.object_detector.YOLO')
    def test_get_status_loaded(self, mock_yolo_class):
        mock_yolo_instance = MagicMock()
        mock_yolo_instance.device = "cuda:0" # Mocking the device attribute
        mock_yolo_class.return_value = mock_yolo_instance

        detector = ObjectDetector(self.model_id, self.config)
        detector.load_model()
        status = detector.get_status()

        self.assertEqual(status["model_id"], self.model_id)
        self.assertEqual(status["type"], "ObjectDetector")
        self.assertTrue(status["loaded"])
        self.assertEqual(status["model_path"], self.model_path)
        self.assertEqual(status["device"], "cuda:0")

    def test_get_status_not_loaded(self):
        detector = ObjectDetector(self.model_id, self.config)
        status = detector.get_status()

        self.assertEqual(status["model_id"], self.model_id)
        self.assertEqual(status["type"], "ObjectDetector")
        self.assertFalse(status["loaded"])
        self.assertEqual(status["model_path"], self.model_path)
        self.assertEqual(status["device"], "N/A")

if __name__ == '__main__':
    unittest.main()