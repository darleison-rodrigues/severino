import unittest
import os
import cv2
import numpy as np
from unittest.mock import MagicMock, patch

from src.perception.sensors.base_sensor import SensorInterface
from src.perception.sensors.video_sensor import VideoSensor

class TestVideoSensor(unittest.TestCase):

    def setUp(self):
        self.sensor_id = "test_video_sensor"
        self.rtsp_url = "rtsp://test.url/stream"
        self.config = {"rtsp_url": self.rtsp_url}

    def test_video_sensor_initialization(self):
        sensor = VideoSensor(self.sensor_id, self.config)
        self.assertIsInstance(sensor, VideoSensor)
        self.assertIsInstance(sensor, SensorInterface)
        self.assertEqual(sensor.sensor_id, self.sensor_id)
        self.assertEqual(sensor.rtsp_url, self.rtsp_url)
        self.assertIsNone(sensor.cap)
        self.assertFalse(sensor._is_connected)

    def test_video_sensor_initialization_no_rtsp_url(self):
        with self.assertRaises(ValueError) as cm:
            VideoSensor(self.sensor_id, {})
        self.assertIn("RTSP URL must be provided", str(cm.exception))

    @patch('cv2.VideoCapture')
    def test_connect_success(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap_instance

        sensor = VideoSensor(self.sensor_id, self.config)
        self.assertTrue(sensor.connect())
        self.assertTrue(sensor._is_connected)
        self.assertIsNotNone(sensor.cap)
        mock_video_capture.assert_called_once_with(self.rtsp_url)
        mock_cap_instance.isOpened.assert_called_once()

    @patch('cv2.VideoCapture')
    def test_connect_failure(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap_instance

        sensor = VideoSensor(self.sensor_id, self.config)
        self.assertFalse(sensor.connect())
        self.assertFalse(sensor._is_connected)
        self.assertIsNone(sensor.cap)
        mock_video_capture.assert_called_once_with(self.rtsp_url)
        mock_cap_instance.isOpened.assert_called_once()

    @patch('cv2.VideoCapture')
    def test_read_data_success(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cap_instance.read.return_value = (True, mock_frame)
        mock_video_capture.return_value = mock_cap_instance

        sensor = VideoSensor(self.sensor_id, self.config)
        sensor.connect() # Establish connection
        
        frame = sensor.read_data()
        self.assertIsNotNone(frame)
        np.testing.assert_array_equal(frame, mock_frame)
        mock_cap_instance.read.assert_called_once()

    @patch('cv2.VideoCapture')
    def test_read_data_failure(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.read.return_value = (False, None) # Simulate read failure
        mock_video_capture.return_value = mock_cap_instance

        sensor = VideoSensor(self.sensor_id, self.config)
        sensor.connect()

        frame = sensor.read_data()
        self.assertIsNone(frame)
        mock_cap_instance.read.assert_called_once()

    @patch('cv2.VideoCapture')
    def test_read_data_not_connected(self, mock_video_capture):
        sensor = VideoSensor(self.sensor_id, self.config)
        # Do not call connect()
        frame = sensor.read_data()
        self.assertIsNone(frame)
        mock_video_capture.assert_not_called() # VideoCapture should not be used if not connected

    @patch('cv2.VideoCapture')
    def test_release(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap_instance

        sensor = VideoSensor(self.sensor_id, self.config)
        sensor.connect()
        sensor.release()

        mock_cap_instance.release.assert_called_once()
        self.assertFalse(sensor._is_connected)

    @patch('cv2.VideoCapture')
    def test_get_status_connected(self, mock_video_capture):
        mock_cap_instance = MagicMock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.get.side_effect = [640, 480, 30.0] # Simulate width, height, fps
        mock_video_capture.return_value = mock_cap_instance

        sensor = VideoSensor(self.sensor_id, self.config)
        sensor.connect()
        status = sensor.get_status()

        self.assertEqual(status["sensor_id"], self.sensor_id)
        self.assertEqual(status["type"], "VideoSensor")
        self.assertTrue(status["connected"])
        self.assertEqual(status["rtsp_url"], self.rtsp_url)
        self.assertEqual(status["frame_width"], 640)
        self.assertEqual(status["frame_height"], 480)
        self.assertEqual(status["fps"], 30.0)

    @patch('cv2.VideoCapture')
    def test_get_status_not_connected(self, mock_video_capture):
        sensor = VideoSensor(self.sensor_id, self.config)
        status = sensor.get_status()

        self.assertEqual(status["sensor_id"], self.sensor_id)
        self.assertEqual(status["type"], "VideoSensor")
        self.assertFalse(status["connected"])
        self.assertEqual(status["rtsp_url"], self.rtsp_url)
        self.assertIsNone(status["frame_width"])
        self.assertIsNone(status["frame_height"])
        self.assertIsNone(status["fps"])

if __name__ == '__main__':
    unittest.main()
