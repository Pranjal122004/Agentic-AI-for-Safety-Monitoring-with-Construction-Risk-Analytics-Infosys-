class AgentOrchestrator:
    """
    Coordinates the construction risk agents
    and combines their results into one workflow.
    """

    def __init__(
        self,
        safety_agent,
        compliance_agent,
        insurance_agent,
        risk_intelligence_agent,
        reporting_agent
    ):
        self.safety_agent = safety_agent
        self.compliance_agent = compliance_agent
        self.insurance_agent = insurance_agent
        self.risk_intelligence_agent = risk_intelligence_agent
        self.reporting_agent = reporting_agent

    def run(
        self,
        ppe_result,
        site_risk_result
    ):
        # --------------------------------------------------
        # 1. Safety Agent
        # --------------------------------------------------

        detections = ppe_result.get("detections", [])

        safety_result = self.safety_agent.analyze_detections(
            detections
        )

        # --------------------------------------------------
        # 2. Compliance Agent
        # --------------------------------------------------

        compliance_result = self.compliance_agent.analyze(
            ppe_result
        )

        # --------------------------------------------------
        # 3. Insurance Agent
        # --------------------------------------------------

        insurance_result = self.insurance_agent.assess_risk(
            ppe_result=ppe_result,
            site_risk_result=site_risk_result,
            compliance_result=compliance_result
        )

        # --------------------------------------------------
        # 4. Claim Risk
        # --------------------------------------------------

        claim_risk = self.insurance_agent.assess_claim_risk(
            insurance_result
        )

        insurance_result = {
            **insurance_result,
            "claim_risk": claim_risk
        }

        # --------------------------------------------------
        # 5. Risk Intelligence Engine
        # --------------------------------------------------

        risk_intelligence_result = (
            self.risk_intelligence_agent.analyze(
                site_risk_result=site_risk_result,
                safety_result=safety_result
            )
        )

        # --------------------------------------------------
        # 6. Reporting Agent
        # --------------------------------------------------

        report = self.reporting_agent.generate_report(
            site_risk_result=site_risk_result,
            safety_result=safety_result,
            compliance_result=compliance_result,
            insurance_result=insurance_result,
            risk_intelligence_result=risk_intelligence_result
        )

        # --------------------------------------------------
        # 7. Final Orchestrated Result
        # --------------------------------------------------

        return {
            "workflow": [
                "Safety Agent",
                "Compliance Agent",
                "Insurance Agent",
                "Risk Intelligence Engine",
                "Reporting Agent"
            ],
            "site_risk": site_risk_result,
            "safety": safety_result,
            "compliance": compliance_result,
            "insurance": insurance_result,
            "risk_intelligence": risk_intelligence_result,
            "report": report
        }