from app.agents.safety_agent import SafetyAgent


agent = SafetyAgent()


# Example output from the real PPE detector
detections = [
    {
        "class": "Person",
        "confidence": 0.94
    },
    {
        "class": "NO-Hardhat",
        "confidence": 0.88
    },
    {
        "class": "Safety Vest",
        "confidence": 0.91
    }
]


result = agent.analyze_detections(detections)


print("=" * 60)
print("SAFETY INTELLIGENCE RESULT")
print("=" * 60)

print("Detected PPE:", result["detected_ppe"])
print("Violations:", result["violations"])
print("Safety Score:", result["safety_score"])
print("Safety Level:", result["safety_level"])
print("Alert:", result["alert"])
