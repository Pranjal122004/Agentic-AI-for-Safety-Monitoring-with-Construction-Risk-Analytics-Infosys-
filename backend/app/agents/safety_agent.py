class SafetyAgent:
    """
    Safety Agent for construction-site safety analysis.

    Combines:
    1. PPE detection results
    2. Site risk results

    The agent also considers the confidence level of
    AI detections before declaring a PPE violation.
    """

    def analyze_detections(self, detections):
        confirmed_hazards = []
        review_hazards = []
        confirmed_recommendations = []
        review_recommendations = []

        for detection in detections:
            class_name = str(detection.get("class", "")).lower()
            class_name = class_name.replace(" ", "")

            confidence = float(detection.get("confidence", 0))

            confidence_level = detection.get("confidence_level")

            if not confidence_level:
                if confidence >= 0.80:
                    confidence_level = "HIGH"
                elif confidence >= 0.50:
                    confidence_level = "REVIEW"
                else:
                    confidence_level = "LOW"

            hazard = None
            recommendation = None

            if class_name == "no-hardhat":
                hazard = "Worker without hardhat"
                recommendation = "Ensure workers wear hardhats."

            elif class_name == "no-mask":
                hazard = "Worker without mask"
                recommendation = "Ensure workers wear required masks."

            elif class_name == "no-safetyvest":
                hazard = "Worker without safety vest"
                recommendation = "Ensure workers wear safety vests."

            if not hazard:
                continue

            if confidence_level == "HIGH":
                confirmed_hazards.append(hazard)
                confirmed_recommendations.append(recommendation)

            elif confidence_level == "REVIEW":
                review_hazards.append(
                    f"Potential issue: {hazard}"
                )

                review_recommendations.append(
                    f"Manual verification recommended: {recommendation}"
                )

        # Remove duplicates
        confirmed_hazards = list(dict.fromkeys(confirmed_hazards))
        review_hazards = list(dict.fromkeys(review_hazards))

        confirmed_recommendations = list(
            dict.fromkeys(confirmed_recommendations)
        )

        review_recommendations = list(
            dict.fromkeys(review_recommendations)
        )

        # Determine PPE risk
        if confirmed_hazards:
            risk_level = "HIGH"
            status = "High-confidence PPE safety violation detected."

        elif review_hazards:
            risk_level = "MEDIUM"
            status = (
                "Potential PPE violation detected. "
                "Manual verification recommended."
            )

        else:
            risk_level = "LOW"
            status = "No high-confidence PPE violation detected."

        hazards = confirmed_hazards + review_hazards

        recommendations = (
            confirmed_recommendations
            + review_recommendations
        )

        return {
            "risk_level": risk_level,
            "hazards": hazards,
            "recommendations": recommendations,
            "status": status,
            "confirmed_violations": len(confirmed_hazards),
            "review_required": len(review_hazards)
        }

    def analyze(self, ppe_result, site_risk_result):
        hazards = []
        recommendations = []

        # -----------------------------
        # PPE ANALYSIS
        # -----------------------------
        ppe_detections = ppe_result.get("detections", [])

        ppe_analysis = self.analyze_detections(
            ppe_detections
        )

        hazards.extend(
            ppe_analysis.get("hazards", [])
        )

        recommendations.extend(
            ppe_analysis.get("recommendations", [])
        )

        # -----------------------------
        # SITE RISK ANALYSIS
        # -----------------------------
        site_risk = site_risk_result.get(
            "risk_score",
            0
        )

        site_level = site_risk_result.get(
            "risk_level",
            "LOW"
        )

        site_hazards = site_risk_result.get(
            "hazards",
            []
        )

        hazards.extend(site_hazards)

        site_recommendation = site_risk_result.get(
            "recommendation"
        )

        if site_recommendation:
            recommendations.append(
                site_recommendation
            )

        # -----------------------------
        # OVERALL RISK
        # -----------------------------
        risk_priority = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4
        }

        overall_level = site_level

        ppe_level = ppe_analysis["risk_level"]

        if (
            risk_priority.get(ppe_level, 1)
            > risk_priority.get(overall_level, 1)
        ):
            overall_level = ppe_level

        # Remove duplicates
        hazards = list(dict.fromkeys(hazards))
        recommendations = list(
            dict.fromkeys(recommendations)
        )

        # -----------------------------
        # FINAL STATUS
        # -----------------------------
        if overall_level == "CRITICAL":
            status = "Immediate action required."

        elif overall_level == "HIGH":
            status = "Urgent safety intervention required."

        elif overall_level == "MEDIUM":
            status = "Preventive safety action recommended."

        else:
            status = (
                "No high-confidence safety violation detected."
            )

        return {
            "overall_risk_level": overall_level,
            "site_risk_score": site_risk,
            "ppe_risk_level": ppe_analysis["risk_level"],
            "hazards": hazards,
            "recommendations": recommendations,
            "status": status,
            "confirmed_ppe_violations": (
                ppe_analysis["confirmed_violations"]
            ),
            "ppe_reviews_required": (
                ppe_analysis["review_required"]
            )
        }