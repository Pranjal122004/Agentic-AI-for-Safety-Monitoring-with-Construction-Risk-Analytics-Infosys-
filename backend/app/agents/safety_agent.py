import pandas as pd


class SafetyAgent:
    """
    Safety Agent for construction worker safety.

    Supports:
    1. PPE analysis from YOLO detections
    2. Worker safety analysis from CSV data
    """

    # PPE classes that represent violations
    PPE_VIOLATIONS = {
        "NO-Hardhat": "Missing hardhat",
        "NO-Safety Vest": "Missing safety vest",
        "NO-Mask": "Missing safety mask",
    }

    # PPE classes that represent compliant equipment
    PPE_CLASSES = {
        "Hardhat",
        "Safety Vest",
        "Mask",
    }

    def __init__(self):
        pass

    # =========================================================
    # REAL-TIME PPE DETECTION ANALYSIS
    # =========================================================

    def analyze_detections(self, detections):
        """
        Analyze PPE detections produced by the YOLO detector.

        Example input:

        [
            {
                "class": "Person",
                "confidence": 0.94
            },
            {
                "class": "Hardhat",
                "confidence": 0.88
            },
            {
                "class": "Safety Vest",
                "confidence": 0.91
            }
        ]
        """

        violations = []
        detected_ppe = []
        detected_objects = []

        # -----------------------------------------------------
        # Process YOLO detections
        # -----------------------------------------------------

        for detection in detections:

            class_name = detection.get("class")
            confidence = detection.get("confidence", 0)

            if not class_name:
                continue

            detected_objects.append(
                {
                    "class": class_name,
                    "confidence": confidence
                }
            )

            # Check PPE violation
            if class_name in self.PPE_VIOLATIONS:

                violation = self.PPE_VIOLATIONS[class_name]

                if violation not in violations:
                    violations.append(violation)

            # Check correct PPE
            elif class_name in self.PPE_CLASSES:

                if class_name not in detected_ppe:
                    detected_ppe.append(class_name)

        # -----------------------------------------------------
        # Calculate safety score
        # -----------------------------------------------------

        safety_score = 100

        if "Missing hardhat" in violations:
            safety_score -= 30

        if "Missing safety vest" in violations:
            safety_score -= 25

        if "Missing safety mask" in violations:
            safety_score -= 15

        # Never allow negative score
        safety_score = max(0, safety_score)

        # -----------------------------------------------------
        # Determine safety level
        # -----------------------------------------------------

        safety_level = self._get_safety_level(
            safety_score
        )

        # -----------------------------------------------------
        # Generate recommendation / alert
        # -----------------------------------------------------

        alert = self._generate_alert(
            safety_level,
            violations
        )

        # -----------------------------------------------------
        # Return result
        # -----------------------------------------------------

        return {
            "detected_objects": detected_objects,
            "detected_ppe": detected_ppe,
            "violations": violations,
            "safety_score": safety_score,
            "safety_level": safety_level,
            "alert": alert
        }

    # =========================================================
    # SAFETY LEVEL
    # =========================================================

    def _get_safety_level(self, safety_score):

        if safety_score >= 80:
            return "SAFE"

        elif safety_score >= 60:
            return "MODERATE"

        elif safety_score >= 40:
            return "HIGH RISK"

        else:
            return "CRITICAL"

    # =========================================================
    # SAFETY ALERT
    # =========================================================

    def _generate_alert(
        self,
        safety_level,
        violations
    ):

        if safety_level == "SAFE":

            return (
                "Worker PPE compliance is satisfactory. "
                "Continue regular safety monitoring."
            )

        elif safety_level == "MODERATE":

            return (
                "Monitor the worker and improve PPE compliance."
            )

        elif safety_level == "HIGH RISK":

            if violations:

                return (
                    "Urgent safety action required. "
                    "Detected violations: "
                    + ", ".join(violations)
                )

            return (
                "Urgent safety action required. "
                "PPE compliance is inadequate."
            )

        else:

            return (
                "Immediate intervention required. "
                "Critical PPE violations detected: "
                + ", ".join(violations)
            )

    # =========================================================
    # CSV WORKER SAFETY ANALYSIS
    # =========================================================

    def analyze_dataset(self, file_path):
        """
        Analyze the existing worker_monitoring.csv.

        This method is kept so your existing
        /safety-risk API and manual test data continue to work.
        """

        df = pd.read_csv(file_path)

        results = []

        for _, row in df.iterrows():

            violations = []

            # -------------------------------------------------
            # Check helmet
            # -------------------------------------------------

            if str(
                row.get("helmet", "yes")
            ).strip().lower() != "yes":

                violations.append(
                    "Missing hardhat"
                )

            # -------------------------------------------------
            # Check safety vest
            # -------------------------------------------------

            if str(
                row.get("safety_vest", "yes")
            ).strip().lower() != "yes":

                violations.append(
                    "Missing safety vest"
                )

            # -------------------------------------------------
            # Check safety boots
            # -------------------------------------------------

            if str(
                row.get("safety_boots", "yes")
            ).strip().lower() != "yes":

                violations.append(
                    "Missing safety boots"
                )

            # -------------------------------------------------
            # Check gloves
            # -------------------------------------------------

            if str(
                row.get("gloves", "yes")
            ).strip().lower() != "yes":

                violations.append(
                    "Missing gloves"
                )

            # -------------------------------------------------
            # Calculate score
            # -------------------------------------------------

            safety_score = 100

            if "Missing hardhat" in violations:
                safety_score -= 20

            if "Missing safety vest" in violations:
                safety_score -= 15

            if "Missing safety boots" in violations:
                safety_score -= 15

            if "Missing gloves" in violations:
                safety_score -= 10

            safety_score = max(
                0,
                safety_score
            )

            # -------------------------------------------------
            # Safety level
            # -------------------------------------------------

            safety_level = self._get_safety_level(
                safety_score
            )

            # -------------------------------------------------
            # Recommendation
            # -------------------------------------------------

            if safety_level == "SAFE":

                recommendation = (
                    "Worker safety conditions are acceptable. "
                    "Continue regular monitoring."
                )

            elif safety_level == "MODERATE":

                recommendation = (
                    "Monitor the worker and take "
                    "preventive safety measures."
                )

            elif safety_level == "HIGH RISK":

                recommendation = (
                    "Urgent safety review and "
                    "corrective action required."
                )

            else:

                recommendation = (
                    "Immediate intervention and "
                    "corrective action required."
                )

            # -------------------------------------------------
            # Build result
            # -------------------------------------------------

            result = {
                "site_id": row.get(
                    "site_id",
                    "UNKNOWN"
                ),

                "worker_id": row.get(
                    "worker_id",
                    "UNKNOWN"
                ),

                "timestamp": row.get(
                    "timestamp",
                    ""
                ),

                "safety_score": safety_score,

                "safety_level": safety_level,

                "ppe_violations": violations,

                "recommendation": recommendation
            }

            results.append(result)

        return results