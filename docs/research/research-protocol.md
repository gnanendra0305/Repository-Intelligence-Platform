# Research Protocol: Research Questions, Hypotheses & Methodology
**Project:** AI-Assisted Developer Decision Support and Repository Intelligence Platform  
**Document Code:** M1.1  
**Date:** 2026-11-06  
**Status:** Pre-registered Research Design (Pending Project Guide Formal Review)  
**Evidence Standard:** Every statement conforms to the project evidence legend: `[FACT]`, `[DERIVED]`, `[REC]`, `[ASSUME]`.

---

## 1. Research Objectives & Context

**[FACT]** Organizations and developers increasingly rely on open-source software (OSS) components as critical operational dependencies. However, technology intake decisions on public code-hosting platforms such as GitHub are frequently driven by superficial popularity metrics (stars, forks) rather than robust evaluations of maintainer throughput, governance stability, and sustainability.

**[FACT]** The project's designated base paper—**Linåker et al. (2026)** (*"Assessing Open Source Software Health in Organizations' Intake Processes: A Qualitative Study on the Practitioners' Perspective"*, *Empirical Software Engineering*, Springer)—identifies **21 OSS health aspects and 72 metrics across 5 areas of health** (Community Productivity, Community Stability, Orchestration, Production Process, Production Output).

**[FACT]** The base paper established qualitative categories and practitioner priorities through semi-structured interviews, but explicitly provides **no mathematical equations, weighting schemes, or operational algorithms** (Linåker et al. 2026, §1.1.1).

**[DERIVED]** To bridge the gap between qualitative practitioner priorities and automated intake tooling, this platform operationalises a core subset of computable health indicators, combines them into a multi-attribute **Repository Health Index (RHI)**, evaluates longitudinal survival dynamics, and synthesizes grounded risk assessments.

---

## 2. Research Questions (RQ1 – RQ3)

### RQ1: Construct Operationalisation and Measurement Validity
> **To what extent can the qualitative OSS health dimensions identified by Linåker et al. (2026) and the Linux Foundation CHAOSS metric families be operationalised into objective, computable quantitative metrics using public repository mining (GitHub REST API)?**

* **Motivation:** Practitioners identify 21 health aspects, but many rely on subjective impressions or inaccessible internal telemetry (e.g. private chat logs, internal developer satisfaction). We must establish the empirical feasibility, data completeness, and construct validity of computing health metrics purely from public repository event streams.
* **Scope of Inquiry:**
  1. What proportion of the 21 Linåker aspects and 72 metrics are fully measurable, partially measurable, or unobservable via public GitHub APIs?
  2. How consistently do the operationalised metrics map onto the 5 standardized CHAOSS Metric Families (Evolution, Risk, Value, DEI, Common)?
  3. Does missing data or API-induced truncation (pagination caps) threaten the construct validity of composite indicators?

### RQ2: Predictive Validity and Longitudinal Sustainability
> **How accurately do composite indicators of OSS health—specifically the Repository Health Index (RHI) and individual metric families—predict repository survival versus dormancy/abandonment at $t + 12$ months?**

* **Motivation:** Health is meaningful to an adopter only if it forecasts future viability. If a high health score does not lower the risk of subsequent maintainer abandonment, the metric lacks criterion-related predictive validity.
* **Scope of Inquiry:**
  1. Does a low baseline RHI score at time $t$ statistically predict dormancy (zero maintenance activity) or formal deprecation over the subsequent 12-month follow-up window $[t, t + 12\text{ months}]$?
  2. Which individual metric family (e.g. PR throughput vs. issue resolution efficiency vs. contributor concentration) provides the strongest prognostic signal in survival analysis models (Cox Proportional Hazards)?
  3. How does the predictive discrimination (Harrell's $C$-index and ROC-AUC) of RHI compare against raw surface popularity metrics (stars, forks)?

### RQ3: Decision-Support Utility and Risk Discrepancy
> **To what extent does multi-attribute composite intelligence expose critical governance and maintenance bottlenecks that are masked by raw surface metrics (stars, forks)?**

* **Motivation:** Adopters frequently fall prey to the "popularity illusion," assuming heavily starred projects are actively maintained and legally sound.
* **Scope of Inquiry:**
  1. What percentage of highly starred repositories ($>1,000$ stars) exhibit critical maintenance bottlenecks (e.g. PR backlog ratio $>0.80$, median issue turnaround $>30$ days, or missing open-source licenses)?
  2. Can evidence-grounded rule synthesis reliably differentiate active sustainable libraries from "zombie" repositories that have high historical stars but zero active maintainer responsiveness?

---

## 3. Testable Hypotheses ($H_1 – H_3$)

| Hypothesis | Conceptual Rationale | Operational Formulation | Statistical Test & Falsification Threshold |
|---|---|---|---|
| **$H_1$ (Maintenance Efficiency)** | Maintainer responsiveness reflects active community intake and lower burnout. | Repositories with higher PR Acceptance Rate ($A_1$) and shorter median PR Latency ($A_3$) at time $t$ exhibit lower 12-month dormancy rates. | **Cox PH Regression:** Hazard Ratio $\text{HR}(A_1) < 1.0$ and $\text{HR}(A_3) > 1.0$ with $p < 0.05$. Falsified if $p \ge 0.05$ or coefficient sign reverses. |
| **$H_2$ (Composite Predictive Power)** | Multi-attribute composite RHI aggregates systemic health better than single metrics. | Repositories in the top RHI quartile ($Q_4$) at baseline exhibit significantly higher 12-month survival than repositories in the bottom quartile ($Q_1$). | **Kaplan-Meier Log-Rank Test & Logistic Regression:** Log-rank $p < 0.01$; ROC-AUC for 12-month abandonment classification $\ge 0.75$. Falsified if AUC $\le 0.65$. |
| **$H_3$ (Popularity Discrepancy)** | Stars reflect cumulative historical curiosity, not current maintenance capacity. | Stargazer count ($X_1$) does not correlate strongly with maintainer operational efficiency ($A_2$) or issue resolution rate ($A_5$). | **Rank Correlation:** Kendall's $\tau < 0.25$ between $X_1$ and $A_2$, and between $X_1$ and $A_5$. Falsified if Kendall's $\tau \ge 0.40$ ($p < 0.01$). |

---

## 4. Pre-Registered Study Protocol

### 4.1 Variables

1. **Independent Variables (M0.1 / M0.3 Indicators at baseline $t$):**
   * *Production Process:* $A_1$ (PR Acceptance Rate, ratio), $A_2$ (PR Resolution Efficiency, days), $A_3$ (PR Resolution Latency Median, days), $A_4$ (PR Backlog Ratio, ratio).
   * *Community Productivity:* $A_5$ (Issue Resolution Rate, ratio), $A_6$ (Issue Resolution Latency, days), $A_7$ (Issue Backlog Ratio, ratio).
   * *Governance & Scaffolding:* $M_{45}$ (Declared License, boolean), $M_{67}$ (Documentation Presence, boolean).
   * *Composite Score:* $\text{RHI} \in [0.0, 100.0]$ (calculated only when coverage $\ge 40\%$).
2. **Contextual Variables (Covariates, excluded from RHI):**
   * $C_1$ (Repository Age in days), $X_1$ (Stargazer Count), $F$ (Fork Count).
3. **Dependent Variables (Longitudinal Outcomes over $[t, t + 12\text{ months}]$):**
   * $\text{Dormancy}_{t+12} \in \{0, 1\}$: 1 if zero commits, zero PR merges, and zero maintainer issue closures in the follow-up year; 0 otherwise.
   * $\text{Archived}_{t+12} \in \{0, 1\}$: 1 if repo entered GitHub archived state; 0 otherwise.
   * $\text{Lifespan}$ (days): Duration from repository birth to observed terminal event or right-censoring date.

### 4.2 Observation Periods & Timing

```
Timeline:
--------------------|---------------------------------|-------------------->
                  t_0                               t_0 + 12 months
           (Baseline Snapshot)                    (Follow-Up Evaluation)
         Compute M0.1-M0.3 Indicators           Evaluate Dormancy/Abandonment
```

* **Baseline Observation Date ($t_0$):** Fixed historical cut-off date (e.g. 2024-01-01 or 12 months prior to current harvest).
* **Follow-up Window:** Strict 365-day interval $[t_0, t_0 + 365\text{ days}]$.
* **Right-Censoring Rule:** Any repository evaluated with less than 365 days of subsequent event observation is marked `censored_insufficient_followup` and evaluated using survival estimators rather than binary classification.

### 4.3 Evaluation Metrics

1. **Survival Discrimination:** Harrell's Concordance Index ($C$-index, target $\ge 0.70$) for Cox Proportional Hazards regression.
2. **Classification Performance:** Area Under the ROC Curve (ROC-AUC), Precision, Recall, and Brier Score for 12-month dormancy prediction.
3. **Known-Group Validation:** Wilcoxon Rank-Sum (Mann-Whitney $U$) test comparing Apache Incubator graduated vs. retired projects (expecting $p < 0.01$).

### 4.4 Threats to Validity & Mitigation

* **Construct Validity:** "Health" is a latent construct. Mitigated by using Linåker et al.'s peer-reviewed 21 aspects and CHAOSS standard definitions rather than ad-hoc heuristics.
* **Internal Validity (Survivorship Bias):** Sampling only surviving projects biases health estimates upward. Mitigated in M1.5 by explicitly including archived, dead, and retired repositories.
* **External Validity (Ecosystem Generalisability):** Different programming languages possess distinct collaboration norms. Mitigated by stratifying across three major ecosystems: Python (PyPI), JavaScript (npm), and Rust (crates.io).
* **Statistical Conclusion Validity (Heavy Tails):** OSS metrics exhibit extreme power-law distributions. Mitigated by employing non-parametric statistics (medians, Kendall's tau, Kaplan-Meier, Greenwood variance).

---

## 5. Explicit Assumptions Requiring Project Guide Approval

> [!IMPORTANT]
> The following four research design assumptions are formally submitted for review and approval by Project Guide **Dr. K. Gnanendra**:

| # | Assumption | Formal Definition in this Protocol | Guide Approval Decision |
|---|---|---|---|
| **A-1** | **12-Month Inactivity Threshold for Dormancy** | A repository is defined as *dormant* at $t+12$ if and only if during the 365-day window following $t$ there are 0 commits to default branch, 0 merged pull requests, and 0 closed issues. | `[PENDING GUIDE REVIEW]` |
| **A-2** | **Equal Block Weighting in Baseline RHI** | The composite RHI assigns equal $25\%$ block weights to the four evaluable Linåker health areas (Production Process, Community Productivity, Community Stability, Orchestration) rather than subjective arbitrary weights. | `[PENDING GUIDE REVIEW]` |
| **A-3** | **Three Target Ecosystems** | Sampling is stratified across Python (PyPI), JavaScript/TypeScript (npm), and Rust (crates.io), representing dynamic scripting, high-turnover web packages, and modern compiled systems software respectively. | `[PENDING GUIDE REVIEW]` |
| **A-4** | **Apache Incubator as Known-Group Ground Truth** | Apache Software Foundation (ASF) Incubator outcomes (Graduated to Top-Level Project vs. Retired/Moved to Attic) are adopted as the empirical ground truth for known-group construct validation. | `[PENDING GUIDE REVIEW]` |

---
*End of Document M1.1 — Research Questions, Hypotheses & Pre-registered Protocol.*

