class InsuranceAgent:
    """
    Insurance Agent for construction risk assessment.

    Evaluates safety, compliance, and site conditions to estimate
    insurance exposure and claim risk.

    The agent distinguishes between confirmed risks and
    AI findings that require manual verification.
    """

    def __init__(self):

        self.risk_factors = {
            "ppe_violation": 30,
            "ppe_review": 10,
            "site_high_risk": 25,
            "site_critical_risk": 40,
            "equipment_fault": 20,
            "unsafe_condition": 15,
            "compliance_violation": 20,
            "compliance_review": 5
        }

    def assess_risk(
        self,
        ppe_result=None,
        site_risk_result=None,
        compliance_result=None
    ):

        ppe_result = ppe_result or {}
        site_risk_result = site_risk_result or {}
        compliance_result = compliance_result or {}

        risk_score = 0

        risk_factors = []

        review_factors = []

        # =====================================================
        # 1. PPE RISK
        # =====================================================

        ppe_analysis = ppe_result.get(
            "safety_analysis",
            {}
        )

        ppe_risk = ppe_analysis.get(
            "risk_level",
            "LOW"
        )

        confirmed_ppe = ppe_analysis.get(
            "confirmed_violations",
            0
        )

        ppe_reviews = ppe_analysis.get(
            "review_required",
            0
        )

        # Backward compatibility:
        # If confirmed_violations is not available,
        # use the older HIGH risk logic.
        if confirmed_ppe > 0:

            risk_score += self.risk_factors[
                "ppe_violation"
            ]

            risk_factors.append(
                "Confirmed PPE safety violation detected"
            )

        elif ppe_risk == "HIGH":

            risk_score += self.risk_factors[
                "ppe_violation"
            ]

            risk_factors.append(
                "High-confidence PPE safety violation detected"
            )

        # Moderate-confidence PPE findings
        if ppe_reviews > 0:

            risk_score += self.risk_factors[
                "ppe_review"
            ]

            review_factors.append(
                "PPE finding requires manual verification"
            )

        # =====================================================
        # 2. COMPLIANCE RISK
        # =====================================================

        compliance_status = compliance_result.get(
            "compliance_status",
            "COMPLIANT"
        )

        confirmed_compliance_violations = compliance_result.get(
            "total_violations",
            0
        )

        compliance_reviews = compliance_result.get(
            "total_reviews",
            0
        )

        if (
            compliance_status == "NON-COMPLIANT"
            and confirmed_compliance_violations > 0
        ):

            risk_score += self.risk_factors[
                "compliance_violation"
            ]

            risk_factors.append(
                "Confirmed regulatory compliance violation detected"
            )

        elif compliance_status == "REVIEW REQUIRED":

            risk_score += self.risk_factors[
                "compliance_review"
            ]

            review_factors.append(
                "Compliance finding requires manual verification"
            )

        # =====================================================
        # 3. SITE RISK
        # =====================================================

        site_level = site_risk_result.get(
            "risk_level",
            "LOW"
        )

        site_score = site_risk_result.get(
            "risk_score",
            0
        )

        if site_level == "CRITICAL":

            risk_score += self.risk_factors[
                "site_critical_risk"
            ]

            risk_factors.append(
                "Critical site risk detected"
            )

        elif site_level == "HIGH":

            risk_score += self.risk_factors[
                "site_high_risk"
            ]

            risk_factors.append(
                "High site risk detected"
            )

        elif site_score >= 50:

            risk_score += self.risk_factors[
                "site_high_risk"
            ]

            risk_factors.append(
                "Elevated site risk detected"
            )

        # =====================================================
        # 4. EQUIPMENT HAZARDS
        # =====================================================

        site_hazards = site_risk_result.get(
            "hazards",
            []
        )

        for hazard in site_hazards:

            hazard_text = str(
                hazard
            ).lower()

            if "equipment" in hazard_text:

                risk_score += self.risk_factors[
                    "equipment_fault"
                ]

                risk_factors.append(
                    "Equipment-related hazard detected"
                )

                break

        # =====================================================
        # 5. UNSAFE SITE CONDITION
        # =====================================================

        unsafe_condition = site_risk_result.get(
            "unsafe_condition",
            False
        )

        if unsafe_condition:

            risk_score += self.risk_factors[
                "unsafe_condition"
            ]

            risk_factors.append(
                "Unsafe site condition reported"
            )

        # =====================================================
        # 6. LIMIT SCORE
        # =====================================================

        risk_score = min(
            risk_score,
            100
        )

        # =====================================================
        # 7. DETERMINE INSURANCE RISK LEVEL
        # =====================================================

        if risk_score >= 75:

            risk_level = "CRITICAL"

        elif risk_score >= 50:

            risk_level = "HIGH"

        elif risk_score >= 25:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        # =====================================================
        # 8. CLAIM RISK
        # =====================================================

        if risk_level == "CRITICAL":

            claim_risk = "VERY HIGH"

        elif risk_level == "HIGH":

            claim_risk = "HIGH"

        elif risk_level == "MEDIUM":

            claim_risk = "MODERATE"

        else:

            claim_risk = "LOW"

        # =====================================================
        # 9. RECOMMENDATION
        # =====================================================

        if risk_level == "CRITICAL":

            recommendation = (
                "Immediate risk mitigation and insurance "
                "review are recommended."
            )

        elif risk_level == "HIGH":

            recommendation = (
                "Prompt corrective action and risk "
                "documentation are recommended."
            )

        elif risk_level == "MEDIUM":

            recommendation = (
                "Monitor risk factors and complete "
                "preventive corrective actions."
            )

        else:

            recommendation = (
                "Continue routine safety monitoring and "
                "maintain compliance records."
            )

        # Add review information to the recommendation
        if review_factors:

            recommendation += (
                " Some findings require manual verification "
                "before being treated as confirmed insurance risks."
            )

        # Remove duplicates
        risk_factors = list(
            dict.fromkeys(
                risk_factors
            )
        )

        review_factors = list(
            dict.fromkeys(
                review_factors
            )
        )

        # =====================================================
        # 10. FINAL RESULT
        # =====================================================

        return {

            "insurance_risk_score": risk_score,

            "insurance_risk_level": risk_level,

            "claim_risk": claim_risk,

            "risk_factors": risk_factors,

            "review_factors": review_factors,

            "manual_review_required": len(
                review_factors
            ) > 0,

            "recommendation": recommendation
        }

    def assess_claim_risk(
        self,
        insurance_result
    ):

        risk_level = insurance_result.get(
            "insurance_risk_level",
            "LOW"
        )

        if risk_level == "CRITICAL":

            return "VERY HIGH"

        elif risk_level == "HIGH":

            return "HIGH"

        elif risk_level == "MEDIUM":

            return "MODERATE"

        else:

            return "LOW"