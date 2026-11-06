"""
Repository Survival Analysis Engine
Module: M0.4 – Survival Analysis

Implements non-parametric Kaplan-Meier survival estimation,
semi-parametric Cox Proportional Hazards regression,
synthetic OSS benchmark cohort generation, and single-repository lifespan diagnostics.
"""

import math
import datetime
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import scipy.stats as stats
import scipy.optimize as optimize

from ..schemas.survival import (
    SurvivalObservation,
    KaplanMeierPoint,
    KaplanMeierResult,
    CoxCovariateResult,
    CoxRegressionResult,
    SurvivalAnalysisReport,
    SingleRepoSurvivalAssessment,
)


class RepositorySurvivalService:
    """Statistical engine for repository lifespan and survival analysis."""

    def fit_kaplan_meier(self, observations: List[SurvivalObservation]) -> KaplanMeierResult:
        """
        Fits a non-parametric Kaplan-Meier survival curve.
        Computes Greenwood confidence intervals and identifies median survival time.
        """
        if not observations:
            return KaplanMeierResult(
                timeline=[],
                survival_table=[],
                median_survival_time=None,
                sample_size=0,
                event_count=0,
                censored_count=0,
            )

        n_total = len(observations)
        # Extract durations and events
        durations = np.array([float(obs.duration) for obs in observations])
        events = np.array([int(obs.event) for obs in observations])

        total_events = int(np.sum(events == 1))
        total_censored = int(np.sum(events == 0))

        # Get unique sorted event times
        unique_times = np.sort(np.unique(durations))

        survival_prob = 1.0
        greenwood_sum = 0.0
        n_at_risk = n_total
        median_time: Optional[float] = None

        points: List[KaplanMeierPoint] = []
        timeline: List[float] = []

        # Time 0 baseline point
        points.append(
            KaplanMeierPoint(
                timeline=0.0,
                n_at_risk=n_total,
                n_events=0,
                n_censored=0,
                survival_probability=1.0,
                confidence_lower=1.0,
                confidence_upper=1.0,
            )
        )
        timeline.append(0.0)

        for t in unique_times:
            # Events and censorings at this exact time
            mask_t = (durations == t)
            d_i = int(np.sum(events[mask_t] == 1))
            c_i = int(np.sum(events[mask_t] == 0))

            if n_at_risk <= 0:
                break

            # Update survival probability only if events occurred
            if d_i > 0:
                hazard_factor = 1.0 - (d_i / n_at_risk)
                survival_prob *= hazard_factor

                # Greenwood's variance term
                if n_at_risk > d_i:
                    greenwood_sum += d_i / (n_at_risk * (n_at_risk - d_i))

                var_s = (survival_prob ** 2) * greenwood_sum
                se_s = math.sqrt(max(0.0, var_s))
                ci_low = max(0.0, survival_prob - 1.96 * se_s)
                ci_high = min(1.0, survival_prob + 1.96 * se_s)
            else:
                ci_low = points[-1].confidence_lower if points else 1.0
                ci_high = points[-1].confidence_upper if points else 1.0

            # Check for median survival crossing (first time S(t) <= 0.50)
            if median_time is None and survival_prob <= 0.50:
                median_time = float(t)

            km_point = KaplanMeierPoint(
                timeline=float(t),
                n_at_risk=n_at_risk,
                n_events=d_i,
                n_censored=c_i,
                survival_probability=round(survival_prob, 4),
                confidence_lower=round(ci_low, 4) if ci_low is not None else None,
                confidence_upper=round(ci_high, 4) if ci_high is not None else None,
            )
            points.append(km_point)
            timeline.append(float(t))

            # Decrement risk set for next time point
            n_at_risk -= (d_i + c_i)

        return KaplanMeierResult(
            timeline=timeline,
            survival_table=points,
            median_survival_time=median_time,
            sample_size=n_total,
            event_count=total_events,
            censored_count=total_censored,
        )

    def fit_cox_ph(self, observations: List[SurvivalObservation]) -> Optional[CoxRegressionResult]:
        """
        Fits a semi-parametric Cox Proportional Hazards regression model
        using numerical maximization of Breslow partial log-likelihood.
        """
        if len(observations) < 10:
            return CoxRegressionResult(
                is_fitted=False,
                notes="Sample size too small (N < 10) to reliably estimate Cox proportional hazards."
            )

        # Identify all distinct covariate names
        all_cov_keys = sorted(list({k for obs in observations for k in obs.covariates.keys()}))
        if not all_cov_keys:
            return CoxRegressionResult(
                is_fitted=False,
                notes="No numeric predictor covariates provided for Cox regression."
            )

        n = len(observations)
        p = len(all_cov_keys)

        # Build feature matrix X, durations T, events E
        X = np.zeros((n, p))
        T = np.zeros(n)
        E = np.zeros(n, dtype=int)

        for i, obs in enumerate(observations):
            T[i] = float(obs.duration)
            E[i] = int(obs.event)
            for j, key in enumerate(all_cov_keys):
                X[i, j] = float(obs.covariates.get(key, 0.0))

        # Check that we have at least 5 terminal events
        event_indices = np.where(E == 1)[0]
        if len(event_indices) < 5:
            return CoxRegressionResult(
                is_fitted=False,
                notes=f"Insufficient events (observed events={len(event_indices)}). Cox PH requires >= 5 events."
            )

        # Standardize features for numerical stability
        means = np.mean(X, axis=0)
        stds = np.std(X, axis=0)
        stds[stds == 0] = 1.0  # Prevent divide-by-zero on zero-variance
        X_scaled = (X - means) / stds

        # Sort descending or track risk sets
        # Risk set R(t_i) contains all j where T[j] >= T[i]
        def neg_log_partial_likelihood(beta: np.ndarray) -> float:
            risk_scores = np.dot(X_scaled, beta)
            # Clip for numerical stability
            risk_scores = np.clip(risk_scores, -30.0, 30.0)
            exp_risk = np.exp(risk_scores)

            log_lik = 0.0
            for idx in event_indices:
                t_event = T[idx]
                risk_set_mask = (T >= t_event)
                sum_exp_risk = np.sum(exp_risk[risk_set_mask])
                if sum_exp_risk <= 0:
                    continue
                log_lik += risk_scores[idx] - np.log(sum_exp_risk)

            # L2 regularization for stability
            reg = 1e-4 * np.sum(beta ** 2)
            return -(log_lik - reg)

        beta_init = np.zeros(p)
        try:
            res = optimize.minimize(
                neg_log_partial_likelihood,
                beta_init,
                method="BFGS",
                options={"maxiter": 150, "disp": False}
            )
            if not res.success and res.status != 2:
                # Still use if converged reasonably
                pass

            beta_opt_scaled = res.x
            # Transform coefficients back to original scale
            beta_opt = beta_opt_scaled / stds

            # Approximate variance via inverse Hessian
            if hasattr(res, "hess_inv") and res.hess_inv is not None:
                hess_inv = res.hess_inv
                var_scaled = np.diag(hess_inv)
                se_scaled = np.sqrt(np.maximum(1e-6, var_scaled))
                se = se_scaled / stds
            else:
                se = np.ones(p) * 0.1

            covariate_results: List[CoxCovariateResult] = []
            for j, key in enumerate(all_cov_keys):
                b = float(beta_opt[j])
                s = float(se[j])
                z = b / s if s > 0 else 0.0
                p_val = float(2.0 * (1.0 - stats.norm.cdf(abs(z))))
                hr = float(math.exp(np.clip(b, -10.0, 10.0)))
                ci_lo = float(math.exp(np.clip(b - 1.96 * s, -10.0, 10.0)))
                ci_hi = float(math.exp(np.clip(b + 1.96 * s, -10.0, 10.0)))

                covariate_results.append(
                    CoxCovariateResult(
                        name=key,
                        coef=round(b, 4),
                        hazard_ratio=round(hr, 4),
                        std_err=round(s, 4),
                        z_score=round(z, 3),
                        p_value=round(p_val, 4),
                        ci_lower=round(ci_lo, 4),
                        ci_upper=round(ci_hi, 4),
                    )
                )

            # Calculate C-index (Concordance)
            risk_preds = np.dot(X, beta_opt)
            concordant, discordant, ties = 0, 0, 0
            for i in event_indices:
                for j in range(n):
                    if T[j] > T[i]:
                        if risk_preds[i] > risk_preds[j]:
                            concordant += 1
                        elif risk_preds[i] < risk_preds[j]:
                            discordant += 1
                        else:
                            ties += 1

            total_pairs = concordant + discordant + ties
            c_index = round((concordant + 0.5 * ties) / total_pairs, 4) if total_pairs > 0 else None

            log_lik_null = -float(neg_log_partial_likelihood(beta_init))
            log_lik_fit = -float(res.fun)

            return CoxRegressionResult(
                is_fitted=True,
                log_likelihood=round(log_lik_fit, 2),
                log_likelihood_null=round(log_lik_null, 2),
                concordance_index=c_index,
                covariates=covariate_results,
                notes="Estimated via partial log-likelihood optimization with L2 regularization."
            )

        except Exception as e:
            return CoxRegressionResult(
                is_fitted=False,
                notes=f"Optimization failed to converge: {str(e)}"
            )

    def generate_synthetic_benchmark_cohort(self, sample_size: int = 150, seed: int = 42) -> List[SurvivalObservation]:
        """
        Generates a statistically realistic benchmark cohort of open-source repositories
        for testing, calibration, and baseline hazard projection.
        Simulates realistic OSS lifespans, right-censoring, and hazard covariates.
        """
        rng = np.random.default_rng(seed)
        observations: List[SurvivalObservation] = []

        study_duration = 3650.0  # 10-year follow-up window (days)

        for i in range(sample_size):
            repo_id = f"benchmark-org/simulated-repo-{i + 1:03d}"

            # Covariates
            log_stars = float(rng.normal(loc=5.5, scale=1.8))
            stars = max(int(np.exp(log_stars)), 1)
            prar = float(np.clip(rng.beta(a=3.5, b=2.0), 0.05, 0.98))
            activity_slope = float(rng.normal(loc=-0.02, scale=0.15))
            prs_per_month = float(max(rng.exponential(scale=12.0), 0.5))

            # Base hazard rate lambda_0
            # Higher stars & higher PRAR reduce deprecation hazard; negative slope increases hazard
            log_hazard = -7.5 - (0.35 * (log_stars - 5.5)) - (1.2 * (prar - 0.5)) - (2.0 * activity_slope)
            hazard = math.exp(np.clip(log_hazard, -12.0, -3.0))

            # Simulate true lifespan from exponential distribution
            true_lifespan = float(rng.exponential(scale=1.0 / hazard))

            # Random entry time into study
            entry_time = float(rng.uniform(0.0, study_duration * 0.7))
            follow_up = study_duration - entry_time

            if true_lifespan <= follow_up:
                observed_time = max(round(true_lifespan, 1), 10.0)
                event = 1  # Deprecated / Archived
            else:
                observed_time = max(round(follow_up, 1), 10.0)
                event = 0  # Right-censored (active at study conclusion)

            observations.append(
                SurvivalObservation(
                    subject_id=repo_id,
                    duration=observed_time,
                    event=event,
                    covariates={
                        "stars": float(stars),
                        "prar": round(prar, 4),
                        "activity_slope": round(activity_slope, 4),
                        "prs_per_month": round(prs_per_month, 2),
                    }
                )
            )

        return observations

    def run_benchmark_analysis(self) -> SurvivalAnalysisReport:
        """Runs complete survival analysis on the synthetic benchmark cohort."""
        cohort = self.generate_synthetic_benchmark_cohort(sample_size=150)
        km_res = self.fit_kaplan_meier(cohort)
        cox_res = self.fit_cox_ph(cohort)

        censored_rate = round(km_res.censored_count / km_res.sample_size, 4) if km_res.sample_size > 0 else 0.0

        return SurvivalAnalysisReport(
            dataset_type="synthetic_benchmark",
            sample_size=km_res.sample_size,
            event_count=km_res.event_count,
            censored_count=km_res.censored_count,
            censoring_rate=censored_rate,
            kaplan_meier=km_res,
            cox_regression=cox_res,
            data_limitations=[
                "Generated using calibrated synthetic open-source survival distributions.",
                "Real repository survival modeling requires longitudinal cross-sectional datasets (e.g. GH Archive / BigQuery).",
                "A single snapshot of a live repository cannot establish a survival curve."
            ],
            future_data_requirements=[
                "Cross-sectional repository dataset with historical deprecation labels (e.g. He et al. 2024 dataset of 103k repos).",
                "Longitudinal monthly activity snapshots to record exact timing of abandonment.",
                "Explicit ground truth for inactivity vs maintenance pause."
            ]
        )

    def assess_single_repository(self, repo_meta: Dict[str, Any]) -> SingleRepoSurvivalAssessment:
        """
        Assesses survival context for an individual live repository snapshot,
        clearly diagnosing right-censoring and explaining scientific limitations.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        created_str = repo_meta.get("created_at")
        repo_name = repo_meta.get("full_name") or repo_meta.get("name") or "unknown/repository"
        is_archived = bool(repo_meta.get("is_archived", False))

        created_dt = None
        if created_str:
            try:
                created_dt = datetime.datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            except Exception:
                pass

        if created_dt:
            age_days = float(max((now - created_dt).days, 1))
        else:
            age_days = 365.0  # fallback 1 year if unparsed

        age_years = round(age_days / 365.25, 2)

        # Right-censored if repository is active and not archived
        if is_archived:
            censoring_status = "event_observed"
            is_censored = False
        else:
            censoring_status = "right_censored"
            is_censored = True

        # Methodological caveats
        caveats = [
            "A single snapshot of one repository cannot construct an empirical Kaplan-Meier survival curve.",
            "Survival estimation requires a cohort of repositories tracked across time with observable terminal events.",
            f"This repository is currently classified as '{censoring_status}' with an observed lifespan of {age_years} years ({int(age_days)} days).",
            "True time-to-deprecation remains unknown for active projects until a terminal transition occurs.",
            "Compatibility: The data schema is structured for seamless ingestion of historical cohorts from GH Archive or BigQuery."
        ]

        return SingleRepoSurvivalAssessment(
            repository_name=repo_name,
            observed_lifespan_days=age_days,
            observed_lifespan_years=age_years,
            censoring_status=censoring_status,
            is_censored=is_censored,
            is_archived=is_archived,
            eligible_for_standalone_km=False,
            methodological_caveats=caveats,
        )


survival_service = RepositorySurvivalService()

