import cv2
import numpy as np
from typing import Optional, Any, Dict
from .base_sensor import SensorInterface

class VideoSensor(SensorInterface):
    """
    Manages connection to an RTSP/IP camera stream and provides frame reading.
    Implements the SensorInterface for video data.
    """
    def __init__(self, sensor_id: str, config: Dict[str, Any]):
        super().__init__(sensor_id, config)
        self.rtsp_url = config.get("rtsp_url")
        if not self.rtsp_url:
            raise ValueError("RTSP URL must be provided in sensor configuration.")
        self.cap: Optional[cv2.VideoCapture] = None
        self._is_connected = False

    def connect(self) -> bool:
        """
        Establishes connection to the camera stream.
        Returns: True if connection is successful, False otherwise.
        """
        print(f"Attempting to connect to video sensor '{self.sensor_id}' at: {self.rtsp_url}")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            print(f"Error: Could not open video stream from {self.rtsp_url}")
            self.cap = None
            self._is_connected = False
            return False
        print(f"Successfully connected to video sensor '{self.sensor_id}'.")
        self._is_connected = True
        return True

    def read_data(self) -> Optional[np.ndarray]:
        """
        Reads a single frame from the camera stream.
        Returns: A numpy array representing the frame, or None if no frame is available.
        """
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                # print("Warning: Could not read frame from stream.")
                return None
        return None

    def release(self):
        """
        Releases the camera resource.
        """
        if self.cap:
            self.cap.release()
            self._is_connected = False
            print(f"Video sensor '{self.sensor_id}' stream released.")

    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the video sensor.
        """
        return {
            "sensor_id": self.sensor_id,
            "type": "VideoSensor",
            "connected": self._is_connected,
            "rtsp_url": self.rtsp_url,
            "frame_width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if self.cap and self.cap.isOpened() else None,
            "frame_height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if self.cap and self.cap.isOpened() else None,
            "fps": self.cap.get(cv2.CAP_PROP_FPS) if self.cap and self.cap.isOpened() else None
        }
