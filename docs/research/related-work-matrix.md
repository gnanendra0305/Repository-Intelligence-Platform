# Related-Work Matrix: Comparative Analysis of OSS Health Frameworks & Literature
**Project:** AI-Assisted Developer Decision Support and Repository Intelligence Platform  
**Document Code:** M1.3  
**Date:** 2026-11-06  
**Status:** Complete Comparative Analysis  
**Evidence Standard:** Cites verified literature and platform specifications. Any unverified or extrapolated details are explicitly tagged `[UNVERIFIED]`.

---

## 1. Introduction

Evaluating open-source repository health, security, and sustainability is a prominent challenge across both industry and empirical software engineering research. Existing solutions diverge widely in their primary objectives (e.g. security posture, community vitality, dependency risk, or predictive modeling).

This document presents a structured comparative analysis of **10 prominent tools, frameworks, and empirical studies**:
1. **OpenSSF Scorecard** (Open Source Security Foundation / Linux Foundation)
2. **CHAOSS / Augur** (Community Health Analytics Open Source Software)
3. **OSS Compass** (Linux Foundation / Baidu / Huawei / Peking University)
4. **OpenDigger** (X-lab / Open Collaboration Analysis Engine)
5. **deps.dev** (Google Open Source Insights)
6. **Yin et al.** (Empirical Abandonment & Sustainability Forecasting)
7. **Ashok et al.** (Contributor Turnover & Bus Factor Analysis)
8. **Xia et al.** (Health Indicator Prediction with Hyperparameter Optimization)
9. **He et al.** (Lifespan & Deprecation Prediction via Repository Centrality)
10. **Yehudi et al.** (Research Software Sustainability & Community Health)

---

## 2. Comparative Matrix

| System / Study | Primary Objectives | Primary Data Sources | Key Metrics / Indicators Evaluated | Methodological Approach | Key Strengths | Key Limitations | Relevance to this Project |
|---|---|---|---|---|---|---|---|
| **1. OpenSSF Scorecard** | Assess security health and supply-chain risk of open-source projects. | GitHub / GitLab REST APIs, commit histories, package metadata. | 18 heuristic checks: Binary-Artifacts, Branch-Protection, CI-Tests, Dependency-Update-Tool, Fuzzing, Maintained, Pinned-Dependencies, SAST, Security-Policy, Signed-Releases, Token-Permissions, Vulnerabilities. | Deterministic rule-based scoring ($0-10$ scale) with heuristic risk weights. | Highly automated, industry standard for security hygiene, actionable check results. | Exclusively security/supply-chain focused; ignores community governance, contributor turnover, issue resolution efficiency, and longitudinal survival. | Directly informs our **M45-LICENSE**, **M60 (Code Scanning)**, and **M58 (Security Policy)** checks. |
| **2. CHAOSS / Augur** | Quantify community health, sustainability, and open-source vitality. | Git commit logs, GitHub/GitLab REST & GraphQL APIs, mailing lists, Pipermail, Discourse. | Standardized metrics across 5 families: Evolution (code changes, issues, PRs), Risk (bus factor, licensing), Value (labor investment), DEI (contributor demographics), Common. | SQL/Relational data warehousing (Augur schema) with REST API querying; metric operationalisation guidelines. | Comprehensive metric taxonomy, international standardisation, multi-platform collection (git + issue trackers + mailing lists). | Heavy operational footprint (requires complex database ingestion pipeline); no unified composite score or prescriptive adoption verdict. | Serves as our platform's **primary metric classification architecture** (5 CHAOSS families). |
| **3. OSS Compass** | Continuous community vitality evaluation and repository benchmarking. | GitHub, Gitee, Git commit logs. | Vitality index, Service Level Agreements (issue first-response, bug turnaround), Contributor Activity, Collaboration Network Density. | Weighted multi-attribute composite scoring, radar charts, comparative percentile ranking against domain cohorts. | User-friendly SaaS dashboard, covers both GitHub and Gitee, evaluates response latency. | Weightings are proprietary/expert-derived rather than empirically validated; lacks right-censored survival analysis. | Validates our **RHI composite scoring** and provides comparative benchmark inspiration. |
| **4. OpenDigger** | Open-source ecosystem open collaboration and social network analysis. | GitHub public event archive (GH Archive), GraphQL API. | OpenRank (collaborative PageRank), Developer Activity, Project Attention Index, Contributor network graphs. | Graph algorithms (PageRank, network centralities), time-series event stream analytics. | Advanced topological analysis of cross-project contributor mobility; overcomes simple star counts. | Computationally intensive; complex graph metrics are difficult for general software developers to interpret for intake. | Supports our justification for rejecting naive star counts ($X_1$) in favor of network/turnover measures. |
| **5. deps.dev (Google)** | Understand transitive dependencies, licensing, and supply chain security. | Upstream package managers (npm, PyPI, Maven, Go, Cargo), OpenSSF Scorecard, GitHub advisories. | Dependency depth, direct vs transitive dependencies, licenses, known vulnerabilities (OSV), Scorecard metrics. | Automated dependency resolution graph crawler, cross-referencing package releases with GitHub sources. | Unrivalled visibility into downstream dependency trees; tracks ecosystem impact and license compatibility. | Focuses on package artifacts rather than repository community health; does not analyze PR/issue workflow latency. | Cross-validates our ecosystem sampling strategy (npm, PyPI, crates.io) and dependency health considerations. |
| **6. Yin et al. (2021)** | Empirical investigation of package abandonment and maintainer sustainment in package registries. | npm & PyPI registries, GitHub commit histories. | Commit cessation, maintainer inactivity duration, unmerged pull request pileups, issue responsiveness drops. | Quantitative survival modeling and longitudinal event-history analysis across multi-year observation windows. | Robust empirical definition of maintainer abandonment beyond surface git activity; large package sample. | Focuses on npm/PyPI registry level rather than multi-dimensional repository health intake. | Directly informs our **M1.4 ground-truth definitions** for 12-month dormancy and abandonment. |
| **7. Ashok et al. (2023)** | Investigate contributor turnover, truck factor / bus factor, and maintainer burnout. | GitHub event streams, commit authorship, issue comment threads. | Contributor retention, new committer onboarding rate, Shannon entropy of code contributions, Bus Factor. | Social network analysis, statistical distribution fitting (Lorenz curves, Gini coefficient of authorship). | Rigorous mathematical modeling of knowledge concentration; addresses the single-maintainer vulnerability. | High API data extraction requirement (commit file-level blame); sensitive to bot and automated accounts. | Directly informs our operationalisation of **M30 (Bus Factor)** and **M33/M34 (Turnover)**. |
| **8. Xia et al. (2022/2023)** *(Supporting Paper S6)* | Predict future values of repository health indicators using machine learning. | GHTorrent, GitHub historical activity logs (commits, issues, PRs). | Five primary indicators: commit volume, closed issues, closed PRs, active contributors, response times. | Supervised regression/classification using Random Forests, XGBoost, and hyperparameter optimization (DODGE). | Empirically proves that repository health indicators are predictable from past history using optimized learners. | Retrospective indicator prediction rather than holistic decision support; does not generate qualitative adoption reports. | Provides the core methodological foundation for our **longitudinal predictive validity** ($H_2$). |
| **9. He et al. (2024)** *(Supporting Paper S1)* | Predict open-source project lifespan and deprecation hazard using repository centrality. | 103,354 non-fork GitHub repositories (2011–2023), star interaction graph. | Lifespan (days), HITS centrality (authority/hub scores in repository-user star network), deprecation status. | Semi-parametric survival analysis: Accelerated Failure Time (AFT) and Deep Recurrent Survival Analysis (DRSA). | Demonstrates survival analysis on massive OSS datasets; proves temporal popularity shifts outperform static counts. | Definition of deprecation requires full star edge lists or keyword regex in READMEs (`[FACT]` unfeasible on snapshot APIs). | Directly inspires our **M0.4 / M1.4 survival modeling** (Kaplan-Meier and Cox PH regression). |
| **10. Yehudi et al. (2022)** | Research software sustainability, open science community health, and maintainer well-being. | Qualitative surveys, Zenodo, GitHub metadata in academic software. | Community inclusivity, documentation clarity, citation readiness, licensing, longevity. | Mixed-methods: thematic qualitative coding combined with open repository audit checklists. | Strong focus on human factors, DEI, and long-term research software stewardship. | Qualitative survey data cannot be automated into a CI/CD or real-time intake tool; small academic sample. | Supports our inclusion of Linåker's **Discussion Climate** and **Documentation** aspects (M67). |

---

## 3. Synthesis & Research Gap Analysis

### 3.1 Where Existing Tools Stop Short
1. **Security Tools (OpenSSF Scorecard, deps.dev):** Highly effective at spotting missing branch protection or known CVEs, but blind to whether maintainers take 90 days to review a pull request or whether the project is on the verge of developer burnout.
2. **Metrics Dashboards (CHAOSS / Augur, OSS Compass):** Offer vast catalogues of metrics or composite charts, but do not provide an integrated intake decision framework: they require the adopter to manually weigh and interpret dozens of charts.
3. **Pure Research Papers (Xia et al., He et al., Yin et al.):** Establish foundational survival models and ML prediction accuracy on historical datasets, but exist as offline scripts rather than a modular, interactive developer decision-support platform.

### 3.2 The Unique Positioning of this Platform
Our platform bridges these three silos by combining:
* **M0.1 Metric Registry:** CHAOSS-aligned taxonomy mapped to Linåker's 21 qualitative intake aspects.
* **M0.2 Mining Pipeline:** Public REST API collection with automated pagination and rate-limit resilience.
* **M0.3 Composite Indicators:** Objective normalization and coverage-bounded Repository Health Index (RHI).
* **M0.4 Survival Analysis:** Kaplan-Meier estimation and Cox Proportional Hazards regression for lifespan risk.
* **M0.5 Evidence-Grounded AI Reports:** Synthesis of quantitative indicators into defensible, grounded adoption verdicts without hallucination.

---
*End of Document M1.3 — Related-Work Matrix.*

