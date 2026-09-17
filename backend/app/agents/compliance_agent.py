class ComplianceAgent:
    """
    Compliance Agent for construction-site regulatory validation.

    The agent checks PPE observations against configured
    construction safety rules.

    Detection confidence is considered when deciding whether
    a finding is confirmed or requires manual review.
    """

    def __init__(self):
        self.rules = {
            "hardhat": {
                "name": "Hardhat Requirement",
                "violation_class": "no-hardhat",
                "description": "Workers must wear protective hardhats.",
                "priority": "HIGH"
            },
            "mask": {
                "name": "Mask Requirement",
                "violation_class": "no-mask",
                "description": "Workers must wear required protective masks.",
                "priority": "MEDIUM"
            },
            "safety_vest": {
                "name": "Safety Vest Requirement",
                "violation_class": "no-safetyvest",
                "description": "Workers must wear high-visibility safety vests.",
                "priority": "HIGH"
            }
        }

    def get_confidence_level(self, detection):
        """
        Determine the reliability of a detection.

        HIGH   : confidence >= 0.80
        REVIEW : confidence >= 0.50 and < 0.80
        LOW    : confidence < 0.50
        """

        confidence_level = detection.get(
            "confidence_level"
        )

        if confidence_level:
            return confidence_level

        confidence = float(
            detection.get("confidence", 0)
        )

        if confidence >= 0.80:
            return "HIGH"
        elif confidence >= 0.50:
            return "REVIEW"
        else:
            return "LOW"

    def validate_ppe(self, detections):

        confirmed_violations = []
        review_findings = []

        for detection in detections:

            class_name = str(
                detection.get("class", "")
            ).lower()

            class_name = class_name.replace(
                " ",
                ""
            )

            confidence_level = self.get_confidence_level(
                detection
            )

            for rule in self.rules.values():

                if class_name != rule["violation_class"]:
                    continue

                violation_data = {
                    "rule": rule["name"],
                    "violation": rule["description"],
                    "priority": rule["priority"],
                    "detected_class": detection.get("class"),
                    "confidence": detection.get("confidence"),
                    "confidence_level": confidence_level
                }

                # High confidence = confirmed violation
                if confidence_level == "HIGH":

                    confirmed_violations.append(
                        violation_data
                    )

                # Medium confidence = manual review
                elif confidence_level == "REVIEW":

                    review_data = violation_data.copy()

                    review_data["review_reason"] = (
                        "Detection confidence is moderate. "
                        "Manual verification recommended."
                    )

                    review_findings.append(
                        review_data
                    )

                # Low confidence detections are ignored
                # for automatic compliance decisions.

        return {
            "confirmed_violations": confirmed_violations,
            "review_findings": review_findings
        }

    def generate_report(self, detections):

        validation_result = self.validate_ppe(
            detections
        )

        confirmed_violations = validation_result[
            "confirmed_violations"
        ]

        review_findings = validation_result[
            "review_findings"
        ]

        recommendations = []

        # Recommendations for confirmed violations
        for violation in confirmed_violations:

            if violation["rule"] == "Hardhat Requirement":

                recommendations.append(
                    "Ensure all workers wear protective hardhats."
                )

            elif violation["rule"] == "Mask Requirement":

                recommendations.append(
                    "Ensure workers use required protective masks."
                )

            elif violation["rule"] == "Safety Vest Requirement":

                recommendations.append(
                    "Ensure all workers wear high-visibility safety vests."
                )

        # Recommendations for findings requiring review
        for finding in review_findings:

            if finding["rule"] == "Hardhat Requirement":

                recommendations.append(
                    "Manually verify the worker's hardhat compliance."
                )

            elif finding["rule"] == "Mask Requirement":

                recommendations.append(
                    "Manually verify the worker's mask compliance."
                )

            elif finding["rule"] == "Safety Vest Requirement":

                recommendations.append(
                    "Manually verify the worker's safety vest compliance."
                )

        recommendations = list(
            dict.fromkeys(
                recommendations
            )
        )

        # Determine compliance status
        if confirmed_violations:

            compliance_status = "NON-COMPLIANT"

        elif review_findings:

            compliance_status = "REVIEW REQUIRED"

        else:

            compliance_status = "COMPLIANT"

        return {
            "compliance_status": compliance_status,

            "total_violations": len(
                confirmed_violations
            ),

            "violations": confirmed_violations,

            "review_findings": review_findings,

            "total_reviews": len(
                review_findings
            ),

            "recommendations": recommendations
        }

    def analyze(self, ppe_result):

        detections = ppe_result.get(
            "detections",
            []
        )

        return self.generate_report(
            detections
        )