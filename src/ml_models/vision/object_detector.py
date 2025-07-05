import numpy as np
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
from ..base_ml_model import MLModelInterface

class ObjectDetector(MLModelInterface):
    """
    Loads a YOLOv8 model and performs object detection on image frames.
    Implements the MLModelInterface for vision-based object detection.
    """
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        self.model_path = config.get("model_path", 'yolov8n.pt')
        self.model: Optional[YOLO] = None

    def load_model(self) -> bool:
        """
        Loads the YOLOv8 model into memory.
        Returns True if model is loaded successfully, False otherwise.
        """
        print(f"Loading YOLOv8 model '{self.model_id}' from: {self.model_path}")
        try:
            self.model = YOLO(self.model_path)
            print(f"YOLOv8 model '{self.model_id}' loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading YOLOv8 model '{self.model_id}': {e}")
            self.model = None
            return False

    def predict(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Performs object detection on a single image frame.
        Args:
            frame (np.ndarray): The input image frame (H, W, C) in BGR format.
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a detected object.
                                  Each dictionary contains 'box' (xyxy format), 'confidence', and 'class_name'.
        """
        if self.model is None:
            print("Error: Model not loaded. Cannot perform detection.")
            return []

        results = self.model(frame, verbose=False) # verbose=False to suppress extensive output

        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                confidence = round(box.conf[0].item(), 2)
                class_id = int(box.cls[0].item())
                class_name = self.model.names[class_id]

                detections.append({
                    "box": [x1, y1, x2, y2], # [x_min, y_min, x_max, y_max]
                    "confidence": confidence,
                    "class_name": class_name
                })
        return detections

    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current status of the object detector model.
        """
        return {
            "model_id": self.model_id,
            "type": "ObjectDetector",
            "loaded": self.model is not None,
            "model_path": self.model_path,
            "device": str(self.model.device) if self.model else "N/A"
        }

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Create a dummy frame for testing
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8) # Black 640x480 image
    print("\n--- Object Detector Example ---")

    detector = ObjectDetector(model_id="test_detector", config={"model_path": 'yolov8n.pt'})
    if detector.load_model():
        # Perform detection on the dummy frame (will likely detect nothing)
        dummy_detections = detector.predict(dummy_frame)
        print(f"Detections on dummy frame: {dummy_detections}")

        # To test with a real image, you would load it like this:
        # import cv2
        # try:
        #     img = cv2.imread("path/to/your/image.jpg")
        #     if img is not None:
        #         real_detections = detector.predict(img)
        #     else:
        #         print("Could not load image. Make sure the path is correct.")
        # except Exception as e:
        #     print(f"Error loading/processing image: {e}")

