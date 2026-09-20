# Measurement & Formula Design

**Project:** AI-Assisted Developer Decision Support and Repository Intelligence Platform (Batch CSM-B2)
**Task:** Measurement & Formula Design — the step between the Dataset Feasibility Study and any model training
**Date:** 2026-08-31
**Status:** Research design only. No model trained, no backend or frontend started, no dataset modified.

**Inputs used:**
- `BasePaper.pdf`, `S1.pdf`–`S5.pdf` in `C:\Users\rajes\Downloads\MajorProject\` (read directly, not summarised from memory)
- `CSM_B2_ABSTRACT.pdf` — the project registration form
- [dataset-feasibility-report.md](dataset-feasibility-report.md)
- [health-assessment-framework.md](health-assessment-framework.md)

---

## Evidence Legend

| Tag | Meaning |
|---|---|
| **[FACT]** | Explicitly stated in a named paper, at a locatable place in it. |
| **[DERIVED]** | Directly calculated from a paper's stated definition, or computed by us from the dataset. |
| **[REC]** | Our recommendation. A judgement call. |
| **[ASSUME]** | An assumption, stated so it can be challenged. |

A **[REC]** is never presented as a paper's claim. Where a paper is silent, this document says so.

---

## 0. Two Source Discrepancies Found Before Any Design Work

These must be resolved before the paper is written, because both affect citation correctness.

### 0.1 The base paper is Linåker et al., not Xia et al.

**[FACT]** `CSM_B2_ABSTRACT.pdf` page 2, "References (Category specific)", lists:

> **1. Base Paper** — *Assessing Open Source Software Health in Organizations' Intake Processes: A
> Qualitative Study on the Practitioners' Perspective.* Linåker, Olsson, Papatheocharous. 2026.
> Springer, Empirical Software Engineering.

**[FACT]** Xia, Fu, Shu, Agrawal, Menzies — *Predicting Health Indicators for Open Source Projects
(using Hyperparameter Optimization)* — appears in the same list as **Supporting Paper 6**, not as
the base paper.

**[FACT]** `BasePaper.pdf` is Linåker et al. 2026, EMSE 31:105, DOI `10.1007/s10664-026-10846-y`.

**[DERIVED]** The existing [health-assessment-framework.md](health-assessment-framework.md) (Step 1A)
names Xia et al. as the base paper throughout §2. **That document is inconsistent with the
registration form and needs correction.** Step 1A was written before the registration form was
available; the framework's dimension definitions remain valid, but its "Relationship to Base Paper"
section attributes the foundation to the wrong paper.

**[REC]** Correct Step 1A §2 to treat Linåker et al. as the base paper and Xia et al. as the
methodological supporting paper. This document uses the registration form's assignment.

### 0.2 Two source files do not match the reference list

**[FACT]**

| File | Actual content | Registration-form reference |
|---|---|---|
| `BasePaper.pdf` | Linåker, Olsson, Papatheocharous 2026 | **Base Paper** ✓ |
| `S1.pdf` | He, Ye, Zhou — *Repository Centrality in Lifespan Prediction* | Supporting 2 ✓ |
| `S2.pdf` | Alami, Pardo, Linåker 2024 — *FOSS Communities Sustainability* | Supporting 3 ✓ |
| `S3.pdf` | Tamburri, Palomba, Serebrenik, Zaidman 2019 — *YOSHI* | Supporting 4 ✓ |
| `S4.pdf` | Kaushik, Chahal — *Community Engagement and Lifespan* | Supporting 5 ✓ |
| `S5.pdf` | Xiao, He, Xu, Zhang, Zhou — *How Early Participation Determines Long-Term Sustained Activity* | **not in the list** |
| *(missing)* | Xia et al. — *Predicting Health Indicators* | **Supporting 6 — no PDF present** |

**[FACT]** No file named `BasePaper(2).pdf` exists; the file is `BasePaper.pdf`.

**[REC]** Either add S5 to the reference list or drop it from the source set, and obtain the Xia et
al. PDF. This document cites S5 where it is genuinely used and **makes no claims about Xia et al.
beyond the title and framing given in the registration form**, because the paper itself was not
available to read.

---

# STEP 1 — Review of the Research Sources

## 1.1 The base paper's structure

**[FACT]** Linåker et al. conducted a **qualitative interview survey with 17 industry experts**,
mapped the results against the CHAOSS and OpenSSF Scorecard frameworks, and validated a subset in a
case study at a large automotive manufacturer.

**[FACT]** The output is **21 health aspects and 72 metrics across 5 areas** (Fig. 2, p. 11):

```
Areas of Health          Health aspects                          Metrics
─────────────────────────────────────────────────────────────────────────────
Community productivity   Social activity                         M1  – M4
                         Responsiveness                          M5  – M7
                         External visibility                     M8  – M9
                         Development activity                    M10 – M13
                         Development efficiency                  M14 – M17
Community stability      Adoption                                M18 – M20
                         Organizational diversity                M21 – M23
                         Demographic diversity                   M24 – M25
                         Discussion climate                      M26 – M29
                         Knowledge concentration                 M30 – M32
                         Contributor turnover                    M33 – M35
                         Financial sustainability                M36 – M37
Orchestration            Governance structure                    M38 – M41
                         Openness                                M42 – M44
                         Licenses                                M45 – M48
Production process       Development process                     M49 – M52
                         Release management                      M53 – M57
                         Security management                     M58 – M63
                         Scaffolding                             M64 – M66
Production output        Documentation                           M67 – M69
                         Technical quality                       M70 – M72
```

**[FACT]** Supporting evidence from prior literature was found for **61 of the 72 metrics**; the 11
without support were spread across 7 aspects, with Licensing, Security and Adoption having 2 each
(p. 12).

### 1.1.1 ⚠ The base paper contains no mathematical formulas

**[FACT]** Appendix A gives each of the 72 metrics a **name and a prose definition** plus framework
and literature cross-references. It gives **no equations, no thresholds, no units, no aggregation
rules, and no weights**. This is a property of the study design — it is a qualitative interview
survey, not a measurement paper.

**[DERIVED]** Therefore **every formula in this project is either adopted from a supporting paper,
derived from a base-paper definition, or our own proposal.** No formula can be attributed to the
base paper. This is the single most important constraint on how the research contribution is
claimed.

**[FACT]** The base paper additionally identifies **four project traits that moderate how metrics
should be interpreted and compared**: life-cycle stage, project complexity, governance
concentration, and strategic importance to the assessing organisation (p. 9). It also concludes
that "not all aspects and metrics may be leveraged due to resource constraints and complexity.
Instead, subsets of metrics need to be prioritized" (Abstract).

## 1.2 Base-paper metrics relevant to our dataset

**[FACT]** Verbatim definitions from Appendix A. `[C]` = also in CHAOSS, `[O]` = also in OpenSSF
Scorecard.

| ID | Metric name | Definition (Appendix A) | Aspect | Frameworks |
|---|---|---|---|---|
| **M5** | General Responsiveness | "The timeliness and quality of responses to, e.g., new discussion questions, pull requests, or issues" | Responsiveness | [C] |
| M7 | Maintainer Reactivity | "The responsiveness of the maintainer in contrast to the rest of the community" | Responsiveness | [C] |
| **M9** | Project Popularity | "The project's external visibility signaled through various popularity indicators, e.g., stars and followers on GitHub, or downloads from the package manager" | External visibility | [C] |
| **M10** | Code Activity | "The contribution activity to the code base over time, **e.g., last 45, 90, and 365 days**" | Development activity | [C, O] |
| **M11** | Review Throughput | "The activity in development-related activities, such as **code reviews, merging of PRs, and actions on issues over equal periods of time**" | Development activity | [C] |
| M12 | Non-code Activity | "The activity in contributions to non-code tasks, e.g., documentation, test cases, and release management activities" | Development activity | [C] |
| M13 | Role Balance | "The different types of activities in contrast between the maintainer(s), long-term contributors, and drive-by contributors" | Development activity | [C] |
| **M14** | Issue Load | "The size and evolution of the project's backlog in terms of open and unresolved issues" | Development efficiency | [C] |
| **M15** | Issue Turnover | "The pace in how issues are being addressed and closed and **PRs merged**" | Development efficiency | [C] |
| M16 | Bug Handling | "The corresponding responsiveness towards bugs and security-related issues and PRs" | Development efficiency | [C] |
| M17 | Release Tempo | "The cadence and timeliness at which releases are made and planned" | Development efficiency | [C] |
| **M20** | Popularity | "The project's adoption signaled through various popularity indicators, e.g., stars and followers on GitHub, or downloads from the package manager" | Adoption | [C] |
| M30 | Bus Factor | "The number of individuals doing most of the development in the project (i.e., bus factor), e.g., in terms of 50 and 80 percent" | Knowledge concentration | [C] |
| M33 | Newcomer Rate | "The number of new contributors attracted to the community over time, e.g., last 45, 90, and 365 days" | Contributor turnover | [C] |
| M34 | Retention Rate | "The number of new contributors that have made recurrent contributions… over the same periods" | Contributor turnover | [C] |
| **M42** | External Openness | "The openness for external contributions" | Openness | [C] |
| M43 | Volunteer Inclusion | "The extent contributions beyond maintainers and long-term contributors are accepted, e.g., from episodic volunteers" | Openness | [C] |
| M45 | License Type | "The types of OSS licenses the project is published under" | Licenses | [C, O] |
| M57 | Release Rhythm | "The cadence and consistency of releases" | Release management | [C] |
| M60 | PR Checks | "The review and quality assurance practices for pull requests" | Security management | [C] |
| M65 | Test Coverage | "Presence of a functioning test automation, and the test coverage of the project" | Scaffolding | [C] |
| M67 | Tech Docs | "The technical documentation of deliverables, including source code and releases…" | Documentation | [C] |

**[FACT]** The **45 / 90 / 365-day windows** appear twice in the base paper (M10 and M33) and again
in Table 3, where the case company prioritised: *"The contribution activity to the code base over
time, e.g., last 45, 90, and 365 days"* and *"The activity in development-related activities, such
as code-reviews, merging of PRs, and actions on issues over equal periods of time."*

**[DERIVED]** These are the only concrete quantitative parameters the base paper supplies. Our
time-window choice is therefore traceable to the base paper rather than arbitrary.

## 1.3 Supporting paper S2 — the only source with actual formulas

**[FACT]** Alami, Pardo, Linåker (2024), EMSE 29:114. Sampled **16 sustainability metrics across
four themes** (Communication, Popularity, Stability, Technical), applied to **217 Apache Software
Foundation Incubator projects**, analysed against 8 software-quality metrics using Bayesian data
analysis.

**[FACT]** Its Table 2 credits the parameter definitions to Linåker et al. (2022) — the base
paper's own earlier literature survey. **Table 4 gives the computation formulas.** Notation: `I` =
issues, `C` = comments, `PR` = pull requests, `CM` = commits, `F`/`S`/`W` = forks/stars/watchers,
`r` = repository.

| ID | Parameter | Formula (Table 4) | Computable on our data? |
|---|---|---|---|
| COM-1 | Response time | `Σ_{i∈I}(time(c¹ᵢ) − time(i)) / \|I\|` | ✗ no comments |
| COM-2 | Frequency of communication | `\|C\| + \|I\|` | ~ partial — `\|I\|` only |
| **POP-1** | Project popularity | `\|F\| + \|S\| + \|W\|` | ~ partial — no watchers |
| **STA-1** | Age | `2023 − year(r)` | ✓ **yes** |
| STA-2 | Attrition | commit deltas over 12-week periods | ✗ no commits |
| **STA-3** | Forks | `\|F\|` | ✓ yes |
| **STA-4** | Growth | `Σ Incs`, `Incs = {\|PR_{t+1}\| − \|PR_t\|}` over 12-week periods | ✓ **yes** |
| STA-5 | Knowledge concentration | Avelino et al. (2016) truck-factor algorithm | ✗ no authors |
| STA-6 | Life-cycle stage | commit-count condition | ✗ no commits |
| STA-7 | Retention | active-contributor deltas | ✗ no authors |
| STA-8 | Size | `\|contributors(CM) ∪ contributors(PR) ∪ …\|` | ✗ no authors |
| STA-9 | Turnover | contributors with commits < 6 months before end | ✗ no authors |
| TEC-1 | Contributors' dev. activity | contributors not in mergers(PR) | ✗ no authors |
| **TEC-2** | **Efficiency** | `Σ_{t∈T} t / \|PR\|`, `T = {time_merged/closed(pr) − time(pr)}` | ✓ **yes — exactly** |
| TEC-3 | Non-code contributions | commits touching doc files | ✗ no commits |
| TEC-4 | Overall development activity | commits touching code files | ✗ no commits |

**[FACT]** S2 restates TEC-2 in prose (p. 17): *"TEC-2 (efficiency) measures the time elapsed from
PR creation until it is merged or closed"*, and in Table 2: *"We measured the average time from PR
creation to its closure to reflect the project's operational effectiveness."*

**[DERIVED]** **TEC-2 is the one formula in the entire source set that our dataset can implement
exactly as published.** Its inputs are `pr.created_at`, `pr.merged_at`, `pr.closed_at` — all present
and verified exact in the feasibility report.

**[FACT]** S2's empirical result was largely **null**: "selected sustainability metrics do not
significantly affect defect density or code coverage", with a positive effect of community age on
some code-quality metrics.

**[DERIVED]** S2 therefore supports these metrics as **operational definitions**, not as validated
predictors of quality. We may cite it for *how to compute*, not for *this metric predicts health*.

## 1.4 Supporting paper S4 — normalisation and two named ratio metrics

**[FACT]** Kaushik & Chahal, *Information and Software Technology*. Analysed **33,946 GitHub
repositories**.

**[FACT]** Normalisation formula, stated explicitly:

```
CPM = commits / (active_lifespan_days / 30.44)
```

with active lifespan defined as "the period between a repository's `createdAt` and `lastCommit`
timestamps, measured in days and converted into months using an average of 30.44 days per month."
Projects with zero-day lifespan were excluded.

**[FACT]** S4 names two ratio metrics and **explicitly excludes them from lifespan normalisation**:

> "Metrics that represent ratios, such as **Pull Request Acceptance Rate (PRAR)** and **Issue
> Resolution Rate (IRR)**, were excluded from lifespan normalization."

- **PRAR**: "A high rate suggests active maintainer participation and inclusive contribution practices."
- **IRR**: "Reflects effectiveness in managing and resolving reported problems, promoting sustained contributor involvement."

**[FACT]** S4 documents the failure mode of per-month normalisation: "the maximum values of several
metrics were inflated due to the normalization process. For example, commits per month (CPM) reaches
11,794,250.0000, exceeding the raw commit count maximum of 692,245… repositories with extremely
short lifespans (e.g., 10–15 days) and high commit activity yield inflated per-month rates."

**[FACT]** S4 also reports that skew persists after normalisation: "most accumulated attributes, when
expressed as per-month rates, still exhibited a high concentration towards lower values… suggesting a
**Pareto-like distribution** even for per-month metrics."

**[FACT]** S4's exploratory factor analysis found **two latent engagement dimensions**:
- **Passive Engagement** = Watchers per month + Stargazers per month
- **Active Engagement** = Total Issues per month + Issue Comments per month

**[DERIVED]** S4 supplies our normalisation method, two of our ratio metrics by name, a documented
warning about the method's failure mode, and empirical evidence that a data-driven grouping of
engagement metrics is achievable — but only at n ≈ 34,000.

## 1.5 Supporting paper S1 — deprecation, not usable here

**[FACT]** He, Ye, Zhou. 103,354 non-fork GitHub projects, 2011–2023. Proposes **repository
centrality**, "a family of HITS (Hyperlink-Induced Topic Search) weights that captures shifts in
the popularity of a repository in the repository-user star network", and fits survival-analysis
models (AFT, DRSA) to predict lifespan and hazard.

**[FACT]** Operational definition of deprecation (§III-A): a repository is deprecated if **either**
(a) it is archived on GitHub, **or** (b) it "has deprecation-indicating keywords in its README or
description".

**[DERIVED]** Neither criterion is computable here. Our `stale` column is constant `False`, there is
no `archived` field, and no README text. The HITS centrality metric requires a user→repository star
edge list, which we do not have — our data has star *counts*, not star *events with users*.

**[REC]** Cite S1 for the framing that deprecation risk is predictable and time-varying, and for the
argument that point-in-time features are weaker than temporal ones. Do **not** claim to implement
repository centrality.

## 1.6 Supporting paper S5 — a target definition we cannot yet compute

**[FACT]** Xiao, He, Xu, Zhang, Zhou, ESEC/FSE 2023. XGBoost + LIME on **290,255 GitHub projects**,
predicting two-year sustained activity from the first three months of participation, **AUC up to
0.84**.

**[FACT]** Definition: *"we consider a project as having t-year sustained activity if 1) they have
commit activity for more than t year(s), and 2) the median number of commits per month is at least
k."* Used with **t = 2, k = 1**. They note it is "inadequate to measure the sustained activity of a
project with only the first and last commits" because abandoned projects often restart.

**[DERIVED]** Commit-based, so not computable on our dataset. But the **shape** of the definition —
a duration condition **and** an intensity condition — is a template we can adapt to PR events. Any
such adaptation is ours, not S5's.

## 1.7 Supporting paper S3 — not usable here

**[FACT]** Tamburri, Palomba, Serebrenik, Zaidman (2019), EMSE 24:1369–1417. The **YOSHI** tool maps
communities onto community patterns using six characteristics: **community structure, geodispersion,
longevity, engagement, formality, cohesion**. Evaluated on 25 GitHub communities.

**[DERIVED]** Five of the six require contributor identity, location, or communication content.
None is computable from our three files. S3 supports the *conceptual* claim that community structure
matters for health; it contributes no implementable metric to this prototype.

## 1.8 Supporting paper 6 (Xia et al.) — not read

**[FACT]** No PDF present. **[REC]** No metric, formula, target, or empirical claim in this document
is attributed to Xia et al. It is cited only as the registration form describes it: an ML approach
to predicting health indicators. Obtain and read it before the paper's methodology section is
written.

---

# STEP 2 — Cross-Check Against Our Actual Dataset

**[FACT]** Available columns, from [dataset-feasibility-report.md](dataset-feasibility-report.md):

- `repo_data.csv` (28 rows): `id, created, updated, created_at, description, forks, full_name, name, open_issues, stars, updated_at, repository, issue_contributors, pr_contributors, total_contributors, size_category, stale, stars_per_fork, stars_per_issue, contributor_per_star`
- `issues_data.csv` (7,082 rows): `id, created, updated, closed_at, created_at, number, repository, state, title, updated_at, resolution_time_days`
- `pr_data.csv` (248,320 rows): `id, created, updated, closed_at, created_at, merged_at, number, repository, state, title, updated_at, merge_time_days`

**[FACT] Excluded by prior finding.** `issue_contributors`, `pr_contributors`, `total_contributors`
and `contributor_per_star` count **distinct issue/PR titles**, verified 28/28 exact. They are used
nowhere in this design as contributor measures.

## 2.1 Candidate metric feasibility

| Candidate metric | Source | Required columns | Available | Calculable | Level | Blocking gap |
|---|---|---|---|---|---|---|
| PR acceptance rate | S4 PRAR; BP M42, M15 | `pr.state` | ✓ | **Full** | Repository | — |
| PR resolution efficiency | **S2 TEC-2** | `pr.created_at, merged_at, closed_at` | ✓ | **Full** | Repository | — |
| PR resolution latency (median) | BP M5 | `pr.merge_time_days` | ✓ | **Full** | Repository | — |
| PR backlog ratio | BP M14 (PR analogue) | `pr.state` | ✓ | **Full** | Repository | — |
| Issue resolution rate | S4 IRR; BP M15 | `issues.state` | ✓ | **Full** | Repository | — |
| Issue resolution latency | BP M5, M15 | `issues.resolution_time_days` | ✓ | **Full** | Repository | — |
| Review throughput (45/90/365 d) | **BP M11 + M10 windows** | `pr.created_at` | ✓ | **Partial** | Repository | sampling caps truncate history |
| Development activity trend | **S2 STA-4** | `pr.created_at` | ✓ | **Partial** | Repository | needs ≥ 2 twelve-week intervals |
| Repository age | **S2 STA-1** | `repo.created_at` | ✓ | **Full** | Repository | — |
| Forks | S2 STA-3 | `repo.forks` | ✓ | **Full** | Repository | — |
| Project popularity | S2 POP-1 | `forks + stars + watchers` | ~ | **Partial** | Repository | **no watchers column** |
| Communication frequency | S2 COM-2 | `\|C\| + \|I\|` | ~ | **Partial** | Repository | no comments |
| Response time | S2 COM-1 | first-comment timestamp | ✗ | **No** | — | no comment data |
| Commits per month | S4 CPM | commit log | ✗ | **No** | — | no commit data |
| Contributors per month | S4 CNT/m | author field | ✗ | **No** | — | **no author column** |
| Watchers / Stargazers per month | S4 WT/m, STR/m | time series | ✗ | **No** | — | snapshot only |
| Bus factor | BP M30; S2 STA-5 | author per commit | ✗ | **No** | — | no author column |
| Newcomer / retention rate | BP M33, M34; S2 STA-7 | author + first-seen | ✗ | **No** | — | no author column |
| Bug handling | BP M16 | issue labels | ✗ | **No** | — | no labels |
| Release rhythm / tempo | BP M17, M57 | release/tag data | ✗ | **No** | — | not collected |
| License type | BP M45 | license field | ✗ | **No** | — | **no license column** |
| Tech / process / onboarding docs | BP M67–M69 | repo file tree | ✗ | **No** | — | not collected |
| Test coverage, CI/CD | BP M64, M65 | workflow config | ✗ | **No** | — | not collected |
| Repository centrality (HITS) | S1 | user→repo star edges | ✗ | **No** | — | star counts only, no user edges |
| Community structure / geodispersion | S3 YOSHI | author identity + location | ✗ | **No** | — | no author column |
| t-year sustained activity | S5 | commit log | ✗ | **No** | — | no commit data |
| Deprecation label | S1 | `archived` or README | ✗ | **No** | — | `stale` constant False |

**[DERIVED]** **12 candidates are calculable (9 fully, 3 partially); 16 are not.** Every blocked
candidate is blocked by a *missing column*, not by a modelling choice.

## 2.2 Calculation level

**[DERIVED]** A structural point that governs the whole prototype:

| Level | Rows available | What it can support |
|---|---:|---|
| **PR / issue event level** | 248,320 PRs + 7,082 issues | Model training, validation, generalisation claims |
| **Repository level** | 28 | Descriptive dashboards, worked examples — **not** model training |

All metrics in this document are **repository-level aggregates**. The ML target (Step 10) is
**event-level**. These are two different tables and must not be conflated.

---

# STEP 3 — Metric Selection Table

**[DERIVED]** Master table. "Formula from source" is `—` wherever the source gives a construct but
no equation, which is the case for every base-paper metric.

| ID | Health Dimension | Metric | Definition | Research Source | Formula from Source | Required Data | Available? | Calculation Level | Prototype Status | Reason |
|---|---|---|---|---|---|---|---|---|---|---|
| **A1** | 3 Issue & PR | PR Acceptance Rate | Share of decided PRs that were merged | **S4 (PRAR)**; BP M42, M15 | Named, no equation | `pr.state` | YES | Repository | **SUPPORTED** | State field complete, 3-valued, verified consistent |
| **A2** | 3 Issue & PR | PR Resolution Efficiency | Mean time from PR creation to merge or close | **S2 TEC-2** | **`Σt/\|PR\|`, `T={t_merged/closed − t_created}`** | `pr.created_at, merged_at, closed_at` | YES | Repository | **SUPPORTED** | Only exactly-reproducible published formula in the source set |
| **A3** | 3 Issue & PR | PR Resolution Latency | **Median** time from creation to merge/close | BP M5 (construct) | — | same as A2 | YES | Repository | **SUPPORTED** | Robust companion to A2; justified by measured skew |
| **A4** | 3 Issue & PR | PR Backlog Ratio | Share of all PRs still open | BP **M14** (PR analogue) | — | `pr.state` | YES | Repository | **SUPPORTED** | M14 is stated for issues; PR application is our extension |
| **A5** | 3 Issue & PR | Issue Resolution Rate | Share of issues closed | **S4 (IRR)**; BP M15 | Named, no equation | `issues.state` | YES | Repository | **SUPPORTED** | Complete for 22 of 28 repos |
| **A6** | 3 Issue & PR | Issue Resolution Latency | Median days from issue open to close | BP M5, M15 | — | `issues.resolution_time_days` | YES | Repository | **SUPPORTED** | Verified exact; `-1` sentinel handled |
| **A7** | 1 Dev & Maint. | Review Throughput | PR events created within 45 / 90 / 365 days | BP **M11** + **M10** windows | — (windows given) | `pr.created_at` | YES | Repository | **PARTIALLY SUPPORTED** | Sampling caps truncate history for 9 repos |
| **A8** | 1 Dev & Maint. | Development Activity Trend | Net change in PR volume across 12-week intervals | **S2 STA-4** | **`Σ Incs`, `Incs={\|PR_{t+1}\|−\|PR_t\|}`** | `pr.created_at` | YES | Repository | **PARTIALLY SUPPORTED** | Undefined for 4 repos with < 2 intervals observed |
| **C1** | *(context)* | Repository Age | Years/days from creation to snapshot | **S2 STA-1** | **`2023 − year(r)`** | `repo.created_at` | YES | Repository | **SUPPORTED (context)** | A moderator, not a health score — BP lists life-cycle stage as a trait, not an aspect |
| **C2** | *(context)* | PR Capture Rate | Rows present ÷ highest PR number observed | *ours* | — | `pr.number` | YES | Repository | **SUPPORTED (context)** | Required to make A7/A8 interpretable |
| **X1** | 4 Popularity | Project Popularity (partial) | `stars + forks` | **S2 POP-1** (modified) | **`\|F\|+\|S\|+\|W\|`** | `repo.stars, forks` | PARTIAL | Repository | **PARTIALLY SUPPORTED** | **Watchers column absent** — cannot implement POP-1 as published |
| N1 | 2 Contributor | Bus Factor | Individuals doing most development | BP M30; S2 STA-5 | Avelino et al. (2016) | author per commit | NO | — | **NOT SUPPORTED** | No author column anywhere |
| N2 | 2 Contributor | Newcomer Rate | New contributors per window | BP M33 | — | author + first-seen | NO | — | **NOT SUPPORTED** | No author column |
| N3 | 2 Contributor | Retention Rate | Newcomers making recurrent contributions | BP M34; S2 STA-7 | contributor deltas | author + history | NO | — | **NOT SUPPORTED** | No author column |
| N4 | 2 Contributor | Contributor Diversity | Organisations represented among contributors | BP M22 | — | author + affiliation | NO | — | **NOT SUPPORTED** | No author column |
| N5 | 1 Dev & Maint. | Code Activity | Commits over 45/90/365 days | BP **M10**; S2 TEC-4 | commit counts | commit log | NO | — | **NOT SUPPORTED** | **No commit data — M10 cannot be implemented despite being a prioritised base-paper metric** |
| N6 | 3 Issue & PR | Response Time | Time to first comment on an issue | **S2 COM-1** | **`Σ(time(c¹ᵢ)−time(i))/\|I\|`** | comment timestamps | NO | — | **NOT SUPPORTED** | No comment data |
| N7 | 3 Issue & PR | Bug Handling | Responsiveness to bug/security issues | BP M16 | — | issue labels | NO | — | **NOT SUPPORTED** | No labels; title keywords unreliable |
| N8 | 1 Dev & Maint. | Release Rhythm | Cadence and consistency of releases | BP M17, M57 | — | release/tag data | NO | — | **NOT SUPPORTED** | Not collected |
| N9 | 5 Sustainability | Deprecation Status | Archived, or README deprecation keywords | **S1 §III-A** | Archived ∨ keyword | `archived`, README | NO | — | **NOT SUPPORTED** | `stale` constant False; no README |
| N10 | 5 Sustainability | Sustained Activity | ≥ t years activity ∧ median commits/month ≥ k | **S5** | **`t=2, k=1`** | commit log | NO | — | **NOT SUPPORTED** | No commit data |
| N11 | 5 Sustainability | Repository Centrality | HITS weights on user–repo star network | **S1** | HITS | star *events* with user ids | NO | — | **NOT SUPPORTED** | We have star counts, not star edges |
| N12 | — | Community Structure / Geodispersion | YOSHI community characteristics | **S3** | Observability functions δ | author identity + location | NO | — | **NOT SUPPORTED** | No author column |
| N13 | 5 Sustainability | License Type | OSS licence the project is published under | BP M45 | — | licence field | NO | — | **NOT SUPPORTED** | No licence column |
| N14 | — | Documentation Quality | Tech / process / onboarding docs | BP M67–M69 | — | repo file tree | NO | — | **NOT SUPPORTED** | Not collected |
| N15 | 4 Popularity | Star / Fork Growth | Change in stars and forks over time | BP M9, M20; S4 STR/m | per-month rate | star time series | NO | — | **NOT SUPPORTED** | Single snapshot |
| N16 | 2 / 4 | Passive vs Active Engagement | S4's two EFA factors | **S4** | EFA loadings | watchers, comments | NO | — | **NOT SUPPORTED** | Watchers and comments both absent |

**[DERIVED] Totals: 10 SUPPORTED (8 metrics + 2 context), 2 PARTIALLY SUPPORTED, 16 NOT SUPPORTED.**

---

# STEP 4 — Selected Prototype Metrics

**[REC]** **Eight metrics, two context variables, one descriptive-only variable.** This is
deliberately smaller than the feasible set. Three feasible candidates were **rejected**, with
reasons given in §4.2 — a metric being computable is not sufficient grounds to include it.

## 4.1 The selected set

| ID | Metric | Dimension | Why selected |
|---|---|---|---|
| **A1** | PR Acceptance Rate | 3 | Named metric in S4 (PRAR); operationalises base-paper **M42 External Openness** and part of **M15 Issue Turnover**. Bounded [0,1], needs no normalisation, manually checkable by counting three state values. Zero dependence on any defective column. |
| **A2** | PR Resolution Efficiency | 3 | **The only formula in the entire source set we can reproduce exactly as published** (S2 TEC-2). Its research provenance is unambiguous, which matters more for the paper than its statistical behaviour. |
| **A3** | PR Resolution Latency (median) | 3 | Included *because* A2's mean is unstable on our data (§4.3). Reporting both makes the instability visible instead of hiding it. Operationalises **M5 General Responsiveness**. |
| **A4** | PR Backlog Ratio | 3 | Base-paper **M14 Issue Load** defines backlog as "the size and evolution of the project's backlog in terms of open and unresolved issues". Applying it to PRs is our extension, marked as such. Bounded [0,1]. |
| **A5** | Issue Resolution Rate | 3 | Named metric in S4 (IRR); operationalises **M15 Issue Turnover**. Bounded [0,1]. Directly comparable to A1, giving the dimension a symmetric PR/issue structure. |
| **A6** | Issue Resolution Latency (median) | 3 | Issue-side counterpart of A3. Column verified exact to 10⁻¹² in the feasibility study. |
| **A7** | Review Throughput | 1 | The **closest available proxy** to base-paper M11, using the M10 windows. Included with a mandatory capture-rate caveat, because Dimension 1 would otherwise have no representation at all. |
| **A8** | Development Activity Trend | 1 | S2 **STA-4** supplies a published formula, and it is the only metric in the set that measures *change over time* rather than a level. S1's central argument is that point-in-time features are weaker than temporal ones. |

| ID | Context variable | Why |
|---|---|---|
| **C1** | Repository Age (S2 STA-1) | The base paper names life-cycle stage as one of four **traits that moderate interpretation**, not as a health aspect. Age is therefore a covariate, never a score component. |
| **C2** | PR Capture Rate | Without it, A7 and A8 are uninterpretable. It is a data-quality variable that must travel with every repository row. |

| ID | Descriptive only | Why not a prototype metric |
|---|---|---|
| **X1** | Project Popularity (`stars + forks`) | S2 POP-1 is `\|F\|+\|S\|+\|W\|`; **we cannot implement it — there is no watchers column**. Reporting a two-of-three variant under the name "POP-1" would misattribute. Also a snapshot with n = 28, and a known leakage co-signal. Displayed on the dashboard, **excluded from RHI and from all ML features**. |

## 4.2 Feasible candidates deliberately rejected

**[REC]**

| Rejected | Computable? | Why excluded |
|---|---|---|
| **Activity Recency** (days since last PR) | Yes | **[FACT]** Observed range 0–17 days across all 28 repos. Near-zero variance — every repository in this sample is currently active. A metric that cannot separate any two repositories in the sample contributes nothing and would create a false impression that abandonment detection is being demonstrated. |
| **p90 Time-to-Merge** | Yes | Adds a third latency measure to a set that already has A2 and A3. No independent research source names a tail-latency metric. Redundant. |
| **Star-to-Fork Ratio** | Yes | **[DERIVED]** Perfectly collinear with `stars` and `forks` together; adds no information. Already present as a precomputed column. No source names it. |
| **Communication Frequency** (S2 COM-2) | Partially | The formula is `\|C\|+\|I\|`. With `\|C\|` unavailable it degenerates to "count of issues", which is not what COM-2 measures. Implementing half a formula under its published name would be a misattribution. |

## 4.3 Evidence for including both A2 and A3

**[DERIVED]** Computed on all 28 repositories. S2's TEC-2 specifies the **mean**. Our data:

| Repository | A2 mean (days) | A3 median (days) | mean ÷ median |
|---|---:|---:|---:|
| `linux` | 114.06 | 0.02 | **5,298×** |
| `guava` | 3.40 | 0.02 | 172× |
| `flask` | 25.07 | 0.18 | 137× |
| `numpy` | 45.24 | 0.69 | 65× |
| `react` | 39.33 | 0.74 | 53× |
| *(all 28: median ratio)* | | | **13.4×** |

**[DERIVED]** The mean exceeds the median by more than an order of magnitude for the typical
repository in this sample. TEC-2 as published is a valid operational definition but a **fragile
estimator on heavy-tailed PR data**.

**[REC]** Report **both**: A2 for research traceability (Category A, exactly as S2 specifies), A3 as
the robust variant (Category C, ours). Use **A3** in any dimension score. State the discrepancy in
the paper — it is a genuine, quantified methodological finding, not a criticism of S2, whose 217 ASF
Incubator projects differ substantially from our 28 flagship projects.

---

# STEP 5 — Measurement Method

Notation used throughout. For repository `r`:

- `PR(r)` = all PR rows with `repository = r`; `I(r)` = all issue rows with `repository = r`
- `state(p) ∈ {merged, closed, open}` for PRs; `state(i) ∈ {closed, open}` for issues
- `S` = snapshot instant = **2024-09-06 11:30:17 UTC** = `max(repo_data.updated_at)`
- `NaN` denotes *undefined*, never zero

---

### A1 — PR Acceptance Rate (PRAR)

**Metric.** The proportion of pull requests that reached a decision and were accepted.

**Raw data.** `pr_data.csv` → `repository`, `state`

**Unit.** ratio, bounded [0, 1] **Aggregation.** per repository **Time window.** all observed history

**Formula.**
```
PRAR(r) = |{p ∈ PR(r) : state(p) = merged}|
          ─────────────────────────────────────────────
          |{p ∈ PR(r) : state(p) ∈ {merged, closed}}|
```

**Interpretation.** High = contributions are usually accepted; the project is open to external
input. Low = most contributions are declined, or the project does not use GitHub PRs for real review.

**Direction.** **Context-dependent.** Higher generally indicates openness (base paper M42), but a
value near 1.0 can equally indicate absent review. **[REC]** Never treat this as monotonically
"higher is healthier" without pairing it with A2/A3.

**Edge cases.**
| Condition | Behaviour |
|---|---|
| `PR(r)` empty | `NaN` — **[FACT]** occurs for `streamlit` |
| No decided PRs (all open) | `NaN` (zero denominator) — **[FACT]** occurs for 0 of 28 repos |
| Project does not use GitHub PRs | Returns a valid but misleading near-zero value — **[FACT]** `httpd` 0.0000, `git` 0.0012, `linux` 0.0193. **[REC]** Flag repositories with PRAR < 0.05 for manual review rather than scoring them. |

---

### A2 — PR Resolution Efficiency (S2 TEC-2)

**Metric.** Mean elapsed time from PR creation to the moment it was merged or closed.

**Raw data.** `pr_data.csv` → `created_at`, `merged_at`, `closed_at`

**Unit.** days **Aggregation.** per repository **Time window.** all observed history

**Formula.** *(S2 Table 4, TEC-2, verbatim)*
```
             Σ_{t ∈ T} t
PRE(r) = ─────────────────      T = { end(p) − created_at(p) : p ∈ PR(r), end(p) ≠ null }
              |T|

where end(p) = merged_at(p) if merged_at(p) ≠ null, else closed_at(p)
```

**Interpretation.** Lower = PRs are dispositioned quickly. Higher = contributions sit unresolved.

**Direction.** **Lower is healthier.**

**Edge cases.**
| Condition | Behaviour |
|---|---|
| No PR has ended (all open) | `NaN` — **[FACT]** 0 of 28 repos |
| `PR(r)` empty | `NaN` — `streamlit` |
| Open PRs | **Excluded from `T`** (they have no end). **[REC]** This makes PRE survivorship-biased: a project that never closes anything looks fast. Always report alongside A4. |
| Extreme tail | **[DERIVED]** max observed 2,031 days for a single PR; drives the mean (§4.3) |

---

### A3 — PR Resolution Latency (median variant)

**Metric.** Median elapsed time from PR creation to merge or close.

**Raw data.** identical to A2 **Unit.** days **Aggregation.** per repository

**Formula.**
```
PRL(r) = median( { end(p) − created_at(p) : p ∈ PR(r), end(p) ≠ null } )
```

**Interpretation / Direction.** As A2. **Lower is healthier.**

**Edge cases.** As A2. **[DERIVED]** Observed range 0.0198 d (`guava`) to 17.31 d (`httpd`) — a
900× spread, versus a 74× spread for the mean, because the median is not dragged by the tail.

---

### A4 — PR Backlog Ratio

**Metric.** Proportion of all observed PRs still awaiting a decision.

**Raw data.** `pr_data.csv` → `state` **Unit.** ratio [0,1] **Aggregation.** per repository

**Formula.**
```
PBR(r) = |{p ∈ PR(r) : state(p) = open}| / |PR(r)|
```

**Interpretation.** High = contributions accumulate unreviewed; the base paper's M14 warns that "a
growing backlog of unaddressed issues or PRs… can be a bad sign, raising the question of whether the
community can manage the workload" (§4.1.5).

**Direction.** **Lower is healthier.**

**Edge cases.**
| Condition | Behaviour |
|---|---|
| `PR(r)` empty | `NaN` |
| Capped repository | **[FACT] Severely distorted.** For `kubernetes` PBR = 0.394 and `linux` 0.424, but their samples are recency-truncated, over-representing open PRs. **[REC]** Report PBR only alongside C2; suppress it where capture rate < 5%. |

---

### A5 — Issue Resolution Rate (IRR)

**Metric.** Proportion of observed issues that have been closed.

**Raw data.** `issues_data.csv` → `state` **Unit.** ratio [0,1] **Aggregation.** per repository

**Formula.**
```
IRR(r) = |{i ∈ I(r) : state(i) = closed}| / |I(r)|
```

**Interpretation.** High = reported problems get resolved. Low = the tracker accumulates unresolved
reports.

**Direction.** **Higher is healthier.**

**Edge cases.**
| Condition | Behaviour |
|---|---|
| `I(r)` empty | `NaN` — **[FACT]** occurs for **6 of 28** repos: `streamlit`, `kafka`, `django`, `httpd`, `linux`, `git` |
| All issues open | Returns 0.0, which is valid — **[FACT]** `hackingtool` = 0.0000 (0 of 19 closed) |
| Right-censoring | Recent issues have had less time to close, biasing IRR downward for fast-growing projects. **[ASSUME]** We assume this bias is acceptable for a prototype; it is not acceptable for a published health claim without survival analysis. |

---

### A6 — Issue Resolution Latency

**Metric.** Median days from issue creation to closure, over closed issues.

**Raw data.** `issues_data.csv` → `resolution_time_days` (or `closed_at − created_at`)

**Unit.** days **Aggregation.** per repository

**Formula.**
```
IRL(r) = median( { resolution_time_days(i) : i ∈ I(r), resolution_time_days(i) ≠ −1 } )
```

**Interpretation.** Lower = problems are resolved quickly.

**Direction.** **Lower is healthier.**

**Edge cases.**
| Condition | Behaviour |
|---|---|
| **`-1` sentinel** | **Must be excluded, never treated as a duration.** [FACT] affects 3,210 of 7,082 rows (45.33%). Treating `-1` as 0 would corrupt every repository's value. |
| No closed issues | `NaN` — **[FACT]** occurs for `hackingtool` (19 issues, 0 closed) |
| `I(r)` empty | `NaN` — 6 repos |
| Survivorship | Issues never closed are excluded, which **flatters slow projects**. **[REC]** Always report A6 next to A5. |

---

### A7 — Review Throughput

**Metric.** Count of PR events created within a fixed recent window.

**Raw data.** `pr_data.csv` → `created_at` **Unit.** count **Aggregation.** per repository

**Time window.** **45, 90, and 365 days** — **[FACT]** the windows stated in base-paper metrics M10
and M33 and in the case-company priority list (Table 3).

**Formula.**
```
RTP_w(r) = |{ p ∈ PR(r) : created_at(p) ≥ S − w days }|      for w ∈ {45, 90, 365}
```

**Interpretation.** Higher = more contribution activity being handled recently.

**Direction.** **Higher suggests more active** — but see edge cases; this is not a clean health
signal.

**Edge cases.**
| Condition | Behaviour |
|---|---|
| Capped repository | **[FACT] Metric measures the cap, not the project.** For `airflow`, `kubernetes`, `swift`, `node`, `RTP_365 = pr_total` exactly (1000/1000, 701/701, 1014/1014, 1002/1002) — their entire observed history falls inside one year. |
| `PR(r)` empty | 0, not `NaN` — a genuine zero count |
| Cross-repository comparison | **[REC] Invalid as a raw count.** Use only within a capture-rate stratum, or convert to a per-month rate using S4's normalisation (§7.2). |

---

### A8 — Development Activity Trend (S2 STA-4)

**Metric.** Net change in PR submission volume across consecutive 12-week intervals.

**Raw data.** `pr_data.csv` → `created_at` **Unit.** signed count **Aggregation.** per repository

**Time window.** 12-week (84-day) intervals — **[FACT]** S2 STA-4: "the cumulative increase in the
number of PRs submitted over twelve-week intervals".

**Formula.** *(S2 Table 4, STA-4)*
```
DAT(r) = Σ_{k=1}^{n−1} ( |PR_{k+1}(r)| − |PR_k(r)| )

where PR_k(r) is the set of PRs in the k-th consecutive 84-day interval
spanning the observed history of r, and n ≥ 2
```

**Interpretation.** Positive = PR volume growing. Negative = declining.

**Direction.** **Higher is healthier** — with the strong caveat below.

**Edge cases.**
| Condition | Behaviour |
|---|---|
| Fewer than 2 intervals observed | `NaN` — **[FACT]** occurs for **4 of 28** repos: `streamlit` (no PRs), and `airflow` (65-day span), `kubernetes` (51 days), `swift` (63 days) — their entire PR history is shorter than two 12-week intervals |
| Telescoping | **[DERIVED]** The sum telescopes to `\|PR_n\| − \|PR_1\|`, so it depends only on the first and last intervals, not the path between them. This is a property of S2's published formula, not an implementation error. **[REC]** Report it as specified for traceability, and additionally report the OLS slope of interval counts as our own more informative variant (Category C). |
| Mature projects | **[FACT]** 12 of 24 computable values are negative, including `elasticsearch` (−1,447) and `grafana` (−2,474). Declining PR volume in a mature project is not necessarily ill health. **[REC]** Do not treat sign alone as a verdict. |

---

### C1 — Repository Age (S2 STA-1)

**Formula.** `AGE_days(r) = (S − created_at(r)).days`, `AGE_years(r) = AGE_days(r) / 365.25`
*(S2 STA-1 is `2023 − year(r)`; we use the exact snapshot instead of a calendar year for precision.)*

**Unit.** days / years **Direction.** **Neither.** A moderator, not a score.
**[FACT]** Observed 221 – 5,888 days. **[FACT]** The base paper lists life-cycle stage as one of four
*traits*, distinct from the 21 health aspects — so age must not enter a health score.

---

### C2 — PR Capture Rate

**Formula.** `CAP(r) = |PR(r)| / max{ number(p) : p ∈ PR(r) }`, and
`is_capped(r) = 1 if 1000 ≤ |PR(r)| ≤ 1100 else 0`

**Unit.** ratio **Direction.** Not a health measure — a **data-quality** measure.
**[FACT]** Observed 0.6% (`kubernetes`) to 100.0% (`kafka`). 9 repositories are capped.
**[REC]** Mandatory companion to A4, A7, A8. Any dashboard row must display it.

---

# STEP 6 — Formula Design and Provenance Classification

**[DERIVED]** Every formula classified. This table is the one the research paper's methodology
section should reproduce.

| ID | Metric | Formula | Class | Justification of class |
|---|---|---|---|---|
| **A1** | PR Acceptance Rate | `merged / (merged + closed)` | **B — derived from a research definition** | S4 names *Pull Request Acceptance Rate (PRAR)* and states it is a ratio excluded from lifespan normalisation, but prints no equation. The denominator choice (decided PRs, excluding open) is ours. |
| **A2** | PR Resolution Efficiency | `Σ(end − created) / \|ended\|` | **A — directly adopted from a research paper** | S2 Table 4, TEC-2, reproduced exactly including the merge-or-close disjunction. |
| **A3** | PR Resolution Latency | `median(end − created)` | **C — our proposed formula** | No source specifies a median. Introduced because A2's mean is unstable on our data (§4.3). |
| **A4** | PR Backlog Ratio | `open / total` | **C — our proposed formula** | Base-paper M14 defines backlog qualitatively **for issues**. Both the PR application and the ratio form are ours. |
| **A5** | Issue Resolution Rate | `closed / total` | **B — derived from a research definition** | S4 names *Issue Resolution Rate (IRR)*; base-paper M15 defines issue turnover. Neither gives an equation. |
| **A6** | Issue Resolution Latency | `median(closed_at − created_at)` | **B — derived from a research definition** | Base-paper M5 defines responsiveness as "the timeliness… of responses"; the median operationalisation is ours. |
| **A7** | Review Throughput | `count(created_at ≥ S − w)`, `w ∈ {45, 90, 365}` | **B — derived from a research definition** | Base-paper M11 defines the construct; M10 and Table 3 supply the exact windows. The count form is ours. |
| **A8** | Development Activity Trend | `Σ(\|PR_{k+1}\| − \|PR_k\|)` over 84-day intervals | **A — directly adopted from a research paper** | S2 Table 4, STA-4, reproduced exactly including the 12-week interval. |
| **A8′** | Trend (OLS variant) | `slope(OLS(interval index → \|PR_k\|))` | **C — our proposed formula** | Addresses the telescoping property of STA-4. |
| **C1** | Repository Age | `S − created_at` | **A — directly adopted** | S2 Table 4, STA-1 (`2023 − year(r)`), with the calendar year replaced by the exact snapshot. |
| **C2** | PR Capture Rate | `rows / max(number)` | **C — our proposed formula** | No source addresses API-pagination truncation. Ours entirely. |
| **X1** | Popularity (partial) | `stars + forks` | **C — our proposed formula** | **Not** POP-1. S2 POP-1 is `\|F\|+\|S\|+\|W\|`; the watchers term cannot be implemented, so this must not carry S2's name. |

**[DERIVED] Provenance totals: 3 formulas Class A, 4 Class B, 5 Class C.**

**[REC]** For the paper, the honest statement is: *"Of the measurement formulas used, three are
adopted directly from Alami et al. (2024), four are derived from construct definitions given by
Linåker et al. (2026) and Kaushik & Chahal, and five are our own proposals. The base paper supplies
no formulas; it supplies the construct taxonomy against which our formulas are justified."*

---

# STEP 7 — Normalisation Design

## 7.1 Four of the eight metrics need no normalisation

**[DERIVED]** Measured distributions:

```
             count    min    25%    50%    75%    max
PRAR   (A1)     27  0.0000 0.5296 0.7146 0.8573 0.9300
PBR    (A4)     27  0.0013 0.0128 0.0590 0.1360 0.4236
IRR    (A5)     22  0.0000 0.3816 0.4926 0.6308 0.9245
```

**[REC]** A1, A4, A5 are **already bounded on [0,1] by construction**. Applying min-max to them
would *destroy* information: it would rescale a value that already has an absolute meaning ("62% of
PRs were merged") into a sample-relative rank. **Leave them unnormalised.** Only direction-align A4
by inverting: `A4_health = 1 − PBR`.

## 7.2 The unbounded metrics are heavily skewed

**[DERIVED]**

| Metric | min | median | max | max ÷ median | skewness |
|---|---:|---:|---:|---:|---:|
| A2 PRE (mean days) | 2.38 | 12.14 | 177.34 | 14.6× | 2.73 |
| A6 IRL (median days) | 0.06 | 8.71 | 252.11 | 28.9× | 2.28 |
| A7 RTP_365 (count) | 22 | 1,000 | 12,856 | 12.9× | 2.16 |
| X1 Popularity | 4,645 | 71,099 | 273,250 | 3.8× | 1.62 |

**[FACT]** This matches S4's finding of a "Pareto-like distribution" persisting even after per-month
normalisation.

## 7.3 Why min-max is **not** appropriate here

**[REC]** The template formula `x_norm = (x − min)/(max − min)` is rejected for this project, for
four reasons, in order of severity:

1. **Sample dependence breaks comparability.** `min` and `max` are estimated from our 28
   repositories. Adding a 29th repository changes the normalised score of all 28. A health index
   whose value for `numpy` changes because someone added `redis` to the dataset is not a
   measurement — it is a ranking. The project's stated goal is *repository comparison and adoption
   decisions*, which requires scores stable across runs.
2. **A single outlier sets the scale.** **[FACT]** `guava`'s A6 of 252 days and `httpd`'s A2 of 177
   days would define the maxima. **[DERIVED]** With skewness > 2.2, more than 75% of repositories
   would compress into the bottom quarter of the [0,1] range, and genuine differences between
   healthy projects would become invisible.
3. **It cannot extrapolate.** A newly assessed repository worse than the current max yields a
   normalised value outside [0,1], or must be clipped — silently discarding information.
4. **It is unjustified by any source.** **[FACT]** No paper in the source set uses min-max
   normalisation for a health index. S4 uses lifespan normalisation; S2 uses raw parameters in a
   Bayesian regression; the base paper normalises nothing.

## 7.4 Recommended approach

**[REC]** A three-tier scheme matched to each metric's measurement scale:

**Tier 1 — Bounded ratios (A1, A4, A5): use directly.**
```
health(A1) = PRAR                    health(A4) = 1 − PBR                health(A5) = IRR
```

**Tier 2 — Durations (A2, A3, A6): a saturating transform with a fixed reference.**
```
health(x) = 1 / (1 + x / x_ref)          x ≥ 0
```
Properties: bounded (0,1]; monotone decreasing so lower latency scores higher; `health(0) = 1`;
`health(x_ref) = 0.5`; **independent of the sample**, so a repository's score never changes when
another repository is added; handles the long tail without clipping.

**[ASSUME]** `x_ref` must be a defensible reference latency, not a sample statistic.
**[REC]** Calibrate `x_ref` on a large external corpus before publication. As an interim, use the
sample median (A3: `x_ref = 0.74` d; A6: `x_ref = 8.71` d) **and label every resulting score as
provisional**. Do not present provisionally calibrated scores as validated health measures.

**Tier 3 — Counts (A7, A8): rate-normalise first, then Tier 2.**
**[FACT]** S4's formula: `rate = raw / (active_lifespan_days / 30.44)`.
**[REC]** Apply it with `active_lifespan_days` = span of *observed* PR history, not repository age,
because our history is truncated by the cap. Then apply `log1p` before any bounded transform.
**[FACT]** S4 documents the failure mode we must guard: repositories with very short observed
lifespans produce inflated rates (their CPM reached 11,794,250 against a raw maximum of 692,245).
**[REC]** Our equivalent guard: refuse to compute a rate where the observed span is under 90 days —
which **[DERIVED]** excludes `airflow`, `kubernetes` and `swift`, the same three repositories that
fail A8.

## 7.5 Specific problems and their handling

| Problem | Evidence in our data | Handling |
|---|---|---|
| **Outliers** | A6 max 252 d vs median 8.7 d | Saturating transform (§7.4 Tier 2); never min-max |
| **Skewed distributions** | skewness 1.6–2.7 on all unbounded metrics | `log1p` before bounding for counts; median rather than mean for durations (A3, A6) |
| **Extremely popular repositories** | `react` 226,971 stars vs `httpd` 3,522 — a 64× spread | X1 is excluded from the RHI entirely. **[REC]** Popularity is an adoption *context* variable, and the feasibility study already showed it acts as a leakage co-signal. |
| **Zero values** | `httpd` PRAR = 0.0000; `hackingtool` IRR = 0.0000 | Genuine zeros — preserve. `log1p` is zero-safe. Distinguish in the schema from `NaN` (undefined). |
| **Zero denominators** | 6 repos have no issues; 1 has no PRs | Propagate `NaN`, never substitute 0. **[REC]** A repository missing a dimension's inputs must be reported as *not assessed* for that dimension, not as scoring zero. |
| **Truncated history** | 9 capped repositories | C2 travels with every row; suppress A4/A7/A8 below a capture threshold |

---

# STEP 8 — Health Dimension Aggregation

## 8.1 Which dimensions can be formed

**[DERIVED]**

| Our dimension | Metrics available | Aggregable? |
|---|---|---|
| **3 Issue & PR Health** | A1, A3, A4, A5, A6 (+A2 for traceability) | **Yes** — 5 metrics covering both PR and issue sides |
| **1 Development & Maintenance Health** | A7, A8 | **Weakly** — 2 metrics, both activity-volume proxies, both cap-affected, **no commit data** |
| **4 Community Engagement / Popularity** | X1 only | **No** — one snapshot variable, n = 28, no time series |
| **2 Contributor / Community Health** | none | **No** — no author column |
| **5 Sustainability / Maintenance Risk** | none usable | **No** — no bus factor, no licence, no deprecation label, `stale` constant |

**[REC]** Form **two** dimension scores (D3 and D1). Report D4 as a descriptive panel without a
score. State plainly that D2 and D5 are **not assessed**. Do not emit a placeholder value for an
unassessed dimension — a zero or a neutral 0.5 would be read as a measurement.

## 8.2 Aggregation flow

```
   raw event rows                  metric layer                dimension layer
   ──────────────                  ────────────                ───────────────

   pr_data.csv  ──┬──► A1 PR Acceptance Rate      ─┐
                  ├──► A3 PR Resolution Latency   ─┤
                  ├──► A4 PR Backlog Ratio        ─┼─► D3  Issue & PR Health
   issues_data ──┬┴──► A5 Issue Resolution Rate   ─┤       (5 metrics, equal weight)
                 └───► A6 Issue Resolution Latency─┘

   pr_data.csv  ──┬──► A7 Review Throughput       ─┐
                  └──► A8 Development Trend       ─┴─► D1  Development & Maintenance
                                                          (2 metrics, equal weight)
   repo_data.csv ────► X1 Popularity              ───► D4  descriptive only, NO score

                       (no inputs exist)          ───► D2  NOT ASSESSED
                       (no inputs exist)          ───► D5  NOT ASSESSED

   repo_data.csv ────► C1 Age, C2 Capture Rate    ───► context — reported, never scored
```

## 8.3 Weighting — what the evidence actually supports

**[FACT] The base paper provides no weights.** It is a qualitative study; it ranks nothing and
assigns no numeric importance to any aspect or metric.

**[FACT]** The base paper argues *against* a universal weighting. Its abstract concludes that
"subsets of metrics need to be prioritized, and applied in a structured approach", and it identifies
four traits — **life-cycle stage, project complexity, governance concentration, strategic
importance** — that determine "how the various aspects and metrics should be interpreted and applied
when evaluating and comparing projects" (p. 9).

**[DERIVED]** A single fixed weight vector applied to all repositories would **contradict the base
paper's own finding**. Weighting in this framework is properly a function of the assessing
organisation's context, not a property of the metric set.

**[FACT]** S4 demonstrates that **data-driven** weighting is achievable — exploratory factor
analysis recovered two latent engagement dimensions with cross-validation — but it did so on
**33,946 repositories**.

**[DERIVED]** With **n = 28** and 5 metrics in D3, factor analysis, PCA, or any variance-based
weighting is not estimable. A rule of thumb of 10 observations per variable would require ≈ 50
repositories for D3 alone; we have 28, of which only 21 have all five metrics defined.

**[REC] OUR PROPOSAL — equal weighting within a dimension, no cross-dimension aggregation.**

```
D3(r) = mean( health(A1), health(A3), health(A4), health(A5), health(A6) )     over defined metrics
D1(r) = mean( health(A7), health(A8) )                                          over defined metrics
```

Justification: equal weighting is the **maximum-entropy choice under ignorance** — it introduces no
unjustified preference. It is not claimed to be optimal. It is explicitly labelled as our proposal
and as a placeholder for a later, data-driven or context-elicited weighting.

**[REC]** Weighting should remain a **later research decision**, revisited when (a) a repository
sample large enough for factor analysis exists, or (b) practitioner elicitation in the style of the
base paper's interview survey is conducted for our specific decision context.

**[REC]** When fewer than 3 of D3's 5 metrics are defined for a repository, emit `NaN` for D3 rather
than averaging over 1–2 metrics. **[DERIVED]** This affects the 6 repositories with no issue data.

---

# STEP 9 — Candidate RHI Framework

## 9.1 Structure

```
         ┌──────────────────────────────────────────────────────────────┐
  LAYER 1│  RAW EVENTS       248,320 PR rows  ·  7,082 issue rows       │
         │                   28 repository snapshot rows                │
         └────────────────────────────┬─────────────────────────────────┘
                                      │  Step 5 formulas
         ┌────────────────────────────▼─────────────────────────────────┐
  LAYER 2│  METRIC SCORES    A1 A2 A3 A4 A5 A6 A7 A8   (natural units)  │
         │                   + C1 C2 context  + X1 descriptive          │
         └────────────────────────────┬─────────────────────────────────┘
                                      │  Step 7 normalisation
         ┌────────────────────────────▼─────────────────────────────────┐
  LAYER 3│  HEALTH SCORES    each metric mapped to [0,1], direction-    │
         │                   aligned so that 1 = healthier              │
         └────────────────────────────┬─────────────────────────────────┘
                                      │  Step 8 equal weighting
         ┌────────────────────────────▼─────────────────────────────────┐
  LAYER 4│  DIMENSION SCORES D3 ✓   D1 ✓   D4 (no score)                │
         │                   D2 NOT ASSESSED   D5 NOT ASSESSED          │
         └────────────────────────────┬─────────────────────────────────┘
                                      │  ⚠ BLOCKED — see §9.3
         ┌────────────────────────────▼─────────────────────────────────┐
  LAYER 5│  RHI              NOT COMPUTED IN THIS PROTOTYPE             │
         └──────────────────────────────────────────────────────────────┘
```

## 9.2 Candidate formula

**[REC] OUR PROPOSAL — recorded for the design record, not for execution now.**

```
RHI(r) = Σ_{d ∈ D} w_d · Score_d(r)          with  Σ w_d = 1,  D = assessed dimensions
```

| Component | Specification | Status |
|---|---|---|
| Metric normalisation | §7.4 three-tier scheme | **[REC]** ours |
| Within-dimension weighting | equal | **[REC]** ours, placeholder |
| Cross-dimension weighting `w_d` | **undetermined** | **[REC]** deferred — see §8.3 |
| Score range | [0, 1], 1 = healthier | **[REC]** ours |
| Interpretation | relative, within a comparison set of similar life-cycle stage and complexity | **[FACT]** the base paper's four traits require this qualification |

## 9.3 ⚠ The 28-repository dataset cannot validate a repository-level RHI

**[DERIVED]** Stated explicitly, as required:

1. **[FACT]** n = 28, of which 21 have all five D3 metrics defined and 24 have A8 defined. No
   train/validation split of 28 rows supports a generalisation claim.
2. **[FACT]** There is **no ground truth**. Validating a health index requires an external criterion
   — deprecation (S1), sustained activity (S5), or defect density (S2). **None is available**:
   `stale` is constant `False`, there are no commits, and there are no defect labels.
3. **[FACT]** There is **no negative class**. All 28 repositories are large, currently-maintained
   flagship projects. An index that cannot be shown to separate healthy from unhealthy projects,
   because no unhealthy project is present, is untested by construction.
4. **[DERIVED]** Two of five dimensions cannot be scored at all, so any composite would describe
   40% of the declared framework while carrying a name that implies all of it.
5. **[FACT]** Cross-repository comparability is compromised by the sampling caps for 9 of 28
   repositories.

**[REC]** **Do not compute an RHI number in this prototype.** Implement Layers 1–4 and display a
**dimension profile** — D3 and D1 side by side with C1, C2 and explicit "not assessed" markers for
D2, D4 and D5. This is defensible, useful to a developer choosing between repositories, and honest.
Reserve the RHI for the final system, where it becomes computable and, more importantly, testable.

**[REC]** The research contribution to claim at this stage is **the integration framework and its
traceability**, not a validated index. This is consistent with
[health-assessment-framework.md](health-assessment-framework.md) §2.5, which already records that
the RHI is our proposal and not present in any source paper.

---

# STEP 10 — Target Design for ML

**[REC]** `stars` is not reconsidered. The previous experiment was exploratory; with 28 repositories
it is not a candidate.

## 10.1 Candidate comparison

| # | Target | Type | Source | Rows | Leakage risk | Research relevance | Prototype? | Final system? |
|---|---|---|---|---|---|---|---|---|
| **T1** | **PR merge outcome** (merged vs closed-unmerged) | Binary classification | `pr.state` | **240,241** | **High but fully controllable** — `merged_at`, `merge_time_days`, `closed_at`, `updated_at`, and the four contributor-family columns must be dropped | Operationalises base-paper **M42 External Openness** and part of **M15 Issue Turnover** | **YES** | As a component, not as the health target |
| T2 | PR time-to-merge | Regression | `pr.merge_time_days` | 183,836 | High, controllable | Base-paper **M5**; S2 **TEC-2** | Possible | Possible |
| T3 | Issue resolution time | Regression | `issues.resolution_time_days` | 3,872 | Moderate | Base-paper **M5**, **M15** | Marginal — 21 repos | No |
| T4 | Issue closed vs open | Binary classification | `issues.state` | 7,082 | **Invalid** — right-censored | — | **NO** | No |
| T5 | Repository health index | Regression | constructed | 28 | — | Our RHI | **NO** — n = 28 | **Yes, eventually** |
| T6 | t-year sustained activity | Binary classification | **S5** definition | 0 | — | **S5** — the closest published analogue to our goal | **NO** — needs commits | **Yes — recommended** |
| T7 | Deprecation / archived | Binary classification | **S1** definition | 0 | — | **S1** | **NO** — `stale` constant | **Yes — recommended** |

## 10.2 Recommended prototype target

**[REC] T1 — PR merge outcome.**

**Why it is defensible.**
- **[FACT]** 240,241 labelled rows — the only target in the dataset with enough observations for a
  credible train/test split.
- **[DERIVED]** It maps to a named base-paper metric (**M42 External Openness**, "the openness for
  external contributions") rather than to an invented construct.
- **[FACT]** Its leakage sources are enumerable and were enumerated in the feasibility study.
- **[DERIVED]** It answers a question a developer actually asks — *will my contribution be
  accepted?* — which is within the platform's stated decision-support scope.

**What it does not do.**
- **[DERIVED]** It is a **PR-level** target. It **does not predict repository health** and must never
  be described as doing so. It demonstrates the modelling methodology on the one dimension the data
  supports.
- **[FACT]** Class balance 76.5% / 23.5%; always-predict-merged scores 76.5% accuracy. Accuracy alone
  is the wrong metric; report precision/recall or AUC.
- **[FACT]** 8,079 open PRs are excluded, producing survivorship bias.
- **[FACT]** `httpd` (PRAR 0.0000), `git` (0.0012) and `linux` (0.0193) do not use GitHub PRs for
  real review. **[REC]** Either exclude these three repositories or add a workflow indicator; leaving
  them in trains the model on a workflow artefact.
- **[REC]** Split by **repository group or by time**, never randomly — a random split lets the model
  memorise repository-specific title conventions.

## 10.3 What the final research system should target

**[REC]** The final system's target should be an **external, repository-level health criterion**,
following the published precedents:

| Precedent | Definition | What it needs |
|---|---|---|
| **S5** — sustained activity | "t-year sustained activity if 1) commit activity for more than t year(s), and 2) median commits per month ≥ k"; t = 2, k = 1 | Commit history |
| **S1** — deprecation | archived **∨** deprecation keywords in README/description | `archived` flag + README text |
| **S2** — quality outcome | defect density, code coverage | Issue labels + source analysis |

**[REC]** Adopt **S5's t-year sustained activity** as the primary final target, because it is
positive-framed (matching a "health index"), has a published operational definition, and was shown
predictable at AUC 0.84 on 290,255 projects. Use **S1's deprecation** as a secondary, negative-framed
target for risk analysis. **[ASSUME]** Both require data collection we have not yet performed.

**[REC]** A PR-event-based adaptation of S5's definition — substituting PR activity for commit
activity — would be **Category C, our own**, and would need validating against the commit-based
original before being claimed as equivalent.

---

# STEP 11 — Implementation Specification

*Written so another developer can implement it without making research judgements.*

## A. Final prototype metrics

**8 metrics + 2 context variables + 1 descriptive variable.**

| ID | Name | Dimension |
|---|---|---|
| A1 | PR Acceptance Rate | D3 |
| A2 | PR Resolution Efficiency (S2 TEC-2) | D3 — traceability only, not in the score |
| A3 | PR Resolution Latency (median) | D3 |
| A4 | PR Backlog Ratio | D3 |
| A5 | Issue Resolution Rate | D3 |
| A6 | Issue Resolution Latency | D3 |
| A7 | Review Throughput (45/90/365 d) | D1 |
| A8 | Development Activity Trend | D1 |
| C1 | Repository Age | context |
| C2 | PR Capture Rate + capped flag | context |
| X1 | Popularity (stars + forks) | descriptive — excluded from scores and features |

## B. Exact formulas

```
S = 2024-09-06T11:30:17Z                        # snapshot = max(repo_data.updated_at)
end(p) = merged_at(p) if not null else closed_at(p)

A1  PRAR(r) = |{p: state=merged}| / |{p: state ∈ {merged,closed}}|
A2  PRE(r)  = mean{ end(p) − created_at(p) : end(p) ≠ null }          # days
A3  PRL(r)  = median{ end(p) − created_at(p) : end(p) ≠ null }        # days
A4  PBR(r)  = |{p: state=open}| / |PR(r)|
A5  IRR(r)  = |{i: state=closed}| / |I(r)|
A6  IRL(r)  = median{ resolution_time_days(i) : resolution_time_days(i) ≠ −1 }
A7  RTP_w(r)= |{p: created_at(p) ≥ S − w days}|      w ∈ {45, 90, 365}
A8  DAT(r)  = Σ_{k=1}^{n−1} (|PR_{k+1}(r)| − |PR_k(r)|)   # 84-day intervals, n ≥ 2
A8′ DAT_slope(r) = OLS slope of (k → |PR_k(r)|)
C1  AGE_days(r) = (S − created_at(r)).days
C2  CAP(r)  = |PR(r)| / max{number(p)} ;  is_capped = 1 if 1000 ≤ |PR(r)| ≤ 1100
X1  POP(r)  = stars(r) + forks(r)
```

Health mappings (Step 7):
```
h(A1) = PRAR                     h(A4) = 1 − PBR                  h(A5) = IRR
h(A3) = 1 / (1 + PRL / 0.74)     h(A6) = 1 / (1 + IRL / 8.71)     # x_ref PROVISIONAL
h(A7) = 1 / (1 + 1/log1p(rate))  h(A8) = logistic(DAT_slope)      # both PROVISIONAL
D3 = mean(h(A1), h(A3), h(A4), h(A5), h(A6))    # NaN if fewer than 3 defined
D1 = mean(h(A7), h(A8))                          # NaN if fewer than 1 defined
RHI = NOT COMPUTED
```

## C. Raw columns required

| File | Columns used | Columns explicitly NOT used |
|---|---|---|
| `pr_data.csv` | `repository`, `state`, `created_at`, `merged_at`, `closed_at`, `number` | `id`, `created`, `updated`, `updated_at`, `title`, `merge_time_days`¹ |
| `issues_data.csv` | `repository`, `state`, `resolution_time_days` | `id`, `created`, `updated`, `closed_at`², `created_at`², `number`, `title`, `updated_at` |
| `repo_data.csv` | `name`, `created_at`, `stars`, `forks` | `repository`³, `issue_contributors`⁴, `pr_contributors`⁴, `total_contributors`⁴, `contributor_per_star`⁴, `stale`⁵, `size_category`⁶, `stars_per_fork`⁶, `stars_per_issue`⁶, `description`, `id`, `created`, `updated`, `updated_at`⁷, `open_issues` |

¹ derivable from `merged_at`; used only in A2/A3 as an equivalent
² used only if recomputing A6 from scratch instead of using the provided column
³ **corrupt for `streamlit`** — join on `name`
⁴ **mislabelled — these count distinct titles, not contributors**
⁵ constant `False` — zero variance
⁶ exact functions of other columns — collinear
⁷ used once, to define the snapshot `S`

## D. Feature table schema

**Two tables. They are not interchangeable.**

**D.1 `repository_metrics` — 28 rows, for the dashboard. NOT a training table.**

| Column | Type | Null? | Source |
|---|---|---|---|
| `repository_id` | str | no | `repo_data.name` |
| `full_name` | str | no | `repo_data.full_name` |
| `age_days` | int | no | C1 |
| `pr_total` | int | no | count |
| `issue_total` | int | no | count |
| `pr_capture_rate` | float | yes | C2 |
| `is_capped` | int (0/1) | no | C2 |
| `prar` | float [0,1] | **yes** | A1 |
| `pre_mean_days` | float | **yes** | A2 |
| `prl_median_days` | float | **yes** | A3 |
| `pbr` | float [0,1] | **yes** | A4 |
| `irr` | float [0,1] | **yes** | A5 |
| `irl_median_days` | float | **yes** | A6 |
| `rtp_45d`, `rtp_90d`, `rtp_365d` | int | no | A7 |
| `dat_growth` | float | **yes** | A8 |
| `dat_slope` | float | **yes** | A8′ |
| `popularity` | int | no | X1 — display only |
| `d3_issue_pr_health` | float [0,1] | **yes** | dimension score |
| `d1_dev_maintenance` | float [0,1] | **yes** | dimension score |
| `d2_contributor_health` | — | **always NULL** | not assessed |
| `d4_engagement` | — | **always NULL** | not assessed |
| `d5_sustainability` | — | **always NULL** | not assessed |
| `rhi` | — | **always NULL** | not computed — §9.3 |

**[FACT]** Expected null counts, measured: `prar`/`pbr`/`pre`/`prl` null for 1 repo; `irr` null for
6; `irl` null for 7; `dat_growth` null for 4.

**D.2 `pr_training` — 240,241 rows, for the ML prototype.**

| Column | Type | Role |
|---|---|---|
| `pr_id` | str | identifier — not a feature |
| `repository_id` | str | **grouping key for the split** |
| `title` | str | feature (text) |
| `created_at` | datetime | feature source — derive hour, weekday, month, repo-age-at-creation |
| `number` | int | feature |
| `repo_age_days_at_pr` | int | joined feature |
| `repo_stars`, `repo_forks` | int | joined features — **[REC]** consider excluding; snapshot co-signals |
| **`target_merged`** | int (0/1) | **label** — 1 if `state='merged'`, 0 if `state='closed'` |

**Rows excluded:** the 8,079 PRs with `state='open'` (undecided).
**Columns forbidden:** `merged_at`, `merge_time_days`, `closed_at`, `updated_at`, `state`,
`issue_contributors`, `pr_contributors`, `total_contributors`, `contributor_per_star`.

## E. Health-dimension calculation flow

```
1.  Load three CSVs.  Join event files to repo_data on  repository == name.
2.  Convert `-1` sentinels to NaN in resolution_time_days and merge_time_days.
3.  Parse all *_at columns as timezone-aware UTC.  Ignore `created`/`updated`.
4.  Compute S = max(repo_data.updated_at).
5.  Per repository, compute A1–A8, C1, C2, X1  (Step 11.B).
6.  Suppress A4, A7, A8 where pr_capture_rate < 0.05.
7.  Map each scored metric to [0,1] via Step 7.4.  Direction-align.
8.  D3 = mean of 5 health values, NaN if fewer than 3 defined.
    D1 = mean of 2 health values, NaN if none defined.
9.  Emit NULL for D2, D4, D5 and for RHI.  Do not substitute a default.
10. Every displayed row must carry pr_capture_rate and is_capped.
```

## F. Candidate RHI calculation

**[REC] Specified but NOT implemented in this prototype.** See §9.2 for the formula and §9.3 for the
five reasons it cannot be validated on 28 repositories. The implementation must emit `NULL`.

## G. Prototype ML target

`target_merged` — binary, 240,241 rows, from `pr.state`.

**Limitations that must appear in any reporting of results:**
1. PR-level, not repository-level — does **not** predict repository health.
2. Majority-class baseline is 76.5%; report AUC / precision / recall.
3. Survivorship bias — 8,079 open PRs excluded.
4. Three repositories (`httpd`, `git`, `linux`) do not use GitHub PRs for review.
5. Nine repositories contribute only recency-truncated samples.
6. 27 repositories only — `repository` is a high-influence categorical.

## H. Data limitations — what cannot be implemented

**[FACT]**

| Cannot implement | Blocked by |
|---|---|
| Dimension 2 in any form | no author/login column anywhere |
| Dimension 5 in any form | no bus factor, no licence, no deprecation label, `stale` constant |
| Dimension 4 as a score | single snapshot, n = 28, no watchers |
| Base-paper **M10 Code Activity** | no commit data — despite being a case-company priority |
| Base-paper M12, M13, M16, M17, M30, M33, M34, M45, M57, M60, M65, M67–M69 | required data absent |
| S2 COM-1, COM-2, STA-2, STA-5–STA-9, TEC-1, TEC-3, TEC-4 | no comments, commits, or authors |
| S2 POP-1 as published | **no watchers column** |
| S4 CPM, CNT/m, WT/m, STR/m, IC/m, PRC/m | no commits, authors, watchers, or comments |
| S4's Passive/Active Engagement factors | watchers and comments both absent |
| S1 repository centrality (HITS) | star counts, not star events with user ids |
| S1 deprecation label | no `archived` flag, no README |
| S3 YOSHI characteristics | no author identity or location |
| S5 sustained-activity target | no commit history |
| **A validated RHI** | n = 28, no ground truth, no negative class |

## I. Final research implementation requirements

**[REC]** In priority order, with the specific capability each unblocks:

| # | Data to collect | GitHub API source | Unblocks |
|---|---|---|---|
| 1 | **Author login on every issue, PR, commit** | `user.login` on each event | Dimension 2 entirely; M30 bus factor; M33/M34; S2 STA-5/7/8/9; S3 |
| 2 | **Commit history** — sha, author, date, additions, deletions, files | Commits API | Base-paper **M10**; S2 TEC-3/TEC-4/STA-2/STA-6; S4 CPM; **S5's target** |
| 3 | **n ≥ 1,000 repositories including abandoned and archived ones** | Search API + `archived` | Repository-level modelling; RHI validation; a negative class; **S1's target** |
| 4 | **Uncapped event collection** | paginate to completion | Comparable aggregates; valid trends; removes C2 suppression |
| 5 | **Issue and PR labels** | Labels API | M16 bug handling; S2 defect density |
| 6 | **Comments and reviews with timestamps and authors** | Comments / Reviews APIs | M5 response time; **S2 COM-1** exactly; S4 IC/m, PRC/m; M60 |
| 7 | **Watchers / subscribers + star and fork time series** | Subscribers API, star events | **S2 POP-1** exactly; S4 WT/m, STR/m; **S4's Passive Engagement factor** |
| 8 | **Repository metadata** — licence, README, CONTRIBUTING, CODE_OF_CONDUCT, CI config | Contents API | M45 licence; M67–M69 docs; M38–M41 governance; M64–M66 scaffolding |
| 9 | **Release and tag history** | Releases API | M17 release tempo; M53–M57 |
| 10 | **User→repository star edge list** | Stargazers API with `Accept: star+json` | **S1 repository centrality (HITS)** |

---

## Traceability Summary

| Component | Class | Source | Verified |
|---|---|---|---|
| 21 aspects / 72 metrics taxonomy | Adopted | **BasePaper** Fig. 2, Appendix A | Read directly |
| 45 / 90 / 365-day windows | Adopted | **BasePaper** M10, M33, Table 3 | Read directly |
| Four moderating traits | Adopted | **BasePaper** p. 9 | Read directly |
| A2 formula (TEC-2) | Adopted | **S2** Table 4 | Read directly; computes on 27/28 repos |
| A8 formula (STA-4) | Adopted | **S2** Table 4 | Read directly; computes on 24/28 repos |
| C1 formula (STA-1) | Adopted | **S2** Table 4 | Read directly |
| PRAR, IRR names | Derived | **S4** §5.2.1.1 | Read directly |
| Per-month normalisation | Adopted | **S4** §4.3 | Read directly |
| Skew / Pareto warning | Adopted | **S4** §5.2.2 | Read directly; reproduced (skew 1.6–2.7) |
| Deprecation definition | Cited, not implemented | **S1** §III-A | Read directly |
| Sustained-activity target | Cited, not implemented | **S5** §3 | Read directly |
| YOSHI characteristics | Cited, not implemented | **S3** §1 | Read directly |
| A3, A4, A8′, C2, X1, saturating normalisation, equal weighting, RHI structure | **OUR PROPOSAL** | — | Marked throughout |
| Anything attributed to Xia et al. | **none** | PDF absent | Not read — no claims made |

---

**Next step, not started:** feature construction and model training. This document is design only.

---

# AMENDMENT LOG

Changes to the methodology locked above. **Nothing earlier in this document has
been deleted or rewritten** — the original decisions stand as the record of what
was decided and when. Where an amendment supersedes an earlier decision, the
superseded text remains in place and is cross-referenced here.

---

## Amendment 1 — 2026-08-31 — Step 8 approved changes

**Trigger:** [step8-feature-inspection-and-dimension-design.md](step8-feature-inspection-and-dimension-design.md)
**Approved by:** project owner, 2026-08-31, items 1–5.
**Implementation:** [health-dimension-aggregation.md](../implementation/health-dimension-aggregation.md)

### A1.1 — Workflow applicability rule *(new; supersedes nothing)*

PR-based metrics are marked NOT ASSESSED where GitHub pull requests are not the
project's review mechanism. The decision is external and cited — the project's
own contribution documentation — never inferred from a latency threshold.

Affected: `a1_prar`, `a2_pre_mean_days`, `a3_prl_median_days`, `a4_pbr`
Repositories: `linux`, `git`, `httpd`, `guava`

**Scope change during implementation.** Step 8 proposed gating A1 and A3 only.
Running the rule showed the PR block then collapsed to A4 alone, and `guava`
scored **0.982** on it — the highest PR-block score in the dataset — because its
backlog is near-zero *due to* auto-closure. **A4 was therefore added.** This is a
deviation from the Step 8 proposal, made on evidence and recorded here.

### A1.2 — Precision policy *(new; supersedes nothing)*

§4.3 and §7.4 said nothing about estimate precision. Latency metrics A3 and A6
now carry a percentile bootstrap CI (4,000 resamples, seed = `sha256(repo)`), and
are suppressed from their dimension score when

- `n < 3` — structural: a median from fewer than three observations is one
  observation; **or**
- the 95% CI covers more than **0.5** of the health scale — **[REC] our proposed
  methodological choice**.

**A minimum sample-size threshold was explicitly rejected**: `flask` (n=6) has a
CI width of 0.085 while `terraform` (n=109) has 0.644, so n does not predict
stability. Raw metrics are preserved; only score eligibility changes.

### A1.3 — A8R relative slope *(supersedes §11.B `h(A8) = logistic(DAT_slope)`)*

**Superseded:** `h(A8) = logistic(DAT_slope)` with `SLOPE_LOGISTIC_SCALE = 100.0`.

**Now:**
```
A8R(r) = OLS_slope(k -> |PR_k(r)|) / mean_k(|PR_k(r)|)
h(A8)  = 1 / (1 + exp(-A8R / 0.05))
```

**Reason.** The absolute slope has units of PRs per interval per interval and so
scales with project size: `grafana` declining 9.9% per interval scored 0.065
while `cli` declining 14.2% — a worse decline — scored 0.461, purely because
`grafana` is ~24× larger. A8R is dimensionless and removes the confound.

**Provenance:** **[C] our contribution**, **[PROVISIONAL]**. The scale `0.05` has
**no research support** — S2 Table 4 gives STA-4 as a raw signed count fed to a
Bayesian regression, S4 normalises by lifespan, the base paper normalises
nothing. It reads as "a 5% volume change per 12-week interval is one logistic
unit" and requires calibration on a large external corpus.

The absolute slope and its health score are retained in the output
(`a8p_dat_slope`, `h_a8_dat_absolute_legacy`, `mean_prs_per_interval`) for
sensitivity analysis.

**Step 6 provenance table gains one row:**

| ID | Metric | Formula | Class | Justification |
|---|---|---|---|---|
| **A8R** | Relative Development Trend | `OLS_slope / mean interval volume` | **C — our proposed formula** | No source defines it; addresses size confounding in A8′ |

### A1.4 — D3 nested block aggregation *(supersedes §8.3 D3 flat mean)*

**Superseded:** `D3 = mean(h_A1, h_A3, h_A4, h_A5, h_A6)`, NaN if fewer than 3 defined.

**Now:**
```
PR block    = mean(h_a1_prar, h_a3_prl, h_a4_pbr)   over defined members
issue block = mean(h_a5_irr, h_a6_irl)              over defined members
D3          = 0.5 * PR block + 0.5 * issue block    both blocks required
```

**Reason.** The flat mean silently assigned the PR side 3/5 and the issue side
2/5 — an accident of how many metrics survived on each side. It also
double-counted the issue signal: `h_a5_irr` and `h_a6_irl` correlate at Spearman
**0.648**, against 0.34–0.38 among the PR trio. Block weighting makes the balance
an explicit 50/50 choice between two constructs.

**Provenance:** **[C] our proposal.** The base paper supplies no weights and
argues weighting is context-dependent; data-driven weighting is not estimable at
n = 28.

### A1.5 — D1 requires both members *(supersedes §8.3 `D1_MIN_DEFINED = 1`)*

**Superseded:** D1 emitted with a single defined member.
**Now:** `D1_MIN_DEFINED = 2`. A one-metric D1 previously appeared in a column
indistinguishable from a two-metric D1.

### A1.6 — RHI reassessed *(reaffirms §9.3, adds two reasons)*

The conclusion of §9.3 is unchanged: **no validated RHI.** Two reasons are added
by the implementation:

7. Only **16 of 28** repositories have both dimensions scored, so a composite
   would exist for 57% of the sample.
8. The D1 half depends on a provisional, unvalidated logistic scale (A1.3).

A **PROVISIONAL** `candidate_rhi = 0.5·D1 + 0.5·D3` is emitted for
experimentation only, labelled in every row with
`candidate_rhi_basis = "D1+D3 only (2 of 5 dimensions) - PROVISIONAL, not
validated"`. The `rhi` column remains NULL throughout. The delivered artefact is
a **Repository Health Profile**, not an index.

### A1.7 — Superseded test

`tests/test_metrics.py::test_dimension_score_requires_minimum_members` asserted
the flat five-member mean. It is renamed
`test_dimension_score_uses_block_aggregation`, asserts the block formula, and
records the superseded expectation (0.64) in its docstring.

---

## Amendment 2 — 2026-08-31 — A7/A8R workflow applicability

**Trigger:** open scope question raised at the end of Step 8 implementation.
**Question:** should A7 (Review Throughput) and A8R (Relative Development Trend)
also be gated for the four repositories whose GitHub PR workflow is not
representative?

### A2.1 — The evidence

**[FACT]** A7 and A8R read `pr.created_at` — PR **arrival**. The metrics already
gated (A1, A2, A3, A4) read `pr.state` and the disposition timestamps — PR
**disposition**. Different column families.

**[FACT]** But A7 is a *proxy* for a construct the base paper defines in terms of
disposition:

> **BP M11 Review Throughput** — "The activity in development-related
> activities, such as code reviews, **merging of PRs**, and actions on issues
> over equal periods of time."
> **BP M10 Code Activity** — "The **contribution activity to the code base** over
> time, e.g., last 45, 90, and 365 days."

**[DERIVED]** The proxy is valid only where arrivals lead to review and land in
the code base. Share of counted PR arrivals that ever merge:

| Repository | arrivals | merged | % merged | applicable |
|---|---:|---:|---:|:---:|
| `httpd` | 427 | 0 | **0.0%** | no |
| `git` | 1,000 | 1 | **0.1%** | no |
| `linux` | 897 | 10 | **1.1%** | no |
| `guava` | 1,000 | 281 | **28.1%** (Copybara automation) | no |
| *all 23 applicable repositories* | | | **46.2% – 90.8%** | yes |

**[DERIVED]** Complete separation, no overlap. For `linux`, `git` and `httpd`
more than **98%** of the PR events A7 counts never enter the code base, so the
count measures ignored drive-by traffic rather than development activity. A8R is
the trend in the same arrivals and fails identically.

### A2.2 — Decision: YES, gate them

**[REC]** A7 and A8R are added to `affected_metrics` for all four repositories.

**Rejected alternative.** A7 could be reframed as "inbound contribution
interest", which would be valid. **[DERIVED]** But that is a *different
construct* belonging to D4 Community Engagement, not D1 Development &
Maintenance Health. Renaming a construct to fit the available data is the exact
failure mode this project rejected when it found the `*_contributors` columns
counting titles rather than people.

**[FACT]** The decision was not made on score grounds — it *reduces* coverage.
D1 falls from 22 to **18** assessed repositories, and `linux`, `git`, `httpd`,
`guava` become **fully Not Assessed** (coverage 0.0). That is the correct answer:
for those projects this dataset has no commit data, no issue data for three of
them, and PR data that does not reflect their workflow.

### A2.3 — Reason-bookkeeping correction

**[FACT]** A bug found during the Part 3 inspection: 7 blanked scores carried no
reason, and `streamlit`'s zero-PR case was mislabelled as a capture limitation.
Fixed with an explicit precedence rule — `not_applicable_workflow` and
`suppressed_imprecise` are specific and survive; `suppressed_low_capture` may
overwrite the generic `no_data`; a backstop assigns `no_data` to anything still
unlabelled. **[FACT]** All 55 blanked scores now carry a reason; zero unlabelled.

### A2.4 — Bootstrap memory fix

**[FACT]** A single `(4000, n)` resample draw required 1.08 GiB for
`elasticsearch` (n = 36,255) and aborted the run. Resampling is now chunked
(`BOOTSTRAP_CHUNK = 250`), bounding peak memory while remaining deterministic.

### A2.5 — Metric dominance disclosed

**[DERIVED]** Measured on the final profiles, and to be stated wherever scores
are reported:

| Dimension | Member | variance | corr with its dimension |
|---|---|---:|---:|
| **D1** | `h_a8_dat` | 0.0428 | **+0.919** |
| **D1** | `h_a7_rtp` | 0.0078 | +0.384 |
| D3 | `h_a5_irr` | 0.0389 | +0.848 |
| D3 | `h_a6_irl` | 0.0768 | +0.796 |
| D3 | `h_a3_prl` | 0.0462 | +0.767 |
| D3 | `h_a1_prar` | 0.0221 | +0.407 |
| **D3** | `h_a4_pbr` | **0.0030** | **+0.218** |

**[DERIVED]** Two consequences that must be disclosed rather than corrected:

1. **D1's ranking is effectively A8R's ranking** (r = 0.919). Because A8R's
   health score depends on the provisional, unvalidated logistic scale of 0.05,
   **the D1 ordering inherits that provisionality**. Equal weighting is applied
   as documented; the more variable member simply dominates an unweighted mean.
2. **`h_a4_pbr` is nearly inert** (variance 0.0030, range 0.211). It contributes
   almost no discrimination to D3 and acts close to a constant offset.

**[REC]** Neither is a defect in the implementation — both are arithmetic
consequences of equal weighting over members with unequal spread. They are
recorded here so that no reader mistakes D1 for a two-metric consensus.
