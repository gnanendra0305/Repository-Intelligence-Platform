"""
LLM-Based Health Report Generation Service
Module: M0.5 – LLM-Based Report Generation

Generates evidence-grounded repository intelligence reports synthesized from
M0.3 composite indicators and M0.4 survival analysis.
Supports Google Gemini REST API with zero-dependency deterministic fallback.
"""

import os
import json
import logging
import datetime
from typing import Dict, Any, Optional, List
import httpx

from ..schemas.indicators import HealthIndexResult
from ..schemas.survival import SingleRepoSurvivalAssessment
from ..schemas.report import (
    ReportStrength,
    ReportRisk,
    AdoptionRecommendation,
    RepositoryHealthReport,
    GenerateReportRequest,
    GenerateReportResponse,
)

logger = logging.getLogger("rip-report")


class ReportGenerationService:
    """Service to produce evidence-grounded reports using Gemini API or rule-based fallback."""

    def __init__(self):
        self.gemini_api_key = (
            os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
        )
        self.default_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
        self.timeout = 25.0

    async def generate_report(
        self,
        indicators: HealthIndexResult,
        survival: SingleRepoSurvivalAssessment,
        model_name: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> RepositoryHealthReport:
        """
        Generates an evidence-grounded report.
        Attempts Gemini LLM generation if an API key is configured;
        gracefully falls back to the deterministic evidence-based generator.
        """
        model = model_name or self.default_model
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # If API key is available, attempt Gemini generation
        if self.gemini_api_key:
            try:
                gemini_report = await self._call_gemini(
                    indicators=indicators,
                    survival=survival,
                    model_name=model,
                    client=client,
                    now_iso=now_iso,
                )
                if gemini_report:
                    return gemini_report
            except Exception as e:
                logger.warning("Gemini API call failed (%s). Falling back to deterministic generator.", str(e))

        # Deterministic evidence-grounded fallback
        return self._generate_deterministic_report(indicators, survival, now_iso)

    async def _call_gemini(
        self,
        indicators: HealthIndexResult,
        survival: SingleRepoSurvivalAssessment,
        model_name: str,
        client: Optional[httpx.AsyncClient],
        now_iso: str,
    ) -> Optional[RepositoryHealthReport]:
        """Calls Google Gemini REST API with structured prompt and strict schema grounding."""
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            f"?key={self.gemini_api_key}"
        )

        prompt = (
            "You are an expert empirical open-source software health auditor.\n"
            "Analyze the following computed repository health indicators (M0.3) and survival analysis (M0.4).\n\n"
            "STRICT CONSTRAINTS:\n"
            "1. Ground every finding directly in the provided metric numbers and survival data.\n"
            "2. DO NOT hallucinate or invent numbers, research claims, or repository facts.\n"
            "3. Return ONLY a valid JSON object matching this schema:\n"
            "{\n"
            '  "executive_summary": "string",\n'
            '  "strengths": [{"dimension": "string", "finding": "string", "evidence_metric": "string", "interpretation": "string"}],\n'
            '  "risks_and_bottlenecks": [{"dimension": "string", "severity": "high|medium|low", "finding": "string", "evidence_metric": "string", "mitigation_advice": "string"}],\n'
            '  "survival_sustainability_assessment": "string",\n'
            '  "adoption_recommendation": {"verdict": "RECOMMENDED|RECOMMENDED_WITH_CAUTION|NOT_RECOMMENDED", "summary": "string", "key_drivers": ["string"], "target_audience_notes": "string"},\n'
            '  "methodological_limitations": ["string"]\n'
            "}\n\n"
            f"INPUT DATA FOR {indicators.repository_name}:\n"
            f"- RHI Score: {indicators.rhi_score} (Grade: {indicators.rhi_grade}, Coverage: {indicators.coverage_ratio * 100:.1f}%)\n"
            f"- Metrics: {json.dumps({k: v.model_dump() for k, v in indicators.metrics.items()})}\n"
            f"- Context: {json.dumps({k: v.model_dump() for k, v in indicators.context_variables.items()})}\n"
            f"- Data Quality: {json.dumps({k: v.model_dump() for k, v in indicators.data_quality_indicators.items()})}\n"
            f"- Survival Status: {survival.model_dump_json()}\n"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        async def _do_request(http_client: httpx.AsyncClient) -> httpx.Response:
            return await http_client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )

        if client:
            resp = await _do_request(client)
        else:
            async with httpx.AsyncClient() as http_client:
                resp = await _do_request(http_client)

        if resp.status_code != 200:
            logger.warning("Gemini API error %d: %s", resp.status_code, resp.text[:200])
            return None

        result_json = resp.json()
        candidates = result_json.get("candidates", [])
        if not candidates:
            return None

        text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        # Clean markdown fences if any
        if text_content.startswith("```"):
            text_content = text_content.strip("`").replace("json\n", "", 1).strip()

        parsed = json.loads(text_content)

        return RepositoryHealthReport(
            repository_name=indicators.repository_name,
            generated_at=now_iso,
            provider="gemini",
            executive_summary=parsed.get("executive_summary", ""),
            health_index_summary={
                "rhi_score": indicators.rhi_score,
                "rhi_grade": indicators.rhi_grade,
                "coverage_ratio": indicators.coverage_ratio,
                "coverage_sufficient": indicators.coverage_sufficient,
            },
            strengths=[ReportStrength(**s) for s in parsed.get("strengths", [])],
            risks_and_bottlenecks=[ReportRisk(**r) for r in parsed.get("risks_and_bottlenecks", [])],
            survival_sustainability_assessment=parsed.get("survival_sustainability_assessment", ""),
            adoption_recommendation=AdoptionRecommendation(**parsed.get("adoption_recommendation", {})),
            methodological_limitations=parsed.get("methodological_limitations", indicators.missing_metrics),
        )

    def _generate_deterministic_report(
        self,
        indicators: HealthIndexResult,
        survival: SingleRepoSurvivalAssessment,
        now_iso: str,
    ) -> RepositoryHealthReport:
        """
        Deterministic, rule-based report generation engine.
        Grounded 100% in empirical metric thresholds and survival diagnostics.
        """
        metrics = indicators.metrics
        context = indicators.context_variables
        dq = indicators.data_quality_indicators

        strengths: List[ReportStrength] = []
        risks: List[ReportRisk] = []
        key_drivers: List[str] = []

        # Evaluate PR Acceptance Rate (A1)
        m_a1 = metrics.get("A1")
        if m_a1 and m_a1.raw_value is not None:
            if m_a1.raw_value >= 0.70:
                strengths.append(
                    ReportStrength(
                        dimension="Code Review & PR Efficiency",
                        finding="High pull request acceptance rate reflects open community intake.",
                        evidence_metric=f"A1 (PRAR) = {m_a1.formatted_value}",
                        interpretation="Maintainers consistently review and merge external contributions."
                    )
                )
                key_drivers.append(f"PR Acceptance Rate: {m_a1.formatted_value}")
            elif m_a1.raw_value <= 0.30:
                risks.append(
                    ReportRisk(
                        dimension="Code Review & PR Efficiency",
                        severity="medium",
                        finding="Low PR acceptance rate indicates high rejection or abandoned PR rate.",
                        evidence_metric=f"A1 (PRAR) = {m_a1.formatted_value}",
                        mitigation_advice="Review contribution guidelines to align external submissions with project expectations."
                    )
                )

        # Evaluate PR Resolution Latency (A3)
        m_a3 = metrics.get("A3")
        if m_a3 and m_a3.raw_value is not None:
            if m_a3.raw_value <= 3.0:
                strengths.append(
                    ReportStrength(
                        dimension="Code Review & PR Efficiency",
                        finding="Rapid code review turnaround cadence.",
                        evidence_metric=f"A3 (PRL Median) = {m_a3.formatted_value}",
                        interpretation="Contributions receive quick review decisions, preventing contributor attrition."
                    )
                )
                key_drivers.append(f"Median PR Latency: {m_a3.formatted_value}")
            elif m_a3.raw_value >= 14.0:
                risks.append(
                    ReportRisk(
                        dimension="Code Review & PR Efficiency",
                        severity="high",
                        finding="Prolonged PR review latency suggests maintainer review bottleneck.",
                        evidence_metric=f"A3 (PRL Median) = {m_a3.formatted_value}",
                        mitigation_advice="Establish triage schedules or expand the reviewer pool to prevent contribution stalls."
                    )
                )

        # Evaluate Issue Resolution Rate (A5)
        m_a5 = metrics.get("A5")
        if m_a5 and m_a5.raw_value is not None:
            if m_a5.raw_value >= 0.70:
                strengths.append(
                    ReportStrength(
                        dimension="Issue Management",
                        finding="Strong issue resolution track record.",
                        evidence_metric=f"A5 (IRR) = {m_a5.formatted_value}",
                        interpretation="User-reported issues and bug reports are actively resolved."
                    )
                )
                key_drivers.append(f"Issue Resolution Rate: {m_a5.formatted_value}")
            elif m_a5.raw_value <= 0.40:
                risks.append(
                    ReportRisk(
                        dimension="Issue Management",
                        severity="medium",
                        finding="Substantial unresolved issue backlog accumulation.",
                        evidence_metric=f"A5 (IRR) = {m_a5.formatted_value}",
                        mitigation_advice="Conduct issue grooming sessions to close stale reports and triage open defects."
                    )
                )

        # Evaluate Governance (M45-LICENSE)
        m_lic = metrics.get("M45-LICENSE")
        if m_lic:
            if m_lic.raw_value == 1.0:
                strengths.append(
                    ReportStrength(
                        dimension="Governance & Legal",
                        finding="Approved open source software license declared.",
                        evidence_metric=f"M45-LICENSE = {m_lic.formatted_value}",
                        interpretation="Clear intellectual property and legal adoption terms for commercial and community use."
                    )
                )
            else:
                risks.append(
                    ReportRisk(
                        dimension="Governance & Legal",
                        severity="high",
                        finding="No recognized open source license detected in repository root.",
                        evidence_metric=f"M45-LICENSE = {m_lic.formatted_value}",
                        mitigation_advice="Add a standard SPDX license (e.g. MIT, Apache-2.0) to remove adoption legal barriers."
                    )
                )
                key_drivers.append("Unlicensed repository (legal adoption barrier)")

        # Evaluate Documentation (M67-DOCS)
        m_docs = metrics.get("M67-DOCS")
        if m_docs:
            if m_docs.raw_value == 1.0:
                strengths.append(
                    ReportStrength(
                        dimension="Documentation & Onboarding",
                        finding="Foundational technical documentation and description present.",
                        evidence_metric=f"M67-DOCS = {m_docs.formatted_value}",
                        interpretation="Lowers onboarding and implementation cost for prospective developers."
                    )
                )
            else:
                risks.append(
                    ReportRisk(
                        dimension="Documentation & Onboarding",
                        severity="medium",
                        finding="Incomplete or missing documentation scaffolding.",
                        evidence_metric=f"M67-DOCS = {m_docs.formatted_value}",
                        mitigation_advice="Provide comprehensive README, installation guides, and contribution guidelines."
                    )
                )

        # Determine Adoption Verdict
        has_license = bool(m_lic and m_lic.raw_value == 1.0)
        is_archived = survival.is_archived
        rhi_score = indicators.rhi_score or 0.0

        if not has_license or is_archived:
            verdict = "NOT_RECOMMENDED"
            recom_summary = (
                f"Repository '{indicators.repository_name}' is not recommended for adoption due to critical blockers: "
                + ("Project is archived on GitHub. " if is_archived else "No recognized OSS license is declared. ")
            )
            target_notes = "Unsuitable for production or commercial adoption until governance/licensing is resolved."
        elif rhi_score >= 70.0 and indicators.coverage_sufficient:
            verdict = "RECOMMENDED"
            recom_summary = (
                f"Repository '{indicators.repository_name}' demonstrates sound operational health with an RHI of {rhi_score:.1f} (Grade {indicators.rhi_grade}). "
                "Maintains consistent contributor intake, prompt reviews, and active governance."
            )
            target_notes = "Suitable for enterprise and production dependency adoption."
        elif rhi_score >= 45.0:
            verdict = "RECOMMENDED_WITH_CAUTION"
            recom_summary = (
                f"Repository '{indicators.repository_name}' is viable for adoption with caution (RHI: {rhi_score:.1f}, Grade {indicators.rhi_grade}). "
                "Noticeable maintenance bottlenecks or incomplete metric coverage require internal mitigation."
            )
            target_notes = "Adoptable for non-critical services or with dedicated in-house fork maintenance capacity."
        else:
            verdict = "NOT_RECOMMENDED"
            recom_summary = (
                f"Repository '{indicators.repository_name}' exhibits low health composite scoring (RHI: {rhi_score:.1f}, Grade {indicators.rhi_grade}) "
                "or substantial unresolved bottlenecks."
            )
            target_notes = "High dependency risk; consider alternative open-source projects."

        # Executive Summary
        exec_summary = (
            f"Health assessment for {indicators.repository_name} yields a Repository Health Index (RHI) of "
            f"{rhi_score:.1f}/100 (Grade {indicators.rhi_grade}) with {indicators.coverage_ratio * 100:.1f}% weighted metric coverage. "
            f"The project has been active for {survival.observed_lifespan_years} years ({int(survival.observed_lifespan_days)} days). "
            f"Adoption readiness verdict is {verdict.replace('_', ' ')}."
        )

        # Survival summary
        survival_summary = (
            f"Repository lifespan is currently observed at {survival.observed_lifespan_years} years ({int(survival.observed_lifespan_days)} days). "
            f"Under survival analysis principles, the repository is classified as '{survival.censoring_status}' "
            f"({ 'active project under follow-up' if survival.is_censored else 'terminal event observed' }). "
            "A single snapshot observation cannot establish longitudinal hazard rates; benchmark comparison indicates typical mature OSS longevity."
        )

        # Methodological limitations
        limitations = [
            f"Metric coverage: {indicators.coverage_ratio * 100:.1f}% of weighted framework indicators evaluated.",
        ]
        if indicators.missing_metrics:
            limitations.append(f"Missing metric observations: {', '.join(indicators.missing_metrics)}.")
        m_c2 = dq.get("C2")
        if m_c2 and m_c2.raw_value is not None and m_c2.raw_value < 0.95:
            limitations.append(f"PR sample truncated by API pagination limits ({m_c2.formatted_value}).")
        limitations.extend(survival.methodological_caveats[:2])

        return RepositoryHealthReport(
            repository_name=indicators.repository_name,
            generated_at=now_iso,
            provider="deterministic_fallback",
            executive_summary=exec_summary,
            health_index_summary={
                "rhi_score": indicators.rhi_score,
                "rhi_grade": indicators.rhi_grade,
                "coverage_ratio": indicators.coverage_ratio,
                "coverage_sufficient": indicators.coverage_sufficient,
            },
            strengths=strengths,
            risks_and_bottlenecks=risks,
            survival_sustainability_assessment=survival_summary,
            adoption_recommendation=AdoptionRecommendation(
                verdict=verdict,
                summary=recom_summary,
                key_drivers=key_drivers or ["Composite RHI Score"],
                target_audience_notes=target_notes,
            ),
            methodological_limitations=limitations,
        )


report_service = ReportGenerationService()

