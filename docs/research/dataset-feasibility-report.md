# Dataset Feasibility Report

**Project:** AI-Assisted Developer Decision Support and Repository Intelligence Platform
**Dataset under review:** Kaggle archive — `repo_data.csv`, `issues_data.csv`, `pr_data.csv`
**Location inspected:** `C:\Users\rajes\Downloads\archive (2)\` *(read-only; not copied into the repository)*
**Date of inspection:** 2026-08-31
**Status:** Inspection only. No model built, no target selected, no project code modified.

---

## Evidence Legend

Every claim in this report carries one of four tags. This separation is required for a research
deliverable — a reviewer must be able to tell what the data says from what the analyst concluded.

| Tag | Meaning |
|---|---|
| **[FACT]** | Directly observed in the files by reading them. Reproducible by re-running the inspection. |
| **[DERIVED]** | Computed from the data by this inspection. The computation is stated so it can be checked. |
| **[REC]** | My recommendation. A judgement call, not a property of the data. |
| **[ASSUME]** | An assumption I am making, stated so it can be challenged or verified later. |

---

## Executive Summary

**[FACT]** The archive contains **3 CSV files** describing **28 repositories**, with **7,082 issue
events** and **248,320 pull-request events**.

**[FACT]** The single most consequential finding of this inspection is that the three columns named
`issue_contributors`, `pr_contributors` and `total_contributors` **do not count contributors.** They
count *distinct issue/PR titles*. This was verified against five competing hypotheses and matches on
**28 of 28 repositories exactly**, across values ranging from 0 to 35,594. See §2.3.

**[DERIVED]** Consequently, of the project's five health dimensions, **one (Contributor / Community
Health) has no supporting data at all**, and a second (Community Engagement / Popularity) has only
28 snapshot observations with no time series.

**[REC]** The dataset is **sufficient for a small working prototype at the pull-request event level**
and **insufficient at the repository level** (n = 28 is too small to train or validate any model).

---

# STEP 1 — Dataset Structure

## 1.1 File inventory

**[FACT]**

| File | Bytes | Rows | Cols | Unique repos | Exact dup rows | Dup `id` |
|---|---:|---:|---:|---:|---:|---:|
| `repo_data.csv` | 8,396 | 28 | 20 | 28 | 0 | 0 |
| `issues_data.csv` | 1,548,966 | 7,082 | 11 | 22 | 0 | 0 |
| `pr_data.csv` | 59,941,452 | 248,320 | 12 | 27 | 0 | 0 |

**[FACT]** Parsing note: `wc -l` reports 248,347 physical lines in `pr_data.csv` but the CSV parser
yields 248,320 records. The difference is caused by **newline characters embedded inside quoted
`title` fields**. Any future processing must use a proper CSV parser, never line-based splitting.

## 1.2 `repo_data.csv` — columns, types, missingness

**[FACT]** Missing values: **0.00% in every column**. One record per repository; no repository
appears twice.

| # | Column | Type | Unique | Missing % | Example |
|---:|---|---|---:|---:|---|
| 1 | `id` | str | 28 | 0.00 | `nz3ee913b5wmesq` |
| 2 | `created` | datetime str | 28 | 0.00 | `2024-09-03 00:22:08` |
| 3 | `updated` | datetime str | 27 | 0.00 | `2024-09-03 01:11:59` |
| 4 | `created_at` | datetime str (UTC) | 28 | 0.00 | `2019-08-24 00:14:52+00:00` |
| 5 | `description` | str | 28 | 0.00 | `Streamlit — A faster way to build…` |
| 6 | `forks` | int64 | 28 | 0.00 | `2969` |
| 7 | `full_name` | str | 28 | 0.00 | `streamlit/streamlit` |
| 8 | `name` | str | 28 | 0.00 | `streamlit` |
| 9 | `open_issues` | int64 | 28 | 0.00 | `938` |
| 10 | `stars` | int64 | 28 | 0.00 | `34364` |
| 11 | `updated_at` | datetime str (UTC) | 28 | 0.00 | `2024-09-02 23:26:32+00:00` |
| 12 | `repository` | str | 28 | 0.00 | `0` ← **corrupt for one row** |
| 13 | `issue_contributors` | int64 | 23 | 0.00 | `0` ← **mislabelled, see §2.3** |
| 14 | `pr_contributors` | int64 | 28 | 0.00 | `0` ← **mislabelled, see §2.3** |
| 15 | `total_contributors` | int64 | 28 | 0.00 | `0` ← **mislabelled, see §2.3** |
| 16 | `size_category` | str | 3 | 0.00 | `medium` |
| 17 | `stale` | bool | **1** | 0.00 | `False` ← **zero variance** |
| 18 | `stars_per_fork` | float64 | 27 | 0.00 | `11.57` |
| 19 | `stars_per_issue` | float64 | 28 | 0.00 | `36.64` |
| 20 | `contributor_per_star` | float64 | 17 | 0.00 | `0.0` |

### The 28 repositories

**[FACT]** All 28 are large, well-known open-source projects — not a random sample of GitHub.

| # | `full_name` | stars | forks | open_issues | issue rows | PR rows |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `streamlit/streamlit` | 34,364 | 2,969 | 938 | **0** | **0** |
| 2 | `Z4nzu/hackingtool` | 48,056 | 5,181 | 73 | 19 | 119 |
| 3 | `OpenBMB/MiniCPM-V` | 11,445 | 803 | 80 | 196 | 66 |
| 4 | `microsoft/playwright` | 65,329 | 3,552 | 637 | 589 | 14,806 |
| 5 | `dagster-io/dagster` | 11,096 | 1,393 | 2,735 | 152 | 15,123 |
| 6 | `facebook/react` | 226,971 | 46,279 | 829 | 168 | 15,948 |
| 7 | `frappe/erpnext` | 19,543 | 6,985 | 1,902 | 1,165 | 26,249 |
| 8 | `tensorflow/tensorflow` | 185,313 | 74,151 | 4,550 | 586 | 34,726 |
| 9 | `elastic/elasticsearch` | 69,349 | 24,549 | 4,551 | 488 | 36,925 |
| 10 | `pallets/flask` | 67,474 | 16,143 | 10 | 9 | 2,578 |
| 11 | `keras-team/keras` | 61,554 | 19,416 | 240 | 119 | 7,418 |
| 12 | `numpy/numpy` | 27,468 | 9,809 | 2,122 | 188 | 14,567 |
| 13 | `apache/kafka` | 28,285 | 13,814 | 1,136 | **0** | 17,092 |
| 14 | `hashicorp/terraform` | 42,087 | 9,474 | 1,967 | 190 | 14,358 |
| 15 | `django/django` | 79,035 | 31,476 | 241 | **0** | 18,482 |
| 16 | `grafana/grafana` | 63,622 | 11,932 | 4,120 | 1,280 | 18,821 |
| 17 | `ansible/ansible` | 62,254 | 23,789 | 863 | 132 | 1,000 |
| 18 | `apache/airflow` | 36,129 | 14,024 | 1,068 | 330 | 1,000 |
| 19 | `kubernetes/kubernetes` | 109,616 | 39,253 | 2,610 | 627 | 701 |
| 20 | `apache/httpd` | 3,522 | 1,123 | 64 | **0** | 427 |
| 21 | `torvalds/linux` | 177,813 | 53,112 | 383 | **0** | 897 |
| 22 | `google/guava` | 49,984 | 10,847 | 716 | 14 | 1,000 |
| 23 | `npm/cli` | 8,328 | 3,059 | 681 | 114 | 1,001 |
| 24 | `git/git` | 51,700 | 25,474 | 193 | **0** | 1,000 |
| 25 | `babel/babel` | 43,145 | 5,628 | 789 | 49 | 1,000 |
| 26 | `webpack/webpack` | 64,547 | 8,770 | 258 | 68 | 1,000 |
| 27 | `swiftlang/swift` | 67,260 | 10,325 | 7,563 | 243 | 1,014 |
| 28 | `nodejs/node` | 106,396 | 28,986 | 2,154 | 356 | 1,002 |

## 1.3 `issues_data.csv` — columns, types, missingness

**[FACT]**

| # | Column | Type | Unique | Missing % | Meaning |
|---:|---|---|---:|---:|---|
| 1 | `id` | str | 7,082 | 0.00 | Surrogate event key, unique |
| 2 | `created` | datetime str | 3,436 | 0.00 | **Scrape/ingest** time |
| 3 | `updated` | datetime str | 3,436 | 0.00 | **Scrape/ingest** time |
| 4 | `closed_at` | datetime str (UTC) | 3,827 | **45.33** | Issue closure time; null ⟺ still open |
| 5 | `created_at` | datetime str (UTC) | 7,079 | 0.00 | Issue opening time |
| 6 | `number` | int64 | 6,953 | 0.00 | GitHub issue number |
| 7 | `repository` | str | **22** | 0.00 | **Join key** → `repo_data.name` |
| 8 | `state` | str | 2 | 0.00 | `closed` (3,872) / `open` (3,210) |
| 9 | `title` | str | 7,019 | 0.00 | Issue title text |
| 10 | `updated_at` | datetime str (UTC) | 6,966 | 0.00 | Last activity time |
| 11 | `resolution_time_days` | float64 | 3,852 | 0.00 | Days to close; **`-1` = not closed** |

## 1.4 `pr_data.csv` — columns, types, missingness

**[FACT]**

| # | Column | Type | Unique | Missing % | Meaning |
|---:|---|---|---:|---:|---|
| 1 | `id` | str | 248,320 | 0.00 | Surrogate event key, unique |
| 2 | `created` | datetime str | 67,959 | 0.00 | **Scrape/ingest** time |
| 3 | `updated` | datetime str | 67,959 | 0.00 | **Scrape/ingest** time |
| 4 | `closed_at` | datetime str (UTC) | 239,345 | **3.25** | PR closure time; null ⟺ still open |
| 5 | `created_at` | datetime str (UTC) | 247,989 | 0.00 | PR opening time |
| 6 | `merged_at` | datetime str (UTC) | 183,657 | **25.97** | Merge time; null ⟺ never merged |
| 7 | `number` | int64 | 94,016 | 0.00 | GitHub PR number |
| 8 | `repository` | str | **27** | 0.00 | **Join key** → `repo_data.name` |
| 9 | `state` | str | 3 | 0.00 | `merged` 183,836 / `closed` 56,405 / `open` 8,079 |
| 10 | `title` | str | 229,203 | 0.00 | PR title text |
| 11 | `updated_at` | datetime str (UTC) | 237,184 | 0.00 | Last activity time |
| 12 | `merge_time_days` | float64 | 111,224 | 0.00 | Days to merge; **`-1` = not merged** |

## 1.5 Date / time columns and coverage

**[FACT]** Two distinct families of timestamp exist, and confusing them would be a serious error.

| Family | Columns | Range observed | What it actually is |
|---|---|---|---|
| **Ingest** | `created`, `updated` (all 3 files) | 2024-09-03 → 2024-09-06 | When the *scraper wrote the row*. Carries no information about the repository. |
| **Domain** | `created_at`, `updated_at`, `closed_at`, `merged_at` | 2008-07-23 → 2024-09-06 | Real GitHub event times. |

**[FACT]** Domain date ranges:

| File | Column | Min | Max | Null % |
|---|---|---|---|---:|
| repo | `created_at` (repo birth) | 2008-07-23 14:21 | 2024-01-29 05:30 | 0.00 |
| repo | `updated_at` | 2024-09-02 23:26 | 2024-09-06 11:30 | 0.00 |
| issues | `created_at` | 2011-05-27 11:44 | 2024-09-06 08:32 | 0.00 |
| issues | `closed_at` | 2013-10-03 12:46 | 2024-09-05 21:02 | 45.33 |
| pr | `created_at` | 2010-09-01 03:05 | 2024-09-06 10:59 | 0.00 |
| pr | `closed_at` | 2010-09-01 16:46 | 2024-09-06 05:45 | 3.25 |
| pr | `merged_at` | 2010-09-15 18:40 | 2024-09-06 05:45 | 25.97 |

**[DERIVED]** The observation snapshot is **2024-09-06 11:30:17 UTC** (max of `repo_data.updated_at`).
**[DERIVED]** Repository age at snapshot: min 221 days, median 3,790 days, max 5,888 days (~16 years).

## 1.6 Duplicate analysis

**[FACT]**

| Check | repo | issues | pr |
|---|---:|---:|---:|
| Exact full-row duplicates | 0 | 0 | 0 |
| Duplicate `id` | 0 | 0 | 0 |
| Duplicate `(repository, number)` | n/a | 0 | 0 |

**[DERIVED]** There is **no deduplication decision to make** in this dataset. This is a meaningful
difference from the earlier `repository_data.csv` dataset, where duplicate names had to be preserved
while exact row duplicates were dropped.

## 1.7 Multiple records per repository

**[FACT]**

- `repo_data.csv` — **one row per repository**. This is a snapshot dimension table, not a history.
- `issues_data.csv` — **many rows per repository** (0 to 1,280). Event table.
- `pr_data.csv` — **many rows per repository** (0 to 36,925). Event table.

## 1.8 File relationships and the join key

**[FACT]** The schema is a **star schema**:

```
                        repo_data.csv   (dimension, 28 rows, 1 row per repo)
                              |
                    join on:  name  ==  repository
                              |
              +---------------+---------------+
              |                               |
     issues_data.csv                     pr_data.csv
     (fact, 7,082 rows)                (fact, 248,320 rows)
     22 repos covered                  27 repos covered
```

**[FACT]** Join key verification:

| Check | Result |
|---|---|
| `issues.repository` ⊆ `repo_data.name` | **True** — 22 of 22 match |
| `pr.repository` ⊆ `repo_data.name` | **True** — 27 of 27 match |
| Orphan repos in `issues` not in `repo_data` | **0** |
| Orphan repos in `pr` not in `repo_data` | **0** |
| `repo_data.repository == repo_data.name` | **27 of 28** |

**[FACT]** **Data-quality defect.** In `repo_data.csv`, the row for `streamlit/streamlit` has
`repository = '0'` instead of `'streamlit'`. This is the only mismatch. That repository has
**0 issue rows and 0 PR rows** — it is the one repository with no event data at all.

**[REC]** Join on `repo_data.name`, **not** on `repo_data.repository`. The `repository` column in
`repo_data.csv` is redundant with `name` and is corrupt for one row; it should be dropped.

**[FACT]** Repositories present in `repo_data` but absent from the event files:

- No issue rows (6): `streamlit`, `kafka`, `django`, `httpd`, `linux`, `git`
- No PR rows (1): `streamlit`

**[FACT]** Issue numbers and PR numbers are **disjoint within each repository** (checked on 5 repos;
overlap = 0 in every case). This is consistent with GitHub's single shared numbering sequence for
issues and PRs, and confirms the two files partition one namespace rather than double-count it.

---

# STEP 2 — Mapping the Dataset to the Five Health Dimensions

## 2.1 Dimension 1 — Development & Maintenance Health

**Available raw columns:** `pr.created_at`, `pr.closed_at`, `pr.merged_at`, `pr.state`,
`pr.merge_time_days`, `pr.number`, `issues.created_at`, `issues.closed_at`, `issues.state`,
`repo.created_at`, `repo.updated_at`.

**[DERIVED] Metrics that CAN be calculated:**

| Metric | Basis |
|---|---|
| PR throughput per period (count of PRs created per month/year) | `pr.created_at` |
| Issue throughput per period | `issues.created_at` |
| Repository age in days | `repo.updated_at − repo.created_at` |
| Days since last observed PR | snapshot − max(`pr.created_at`) |
| Days since last observed issue | snapshot − max(`issues.created_at`) |
| Recent activity volume (PRs in last 90 / 365 days) | `pr.created_at` |
| Development-activity trend (slope of monthly PR counts) | `pr.created_at` — **only for repos with sufficient months, see §2.1 caveat** |

**[FACT] Metrics that CANNOT be calculated, and why:**

| Metric | Why not |
|---|---|
| **Commit frequency** | There is **no commit file and no commit column** in any of the three files. |
| **Commit trend / code churn** | Same — no commit data. |
| **Lines added / deleted** | No diff, additions, deletions, or `changed_files` columns. |
| **Release cadence** | No release or tag data. |
| **Branch activity** | No branch column. |
| **Code-review depth** | No review, reviewer, or review-comment columns. |
| **True "last push" date** | `repo.updated_at` is the scrape-window metadata timestamp (2024-09-02 → 2024-09-06), not a real push time. |

**[FACT] Caveat — temporal coverage is unequal.** Distinct months containing at least one PR, per
repository, ranges from **3 months** (`kubernetes`, `airflow`, `swift`) to **169 months**
(`numpy`). Any trend-based metric is only defensible for the subset with long coverage.

## 2.2 Dimension 2 — Contributor / Community Health

**[FACT] Available raw columns: NONE.**

**[FACT]** A regex sweep across all 43 columns in all three files for
`user|author|login|actor|assign|label|comment|commit|review|milestone|branch|language|licen|topic|readme|ci|test|watch|subscrib`
returned **zero matches**.

**[FACT] Metrics that CANNOT be calculated:**

| Metric | Why not |
|---|---|
| Number of unique contributors | No author/login column on any event. |
| New vs returning contributors | Same. |
| Contributor retention / churn | Same. |
| Bus factor / truck factor | Same. |
| Contribution concentration (Gini, top-N share) | Same. |
| Maintainer responsiveness by person | Same. |
| Bot vs human contribution share | No author; only weak title heuristics (see §3). |
| Organisational diversity | No company/affiliation data. |

## 2.3 ⚠ Critical finding — the `*_contributors` columns are mislabelled

**[FACT]** `repo_data.csv` contains `issue_contributors`, `pr_contributors` and
`total_contributors`. These names imply contributor counts. **They are not contributor counts.**

**[DERIVED]** I tested five candidate definitions against all 28 repositories:

| Hypothesis | `issue_contributors` matches | `pr_contributors` matches |
|---|---:|---:|
| = number of event rows | 15 / 28 | 1 / 28 |
| = number of distinct `created_at` | 15 / 28 | 1 / 28 |
| = number of distinct `number` | 15 / 28 | 1 / 28 |
| = number of distinct `updated_at` | 12 / 28 | 1 / 28 |
| **= number of distinct `title`** | **28 / 28** | **28 / 28** |

**[FACT]** The match is exact on every repository, over values spanning 0 to 35,594. For example
`elasticsearch` has `pr_contributors = 35,594` and exactly 35,594 distinct PR titles among its
36,925 PR rows. `erpnext` has `issue_contributors = 1,165` and exactly 1,165 distinct issue titles.

**[FACT]** `total_contributors == issue_contributors + pr_contributors` on 28 / 28 rows.

**[DERIVED]** Therefore:
- These columns measure **title vocabulary size**, which is a function of event volume and title
  repetition. They contain **no contributor information whatsoever**.
- The claim `elasticsearch` has 35,594 contributors is false by a wide margin; the project's real
  contributor count is in the low thousands.
- `contributor_per_star` (= `total_contributors / stars`) inherits the same defect and is therefore
  **also meaningless as a community metric**.

**[REC]** **Do not use `issue_contributors`, `pr_contributors`, `total_contributors`, or
`contributor_per_star` as contributor or community features.** Doing so would put a fabricated
construct into the research, and the error would be detectable by any reviewer who checks. If they
are used at all, they must be renamed to `distinct_issue_titles` / `distinct_pr_titles` and treated
as event-volume proxies.

**[REC]** **They are also a leakage hazard.** Because `pr_contributors` is an exact function of the
contents of `pr_data.csv`, joining it onto PR-level training rows would leak information about the
size and composition of the PR table into every row. Exclude them from any PR-level model.

## 2.4 Dimension 3 — Issue & Pull Request Health

**[FACT]** This is the **only dimension the dataset supports well.**

**Available raw columns:** `pr.state`, `pr.created_at`, `pr.closed_at`, `pr.merged_at`,
`pr.merge_time_days`, `pr.title`, `issues.state`, `issues.created_at`, `issues.closed_at`,
`issues.resolution_time_days`, `issues.title`, `repo.open_issues`.

**[DERIVED] Metrics that CAN be calculated:**

| Metric | Basis | Repos covered |
|---|---|---:|
| PR merge rate | `state == 'merged'` share | 27 |
| PR rejection rate | `state == 'closed'` share | 27 |
| PR open-backlog rate | `state == 'open'` share | 27 |
| Median / p90 time-to-merge | `merge_time_days` where ≠ −1 | 26 |
| Issue closure rate | `state == 'closed'` share | 22 |
| Median issue resolution time | `resolution_time_days` where ≠ −1 | 21 |
| Open-issue backlog (snapshot) | `repo.open_issues` | 28 |
| PR/issue ratio | row counts per repo | 22 |

**[FACT] Metrics that CANNOT be calculated:**

| Metric | Why not |
|---|---|
| **Time to first response** | No comment or comment-timestamp data. |
| **Review turnaround time** | No review events. |
| **Number of review comments per PR** | No comment count column. |
| **Number of review iterations** | No review data. |
| **Issue triage rate** | No label or milestone data — triage cannot be observed. |
| **Bug vs feature vs question split** | No labels. Only unreliable title keywords (see §3). |
| **Stale-issue / stale-PR rate by policy** | Requires last-comment time; only `updated_at` exists, which conflates all activity types. |
| **PR size (lines changed)** | No diff statistics. |
| **Reopened issue rate** | No event log of state transitions — only the final state. |

## 2.5 Dimension 4 — Community Engagement / Popularity

**Available raw columns:** `repo.stars`, `repo.forks`, `repo.open_issues`, `repo.stars_per_fork`,
`repo.stars_per_issue`, `repo.size_category`.

**[DERIVED] Metrics that CAN be calculated:** stars, forks, star-to-fork ratio, size category —
**all as a single snapshot, for 28 repositories only.**

**[FACT] Metrics that CANNOT be calculated:**

| Metric | Why not |
|---|---|
| **Star growth rate / velocity** | Only one snapshot exists. No historical star counts. |
| **Fork growth rate** | Same — one snapshot. |
| **Watchers / subscribers** | **No watchers column exists in this dataset.** |
| **Downloads, dependents, package usage** | Not present. |
| **Traffic / views / clones** | Not present. |
| **Community sentiment** | No comment bodies. |

**[DERIVED]** `size_category` is an exact deterministic function of `stars`
(`< 10,000` → small; `10,000 – 100,000` → medium; `≥ 100,000` → large — verified on 28 / 28 rows).
It adds no information beyond `stars` and would be perfectly collinear with it.

**[DERIVED]** `stars_per_fork`, `stars_per_issue` and `contributor_per_star` are exact arithmetic
functions of columns already present (verified to ±0.02 on 28 / 28 rows). They are **derived
convenience columns, not independent measurements**, and contribute no new information.

## 2.6 Dimension 5 — Sustainability / Maintenance Risk

**Available raw columns:** `pr.created_at`, `issues.created_at`, `pr.state`, `issues.state`,
`repo.created_at`, `repo.open_issues`, `repo.stale`.

**[DERIVED] Metrics that CAN be calculated (as proxies only):**

| Metric | Basis | Caveat |
|---|---|---|
| Days since last observed PR / issue | snapshot − max(`created_at`) | Bounded by the scrape window, not by real inactivity |
| Recent-activity ratio (last 365 d ÷ lifetime) | `pr.created_at` | Distorted by the ~1,000-row cap (§4.3) |
| Backlog pressure | `repo.open_issues ÷ recent closure rate` | Denominator is sampled |
| Abandonment proxy | zero events in the last N days | Only 28 repos, all currently active |

**[FACT] Metrics that CANNOT be calculated:**

| Metric | Why not |
|---|---|
| **Bus factor / key-person risk** | No contributor identity data (§2.2). This is the single most important sustainability metric and it is unavailable. |
| **Maintainer succession / handover** | Same. |
| **Funding / sponsorship risk** | Not present. |
| **License risk** | **No license column in this dataset.** |
| **Security-posture risk** | No CVE, advisory, or dependency data. |
| **Dependency / supply-chain risk** | No dependency data. |
| **Archival / deprecation status** | `stale` is **constant `False` on all 28 rows** — zero variance, no signal. |
| **Governance risk** | No CODE_OF_CONDUCT, CONTRIBUTING, or maintainer-policy data. |

**[FACT]** All 28 repositories are large, currently-maintained flagship projects. There are **no
unhealthy or abandoned repositories in this sample**. Any sustainability-risk model trained on it
would have no negative class to learn from.

## 2.7 Dimension coverage summary

**[DERIVED]**

| # | Dimension | Verdict | Basis |
|---:|---|---|---|
| 1 | Development & Maintenance Health | **PARTIAL** | PR/issue event rates available; **no commit data at all** |
| 2 | Contributor / Community Health | **NOT SUPPORTED** | No author column anywhere; the `*_contributors` columns are title counts |
| 3 | Issue & PR Health | **FULLY SUPPORTED** | State, timestamps and durations all present and internally consistent |
| 4 | Community Engagement / Popularity | **SNAPSHOT ONLY** | Single observation, n = 28, no time series, no watchers |
| 5 | Sustainability / Maintenance Risk | **WEAK PROXY ONLY** | Activity recency computable; bus factor, license, governance all unavailable; `stale` has zero variance |

---

# STEP 3 — Metric Feasibility Table

**[DERIVED]** "Supported" means the metric can be computed from columns that actually exist, without
inventing data.

| # | Metric | Definition | Required columns | Available | Dimension | Supported |
|---:|---|---|---|:---:|---|:---:|
| M1 | PR merge rate | merged PRs ÷ decided PRs | `pr.state` | **YES** | 3 | **YES** |
| M2 | PR rejection rate | closed-unmerged ÷ decided PRs | `pr.state` | **YES** | 3 | **YES** |
| M3 | Median time-to-merge | median of `merge_time_days` ≠ −1 | `pr.merge_time_days` | **YES** | 3 | **YES** |
| M4 | p90 time-to-merge | 90th pct of `merge_time_days` ≠ −1 | `pr.merge_time_days` | **YES** | 3 | **YES** |
| M5 | PR open-backlog rate | open PRs ÷ all PRs | `pr.state` | **YES** | 3 | **YES** |
| M6 | Issue closure rate | closed ÷ all issues | `issues.state` | **YES** | 3 | **YES** |
| M7 | Median issue resolution time | median of `resolution_time_days` ≠ −1 | `issues.resolution_time_days` | **YES** | 3 | **YES** |
| M8 | Repository age | snapshot − `repo.created_at` | `repo.created_at`, `repo.updated_at` | **YES** | 1 | **YES** |
| M9 | PR activity recency | snapshot − max(`pr.created_at`) | `pr.created_at` | **YES** | 1, 5 | **YES** (window-bounded) |
| M10 | Recent PR volume (90 / 365 d) | count in window | `pr.created_at` | **YES** | 1, 5 | **YES** (cap-distorted) |
| M11 | Monthly PR trend | slope of monthly counts | `pr.created_at` | **YES** | 1 | **PARTIAL** — only repos with long coverage |
| M12 | Star-to-fork ratio | `stars ÷ forks` | `repo.stars`, `repo.forks` | **YES** | 4 | **YES** (already present) |
| M13 | Open-issue backlog | `repo.open_issues` | `repo.open_issues` | **YES** | 3, 5 | **YES** (snapshot) |
| M14 | PR-to-issue ratio | PR rows ÷ issue rows | both files | **YES** | 1, 3 | **PARTIAL** — sampling ratios differ per file |
| M15 | Unique contributors | distinct authors | *author column* | **NO** | 2 | **NO** — column does not exist |
| M16 | Bus factor | contribution concentration | *author column* | **NO** | 2, 5 | **NO** — column does not exist |
| M17 | Contributor growth | new authors per period | *author column* | **NO** | 2 | **NO** — column does not exist |
| M18 | Commit frequency | commits per period | *commit data* | **NO** | 1 | **NO** — no commit file |
| M19 | Code churn | lines added/deleted | *diff stats* | **NO** | 1 | **NO** — not collected |
| M20 | Time to first response | first comment − created | *comment timestamps* | **NO** | 3 | **NO** — no comment data |
| M21 | Review depth | reviews/comments per PR | *review data* | **NO** | 3 | **NO** — no review data |
| M22 | Bug ratio | bug-labelled ÷ all issues | *labels* | **NO** | 3 | **NO** — no labels; titles unreliable |
| M23 | Star growth rate | Δ stars ÷ Δ time | *star history* | **NO** | 4 | **NO** — single snapshot |
| M24 | License presence | license field | *license column* | **NO** | 5 | **NO** — column does not exist |
| M25 | Documentation quality | README/docs metrics | *doc data* | **NO** | — | **NO** — not collected |
| M26 | CI/CD presence | workflow config | *CI data* | **NO** | 1 | **NO** — not collected |
| M27 | Archived / deprecated flag | `repo.stale` | `repo.stale` | present but **constant** | 5 | **NO** — zero variance |
| M28 | Bot contribution share | bot authors ÷ all | *author column* | **NO** | 2 | **NO** — titles only, ~1.4% detectable |

**[DERIVED] Score: 14 metrics fully supported, 3 partially, 11 impossible.**

---

# STEP 4 — Historical-Data Analysis

## 4.1 The critical distinction

**[DERIVED]**

| Type | Definition | Present here? |
|---|---|---|
| **A. Point-in-time / snapshot** | One observation per entity at one moment; no history | `repo_data.csv` — **all 20 columns** |
| **B. Event-level historical** | One row per event, each with its own timestamp | `issues_data.csv`, `pr_data.csv` |

**[FACT]** This dataset is a **hybrid**: repository attributes are snapshot-only, while issue and PR
activity is genuine event-level history. This is the central structural fact for prototype design.

## 4.2 What history exists — item by item

**[FACT]**

| History type | Present | Evidence |
|---|:---:|---|
| **Repository history** | ✗ **NO** | One row per repo. `stars`, `forks`, `open_issues` have a single value each. No panel data. |
| **Issue history** | ~ **PARTIAL** | 7,082 event rows with `created_at` / `closed_at`, 2011-05-27 → 2024-09-06. But heavily sampled (§4.3) and missing for 6 of 28 repos. |
| **PR history** | ✓ **YES** | 248,320 event rows with `created_at` / `closed_at` / `merged_at`, 2010-09-01 → 2024-09-06. Sampled for 9 repos (§4.3). |
| **Commit history** | ✗ **NO** | No commit file. No commit-related column in any file. |
| **Contributor history** | ✗ **NO** | No author, user, login, or actor column anywhere (verified by regex sweep across all 43 columns). |
| **Engagement history** | ✗ **NO** | Stars and forks exist only as one snapshot value. No star/fork time series. No watchers column. |
| **Timestamps** | ✓ **YES** | All timezone-aware UTC. Two families — ingest vs domain (§1.5). |
| **Resolution / closure times** | ✓ **YES** | `issues.resolution_time_days`, exact, with `-1` sentinel. |
| **Merge times** | ✓ **YES** | `pr.merge_time_days`, exact, with `-1` sentinel. |
| **Repository age** | ✓ **YES** | `repo.created_at` → snapshot. Range 221 – 5,888 days. |

## 4.3 ⚠ Sampling caps — the history is incomplete and unevenly so

**[FACT]** Nine repositories have **exactly or almost exactly 1,000 PR rows**: `git` (1,000),
`guava` (1,000), `airflow` (1,000), `ansible` (1,000), `webpack` (1,000), `babel` (1,000),
`cli` (1,001), `node` (1,002), `swift` (1,014).

**[DERIVED]** This is a **collection cap**, almost certainly an API pagination limit, not a real
property of those projects. `ansible` genuinely has ~83,901 issues/PRs by its highest observed
number, but only 1,000 PR rows are present.

**[DERIVED]** Capture rate — rows present ÷ highest issue/PR number observed:

| Repository | Issue capture | PR capture |
|---|---:|---:|
| `kafka` | — | **100.0%** |
| `django` | — | 99.7% |
| `linux` | — | 94.5% |
| `httpd` | — | 89.5% |
| `dagster` | 0.6% | 62.5% |
| `erpnext` | 2.7% | 61.0% |
| `react` | 0.5% | 51.7% |
| `numpy` | 0.7% | 53.3% |
| `tensorflow` | 0.8% | 46.3% |
| `playwright` | 1.8% | 45.7% |
| `elasticsearch` | 0.4% | 32.8% |
| `grafana` | 1.4% | 20.3% |
| `babel` | 0.3% | 5.9% |
| `node` | 0.6% | **1.8%** |
| `swift` | 0.3% | **1.3%** |
| `ansible` | 0.2% | **1.2%** |
| `kubernetes` | 0.5% | **0.6%** |

**[DERIVED]** For the capped repositories the sample is a **recent window**, not a random sample.
Evidence: for `airflow`, `kubernetes`, `swift` and `node`, the count of PRs created in the last 365
days **equals the total PR count** (1,000 / 1,000; 701 / 701; 1,014 / 1,014; 1,002 / 1,002). Their
entire PR history in this file falls inside one year.

**[DERIVED]** Consequences that must be respected:

1. **Repository-level aggregates are not comparable across repositories.** `kafka`'s merge rate is
   computed over 100% of its PRs; `kubernetes`'s over 0.6%, and only recent ones.
2. **Cross-repository ranking on any volume-based metric is invalid** without a normalisation that
   accounts for the cap.
3. **Trend metrics are unsafe for capped repos** — their series begins where the cap begins, which
   looks like a sudden burst of activity that never happened.

**[REC]** Restrict any repository-level comparison to the repositories with high capture, or make
every metric a **rate/proportion rather than a count**, and state the caveat explicitly.

## 4.4 Internal consistency verification

**[FACT]** I verified the derived duration columns rather than trusting them:

| Check | Result |
|---|---|
| `issues.resolution_time_days == (closed_at − created_at)` in days | max deviation **5.0 × 10⁻¹²** — exact |
| `pr.merge_time_days == (merged_at − created_at)` in days | max deviation **4.9 × 10⁻¹²** — exact |
| `resolution_time_days == -1` ⟺ `closed_at` is null | **True** — 3,210 = 3,210 |
| `merge_time_days == -1` ⟺ `merged_at` is null | **True** — 64,484 = 64,484 |
| Negative durations (excluding the −1 sentinel) | **0** in both files |
| `state == 'merged'` ⟺ `merged_at` is not null | **True** — 183,836 / 183,836; 0 exceptions |
| `state == 'closed'` with null `closed_at` | **0** |
| `state == 'open'` with non-null `closed_at` | **0** |

**[DERIVED]** The state machine is **internally consistent with no contradictions**. This is a
genuinely clean dataset in that respect.

**[REC]** `-1` must be converted to `NaN` before any statistical use. Treating `-1` as a duration
would drag every mean toward zero and corrupt 45% of issue rows and 26% of PR rows.

---

# STEP 5 — Prototype Target Feasibility

**[REC]** I am explicitly **not** defaulting to `stars`. With 28 repositories, `stars` cannot be a
target for any model — 28 rows is below the threshold at which a train/test split is meaningful.

## Candidate targets, ranked most to least suitable

### T1 — PR merge outcome (merged vs closed-unmerged) — **RANK 1, RECOMMENDED**

| Property | Value |
|---|---|
| **Type** | Binary classification |
| **Source column** | `pr.state` |
| **[FACT] Labelled rows** | **240,241** (183,836 merged + 56,405 closed-unmerged); 8,079 open rows excluded as undecided |
| **[DERIVED] Class balance** | 76.5% merged / 23.5% rejected — imbalanced but workable |
| **Why meaningful** | Directly operationalises Dimension 3 (Issue & PR Health). "Will this contribution be accepted?" is a real decision-support question for the platform. |
| **[FACT] Leakage risk — HIGH, and controllable** | `merged_at`, `merge_time_days` and `closed_at` are **direct functions of the label** and must be dropped. So must `pr_contributors` / `total_contributors` / `contributor_per_star` (§2.3), which are functions of the PR table itself. |
| **Usable features** | `title` (text), `created_at` (hour/weekday/month/age-at-creation), `repository`, `number`, and repo-level snapshot attributes joined in (`stars`, `forks`, `open_issues`, `repo_age_days`) |
| **[FACT] Limitations** | (a) Survivorship — the 8,079 open PRs are excluded, and open PRs are disproportionately old/contentious; (b) sampling caps mean 9 repos contribute only recent PRs; (c) only 27 repositories, so `repository` is a 27-level categorical that could dominate; (d) three repos (`linux`, `git`, `httpd`) do not use GitHub PRs for real review, so their merge rates (1.1%, 0.1%, 0.0%) reflect workflow, not quality. |
| **Suitable for demonstrating the project?** | **YES** — this is the strongest option |

### T2 — PR time-to-merge — **RANK 2**

| Property | Value |
|---|---|
| **Type** | Regression (recommend `log1p` transform) |
| **Source column** | `pr.merge_time_days` where ≠ −1 |
| **[FACT] Rows** | **183,836** |
| **[DERIVED] Distribution** | median 0.57 d, mean 7.16 d, p75 3.15 d, max 2,031 d — extremely right-skewed |
| **Why meaningful** | Maintenance efficiency / responsiveness, Dimension 3. Predicts "how long will review take?" |
| **[FACT] Leakage risk — HIGH** | `merged_at`, `closed_at`, `state`, `updated_at` must all be dropped — each encodes the answer. |
| **[FACT] Limitations** | Conditioned on merge having happened (selection bias — never-merged PRs are excluded entirely); heavy skew requires a log transform; Jensen's inequality will make back-transformed predictions systematically low. |
| **Suitable?** | **YES**, but harder to score well than T1 |

### T3 — Issue resolution time — **RANK 3**

| Property | Value |
|---|---|
| **Type** | Regression |
| **Source column** | `issues.resolution_time_days` where ≠ −1 |
| **[FACT] Rows** | **3,872 only** |
| **[DERIVED] Distribution** | median 15.1 d, mean 233.5 d, max 4,237 d |
| **Why meaningful** | Issue-handling efficiency, Dimension 3 |
| **[FACT] Limitations** | Small sample; covers only 21 repositories; issue capture rate is **below 3% for most repos**, so this is a thin and possibly non-random slice; only `title` and timestamps as features. |
| **Suitable?** | **MARGINAL** — usable as a secondary experiment, not the headline |

### T4 — Issue closed vs open — **RANK 4**

| Property | Value |
|---|---|
| **Type** | Binary classification |
| **Source column** | `issues.state` |
| **[FACT] Rows** | 7,082 — 54.7% closed / 45.3% open, well balanced |
| **[FACT] Leakage / validity risk — SEVERE** | This target is **right-censored**. An "open" issue is not a negative example; it is an issue that has not closed *yet*. A model trained on it learns "how recently was this opened", not "will it be resolved". Recency is the dominant signal and it is an artefact of the snapshot date. |
| **Suitable?** | **NO** — attractive on balance, invalid on semantics. Would need survival analysis, not classification. |

### T5 — Repository-level health aggregates — **RANK 5**

| Property | Value |
|---|---|
| **Type** | Regression or classification on a constructed index |
| **[FACT] Rows** | **27–28** |
| **Why unsuitable** | 28 rows cannot support a train/test split, cross-validation, or any claim of generalisation. Additionally, the aggregates are **not comparable across repositories** because of the sampling caps (§4.3). |
| **Suitable?** | **NO** for modelling. **YES** for descriptive reporting and dashboard demonstration. |

### T6 — Stars regression — **RANK 6**

**[FACT]** 28 rows. **Not viable.** Additionally, `forks` is a popularity co-signal measured in the
same snapshot and would leak, exactly as in the earlier `repository_data.csv` analysis.

### T7 — `stale` flag — **RANK 7, NOT VIABLE**

**[FACT]** `stale` is `False` on **all 28 rows**. Zero variance. There is no target here at all.

## 5.1 Ranked summary

**[DERIVED]**

| Rank | Target | Type | Rows | Verdict |
|---:|---|---|---:|---|
| **1** | **PR merge outcome** | Binary classification | **240,241** | **Recommended** |
| 2 | PR time-to-merge | Regression | 183,836 | Viable, harder |
| 3 | Issue resolution time | Regression | 3,872 | Marginal |
| 4 | Issue closed vs open | Binary classification | 7,082 | Invalid — censored |
| 5 | Repo-level health index | Either | 28 | Not for modelling |
| 6 | Stars | Regression | 28 | Not viable |
| 7 | `stale` | Binary | 28 | No variance |

## 5.2 Leakage register

**[DERIVED]** Columns that must be excluded, by target:

| Column | Leaks into T1 | Leaks into T2 | Reason |
|---|:---:|:---:|---|
| `pr.merged_at` | ✗ **drop** | ✗ **drop** | Non-null ⟺ merged; value *is* the T2 answer |
| `pr.merge_time_days` | ✗ **drop** | ✗ **drop** | −1 ⟺ not merged; value *is* the T2 answer |
| `pr.closed_at` | ✗ **drop** | ✗ **drop** | Equals `merged_at` for merged PRs |
| `pr.state` | — (is the label) | ✗ **drop** | Encodes merge outcome |
| `pr.updated_at` | ✗ **drop** | ✗ **drop** | Approximates the closure time |
| `repo.pr_contributors` | ✗ **drop** | ✗ **drop** | Function of the PR table's own contents (§2.3) |
| `repo.total_contributors` | ✗ **drop** | ✗ **drop** | Same |
| `repo.contributor_per_star` | ✗ **drop** | ✗ **drop** | Same |
| `repo.stars_per_fork` etc. | ⚠ redundant | ⚠ redundant | Exact functions of `stars`/`forks`/`open_issues` |
| `repo.size_category` | ⚠ redundant | ⚠ redundant | Exact function of `stars` |
| `created` / `updated` (ingest) | ✗ **drop** | ✗ **drop** | Scrape metadata; no domain meaning |

---

# STEP 6 — Formula Candidates

**[REC]** Only formulas whose inputs actually exist are listed. No formula is included merely to fill
the table. Let `S` = snapshot = `2024-09-06 11:30:17 UTC`.

### F1 — PR Merge Rate

- **Formula:** `merge_rate = |{PR : state = 'merged'}| / |{PR : state ∈ {merged, closed}}|`
- **Inputs:** `pr.state`
- **Interpretation:** Share of decided contributions that were accepted
- **Direction:** **Higher is better** — up to a point
- **[ASSUME]** Open PRs are undecided and are correctly excluded from the denominator
- **Limitations:** Projects that do not use GitHub PRs score near zero for workflow reasons, not
  quality reasons — **[FACT]** `httpd` 0.0%, `git` 0.1%, `linux` 1.1%. A very high rate can also
  indicate absent review rather than good review.

### F2 — PR Rejection Rate

- **Formula:** `rejection_rate = |{PR : state = 'closed'}| / |{PR : state ∈ {merged, closed}}|`
- **Inputs:** `pr.state`
- **Interpretation:** Share of decided contributions declined
- **Direction:** **Context-dependent** — high can mean strict quality control or an unwelcoming project
- **Limitations:** Cannot distinguish "rejected" from "superseded", "stale-closed", or "duplicate" —
  no label or close-reason data exists.

### F3 — Median Time-to-Merge

- **Formula:** `median_merge_days = median({merge_time_days : merge_time_days ≠ −1})`
- **Inputs:** `pr.merge_time_days`
- **Interpretation:** Typical review latency for accepted contributions
- **Direction:** **Lower is better**
- **[ASSUME]** `-1` is treated as missing, not as zero
- **[REC]** Use the **median, not the mean** — **[FACT]** the distribution is extreme
  (median 0.57 d vs mean 7.16 d vs max 2,031 d)
- **Limitations:** Conditioned on merge; ignores PRs that waited forever and were never merged.
  Pair with F5 to avoid a misleading picture.

### F4 — p90 Time-to-Merge (tail latency)

- **Formula:** `p90_merge_days = quantile_{0.90}({merge_time_days : ≠ −1})`
- **Inputs:** `pr.merge_time_days`
- **Interpretation:** Worst-case review latency a contributor can expect
- **Direction:** **Lower is better**
- **[DERIVED]** Observed range: 0.08 d (`guava`) to 298 d (`linux`)
- **Limitations:** Same conditioning as F3.

### F5 — PR Open-Backlog Rate

- **Formula:** `open_backlog_rate = |{PR : state = 'open'}| / |all PRs|`
- **Inputs:** `pr.state`
- **Interpretation:** Share of contributions awaiting a decision
- **Direction:** **Lower is better**
- **[FACT]** Observed: 0.13% (`playwright`) to 42.4% (`linux`)
- **Limitations:** **Strongly distorted by the sampling cap.** For repos whose 1,000 rows are all
  recent, open PRs are over-represented. Compare only within similar capture regimes.

### F6 — Issue Closure Rate

- **Formula:** `issue_closure_rate = |{issue : state = 'closed'}| / |all issues|`
- **Inputs:** `issues.state`
- **Interpretation:** Share of reported issues resolved
- **Direction:** **Higher is better**
- **[FACT]** Observed: 0.0% (`hackingtool`) to 92.5% (`erpnext`); undefined for 6 repositories
- **Limitations:** Right-censored — recent issues have had less time to close. Issue capture is
  **below 3% for most repositories**, so this may not be representative.

### F7 — Median Issue Resolution Time

- **Formula:** `median_resolution_days = median({resolution_time_days : ≠ −1})`
- **Inputs:** `issues.resolution_time_days`
- **Interpretation:** Typical time to resolve a reported issue
- **Direction:** **Lower is better**
- **[FACT]** Observed: 0.06 d (`flask`) to 252 d (`guava`)
- **Limitations:** Only 3,872 closed issues across 21 repos; survivorship bias — issues that never
  close are excluded, which flatters slow projects.

### F8 — Repository Age

- **Formula:** `repo_age_days = (S − repo.created_at).days`
- **Inputs:** `repo.created_at`
- **Interpretation:** Project maturity
- **Direction:** **Neither** — a context variable, not a health score
- **[FACT]** Observed: 221 – 5,888 days

### F9 — Activity Recency

- **Formula:** `days_since_last_pr = (S − max(pr.created_at)).days`
- **Inputs:** `pr.created_at`
- **Interpretation:** How recently contributions arrived
- **Direction:** **Lower is better**
- **[FACT]** Observed: 0 – 17 days. **[DERIVED]** All 28 repositories are currently active — this
  metric has almost no variance in this sample and cannot demonstrate abandonment detection.

### F10 — Recent Activity Volume

- **Formula:** `pr_last_365d = |{PR : created_at ≥ S − 365 days}|`
- **Inputs:** `pr.created_at`
- **Interpretation:** Current development intensity
- **Direction:** **Higher suggests more active**
- **[FACT] Limitation — serious.** For `airflow`, `kubernetes`, `swift` and `node` this equals the
  total PR count, because the cap truncated their history to one recent year. The metric therefore
  **measures the collection cap, not the project**, for those repositories.

### F11 — Star-to-Fork Ratio

- **Formula:** `stars_per_fork = stars / forks`
- **Inputs:** `repo.stars`, `repo.forks`
- **Interpretation:** Passive interest relative to active engagement
- **Direction:** **Lower may indicate deeper engagement**
- **[FACT]** Already present as a column and verified correct on 28 / 28 rows — do not recompute.
- **Limitations:** Snapshot only; **perfectly collinear** with `stars` and `forks` together, so it
  adds no information to a model that already has both.

### F12 — Monthly PR Trend

- **Formula:** OLS slope of monthly PR counts over the last *k* months
- **Inputs:** `pr.created_at`
- **Interpretation:** Whether contribution volume is growing or declining
- **Direction:** **Positive is better**
- **[ASSUME]** Requires ≥ 24 months of coverage to be meaningful
- **[FACT] Limitation:** Only **20 of 27** repositories have ≥ 24 distinct PR months. The other
  seven (`grafana` 19, `ansible` 10, `MiniCPM-V` 9, `node` 4, `airflow` 3, `kubernetes` 3,
  `swift` 3) cannot support a trend at all.

### Formulas deliberately NOT proposed

**[FACT]** The following are standard repository-health formulas that this dataset **cannot**
support, and I am not proposing approximations for them because any approximation would be invented:
bus factor, contributor growth, contributor retention, commit frequency, code churn, time to first
response, review depth, bug ratio, star velocity, license compliance, documentation score, CI health.

---

# STEP 7 — Final Recommendation

### 1. Number of repositories available

**[FACT]** **28** in `repo_data.csv`. **27** have PR data. **22** have issue data. **21** have at
least one closed issue. Effective *n* for repository-level analysis is therefore **21–28**.

### 2. Number of useful files

**[FACT]** **3 of 3** files are useful, but with very different weight:

| File | Usefulness |
|---|---|
| `pr_data.csv` | **High** — 248,320 event rows; the only file that can support model training |
| `issues_data.csv` | **Moderate** — 7,082 event rows; usable for descriptive metrics, thin for modelling |
| `repo_data.csv` | **Low as a modelling table** (28 rows), **useful as a join dimension** for context features — after dropping the four defective columns |

### 3. Which of the five dimensions can realistically be demonstrated

**[DERIVED]**

| Dimension | Demonstrable? |
|---|---|
| 3 — Issue & PR Health | ✓ **YES, fully** |
| 1 — Development & Maintenance Health | ~ **Partially** — PR/issue activity only, no commits |
| 5 — Sustainability / Maintenance Risk | ~ **Weak proxy only** — and no unhealthy repos exist in the sample to demonstrate against |
| 4 — Community Engagement / Popularity | ~ **Descriptive snapshot only** — no growth, no time series, n = 28 |
| 2 — Contributor / Community Health | ✗ **NO** — no author data exists |

**[DERIVED] Score: 1 of 5 fully, 3 of 5 partially, 1 of 5 not at all.**

### 4. Metrics we can calculate

**[DERIVED]** F1–F12 above: merge rate, rejection rate, median and p90 time-to-merge, PR open-backlog
rate, issue closure rate, median issue resolution time, repository age, activity recency, recent
activity volume, star-to-fork ratio, monthly PR trend. Plus PR/issue counts and PR-to-issue ratio.

### 5. Metrics that are impossible with this dataset

**[FACT]** Bus factor · unique contributors · contributor growth and retention · bot share ·
commit frequency · code churn · release cadence · time to first response · review depth · review
iterations · bug/feature ratio · triage rate · reopened-issue rate · PR size · star growth ·
fork growth · watchers · license presence · documentation quality · CI/CD presence · security
posture · dependency risk · governance · archival status.

### 6. Best prototype target

**[REC]** **T1 — PR merge outcome (binary: merged vs closed-unmerged), 240,241 labelled rows.**

Reasons: it is the only target with enough rows for a credible train/test split; it maps cleanly to
Dimension 3, which is the one dimension the dataset genuinely supports; its leakage sources are
identifiable and removable; and it answers a real decision-support question rather than an artefact
of the snapshot.

**[REC] Non-negotiable conditions:**
1. Drop `merged_at`, `merge_time_days`, `closed_at`, `updated_at`, and the three `*_contributors`
   columns plus `contributor_per_star`.
2. Split by **repository group or by time**, not randomly — a random split lets the model memorise
   repository-specific conventions and inflates the score.
3. Report a baseline. **[DERIVED]** Always-predict-merged gives **76.5% accuracy**; any model must
   beat that, and accuracy alone is the wrong metric — report precision/recall or AUC.

### 7. Recommended formulas

**[REC]** For the prototype dashboard, compute **F1, F3, F5, F6, F7, F8, F9** per repository. These
seven are well-defined, verified against the data, and cover Dimensions 1, 3 and 5. Present F5 and
F10 **only with the sampling-cap caveat attached**.

### 8. Biggest dataset limitations

**[DERIVED]** In order of severity:

1. **No contributor identity data at all** — eliminates Dimension 2 entirely and the most important
   sustainability metric (bus factor). The `*_contributors` columns are **actively misleading**
   because their names promise exactly the data that is missing.
2. **Only 28 repositories** — repository-level modelling is impossible; only event-level modelling is.
3. **Sampling caps at ~1,000 PRs for 9 repositories**, producing recency-truncated histories and
   making cross-repository aggregates non-comparable.
4. **No commit data** — Dimension 1 can only be approximated through PR/issue proxies.
5. **No time series for stars or forks** — Dimension 4 is a single snapshot.
6. **No labels, comments, or reviews** — removes the entire qualitative layer of issue/PR health.
7. **No unhealthy repositories** — all 28 are active flagship projects, `stale` is constant `False`.
   A risk model has no negative class to learn.
8. **Issue coverage below 3% for most repositories**, and entirely absent for 6 of 28.
9. **One corrupt join key** (`streamlit`, `repository = '0'`).
10. **No license, documentation, CI, or governance metadata** — Dimensions from the Step 1A framework
    (D4 Documentation, D5 Governance) have no data here at all.

### 9. Is this dataset sufficient for a complete SMALL working prototype?

**[REC]** **Qualified yes — with the scope stated honestly.**

| Layer | Sufficient? | Reasoning |
|---|---|---|
| **ML model (PR-event level)** | ✓ **YES** | 240,241 labelled rows, clean state machine, identifiable leakage, real signal available |
| **Metric computation layer** | ✓ **YES** | F1–F12 all compute; verified on all 28 repos |
| **Repository comparison view** | ~ **YES, descriptively** | 28 repos is enough for a dashboard demo, with the cap caveat displayed |
| **Repository-level ML / RHI** | ✗ **NO** | n = 28 |
| **Contributor / community analytics** | ✗ **NO** | No data |
| **Sustainability-risk classification** | ✗ **NO** | No unhealthy examples; no bus factor |

**[REC]** The honest framing for the report is: *"a working prototype of the Issue & PR Health
dimension, trained at pull-request event level, with a descriptive repository comparison view over
28 projects."* It is **not** a demonstration of the full five-dimension RHI, and claiming otherwise
would not survive review.

### 10. Additional data needed for the final research implementation

**[REC]** In priority order:

| Priority | Data needed | Unblocks |
|---|---|---|
| **1** | **Author / login on every issue, PR, and commit** | Dimension 2 entirely; bus factor; bot detection; contributor growth and retention |
| **2** | **Commit history** (sha, author, date, additions, deletions, files) | Dimension 1 properly; code churn; real activity trend |
| **3** | **A far larger repository sample (n ≥ 1,000), including unhealthy and abandoned projects** | Repository-level modelling; RHI validation; a negative class for risk |
| **4** | **Uncapped event collection** | Comparable cross-repository aggregates; valid trends |
| **5** | **Issue and PR labels** | Bug ratio; triage rate; issue-type analysis |
| **6** | **Comments and reviews with timestamps and authors** | Time to first response; review depth; responsiveness |
| **7** | **Star / fork / watcher time series** | Dimension 4 growth metrics |
| **8** | **Repository metadata** — license, README, CONTRIBUTING, CODE_OF_CONDUCT, CI config, topics, language | Step 1A dimensions D4 (Documentation) and D5 (Governance), which have **zero** support here |
| **9** | **Release and tag history** | Release cadence; maturity |
| **10** | **Archived / deprecated status with variance** | Sustainability ground truth |

---

## Relationship to the Step 1A Health Assessment Framework

**[DERIVED]** Mapping this dataset against the seven dimensions defined in
[health-assessment-framework.md](health-assessment-framework.md):

| Step 1A dimension | Data support here |
|---|---|
| D1 Development Activity | Partial — PR/issue events only, no commits |
| D2 Contributor & Community Health | **None** |
| D3 Maintenance Efficiency (PR + Issue Health) | **Full** |
| D4 Documentation Quality | **None** |
| D5 Governance | **None** |
| D6 Repository Maturity & Quality | Partial — age and size only |
| D7 Sustainability | Weak proxy; no ground truth |

**[DERIVED]** **1 of 7 Step 1A dimensions is fully supported.** This dataset supports a prototype of
D3, not of the integrated RHI.

---

## Inspection Provenance

**[FACT]** This report is based on four inspection scripts run against the original files in place.
The source CSVs were **read only** — not copied into the repository, not modified, not moved. No
project code was changed, no model was trained, and no target was selected.

Scripts (in the session scratchpad): `ds_inspect.py` (structure, dtypes, missingness, duplicates),
`ds_join.py` (join keys, states, date ranges, sentinels), `ds_repo.py` (per-repo coverage,
truncation, derived-column verification), `ds_deep.py` (derivation checks, caps, temporal density,
title signals), `ds_contrib.py` (the `*_contributors` hypothesis test), `ds_metrics.py` (candidate
metric computation).

**Next step, not yet started:** selection of the prototype target and construction of the feature
set. Awaiting your decision.
