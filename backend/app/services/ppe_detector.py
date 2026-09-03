from ultralytics import YOLO


class PPEDetector:
    """
    YOLO-based PPE detector for construction site images.
    """

    def __init__(self, model_path):
        self.model = YOLO(model_path)

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

                detections.append(
                    {
                        "class": class_name,
                        "confidence": round(confidence, 3)
                    }
                )

        return detections