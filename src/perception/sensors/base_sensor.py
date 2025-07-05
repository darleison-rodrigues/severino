from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class SensorInterface(ABC):
    """
    Abstract base class for all sensor types.
    Defines the common interface for connecting, reading data, and releasing sensors.
    """

    def __init__(self, sensor_id: str, config: Dict[str, Any]):
        self.sensor_id = sensor_id
        self.config = config

    @abstractmethod
    def connect(self) -> bool:
        """
        Establishes connection to the sensor.
        Returns True if connection is successful, False otherwise.
        """
        pass

    @abstractmethod
    def read_data(self) -> Optional[Any]:
        """
        Reads data from the sensor.
        Returns the sensor data, or None if no data is available or an error occurs.
        The type of data returned depends on the specific sensor implementation.
        """
        pass

    @abstractmethod
    def release(self):
        """
        Releases any resources held by the sensor (e.g., closing connections).
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the sensor.
        """
        pass
