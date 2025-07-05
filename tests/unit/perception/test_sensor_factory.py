import unittest
from typing import Any
import unittest
from unittest.mock import MagicMock, patch

from src.perception.sensors.base_sensor import SensorInterface
from src.perception.sensor_factory import SensorFactory

# Mock a concrete Sensor for testing the factory
class MockSensor(SensorInterface):
    def connect(self) -> bool:
        return True

    def read_data(self) -> Any:
        return "mock_data"

    def release(self):
        pass

    def get_status(self) -> dict:
        return {"status": "mocked"}

class TestSensorFactory(unittest.TestCase):

    def setUp(self):
        # Clear registered sensors before each test to ensure isolation
        SensorFactory._sensors = {}

    def test_register_sensor_success(self):
        SensorFactory.register_sensor("mock_sensor", MockSensor)
        self.assertIn("mock_sensor", SensorFactory._sensors)
        self.assertEqual(SensorFactory._sensors["mock_sensor"], MockSensor)

    def test_register_sensor_invalid_class(self):
        with self.assertRaises(ValueError) as cm:
            SensorFactory.register_sensor("invalid_sensor", MagicMock)
        self.assertIn("Sensor class must inherit from SensorInterface", str(cm.exception))

    def test_create_sensor_success(self):
        SensorFactory.register_sensor("mock_sensor", MockSensor)
        config = {"param": "value"}
        sensor = SensorFactory.create_sensor("mock_sensor", "test_instance", config)
        self.assertIsInstance(sensor, MockSensor)
        self.assertEqual(sensor.sensor_id, "test_instance")
        self.assertEqual(sensor.config, config)

    def test_create_sensor_not_registered(self):
        config = {"param": "value"}
        with self.assertRaises(ValueError) as cm:
            SensorFactory.create_sensor("non_existent_sensor", "test_instance", config)
        self.assertIn("Sensor type 'non_existent_sensor' not registered.", str(cm.exception))

    def test_create_sensor_with_actual_video_sensor(self):
        # This test requires VideoSensor to be importable and its dependencies mocked
        from src.perception.sensors.video_sensor import VideoSensor
        SensorFactory.register_sensor("video", VideoSensor)
        
        # Mock cv2.VideoCapture and os.path.exists for VideoSensor's internal workings
        with patch('src.perception.sensors.video_sensor.cv2.VideoCapture') as mock_video_capture_class, \
             patch('src.perception.sensors.video_sensor.np.ndarray'), \
             patch('os.path.exists', return_value=True): # Patch os.path.exists if VideoSensor checks file paths
            
            mock_video_capture_instance = MagicMock()
            mock_video_capture_instance.isOpened.return_value = False # Explicitly mock connection failure
            mock_video_capture_class.return_value = mock_video_capture_instance

            config = {"rtsp_url": "rtsp://fake.url/stream"}
            sensor = SensorFactory.create_sensor("video", "real_video_sensor", config)
            self.assertIsInstance(sensor, VideoSensor)
            self.assertEqual(sensor.sensor_id, "real_video_sensor")
            self.assertEqual(sensor.config, config)
            # Test that connect can be called (it will be mocked internally)
            self.assertFalse(sensor.connect()) # connect will return False by default mock

if __name__ == '__main__':
    unittest.main()
