from app.services.ppe_detector import PPEDetector


model_path = "models/ppe_model.pt"
image_path = "data/test_image.jpg"

detector = PPEDetector(model_path)

detections = detector.detect(image_path)

print("=" * 60)
print("PPE DETECTION RESULTS")
print("=" * 60)

if not detections:
    print("No objects detected.")
else:

    for detection in detections:

        print(
            f"Object: {detection['class']} | "
            f"Confidence: {detection['confidence']}"
        )