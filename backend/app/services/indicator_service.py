"""
Composite Indicator & Repository Health Index (RHI) Calculation Engine
Module: M0.3 – Composite Indicators
"""

import math
import statistics
import datetime
from typing import Dict, Any, List, Optional, Tuple
from ..schemas.indicators import (
    MetricValue,
    DimensionScore,
    HealthIndexResult,
)
from ..schemas.mining import RepositoryMiningData


def _parse_utc_iso(ts_str: Optional[str]) -> Optional[datetime.datetime]:
    """Safely parses ISO-8601 timestamp string into UTC datetime."""
    if not ts_str:
        return None
    try:
        cleaned = ts_str.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None


class CompositeIndicatorService:
    """Calculates M0.1 registered metrics and aggregates the Repository Health Index."""

    # Weights assigned across core health indicators (total = 1.00)
    CORE_WEIGHTS: Dict[str, float] = {
        "A1": 0.20,          # PR Acceptance Rate
        "A3": 0.15,          # PR Resolution Latency (Median)
        "A4": 0.05,          # PR Backlog Ratio (Provisional)
        "A5": 0.15,          # Issue Resolution Rate
        "A6": 0.15,          # Issue Resolution Latency (Median)
        "A7": 0.10,          # Review Throughput (Recent Volume)
        "A8R": 0.10,         # Relative Development Trend
        "M45-LICENSE": 0.08, # Declared License
        "M67-DOCS": 0.07,    # Technical Documentation
    }

    # Reference constants for saturating transforms: S(x) = 1.0 / (1.0 + x / x_ref)
    REF_PR_LATENCY_DAYS = 3.0       # Median PR turnaround reference benchmark
    REF_PR_MEAN_DAYS = 7.0          # Mean PR turnaround reference benchmark
    REF_ISSUE_LATENCY_DAYS = 14.0   # Median Issue resolution reference benchmark
    MIN_COVERAGE_THRESHOLD = 0.40   # Minimum weighted metric coverage required for RHI

    def calculate_indicators(self, mined_data: Any) -> HealthIndexResult:
        """
        Calculates all registered metrics, applies normalization,
        evaluates dimensions, and computes the composite Repository Health Index (RHI).
        """
        # Extract records
        if isinstance(mined_data, RepositoryMiningData):
            repo_meta = mined_data.repository or {}
            prs = mined_data.pull_requests or []
            issues = mined_data.issues or []
            commits = mined_data.commits or []
            contributors = mined_data.contributors or []
        elif isinstance(mined_data, dict):
            repo_meta = mined_data.get("repository") or {}
            prs = mined_data.get("pull_requests") or []
            issues = mined_data.get("issues") or []
            commits = mined_data.get("commits") or []
            contributors = mined_data.get("contributors") or []
        else:
            repo_meta, prs, issues, commits, contributors = {}, [], [], [], []

        repo_name = repo_meta.get("full_name") or repo_meta.get("name") or "unknown/repository"
        now = datetime.datetime.now(datetime.timezone.utc)

        calculated_metrics: Dict[str, MetricValue] = {}
        context_vars: Dict[str, MetricValue] = {}
        data_qualities: Dict[str, MetricValue] = {}
        missing_metric_ids: List[str] = []

        # =====================================================================
        # 1. Core Health Metrics (PR Side)
        # =====================================================================

        # Helper: parse PR durations
        decided_prs = []
        merged_prs = []
        open_prs = []
        pr_latencies_days: List[float] = []

        for p in prs:
            p_dict = p if isinstance(p, dict) else p.model_dump()
            state = (p_dict.get("state") or "").lower()
            is_merged = bool(p_dict.get("is_merged") or p_dict.get("merged_at"))
            created_at = _parse_utc_iso(p_dict.get("created_at"))
            closed_at = _parse_utc_iso(p_dict.get("closed_at"))
            merged_at = _parse_utc_iso(p_dict.get("merged_at"))

            if state == "open" and not is_merged:
                open_prs.append(p_dict)
            elif is_merged or state == "closed":
                decided_prs.append(p_dict)
                if is_merged:
                    merged_prs.append(p_dict)
                
                decision_time = merged_at or closed_at
                if created_at and decision_time and decision_time >= created_at:
                    dur_days = (decision_time - created_at).total_seconds() / 86400.0
                    pr_latencies_days.append(dur_days)

        # A1: PR Acceptance Rate (PRAR)
        if len(decided_prs) > 0:
            prar_raw = len(merged_prs) / len(decided_prs)
            calculated_metrics["A1"] = MetricValue(
                metric_id="A1",
                metric_name="Pull Request Acceptance Rate (PRAR)",
                raw_value=round(prar_raw, 4),
                formatted_value=f"{prar_raw * 100:.1f}%",
                unit="ratio",
                direction="higher_is_better",
                normalized_score=round(prar_raw, 4),
                weight=self.CORE_WEIGHTS.get("A1", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="calculated",
                notes=f"Computed across {len(decided_prs)} decided PRs ({len(merged_prs)} merged)."
            )
        else:
            missing_metric_ids.append("A1")
            calculated_metrics["A1"] = MetricValue(
                metric_id="A1",
                metric_name="Pull Request Acceptance Rate (PRAR)",
                raw_value=None,
                formatted_value="N/A (No decided PRs)",
                unit="ratio",
                direction="higher_is_better",
                normalized_score=None,
                weight=self.CORE_WEIGHTS.get("A1", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="missing_data",
                notes="Zero decided pull requests in collected dataset."
            )

        # A2: PR Resolution Efficiency (Mean Duration)
        if len(pr_latencies_days) > 0:
            pre_mean = statistics.mean(pr_latencies_days)
            pre_norm = 1.0 / (1.0 + pre_mean / self.REF_PR_MEAN_DAYS)
            calculated_metrics["A2"] = MetricValue(
                metric_id="A2",
                metric_name="PR Resolution Efficiency (PRE Mean)",
                raw_value=round(pre_mean, 2),
                formatted_value=f"{pre_mean:.2f} days",
                unit="days",
                direction="lower_is_better",
                normalized_score=round(pre_norm, 4),
                weight=0.0, # Kept for traceability; robust median A3 is weighted in RHI
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="calculated",
                notes=f"Arithmetic mean across {len(pr_latencies_days)} decided PRs. Traceability metric (Alami et al. TEC-2)."
            )
        else:
            missing_metric_ids.append("A2")
            calculated_metrics["A2"] = MetricValue(
                metric_id="A2",
                metric_name="PR Resolution Efficiency (PRE Mean)",
                raw_value=None,
                formatted_value="N/A",
                unit="days",
                direction="lower_is_better",
                normalized_score=None,
                weight=0.0,
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="missing_data",
            )

        # A3: PR Resolution Latency (Median Duration)
        if len(pr_latencies_days) > 0:
            prl_med = statistics.median(pr_latencies_days)
            prl_norm = 1.0 / (1.0 + prl_med / self.REF_PR_LATENCY_DAYS)
            calculated_metrics["A3"] = MetricValue(
                metric_id="A3",
                metric_name="PR Resolution Latency (PRL Median)",
                raw_value=round(prl_med, 2),
                formatted_value=f"{prl_med:.2f} days",
                unit="days",
                direction="lower_is_better",
                normalized_score=round(prl_norm, 4),
                weight=self.CORE_WEIGHTS.get("A3", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="calculated",
                notes=f"Non-parametric median duration over {len(pr_latencies_days)} PRs (ref: {self.REF_PR_LATENCY_DAYS}d)."
            )
        else:
            missing_metric_ids.append("A3")
            calculated_metrics["A3"] = MetricValue(
                metric_id="A3",
                metric_name="PR Resolution Latency (PRL Median)",
                raw_value=None,
                formatted_value="N/A",
                unit="days",
                direction="lower_is_better",
                normalized_score=None,
                weight=self.CORE_WEIGHTS.get("A3", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="missing_data",
            )

        # A4: PR Backlog Ratio (Provisional)
        total_prs_count = len(prs)
        if total_prs_count > 0:
            pbr_raw = len(open_prs) / total_prs_count
            pbr_norm = 1.0 - pbr_raw
            calculated_metrics["A4"] = MetricValue(
                metric_id="A4",
                metric_name="Pull Request Backlog Ratio (PBR)",
                raw_value=round(pbr_raw, 4),
                formatted_value=f"{pbr_raw * 100:.1f}% open",
                unit="ratio",
                direction="lower_is_better",
                normalized_score=round(pbr_norm, 4),
                weight=self.CORE_WEIGHTS.get("A4", 0.0),
                chaoss_family="Evolution",
                linaker_area="Production Process",
                status="provisional",
                notes="Provisional metric. Ratio of open PRs to total sampled PRs."
            )
        else:
            missing_metric_ids.append("A4")
            calculated_metrics["A4"] = MetricValue(
                metric_id="A4",
                metric_name="Pull Request Backlog Ratio (PBR)",
                raw_value=None,
                formatted_value="N/A",
                unit="ratio",
                direction="lower_is_better",
                normalized_score=None,
                weight=self.CORE_WEIGHTS.get("A4", 0.0),
                chaoss_family="Evolution",
                linaker_area="Production Process",
                status="missing_data",
            )

        # =====================================================================
        # 2. Core Health Metrics (Issue Side - Pure Issues)
        # =====================================================================

        closed_issues = []
        open_issues = []
        issue_latencies_days: List[float] = []

        for iss in issues:
            iss_dict = iss if isinstance(iss, dict) else iss.model_dump()
            state = (iss_dict.get("state") or "").lower()
            created_at = _parse_utc_iso(iss_dict.get("created_at"))
            closed_at = _parse_utc_iso(iss_dict.get("closed_at"))

            if state == "closed":
                closed_issues.append(iss_dict)
                if created_at and closed_at and closed_at >= created_at:
                    dur_days = (closed_at - created_at).total_seconds() / 86400.0
                    issue_latencies_days.append(dur_days)
            else:
                open_issues.append(iss_dict)

        total_issues_count = len(issues)

        # A5: Issue Resolution Rate (IRR)
        if total_issues_count > 0:
            irr_raw = len(closed_issues) / total_issues_count
            calculated_metrics["A5"] = MetricValue(
                metric_id="A5",
                metric_name="Issue Resolution Rate (IRR)",
                raw_value=round(irr_raw, 4),
                formatted_value=f"{irr_raw * 100:.1f}%",
                unit="ratio",
                direction="higher_is_better",
                normalized_score=round(irr_raw, 4),
                weight=self.CORE_WEIGHTS.get("A5", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="calculated",
                notes=f"Computed across {total_issues_count} tracked issues ({len(closed_issues)} closed)."
            )
        else:
            missing_metric_ids.append("A5")
            calculated_metrics["A5"] = MetricValue(
                metric_id="A5",
                metric_name="Issue Resolution Rate (IRR)",
                raw_value=None,
                formatted_value="N/A (No issues)",
                unit="ratio",
                direction="higher_is_better",
                normalized_score=None,
                weight=self.CORE_WEIGHTS.get("A5", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="missing_data",
                notes="No issue records found or issues disabled."
            )

        # A6: Issue Resolution Latency (IRL Median)
        if len(issue_latencies_days) > 0:
            irl_med = statistics.median(issue_latencies_days)
            irl_norm = 1.0 / (1.0 + irl_med / self.REF_ISSUE_LATENCY_DAYS)
            calculated_metrics["A6"] = MetricValue(
                metric_id="A6",
                metric_name="Issue Resolution Latency (IRL Median)",
                raw_value=round(irl_med, 2),
                formatted_value=f"{irl_med:.2f} days",
                unit="days",
                direction="lower_is_better",
                normalized_score=round(irl_norm, 4),
                weight=self.CORE_WEIGHTS.get("A6", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="calculated",
                notes=f"Median turnaround over {len(issue_latencies_days)} closed issues (ref: {self.REF_ISSUE_LATENCY_DAYS}d)."
            )
        else:
            missing_metric_ids.append("A6")
            calculated_metrics["A6"] = MetricValue(
                metric_id="A6",
                metric_name="Issue Resolution Latency (IRL Median)",
                raw_value=None,
                formatted_value="N/A",
                unit="days",
                direction="lower_is_better",
                normalized_score=None,
                weight=self.CORE_WEIGHTS.get("A6", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="missing_data",
            )

        # =====================================================================
        # 3. Development Activity & Velocity Metrics (A7, A8R)
        # =====================================================================

        # A7: Review Throughput (Recent PR arrivals in last 90 days)
        recent_prs_90d = 0
        pr_created_dates = []

        for p in prs:
            p_dict = p if isinstance(p, dict) else p.model_dump()
            c_at = _parse_utc_iso(p_dict.get("created_at"))
            if c_at:
                pr_created_dates.append(c_at)
                if (now - c_at).days <= 90:
                    recent_prs_90d += 1

        if len(pr_created_dates) > 0:
            # Normalization via saturating count transform
            rtp_norm = recent_prs_90d / (recent_prs_90d + 10.0)
            calculated_metrics["A7"] = MetricValue(
                metric_id="A7",
                metric_name="Review Throughput (RTP 90d)",
                raw_value=float(recent_prs_90d),
                formatted_value=f"{recent_prs_90d} PRs / 90d",
                unit="count",
                direction="contextual",
                normalized_score=round(rtp_norm, 4),
                weight=self.CORE_WEIGHTS.get("A7", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="calculated",
                notes=f"Count of PRs submitted in the past 90 days."
            )
        else:
            missing_metric_ids.append("A7")
            calculated_metrics["A7"] = MetricValue(
                metric_id="A7",
                metric_name="Review Throughput (RTP 90d)",
                raw_value=None,
                formatted_value="N/A",
                unit="count",
                direction="contextual",
                normalized_score=None,
                weight=self.CORE_WEIGHTS.get("A7", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="missing_data",
            )

        # A8R: Relative Development Trend (OLS slope over 12-week intervals)
        if len(pr_created_dates) >= 4:
            min_date = min(pr_created_dates)
            span_days = max((now - min_date).days, 1)
            num_intervals = max(int(span_days / 84), 2)
            
            # Bin PRs into 84-day intervals
            interval_counts = [0] * num_intervals
            for c_date in pr_created_dates:
                days_ago = (now - c_date).days
                idx = num_intervals - 1 - int(days_ago / 84)
                if 0 <= idx < num_intervals:
                    interval_counts[idx] += 1

            mean_vol = statistics.mean(interval_counts) if interval_counts else 0.0
            if mean_vol > 0 and num_intervals >= 2:
                # OLS slope
                x = list(range(num_intervals))
                x_mean = statistics.mean(x)
                numerator = sum((xi - x_mean) * (yi - mean_vol) for xi, yi in zip(x, interval_counts))
                denominator = sum((xi - x_mean) ** 2 for xi in x)
                ols_slope = numerator / denominator if denominator > 0 else 0.0
                rel_slope = ols_slope / mean_vol

                # Logistic mapping
                trend_norm = 1.0 / (1.0 + math.exp(-rel_slope / 0.10))
                calculated_metrics["A8R"] = MetricValue(
                    metric_id="A8R",
                    metric_name="Relative Development Trend (A8R)",
                    raw_value=round(rel_slope, 4),
                    formatted_value=f"{'+' if rel_slope >= 0 else ''}{rel_slope * 100:.1f}% / interval",
                    unit="ratio/interval",
                    direction="contextual",
                    normalized_score=round(trend_norm, 4),
                    weight=self.CORE_WEIGHTS.get("A8R", 0.0),
                    chaoss_family="Evolution",
                    linaker_area="Community Productivity",
                    status="calculated",
                    notes=f"Computed across {num_intervals} 12-week intervals (mean volume {mean_vol:.1f} PRs/interval)."
                )
            else:
                missing_metric_ids.append("A8R")
                calculated_metrics["A8R"] = MetricValue(
                    metric_id="A8R",
                    metric_name="Relative Development Trend (A8R)",
                    raw_value=None,
                    formatted_value="N/A",
                    unit="ratio/interval",
                    direction="contextual",
                    normalized_score=None,
                    weight=self.CORE_WEIGHTS.get("A8R", 0.0),
                    chaoss_family="Evolution",
                    linaker_area="Community Productivity",
                    status="missing_data",
                )
        else:
            missing_metric_ids.append("A8R")
            calculated_metrics["A8R"] = MetricValue(
                metric_id="A8R",
                metric_name="Relative Development Trend (A8R)",
                raw_value=None,
                formatted_value="N/A (< 4 PRs for trend)",
                unit="ratio/interval",
                direction="contextual",
                normalized_score=None,
                weight=self.CORE_WEIGHTS.get("A8R", 0.0),
                chaoss_family="Evolution",
                linaker_area="Community Productivity",
                status="missing_data",
            )

        # =====================================================================
        # 4. Governance & Documentation Indicators
        # =====================================================================

        # M45-LICENSE: Declared License
        lic_name = repo_meta.get("license_name")
        has_license = bool(lic_name and lic_name not in ("NOASSERTION", "Custom", "None", ""))
        lic_score = 1.0 if has_license else 0.0
        calculated_metrics["M45-LICENSE"] = MetricValue(
            metric_id="M45-LICENSE",
            metric_name="Declared Software License",
            raw_value=lic_score,
            formatted_value=lic_name if has_license else "No Approved License Detected",
            unit="boolean",
            direction="higher_is_better",
            normalized_score=lic_score,
            weight=self.CORE_WEIGHTS.get("M45-LICENSE", 0.0),
            chaoss_family="Risk",
            linaker_area="Orchestration",
            status="calculated",
            notes="Evaluates presence of a declared open-source license."
        )

        # M67-DOCS: Technical Documentation (README / Description)
        desc = repo_meta.get("description")
        size_kb = repo_meta.get("size_kb") or 0
        has_docs = bool(desc and len(desc.strip()) > 5) or (size_kb > 0)
        docs_score = 1.0 if has_docs else 0.0
        calculated_metrics["M67-DOCS"] = MetricValue(
            metric_id="M67-DOCS",
            metric_name="Technical Documentation Presence",
            raw_value=docs_score,
            formatted_value="Present" if has_docs else "Missing / Incomplete",
            unit="boolean",
            direction="higher_is_better",
            normalized_score=docs_score,
            weight=self.CORE_WEIGHTS.get("M67-DOCS", 0.0),
            chaoss_family="Evolution",
            linaker_area="Production Output",
            status="calculated",
            notes="Detects repository description and documentation scaffolding."
        )

        # =====================================================================
        # 5. Context Variables & Data Quality Indicators (Kept SEPARATE from RHI)
        # =====================================================================

        # C1: Repository Age (Contextual Covariate)
        repo_created = _parse_utc_iso(repo_meta.get("created_at"))
        if repo_created:
            age_days = max((now - repo_created).days, 0)
            context_vars["C1"] = MetricValue(
                metric_id="C1",
                metric_name="Repository Chronological Age",
                raw_value=float(age_days),
                formatted_value=f"{age_days} days ({age_days / 365.25:.1f} years)",
                unit="days",
                direction="contextual",
                normalized_score=None,
                weight=0.0,
                chaoss_family="Common Metrics",
                linaker_area="Production Process",
                status="calculated",
                notes="Context covariate. Age is an interpretive moderator, not a health score."
            )
        else:
            context_vars["C1"] = MetricValue(
                metric_id="C1",
                metric_name="Repository Chronological Age",
                raw_value=None,
                formatted_value="N/A",
                unit="days",
                direction="contextual",
                normalized_score=None,
                weight=0.0,
                chaoss_family="Common Metrics",
                linaker_area="Production Process",
                status="missing_data",
            )

        # X1: Project Popularity (Stars + Forks Context)
        stars = repo_meta.get("stars", 0)
        forks = repo_meta.get("forks", 0)
        pop_raw = float(stars + forks)
        context_vars["X1"] = MetricValue(
            metric_id="X1",
            metric_name="Repository External Popularity (Stars + Forks)",
            raw_value=pop_raw,
            formatted_value=f"{stars:,} stars, {forks:,} forks",
            unit="count",
            direction="contextual",
            normalized_score=None,
            weight=0.0,
            chaoss_family="Value",
            linaker_area="Community Stability",
            status="calculated",
            notes="Context variable. Excluded from RHI to avoid popularity confounding."
        )

        # C2: PR Capture Rate (Data Quality Indicator)
        max_pr_num = 0
        for p in prs:
            p_dict = p if isinstance(p, dict) else p.model_dump()
            max_pr_num = max(max_pr_num, p_dict.get("number", 0))

        if max_pr_num > 0:
            cap_rate = min(len(prs) / max_pr_num, 1.0)
            data_qualities["C2"] = MetricValue(
                metric_id="C2",
                metric_name="Pull Request Capture Rate",
                raw_value=round(cap_rate, 4),
                formatted_value=f"{cap_rate * 100:.1f}% ({len(prs)}/{max_pr_num})",
                unit="ratio",
                direction="higher_is_better",
                normalized_score=round(cap_rate, 4),
                weight=0.0,
                chaoss_family="Common Metrics",
                linaker_area="Production Process",
                status="calculated",
                notes="Data quality diagnostic. Measures pagination capture completeness."
            )
        else:
            data_qualities["C2"] = MetricValue(
                metric_id="C2",
                metric_name="Pull Request Capture Rate",
                raw_value=1.0,
                formatted_value="100.0% (Zero PRs)",
                unit="ratio",
                direction="higher_is_better",
                normalized_score=1.0,
                weight=0.0,
                chaoss_family="Common Metrics",
                linaker_area="Production Process",
                status="calculated",
            )

        # =====================================================================
        # 6. Dimensions Aggregation & Composite RHI
        # =====================================================================

        # Dimensions mapping
        dim_mappings = {
            "code_review_pr_efficiency": {
                "name": "Code Review & PR Efficiency",
                "metric_ids": ["A1", "A2", "A3", "A4"]
            },
            "issue_management": {
                "name": "Issue Management & Responsiveness",
                "metric_ids": ["A5", "A6"]
            },
            "velocity_trend": {
                "name": "Activity Velocity & Trend",
                "metric_ids": ["A7", "A8R"]
            },
            "governance_docs": {
                "name": "Governance & Documentation",
                "metric_ids": ["M45-LICENSE", "M67-DOCS"]
            }
        }

        dimensions: Dict[str, DimensionScore] = {}
        for dim_key, dim_info in dim_mappings.items():
            dim_metrics = [calculated_metrics[mid] for mid in dim_info["metric_ids"] if mid in calculated_metrics]
            avail_metrics = [m for m in dim_metrics if m.normalized_score is not None]
            
            dim_score = None
            if avail_metrics:
                dim_score = round(statistics.mean(m.normalized_score for m in avail_metrics) * 100.0, 1)

            dimensions[dim_key] = DimensionScore(
                name=dim_info["name"],
                score=dim_score,
                metrics_available=len(avail_metrics),
                metrics_total=len(dim_info["metric_ids"]),
                metrics=dim_metrics,
            )

        # Composite RHI Calculation:
        # Sum of (weight * normalized_score) / sum of weights for available metrics
        weighted_sum = 0.0
        accumulated_weight = 0.0
        total_possible_weight = sum(self.CORE_WEIGHTS.values())

        for mid, w in self.CORE_WEIGHTS.items():
            metric = calculated_metrics.get(mid)
            if metric and metric.normalized_score is not None:
                weighted_sum += w * metric.normalized_score
                accumulated_weight += w

        coverage_ratio = round(accumulated_weight / total_possible_weight, 4) if total_possible_weight > 0 else 0.0
        coverage_sufficient = coverage_ratio >= self.MIN_COVERAGE_THRESHOLD

        rhi_score = None
        rhi_grade = "Insufficient Data"

        if coverage_sufficient and accumulated_weight > 0:
            normalized_rhi = weighted_sum / accumulated_weight
            rhi_score = round(normalized_rhi * 100.0, 1)

            if rhi_score >= 85.0:
                rhi_grade = "A"
            elif rhi_score >= 70.0:
                rhi_grade = "B"
            elif rhi_score >= 55.0:
                rhi_grade = "C"
            elif rhi_score >= 40.0:
                rhi_grade = "D"
            else:
                rhi_grade = "F"

        return HealthIndexResult(
            repository_name=repo_name,
            rhi_score=rhi_score,
            rhi_grade=rhi_grade,
            coverage_ratio=coverage_ratio,
            coverage_sufficient=coverage_sufficient,
            metrics=calculated_metrics,
            context_variables=context_vars,
            data_quality_indicators=data_qualities,
            dimensions=dimensions,
            missing_metrics=missing_metric_ids,
            calculation_timestamp=now.isoformat(),
        )


indicator_service = CompositeIndicatorService()

