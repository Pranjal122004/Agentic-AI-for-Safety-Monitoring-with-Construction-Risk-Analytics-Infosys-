class SafetyAgent:
    """
    Safety Agent for construction-site safety analysis.

    Combines:
    1. PPE detection results
    2. Site risk results

    to generate an overall safety assessment.
    """

    # ============================================================
    # PPE-ONLY ANALYSIS
    # ============================================================

    def analyze_detections(self, detections):
        """
        Analyze PPE detections from the YOLO detector.
        """

        hazards = []
        recommendations = []

        for detection in detections:

            # ppe_detector.py returns:
            # {"class": "NO-Hardhat", "confidence": 0.85}

            class_name = str(
                detection.get("class", "")
            ).lower()

            # Remove spaces so that:
            # "no-safety vest"
            # becomes:
            # "no-safetyvest"

            class_name = class_name.replace(" ", "")

            # ----------------------------------------------------
            # NO HARDHAT
            # ----------------------------------------------------

            if class_name == "no-hardhat":

                hazards.append(
                    "Worker without hardhat"
                )

                recommendations.append(
                    "Ensure workers wear hardhats."
                )

            # ----------------------------------------------------
            # NO MASK
            # ----------------------------------------------------

            elif class_name == "no-mask":

                hazards.append(
                    "Worker without mask"
                )

                recommendations.append(
                    "Ensure workers wear required masks."
                )

            # ----------------------------------------------------
            # NO SAFETY VEST
            # ----------------------------------------------------

            elif class_name == "no-safetyvest":

                hazards.append(
                    "Worker without safety vest"
                )

                recommendations.append(
                    "Ensure workers wear safety vests."
                )

        # --------------------------------------------------------
        # Remove duplicate hazards
        # --------------------------------------------------------

        hazards = list(
            dict.fromkeys(hazards)
        )

        # --------------------------------------------------------
        # Remove duplicate recommendations
        # --------------------------------------------------------

        recommendations = list(
            dict.fromkeys(recommendations)
        )

        # --------------------------------------------------------
        # Determine PPE risk
        # --------------------------------------------------------

        if hazards:

            risk_level = "HIGH"

            status = (
                "PPE safety violation detected."
            )

        else:

            risk_level = "LOW"

            status = (
                "Required PPE appears compliant."
            )

        # --------------------------------------------------------
        # Return PPE analysis
        # --------------------------------------------------------

        return {
            "risk_level": risk_level,
            "hazards": hazards,
            "recommendations": recommendations,
            "status": status
        }

    # ============================================================
    # COMBINED PPE + SITE RISK ANALYSIS
    # ============================================================

    def analyze(
        self,
        ppe_result,
        site_risk_result
    ):
        """
        Combine PPE analysis with site-risk analysis.
        """

        hazards = []
        recommendations = []

        # ========================================================
        # 1. PPE ANALYSIS
        # ========================================================

        ppe_detections = ppe_result.get(
            "detections",
            []
        )

        ppe_analysis = self.analyze_detections(
            ppe_detections
        )

        # Add PPE hazards

        hazards.extend(
            ppe_analysis.get(
                "hazards",
                []
            )
        )

        # Add PPE recommendations

        recommendations.extend(
            ppe_analysis.get(
                "recommendations",
                []
            )
        )

        # ========================================================
        # 2. SITE RISK ANALYSIS
        # ========================================================

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

        # Add site hazards

        hazards.extend(
            site_hazards
        )

        # Add site recommendation

        site_recommendation = site_risk_result.get(
            "recommendation"
        )

        if site_recommendation:

            recommendations.append(
                site_recommendation
            )

        # ========================================================
        # 3. DETERMINE OVERALL RISK
        # ========================================================

        risk_priority = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4
        }

        # Start with site risk

        overall_level = site_level

        # Compare PPE risk with site risk

        ppe_level = ppe_analysis.get(
            "risk_level",
            "LOW"
        )

        if risk_priority.get(
            ppe_level,
            1
        ) > risk_priority.get(
            overall_level,
            1
        ):

            overall_level = ppe_level

        # ========================================================
        # 4. REMOVE DUPLICATES
        # ========================================================

        hazards = list(
            dict.fromkeys(
                hazards
            )
        )

        recommendations = list(
            dict.fromkeys(
                recommendations
            )
        )

        # ========================================================
        # 5. GENERATE OVERALL STATUS
        # ========================================================

        if overall_level == "CRITICAL":

            status = (
                "Immediate action required."
            )

        elif overall_level == "HIGH":

            status = (
                "Urgent safety intervention required."
            )

        elif overall_level == "MEDIUM":

            status = (
                "Preventive safety action recommended."
            )

        else:

            status = (
                "Site conditions are currently acceptable."
            )

        # ========================================================
        # 6. FINAL COMBINED RESULT
        # ========================================================

        return {

            "overall_risk_level":
                overall_level,

            "site_risk_score":
                site_risk,

            "ppe_risk_level":
                ppe_level,

            "hazards":
                hazards,

            "recommendations":
                recommendations,

            "status":
                status
        }