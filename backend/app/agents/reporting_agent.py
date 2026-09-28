from datetime import datetime


class ReportingAgent:
    """
    Combines findings from the construction risk agents
    into a single report.
    """

    def generate_report(
        self,
        site_risk_result=None,
        safety_result=None,
        compliance_result=None,
        insurance_result=None,
        risk_intelligence_result=None
    ):
        report = {
            "report_title": "Construction Site Risk Report",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "site_risk": site_risk_result or {},
            "safety": safety_result or {},
            "compliance": compliance_result or {},
            "insurance": insurance_result or {},
            "risk_intelligence": risk_intelligence_result or {}
        }

        report["summary"] = self._create_summary(report)

        return report

    def _create_summary(self, report):

        sections = [
            ("Site Risk", report["site_risk"]),
            ("Safety", report["safety"]),
            ("Compliance", report["compliance"]),
            ("Insurance", report["insurance"]),
            ("Risk Intelligence", report["risk_intelligence"])
        ]

        available_sections = [
            name for name, result in sections
            if result
        ]

        if not available_sections:
            return "No agent results were provided."

        return (
            "Report includes findings from: "
            + ", ".join(available_sections)
            + "."
        )