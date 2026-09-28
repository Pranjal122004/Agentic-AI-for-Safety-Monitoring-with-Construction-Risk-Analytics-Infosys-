
class RiskIntelligenceAgent:
    """
    Combines site and safety findings into a simple
    construction risk intelligence summary.
    """

    def analyze(self, site_risk_result=None, safety_result=None):
        site_risk_result = site_risk_result or {}
        safety_result = safety_result or {}

        # Read the site risk score
        risk_score = site_risk_result.get("risk_score", 0)

        # Read the risk level
        risk_level = site_risk_result.get(
            "risk_level", "UNKNOWN"
        )

        # Collect hazards from both agents
        site_hazards = site_risk_result.get("hazards", [])
        safety_hazards = safety_result.get("hazards", [])

        hazards = site_hazards + safety_hazards

        # Collect recommendations
        recommendations = []

        site_recommendation = site_risk_result.get(
            "recommendation"
        )
        if site_recommendation:
            recommendations.append(site_recommendation)

        safety_recommendations = safety_result.get(
            "recommendations", []
        )
        recommendations.extend(safety_recommendations)

        # Check whether manual review is required
        reliability = safety_result.get(
            "reliability_summary", {}
        )
        manual_review_required = reliability.get(
            "manual_review_required", False
        )

        if manual_review_required:
            recommendations.append(
                "Manual review is required for uncertain PPE detections."
            )

        # Remove duplicate recommendations
        recommendations = list(dict.fromkeys(recommendations))

        # Create the intelligence summary
        summary = {
            "site_id": site_risk_result.get(
                "site_id", "UNKNOWN"
            ),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "total_hazards": len(hazards),
            "hazards": hazards,
            "manual_review_required": manual_review_required,
            "recommendations": recommendations,
            "summary": (
                f"Site risk level is {risk_level} "
                f"with a risk score of {risk_score}. "
                f"Detected {len(hazards)} hazards."
            )
        }

        return summary