from app.services.ppe_detector import PPEDetector
from app.agents.safety_agent import SafetyAgent


MODEL_PATH = "models/ppe_model.pt"
IMAGE_PATH = "backend/data/test_image.jpg"


# Create agents
ppe_detector = PPEDetector(MODEL_PATH)
safety_agent = SafetyAgent()


# Detect PPE from real construction image
detections = ppe_detector.detect(IMAGE_PATH)


# Analyze detections using Safety Agent
result = safety_agent.analyze_detections(detections)


print("=" * 60)
print("CONSTRUCTION PPE SAFETY ANALYSIS")
print("=" * 60)

print("\nYOLO DETECTIONS:")

for detection in detections:
    print(
        f"- {detection['class']} "
        f"(confidence: {detection['confidence']})"
    )


print("\nSAFETY ANALYSIS:")
print("Detected PPE:", result["detected_ppe"])
print("Violations:", result["violations"])
print("Safety Score:", result["safety_score"])
print("Safety Level:", result["safety_level"])
print("Alert:", result["alert"])

print("=" * 60)