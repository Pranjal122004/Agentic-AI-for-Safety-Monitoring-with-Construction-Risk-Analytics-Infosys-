from app.agents.insurance_agent import InsuranceAgent


agent = InsuranceAgent()


print("\n========================================")
print("INSURANCE AGENT RELIABILITY TEST")
print("========================================")


# =====================================================
# TEST 1 — CONFIRMED HIGH-CONFIDENCE VIOLATION
# =====================================================

ppe_high = {
    "safety_analysis": {
        "risk_level": "HIGH",
        "confirmed_violations": 1,
        "review_required": 0
    }
}

compliance_high = {
    "compliance_status": "NON-COMPLIANT",
    "total_violations": 1,
    "total_reviews": 0
}

site_low = {
    "risk_level": "LOW",
    "risk_score": 30,
    "hazards": []
}

result = agent.assess_risk(
    ppe_result=ppe_high,
    site_risk_result=site_low,
    compliance_result=compliance_high
)

print("\n--- TEST 1: CONFIRMED VIOLATION ---")
print("Insurance Score:", result["insurance_risk_score"])
print("Insurance Level:", result["insurance_risk_level"])
print("Claim Risk:", result["claim_risk"])
print("Risk Factors:", result["risk_factors"])
print("Manual Review:", result["manual_review_required"])


# =====================================================
# TEST 2 — REVIEW REQUIRED
# =====================================================

ppe_review = {
    "safety_analysis": {
        "risk_level": "MEDIUM",
        "confirmed_violations": 0,
        "review_required": 1
    }
}

compliance_review = {
    "compliance_status": "REVIEW REQUIRED",
    "total_violations": 0,
    "total_reviews": 1
}

result = agent.assess_risk(
    ppe_result=ppe_review,
    site_risk_result=site_low,
    compliance_result=compliance_review
)

print("\n--- TEST 2: REVIEW REQUIRED ---")
print("Insurance Score:", result["insurance_risk_score"])
print("Insurance Level:", result["insurance_risk_level"])
print("Claim Risk:", result["claim_risk"])
print("Risk Factors:", result["risk_factors"])
print("Review Factors:", result["review_factors"])
print("Manual Review:", result["manual_review_required"])


# =====================================================
# TEST 3 — NO PPE VIOLATION
# =====================================================

ppe_clean = {
    "safety_analysis": {
        "risk_level": "LOW",
        "confirmed_violations": 0,
        "review_required": 0
    }
}

compliance_clean = {
    "compliance_status": "COMPLIANT",
    "total_violations": 0,
    "total_reviews": 0
}

result = agent.assess_risk(
    ppe_result=ppe_clean,
    site_risk_result=site_low,
    compliance_result=compliance_clean
)

print("\n--- TEST 3: CLEAN SITE ---")
print("Insurance Score:", result["insurance_risk_score"])
print("Insurance Level:", result["insurance_risk_level"])
print("Claim Risk:", result["claim_risk"])
print("Risk Factors:", result["risk_factors"])
print("Manual Review:", result["manual_review_required"])


print("\n========================================")
print("TEST COMPLETED")
print("========================================")