import pandas as pd


class SiteRiskAgent:
    """
    Site Risk Agent for construction-site monitoring.

    Responsibilities:
    - Analyze site monitoring data
    - Detect potential hazards
    - Calculate risk score
    - Assign risk level
    - Generate recommendations
    """

    def detect_hazards(self, row):
        hazards = []

        if row["temperature"] >= 40:
            hazards.append("High temperature")

        if row["dust_level"] >= 70:
            hazards.append("High dust level")

        if row["noise_level"] >= 85:
            hazards.append("High noise level")

        if str(row["equipment_status"]).lower() in ["faulty", "maintenance"]:
            hazards.append("Equipment-related hazard")

        if str(row["unsafe_condition"]).lower() == "yes":
            hazards.append("Unsafe site condition")

        return hazards

    def calculate_risk_score(self, row):
        score = 0

        # Environmental risk
        if row["temperature"] >= 40:
            score += 20
        elif row["temperature"] >= 35:
            score += 10

        if row["dust_level"] >= 70:
            score += 20
        elif row["dust_level"] >= 50:
            score += 10

        if row["noise_level"] >= 85:
            score += 20
        elif row["noise_level"] >= 75:
            score += 10

        # Equipment risk
        if str(row["equipment_status"]).lower() == "faulty":
            score += 25
        elif str(row["equipment_status"]).lower() == "maintenance":
            score += 15

        # Unsafe condition
        if str(row["unsafe_condition"]).lower() == "yes":
            score += 15

        return min(score, 100)

    def get_risk_level(self, score):
        if score <= 30:
            return "LOW"
        elif score <= 60:
            return "MEDIUM"
        elif score <= 80:
            return "HIGH"
        else:
            return "CRITICAL"

    def generate_recommendation(self, risk_level, hazards):

        if risk_level == "CRITICAL":
            return "Immediate site inspection and corrective action required."

        if risk_level == "HIGH":
            return "Urgent safety review and hazard mitigation required."

        if risk_level == "MEDIUM":
            return "Monitor the site and take preventive safety measures."

        return "Site conditions are acceptable. Continue regular monitoring."

    def analyze_row(self, row):

        hazards = self.detect_hazards(row)

        risk_score = self.calculate_risk_score(row)

        risk_level = self.get_risk_level(risk_score)

        recommendation = self.generate_recommendation(
            risk_level,
            hazards
        )

        return {
            "site_id": row["site_id"],
            "timestamp": row["timestamp"],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "hazards": hazards,
            "recommendation": recommendation
        }

    def analyze_dataset(self, file_path):

        data = pd.read_csv(file_path)

        results = []

        for _, row in data.iterrows():
            result = self.analyze_row(row)
            results.append(result)

        return results