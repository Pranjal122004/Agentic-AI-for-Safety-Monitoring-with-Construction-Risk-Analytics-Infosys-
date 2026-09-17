from app.agents.compliance_agent import ComplianceAgent


agent = ComplianceAgent()


print("\n========================================")
print("COMPLIANCE AGENT RELIABILITY TEST")
print("========================================")


# TEST 1 — HIGH confidence
high_confidence = [
    {
        "class": "NO-Safety Vest",
        "confidence": 0.90,
        "confidence_level": "HIGH"
    }
]

result = agent.analyze({
    "detections": high_confidence
})

print("\n--- TEST 1: HIGH CONFIDENCE ---")
print("Status:", result["compliance_status"])
print("Confirmed violations:", result["total_violations"])
print("Reviews required:", result["total_reviews"])


# TEST 2 — REVIEW confidence
review_confidence = [
    {
        "class": "NO-Safety Vest",
        "confidence": 0.63,
        "confidence_level": "REVIEW"
    }
]

result = agent.analyze({
    "detections": review_confidence
})

print("\n--- TEST 2: REVIEW CONFIDENCE ---")
print("Status:", result["compliance_status"])
print("Confirmed violations:", result["total_violations"])
print("Reviews required:", result["total_reviews"])


# TEST 3 — LOW confidence
low_confidence = [
    {
        "class": "NO-Safety Vest",
        "confidence": 0.43,
        "confidence_level": "LOW"
    }
]

result = agent.analyze({
    "detections": low_confidence
})

print("\n--- TEST 3: LOW CONFIDENCE ---")
print("Status:", result["compliance_status"])
print("Confirmed violations:", result["total_violations"])
print("Reviews required:", result["total_reviews"])


print("\n========================================")
print("TEST COMPLETED")
print("========================================")