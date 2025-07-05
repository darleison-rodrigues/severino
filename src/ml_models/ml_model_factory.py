from typing import Dict, Type, Any
from src.ml_models.base_ml_model import MLModelInterface
from src.ml_models.vision.object_detector import ObjectDetector

class MLModelFactory:
    """
    Factory class to create and manage ML model instances.
    """
    _models: Dict[str, Type[MLModelInterface]] = {
        "object_detector": ObjectDetector,
        # Add other ML model types here (e.g., "anomaly_detector": AnomalyDetector)
    }

    @staticmethod
    def register_model(name: str, model_class: Type[MLModelInterface]):
        """
        Registers a new ML model class with the factory.
        """
        if not issubclass(model_class, MLModelInterface):
            raise ValueError("Model class must inherit from MLModelInterface")
        MLModelFactory._models[name] = model_class

    @staticmethod
    def create_model(name: str, model_id: str, config: Dict[str, Any]) -> MLModelInterface:
        """
        Creates an instance of the specified ML model.
        Args:
            name (str): The name of the model type (e.g., "object_detector").
            model_id (str): A unique ID for this model instance.
            config (Dict[str, Any]): Configuration dictionary for the model.
        Returns:
            MLModelInterface: An instance of the requested ML model.
        Raises:
            ValueError: If the model name is not registered.
        """
        model_class = MLModelFactory._models.get(name)
        if not model_class:
            raise ValueError(f"ML model type '{name}' not registered.")
        return model_class(model_id, config)

# Example Usage (for testing purposes)
if __name__ == "__main__":
    import logging
    import numpy as np

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Example of creating an ObjectDetector
    detector_config = {"model_path": 'yolov8n.pt'}

    try:
        obj_detector = MLModelFactory.create_model("object_detector", "my_yolo_detector", detector_config)
        if obj_detector.load_model():
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            detections = obj_detector.predict(dummy_frame)
            print(f"\nDetections on dummy frame: {detections}")
            print(f"Model Status: {obj_detector.get_status()}")
        else:
            print("Failed to load ML model via factory.")
    except ValueError as e:
        print(f"Error: {e}")
