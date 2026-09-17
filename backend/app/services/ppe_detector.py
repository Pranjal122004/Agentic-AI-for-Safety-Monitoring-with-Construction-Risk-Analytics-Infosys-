
from pathlib import Path

from ultralytics import YOLO


class PPEDetector:
    """
    YOLO-based construction site detector.

    Detects objects, assigns confidence levels,
    and saves an annotated image with bounding boxes.
    """

    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def get_confidence_level(self, confidence):
        if confidence >= 0.80:
            return "HIGH"
        elif confidence >= 0.50:
            return "REVIEW"
        else:
            return "LOW"

    def detect(self, image_path):
        results = self.model(image_path)

        detections = []

        for result in results:
            if result.boxes is None:
                continue

            names = result.names

            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = names[class_id]

                # Bounding box coordinates
                x1, y1, x2, y2 = [
                    round(float(value), 2)
                    for value in box.xyxy[0]
                ]

                confidence_level = self.get_confidence_level(
                    confidence
                )

                detections.append({
                    "class": class_name,
                    "confidence": round(confidence, 3),
                    "confidence_level": confidence_level,
                    "bbox": [x1, y1, x2, y2]
                })

        return detections

    def detect_and_annotate(self, image_path):
        """
        Detect objects and save an image containing
        YOLO's bounding boxes and labels.
        """

        results = self.model(image_path)

        detections = []

        for result in results:
            if result.boxes is None:
                continue

            names = result.names

            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = names[class_id]

                x1, y1, x2, y2 = [
                    round(float(value), 2)
                    for value in box.xyxy[0]
                ]

                confidence_level = self.get_confidence_level(
                    confidence
                )

                detections.append({
                    "class": class_name,
                    "confidence": round(confidence, 3),
                    "confidence_level": confidence_level,
                    "bbox": [x1, y1, x2, y2]
                })

        # Create output path for annotated image
        image_path = Path(image_path)

        output_dir = image_path.parent / "annotated"
        output_dir.mkdir(parents=True, exist_ok=True)

        annotated_path = (
            output_dir / f"{image_path.stem}_annotated.jpg"
        )

        # Draw bounding boxes and labels
        for result in results:
            result.save(filename=str(annotated_path))

        return {
            "detections": detections,
            "annotated_image": str(annotated_path)
        }