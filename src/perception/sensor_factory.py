from typing import Dict, Type, Any
from src.perception.sensors.base_sensor import SensorInterface
from src.perception.sensors.video_sensor import VideoSensor

class SensorFactory:
    """
    Factory class to create and manage sensor instances.
    """
    _sensors: Dict[str, Type[SensorInterface]] = {
        "video": VideoSensor,
        # Add other sensor types here (e.g., "gpio": GPIOSensor, "mqtt": MQTTSensor)
    }

    @staticmethod
    def register_sensor(name: str, sensor_class: Type[SensorInterface]):
        """
        Registers a new sensor class with the factory.
        """
        if not issubclass(sensor_class, SensorInterface):
            raise ValueError("Sensor class must inherit from SensorInterface")
        SensorFactory._sensors[name] = sensor_class

    @staticmethod
    def create_sensor(name: str, sensor_id: str, config: Dict[str, Any]) -> SensorInterface:
        """
        Creates an instance of the specified sensor.
        Args:
            name (str): The name of the sensor type (e.g., "video").
            sensor_id (str): A unique ID for this sensor instance.
            config (Dict[str, Any]): Configuration dictionary for the sensor.
        Returns:
            SensorInterface: An instance of the requested sensor.
        Raises:
            ValueError: If the sensor name is not registered.
        """
        sensor_class = SensorFactory._sensors.get(name)
        if not sensor_class:
            raise ValueError(f"Sensor type '{name}' not registered.")
        return sensor_class(sensor_id, config)

# Example Usage (for testing purposes)
if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Example of creating a VideoSensor
    camera_config = {"rtsp_url": "rtsp://your.camera.url/stream"}

    try:
        video_sensor = SensorFactory.create_sensor("video", "my_home_camera", camera_config)
        print(f"Sensor created: {video_sensor.sensor_id}")
        # In a real scenario, you would connect and read data
        # if video_sensor.connect():
        #     frame = video_sensor.read_data()
        #     if frame is not None:
        #         print(f"Frame read. Shape: {frame.shape}")
        #     video_sensor.release()
        print(f"Sensor Status: {video_sensor.get_status()}")
    except ValueError as e:
        print(f"Error: {e}")
