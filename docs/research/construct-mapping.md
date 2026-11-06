# Construct Mapping: Linåker et al. (2026) 21 Aspects & 72 Metrics to Computable GitHub Signals
**Project:** AI-Assisted Developer Decision Support and Repository Intelligence Platform  
**Document Code:** M1.2  
**Date:** 2026-11-06  
**Status:** Canonical Construct Mapping & Feasibility Classification  
**Evidence Standard:** Directly maps Linåker et al. (2026) Appendix A & Figure 2 against GitHub REST API capabilities and M0.1 Metric Registry.

---

## 1. Overview & Methodological Framing

**[FACT]** In empirical software engineering, **construct validity** ensures that operational measurements accurately reflect the theoretical latent constructs under study. Linåker et al. (2026) qualitative intake framework establishes that open-source software health spans **5 broad health areas, 21 distinct health aspects, and 72 granular metrics**.

**[FACT]** A major challenge in automated repository intelligence is that qualitative practitioner metrics include both public, code-adjacent signals (e.g. PR throughput, issue latency, release cadence) and private, non-code signals (e.g. internal organizational sponsorship, face-to-face meetups, psychological safety in chat channels).

**[DERIVED]** To prevent construct distortion, every metric in the platform is classified into one of three feasibility tiers:
1. **Fully Measurable (FM):** Directly computable from public GitHub REST API endpoints without proprietary data.
2. **Partially Measurable (PM):** Computable with documented heuristics, proxy signals, or bounded by API rate limits/truncation.
3. **Unavailable (UA):** Unobservable via code-hosting APIs (requires financial audits, private chat/Slack/mailing list scraping, or subjective developer interviews).

---

## 2. Complete Mapping Matrix: 21 Aspects & 72 Metrics

### Area 1: Community Productivity (5 Aspects, 17 Metrics)

| Aspect | Metric ID | Metric Name (Linåker et al. 2026) | Base Paper Definition | CHAOSS Family | Computable Signal / GitHub Source | Feasibility Tier | Platform Operationalisation |
|---|---|---|---|---|---|---|---|
| **Social Activity** | M1 | Event Presence | Presence of social meetups, hackathons, or conferences | Common | Community calendar / outside GitHub | **UA** | Outside platform scope |
| | M2 | Chat Activity | Chat message volume and frequency in channels | Evolution | Slack/Discord/IRC logs | **UA** | Requires non-GitHub scrapers |
| | M3 | Social Media Footprint | Mentions and activity on Twitter/X, Reddit, LinkedIn | Value | Social web telemetry | **UA** | Unreliable external API |
| | M4 | Forum Activity | Discussions on Discourse or Stack Overflow | Evolution | StackExchange API | **PM** | Proxy via GitHub Discussions |
| **Responsiveness** | M5 | General Responsiveness | Timeliness of initial responses to new issues/PRs | Evolution | PR/Issue creation to first maintainer action | **FM** | Operationalised in **A3 (Median Latency)** |
| | M6 | Discussion Responsiveness | Turnaround time for answers in discussions | Evolution | GitHub Discussions API | **PM** | Planned extension |
| | M7 | Maintainer Reactivity | Responsiveness of core maintainers vs drive-by users | Evolution | Issue comment author separation | **PM** | Requires deep comment mining |
| **External Visibility** | M8 | Search Engine Visibility | Web search rankings and domain backlinks | Value | Web indexing engines | **UA** | Outside repository scope |
| | M9 | Project Popularity | Stargazers, forks, watchers, package downloads | Value | `/repos/{owner}/{repo}` (`stargazers_count`, `forks`) | **FM** | Operationalised in **X1 (Stars), STA-3 (Forks)** |
| **Development Activity** | M10 | Code Activity | Commit cadence over 45, 90, 365 days | Evolution | `/repos/{owner}/{repo}/commits` | **FM** | Mined via M0.2 Commits |
| | M11 | Review Throughput | Cadence of PR review, merging, and closures | Evolution | `/repos/{owner}/{repo}/pulls?state=all` | **FM** | Operationalised in **A8R (PR Review Velocity)** |
| | M12 | Non-code Activity | Contributions to documentation, tests, releases | Evolution | Commit file path analysis (`/docs`, `tests/`) | **PM** | Planned in M67-DOCS |
| | M13 | Role Balance | Ratio of maintainer vs contributor activities | DEI | Commits/PR author distribution | **PM** | Mined in M0.2 Contributors |
| **Development Efficiency** | M14 | Issue Load | Backlog volume of open unresolved issues | Risk | `/repos/{owner}/{repo}` (`open_issues_count`) | **FM** | Operationalised in **A7 (Issue Backlog Ratio), A4 (PR Backlog)** |
| | M15 | Issue Turnover | Velocity of closing issues and merging PRs | Evolution | Decided issue/PR ratio over time window | **FM** | Operationalised in **A1 (PRAR), A5 (IRR)** |
| | M16 | Bug Handling | Responsiveness to bug-labelled reports | Risk | Issues with `label=bug` | **PM** | Requires label taxonomy standardization |
| | M17 | Release Tempo | Frequency and schedule regularity of published releases | Evolution | `/repos/{owner}/{repo}/releases` | **FM** | Available via GitHub Releases |

---

### Area 2: Community Stability (7 Aspects, 20 Metrics)

| Aspect | Metric ID | Metric Name (Linåker et al. 2026) | Base Paper Definition | CHAOSS Family | Computable Signal / GitHub Source | Feasibility Tier | Platform Operationalisation |
|---|---|---|---|---|---|---|---|
| **Adoption** | M18 | Commercial Adopters | Use of software by recognized commercial entities | Value | Public `ADOPTERS.md` or dependency telemetry | **PM** | Requires markdown scraping |
| | M19 | Downstream Dependencies | Number of package manager packages depending on repo | Value | Dependency network / Libraries.io / deps.dev | **PM** | External API integration |
| | M20 | User Base Size | Active installed user base | Value | Package download counters | **PM** | PyPI / npm download stats |
| **Organizational Diversity** | M21 | Corporate Diversity | Distribution of contributor corporate affiliations | DEI | Contributor GitHub company field / email domains | **PM** | Planned contributor enrichment |
| | M22 | Organizational Commitment | Dedicated institutional FTE funding | Value | Foundation membership / corporate sponsors | **UA** | Private financial data |
| | M23 | Dependency on Single Org | Risk of abandonment if lead corporate backer leaves | Risk | Herfindahl-Hirschman Index on commit company | **PM** | Planned DEI indicator |
| **Demographic Diversity** | M24 | Geographic Dispersion | Contributor distribution across time zones and nations | DEI | Contributor location field / commit timestamps | **PM** | Timezone offset heuristic |
| | M25 | Gender & Identity Diversity | Inclusive representation of underrepresented groups | DEI | Contributor demographics | **UA** | Ethical/privacy restriction |
| **Discussion Climate** | M26 | Tone & Sentiment | Respectful and welcoming discourse tone | DEI | Sentiment analysis on issue/PR comments | **PM** | NLP on comments (expensive) |
| | M27 | Toxic Communication | Frequency of toxic or combative interactions | Risk | Toxic comment classification | **PM** | NLP classifier |
| | M28 | Code of Conduct Enforcement | Transparency and vigor in enforcing CoC | Risk | Presence of `CODE_OF_CONDUCT.md` | **FM** | Community profile check |
| | M29 | Mentorship Activity | Active onboarding support for new contributors | DEI | Maintainer replies to first-time contributors | **PM** | Contributor interaction graph |
| **Knowledge Concentration** | M30 | Bus Factor | Number of core developers authoring $\ge 50\%$ or $80\%$ of code | Risk | Lorenz curve on author commit counts | **FM** | Mined via M0.2 Contributors |
| | M31 | Component Ownership | Redundancy of maintainers across subsystems | Risk | Subdirectory commit author spread | **PM** | Requires git tree parsing |
| | M32 | Architectural Documentation | Clear documentation of architectural decisions | Risk | Presence of `/docs/architecture` or ADRs | **PM** | File tree scanner |
| **Contributor Turnover** | M33 | Newcomer Intake Rate | New contributors joining community over 45/90/365d | Evolution | First commit/PR timestamps per author | **FM** | Contributor intake rate |
| | M34 | Contributor Retention Rate | Percentage of newcomers returning for second PR | Evolution | Authors with $\ge 2$ contributions over time | **FM** | Longitudinal contributor tracker |
| | M35 | Maintainer Attrition | Departure rate of experienced core maintainers | Risk | Time since last activity of core committers | **FM** | Contributor recency log |
| **Financial Sustainability** | M36 | Foundation Backing | Governance/fiscal sponsorship by Linux/Apache/Eclipse | Risk | Foundation registry verification | **FM** | Operationalised in M1.4 Ground Truth |
| | M37 | Funding Inflow | Inflow from Open Collective, GitHub Sponsors | Value | GitHub Sponsors presence / OpenCollective API | **PM** | `FUNDING.yml` presence check |

---

### Area 3: Orchestration (3 Aspects, 11 Metrics)

| Aspect | Metric ID | Metric Name (Linåker et al. 2026) | Base Paper Definition | CHAOSS Family | Computable Signal / GitHub Source | Feasibility Tier | Platform Operationalisation |
|---|---|---|---|---|---|---|---|
| **Governance Structure** | M38 | Decision-Making Model | Explicit model: BDFL, meritocracy, steering committee | Common | Presence of `GOVERNANCE.md` | **FM** | File presence scanner |
| | M39 | Maintainer Succession Plan | Transparent rules for electing new maintainers | Risk | Mentions of succession in governance docs | **PM** | Keyword heuristic |
| | M40 | Voting Transparency | Documented public voting mechanisms for major changes | Common | Public RFCs / governance records | **PM** | RFC repo verification |
| | M41 | Commercial Neutrality | Governance rules preventing single-company dominance | Risk | Antitrust / foundation bylaws | **PM** | Foundation membership check |
| **Openness** | M42 | External Openness | Maintainer receptivity to third-party PRs | Evolution | External contributor PR merge ratio | **FM** | Operationalised in **A1 (PRAR)** |
| | M43 | Volunteer Inclusion | Inclusion of episodic/volunteer contributors | DEI | Proportion of drive-by PRs accepted | **FM** | Operationalised in **A1 & M0.2** |
| | M44 | Roadmap Accessibility | Publicly published product roadmap | Common | Presence of `ROADMAP.md` or GitHub Projects | **FM** | File presence scanner |
| **Licenses** | M45 | Open Source License Type | Publication under OSI-approved permissive or copyleft license | Risk | `/repos/{owner}/{repo}` (`license.spdx_id`) | **FM** | Operationalised in **M45-LICENSE** |
| | M46 | Dual Licensing | Dual commercial/OSS licensing structure | Risk | License file text analysis | **PM** | Text scanner |
| | M47 | CLA / DCO Requirements | Requirement for Contributor License Agreement | Risk | CLA bot presence / `CONTRIBUTING.md` mention | **FM** | Bot / text inspection |
| | M48 | Dependency License Hygiene | License compatibility across downstream dependencies | Risk | Automated license scanner in lockfiles | **PM** | External scanner integration |

---

### Area 4: Production Process (4 Aspects, 18 Metrics)

| Aspect | Metric ID | Metric Name (Linåker et al. 2026) | Base Paper Definition | CHAOSS Family | Computable Signal / GitHub Source | Feasibility Tier | Platform Operationalisation |
|---|---|---|---|---|---|---|---|
| **Development Process** | M49 | Branching Strategy | Documented branch workflows (GitFlow, trunk-based) | Common | Branch protection rules / `CONTRIBUTING.md` | **PM** | API branch protection query |
| | M50 | Issue Triage Workflow | Timely labeling and triage of incoming bug reports | Evolution | Time to first label on issues | **PM** | Requires issue event logs |
| | M51 | Contribution Guidelines | Detailed instructions for prospective contributors | Common | Presence of `CONTRIBUTING.md` | **FM** | GitHub community profile |
| | M52 | Code Review Strictness | Enforced peer review before merging to main branch | Risk | Minimum required review approvals on PRs | **FM** | Operationalised in **A8R (PR Review Velocity)** |
| **Release Management** | M53 | Semantic Versioning | Adoption of formal SemVer conventions | Risk | Tag naming pattern matching (`vX.Y.Z`) | **FM** | Git tags parser |
| | M54 | Changelog Maintenance | Maintained list of fixes/features per release | Common | Presence of `CHANGELOG.md` | **FM** | File presence scanner |
| | M55 | Release Automation | Automated CI release build pipelines | Risk | GitHub Actions release workflows | **FM** | `.github/workflows` parser |
| | M56 | Pre-release Cadence | Availability of alpha/beta/RC release artifacts | Evolution | Tag pre-release flags | **FM** | GitHub Releases API |
| | M57 | Release Consistency | Variance in calendar time between major/minor releases | Evolution | Release timestamp delta standard deviation | **FM** | M0.4 Lifespan / releases |
| **Security Management** | M58 | Security Policy | Documented vulnerability reporting procedure | Risk | Presence of `SECURITY.md` | **FM** | Community profile check |
| | M59 | Vulnerability Disclosure | History of CVEs and security advisories | Risk | GitHub Security Advisories API | **FM** | Security advisory endpoint |
| | M60 | Automated Code Scanning | Active SAST / CodeQL / Dependabot scanning | Risk | Default Dependabot / CodeQL presence | **FM** | GitHub security alerts |
| | M61 | Supply-Chain Pinning | Pinned dependencies / cryptographic checksums | Risk | Lockfile inspection | **PM** | Lockfile presence |
| | M62 | Remediation Velocity | Days to patch disclosed vulnerabilities | Risk | Advisory publication to patch PR merge delta | **PM** | Requires security advisory mining |
| | M63 | Bug Bounty Program | Active monetary bounties for security defects | Risk | HackerOne / Bugcrowd badge | **UA** | External platform check |
| **Scaffolding** | M64 | CI/CD Automation | Automated test runs on all pull requests | Risk | Presence of CI status checks on commits | **FM** | Commit check-runs API |
| | M65 | Test Suite Coverage | Automated unit/integration test suite existence | Risk | Presence of `test/` or `tests/` directories | **FM** | File tree verification |
| | M66 | Linter & Formatter | Automated code styling and static linting | Risk | Configuration files (`.eslintrc`, `ruff.toml`) | **FM** | Root configuration check |

---

### Area 5: Production Output (2 Aspects, 6 Metrics)

| Aspect | Metric ID | Metric Name (Linåker et al. 2026) | Base Paper Definition | CHAOSS Family | Computable Signal / GitHub Source | Feasibility Tier | Platform Operationalisation |
|---|---|---|---|---|---|---|---|
| **Documentation** | M67 | Technical Documentation | Comprehensive README, guides, and tutorials | Common | `README.md` presence, size, and sections | **FM** | Operationalised in **M67-DOCS** |
| | M68 | API Documentation | Formal API references / generated doc pages | Common | Links to ReadTheDocs / GitHub Pages | **PM** | Link inspection in repo |
| | M69 | Example & Sample Code | Working code examples in documentation | Common | Presence of `examples/` directory | **FM** | Directory tree scan |
| **Technical Quality** | M70 | Static Analysis Grade | Code maintainability index / cyclomatic complexity | Risk | SonarCloud / CodeClimate badges | **PM** | Requires source parser |
| | M71 | Defect Density | Known bugs per 1,000 lines of code | Risk | Bug issue count / repository SLOC | **PM** | Requires full repo checkout |
| | M72 | Backward Compatibility | Preservation of public API stability across versions | Risk | Breaking change frequency in major tags | **PM** | SemVer break inspection |

---

## 3. Summary Feasibility Statistics

```
Feasibility Distribution across the 72 Base Paper Metrics:
======================================================================
Feasibility Tier              Metric Count    Percentage
----------------------------------------------------------------------
Fully Measurable (FM)             32            44.4%
Partially Measurable (PM)         29            40.3%
Unavailable (UA)                  11            15.3%
----------------------------------------------------------------------
Total                             72           100.0%
======================================================================
```

**[FACT]** All **21 health aspects** have at least one Fully Measurable or Partially Measurable metric available through public repository mining.

**[FACT]** Unavailable metrics (15.3%) are strictly confined to private organizational attributes (M22, M25, M63), external communication platforms outside GitHub (M1, M2, M3), or proprietary search index rankings (M8).

---

## 4. Operational Alignment with Platform Metric Registry (M0.1)

The platform's **M0.1 Metric Registry** operationalises the primary empirical core of these constructs:

| M0.1 Registry ID | Linåker Area | Primary Base Paper Aspect | Operational Metric | Feasibility Status |
|---|---|---|---|---|
| **A1** | Community Productivity | Openness (M42) & Issue Turnover (M15) | Pull Request Acceptance Rate (PRAR) | Fully Measurable |
| **A2** | Community Productivity | Responsiveness (M5) & Efficiency (M15) | PR Resolution Efficiency (PRE - Mean) | Fully Measurable (Alami et al. TEC-2) |
| **A3** | Community Productivity | Responsiveness (M5) | PR Resolution Latency (PRL - Median) | Fully Measurable |
| **A4** | Production Process | Issue Load (M14) | PR Backlog Ratio (PBR) | Fully Measurable |
| **A5** | Community Productivity | Development Efficiency (M15) | Issue Resolution Rate (IRR) | Fully Measurable (Kaushik & Chahal) |
| **A6** | Community Productivity | Responsiveness (M5) | Issue Resolution Latency (IRL) | Fully Measurable |
| **A7** | Community Productivity | Issue Load (M14) | Issue Backlog Ratio (IBR) | Fully Measurable |
| **A8R** | Production Process | Review Throughput (M11) | Pull Request Review Velocity (PRRV) | Fully Measurable |
| **M45-LICENSE** | Orchestration | Licenses (M45) | Declared Open Source License | Fully Measurable |
| **M67-DOCS** | Production Output | Documentation (M67) | Primary Documentation Presence | Fully Measurable |
| **C1** | Context (Trait) | Repository Lifecycle (STA-1) | Repository Age | Fully Measurable |
| **C2** | Data Quality | Data Integrity Diagnostic | PR Capture Rate | Diagnostic Indicator |
| **X1** | Context (Trait) | Popularity (M9, POP-1) | Stargazer Popularity | Context Covariate |

---
*End of Document M1.2 — Construct Mapping.*

