# Health Assessment Framework

> **Document status**
>
> | Field | Value |
> |---|---|
> | Methodology step | **Step 1A — Framework Definition** |
> | Status | Complete (conceptual definition only) |
> | Date | 2026-08-23 |
> | Scope | Dimension definitions, classification, and research positioning |
> | Explicitly out of scope | Metrics, formulas, weights, normalization, thresholds, models, data collection, implementation |
> | Supersedes | — (first research document in this project) |

**Source inputs consulted for this document**

| Input | Availability at time of writing |
|---|---|
| `README.md` (project title, declared component set, tech stack) | Present in repository |
| Base paper metadata (Xia et al., 2022, EMSE, DOI `10.1007/s10664-022-10171-0`) | Provided as project context |
| Step 1A specification (dimension list, constraints, research requirements) | Provided as project context |
| Project abstract / detailed project description / formal requirements document | **Not present in the repository** at time of writing |

Because the formal abstract and requirements documents are not yet committed to the repository, the
"Project relationship" statements in this document trace to (a) the component set declared in
`README.md` and (b) the Step 1A specification. When the abstract and requirements documents are
added, this framework must be re-checked against them and any divergence recorded as a revision to
this file rather than as a separate framework.

---

## 1. Research Context

### 1.1 The problem

Open-source software is adopted as infrastructure, not merely as a convenience: organisations take
on dependencies whose future maintenance they do not control. The practical question an adopter
faces is therefore not only *"does this repository work today?"* but *"will this repository still be
maintained, responsive, and safe to depend on in the future, and what will it cost us if it is
not?"*

Answering that question is currently a manual, subjective, and inconsistent activity. Practitioners
inspect a handful of surface signals — star count, date of the last commit, whether the README looks
serious — and generalise from them. These signals are individually weak and easily misread: a
repository with a high star count may have a single overloaded maintainer; a repository with recent
commits may have an unresolved-issue backlog growing faster than it is cleared; a repository with
excellent documentation may be legally unusable because it has no license. No single observable
signal maps cleanly onto the adoption decision.

### 1.2 Why a *framework* is the correct first step

Repository health is a **latent construct**: it cannot be observed directly, only inferred from
observable evidence. Constructs of this kind are measured defensibly only when the construct is
defined *before* the measurements are chosen. If metrics are selected first and a definition is
reverse-engineered from whatever the GitHub API happens to expose, the resulting index measures
*data availability* rather than health, and no validity claim about it can be sustained.

Step 1A therefore fixes the conceptual layer only:

- **what** health is taken to consist of (the dimensions),
- **why** each part belongs (research question, justification, and evidential basis),
- **how** each part is classified (direct component, context, derived, or decision output),
- and **what is deliberately left undecided**, so that later steps are visibly constrained by this
  document rather than free to redefine the construct after seeing the data.

### 1.3 Position of this document in the overall project

This framework is the definitional contract for everything downstream. Metrics defined in Step 1B
must each attach to exactly one dimension defined here; the Repository Health Index must be composed
only from dimensions declared here as eligible; risk conditions must each cite evidence from a
dimension defined here; and the decision-support outputs must consume, not re-invent, these
constructs. Any later step that needs a construct not defined here must amend this document first.

---

## 2. Relationship to Base Paper

### 2.1 The base paper

> Tianpei Xia, Wei Fu, Rui Shu, Rishabh Agrawal, Tim Menzies.
> *"Predicting Health Indicators for Open Source Projects (using Hyperparameter Optimization)."*
> Empirical Software Engineering, Springer, 2022. DOI: `10.1007/s10664-022-10171-0`.

### 2.2 What the base paper provides as our research foundation

The base paper establishes three things this project builds directly upon:

1. **That OSS project health is representable by measurable indicators derived from historical
   GitHub activity data.** Health is treated as something recorded in the repository's own event
   history rather than as something assessed by opinion.
2. **That the future values of those indicators can be predicted from their history using machine
   learning.** This converts health from a purely retrospective description into a forward-looking,
   empirically testable quantity — which is what an adoption decision actually requires.
3. **That prediction quality is a function of learner configuration, and that hyperparameter
   optimization applied to well-chosen learners is an effective and computationally reasonable way
   to obtain it.** This gives us a defensible methodological baseline for our own predictive
   component instead of an arbitrary model choice.

Point (3) is the base paper's headline contribution and is the part we intend to **reproduce**.
Points (1) and (2) are the assumptions we **inherit**.

### 2.3 What the base paper does *not* provide

The base paper predicts health indicators. Within the scope relevant to this project, it does not
supply:

- a **composite health index** integrating multiple indicators into one interpretable score;
- coverage of **non-event-based dimensions** — documentation and governance are artifact and policy
  properties, not counts accumulating over time, and so fall outside the indicator family the base
  paper models;
- a **risk formulation** that names concrete deterioration conditions and traces them to evidence;
- **cross-repository comparison** or an **adoption-readiness** judgement;
- an **explanation layer** that renders results actionable for a non-expert decision maker.

These absences are not deficiencies of the base paper — they lie outside its stated scope. They are,
however, precisely where this project locates its contribution.

### 2.4 Reproduction versus extension

This distinction is load-bearing for the research claim of the project and is maintained throughout
the document.

| | **Reproduction** (base paper) | **Extension** (this project) |
|---|---|---|
| Object | Individual health indicators | Integrated multi-dimensional health assessment |
| Temporal stance | Forecast future indicator values | Current-state assessment **and** forward-looking sustainability |
| Method contribution | Hyperparameter-optimized learners | Construct integration, derived risk, decision support, explanation |
| Output | Predicted indicator values | RHI + risk profile + comparison + adoption readiness + rationale |
| Consumer | Researcher | Adopter / maintainer / decision maker |

**We do not claim that the Repository Health Index exists in the base paper.** The RHI is our
proposed integration. Where this document says a dimension is "supported by the base paper", the
claim is only that indicators of that dimension's family belong to the class of quantities the base
paper models — not that the base paper defines the dimension, scores it, or combines it.

### 2.5 Support classification of the dimensions

| Dimension | Base-paper support | Nature of the relationship |
|---|---|---|
| D1 Development Activity | **Strong** | Activity counts over time are the canonical indicator family the base paper models |
| D2 Contributor & Community Health | **Strong (volume) / Partial (distribution)** | Contributor counts belong to the modelled family; contribution *concentration* across individuals does not |
| D3 Maintenance Efficiency (PR + Issue) | **Partial** | Issue/PR volume belongs to the modelled family; *efficiency* as a relational construct (resolution vs. accumulation) is our framing |
| D4 Documentation Quality | **None — extension** | Artifact-presence and content property, outside the event-series indicator family |
| D5 Governance | **None — extension** | Policy/process property, outside the event-series indicator family |
| D6 Repository Maturity & Quality | **Methodological only** | History length is a precondition of the base paper's forecasting, not a scored health property |
| D7 Sustainability | **Strong (method) / Extension (construct)** | The forecasting method is the base paper's core contribution; composing it into a "sustainability" construct is ours |
| DA1 Repository Health Index | **None — our proposal** | Composite integration is not part of the base paper |
| DA2 Risk Assessment | **None — extension** | Derived deterioration assessment is not part of the base paper |
| DS1 Repository Comparison | **None — extension** | — |
| DS2 Adoption Readiness | **None — extension** | — |
| DS3 AI-Assisted Insights | **None — extension** | — |

### 2.6 Verification obligation

Specific quantitative details of the base paper — the exact study subjects, the precise indicator
list, the exact optimizer configuration, and the reported effect sizes — are deliberately **not**
restated in this document. They must be taken from a direct reading of the paper and recorded in the
Step 1B literature review before being cited in the dissertation. Nothing in this framework depends
on those specifics; it depends only on the three foundations stated in §2.2, which follow from the
paper's stated contribution.

### 2.7 Research gap addressed

> The base paper shows that individual OSS health indicators can be **predicted** accurately. It does
> not show how those indicators should be **integrated, interpreted, risk-assessed, compared, or
> explained** so that a practitioner can act on them. Prediction accuracy is necessary for an
> adoption decision but not sufficient for one.

This project addresses that gap by defining an integrated, multi-dimensional, evidence-traceable
health assessment framework that (i) preserves the base paper's predictive foundation for the
forward-looking part of the assessment, (ii) extends coverage to adoption-relevant dimensions the
base paper does not model, and (iii) terminates in decision-support outputs rather than in predicted
values.

---

## 3. Health Assessment Dimensions

**How to read this section.** Each dimension is defined by six fields: *Purpose*, *Research
question*, *Why it matters*, *Base-paper relationship*, *Project relationship*, and *Classification*.

**Meaning of the classifications used:**

- **Core health dimension** — a *candidate* direct component of the RHI. Candidacy is not
  entitlement: final inclusion and weighting are decided in a later step on the basis of validation
  evidence, not asserted here.
- **Supporting / context dimension** — informs interpretation, stratification, and comparability of
  the other dimensions, but is **not** assigned a weight and does not contribute score directly
  unless later evidence justifies promotion.
- **Derived assessment** — computed *from* the dimensions rather than measured alongside them.
- **Decision-support component** — an output for the user, consuming the assessments above.

No weights, no metric definitions, and no thresholds appear anywhere in this section, by design.

---

### 3.1 Development Activity

**Identifier:** D1

**Purpose**
Assess whether the repository is actively and consistently developed — that is, whether development
work is *current*, *sustained over time*, and *stable* rather than sporadic or purely historical.

**Research question**
*RQ-D1: To what extent does a repository exhibit current, sustained, and consistent development
activity over its recent history?*

**Why it matters for OSS health and adoption**
Development activity is the base signal on which most other health judgements rest. A repository
that is no longer being worked on cannot absorb security fixes, cannot track changes in its own
dependencies, and cannot respond to defects an adopter reports — so an adopter of a dormant project
silently inherits its maintenance cost. Activity is also the dimension with the longest and
best-established observational history in empirical software engineering, which makes it the most
defensible anchor for the framework. Critically, *consistency* carries information that *volume*
does not: a steady low rate of development is a materially different signal from a large burst
followed by silence, even where the totals coincide.

**Relationship to the base paper**
**Strongly supported.** Development-activity counts observed per time period are the canonical
member of the indicator family the base paper models and forecasts from historical GitHub data. Our
use of this dimension as *observed evidence* is a direct inheritance from that foundation, and its
time-series form is what makes the base paper's forecasting method applicable to D7.

**Relationship to our project research gap**
D1 supplies the substrate for the Repository Health Index and for Sustainability Analysis, both
declared components in `README.md`. Our extension is not the measurement of activity but its
placement: activity becomes one dimension among several rather than a standalone verdict, which
directly addresses the practitioner failure mode of reading "last commit was recent" as "healthy".

**Classification:** Core health dimension.

---

### 3.2 Contributor & Community Health

**Identifier:** D2

**Purpose**
Assess whether the repository has an active, engaged, and reasonably *distributed*
contributor/maintainer community — covering participation level, concentration of contribution
across individuals, and the community's capacity to renew itself with new contributors.

**Research question**
*RQ-D2: Is the repository's contributor base active, sufficiently distributed across individuals,
and capable of renewal over time?*

**Why it matters for OSS health and adoption**
Activity alone can be generated by a single person, and a single-maintainer project is one life
event away from becoming unmaintained regardless of how healthy its activity curve looks today.
Distribution therefore separates a project that is merely *alive* from one that is *resilient*.
Renewal matters for the same reason over a longer horizon: a community with no inflow of new
contributors has a fixed and depleting maintenance capacity even while its present activity looks
sound. This dimension is consequently the primary evidential source for the maintainer-continuity
and contributor-concentration risk conditions recorded in §4.2.

**Relationship to the base paper**
**Split.** The *volume* aspect — how many people are contributing per period — is strongly supported:
contributor counts over time belong to the indicator family the base paper models. The *distribution*
aspect is an **extension**: the base paper models the magnitude of indicators over time, not the
inequality of contribution *across individuals* within a period. Measuring concentration requires a
per-contributor view that is not part of the base paper's formulation. This split is stated
explicitly because it is one of the clearest places where our framework goes beyond reproduction.

**Relationship to our project research gap**
Contributor Analytics is a declared component in `README.md`. The concentration analysis is a
deliberate extension: it converts contributor data from a headcount into a continuity judgement,
which is what the adoption decision actually depends on.

**Classification:** Core health dimension.

---

### 3.3 Maintenance Efficiency

**Identifier:** D3 (sub-components: D3a Pull Request Health, D3b Issue Health)

**Purpose**
Assess how effectively the project *handles* incoming contributions and reported problems — the
throughput and responsiveness of the maintenance process, as distinct from the raw volume of items
flowing through it.

**Research question**
*RQ-D3: How effectively does the project process incoming contributions and reported problems — that
is, are pull requests and issues resolved rather than accumulated?*

**Why it matters for OSS health and adoption**
This dimension measures whether maintenance capacity is keeping pace with maintenance demand. It is
the earliest reliable indicator of maintainer overload, because a queue begins to grow well before
activity begins to fall: a project can look fully active on D1 while its backlog compounds. For an
adopter it answers the two questions that determine the real cost of depending on the project — *if
we report a defect, will it be addressed?* and *if we contribute a fix, will it be merged?*

**Why one dimension and not two.** Pull request handling and issue handling are deliberately kept as
sub-components of a single dimension rather than promoted to two top-level dimensions. They are two
observations of the same underlying construct — the project's capacity to process incoming work —
and are expected to co-vary because they are constrained by the same maintainer attention. Treating
them as independent top-level dimensions would give that single construct two shares of influence in
any subsequent aggregation, double-counting maintenance capacity relative to every other dimension.

#### Pull Request Health

**Identifier:** D3a

**Purpose**
Assess whether contributions submitted by others are reviewed and brought to a decision — merged or
closed — in a timely and consistent manner.

**Research question**
*RQ-D3a: Are externally submitted contributions reviewed and resolved in a timely and consistent
manner?*

**Why it matters**
The pull request queue is the entry path for every new contributor. A stalled queue is both a
symptom of exhausted maintainer capacity and a *cause* of future community decline, because
contributors whose work sits unanswered do not return. This makes D3a a leading indicator for D2 as
well as a health measure in its own right, and it is the clearest example in the framework of one
dimension mechanistically influencing another.

**Base-paper relationship:** Partial — pull request volume over time belongs to the base paper's
indicator family; the timeliness and disposition of review do not.

**Project relationship:** Evidence source for the stalled-contribution risk condition, and an input to
adoption readiness for adopters who intend to contribute upstream rather than only consume.

#### Issue Health

**Identifier:** D3b

**Purpose**
Assess whether reported problems are triaged and resolved at a rate that keeps the unresolved
backlog stable rather than steadily growing.

**Research question**
*RQ-D3b: Are reported problems resolved at a rate that keeps the unresolved backlog stable rather
than growing over time?*

**Why it matters**
A backlog that grows monotonically is direct, cumulative evidence that demand has exceeded capacity,
and it is one of the few health signals that is difficult to misinterpret and difficult to
manufacture. It also has a direct adopter consequence: an unbounded backlog means a defect an
adopter reports is statistically unlikely to be addressed within any planning horizon.

**Base-paper relationship:** Partial — open and closed issue counts over time belong to the base
paper's indicator family; the accumulation-versus-resolution *relationship* between them is our
construct.

**Project relationship:** Directly produces the "increasing unresolved issues" risk evidence named in
the project's risk requirements, and feeds "Risk Evaluation" in `README.md`.

**Relationship to the base paper (dimension level)**
**Partial.** The underlying counts sit inside the base paper's indicator family, but "efficiency" is a
*relational* reading of those counts — resolution against arrival, disposition against age — and is
not a construct the base paper defines. The measurement inputs are inherited; the construct is ours.

**Relationship to our project research gap**
D3 is where the project converts prediction-oriented count data into an operational judgement about
process capacity, which is one of the concrete forms our integration contribution takes.

**Classification:** Core health dimension (single dimension, two sub-components).

---

### 3.4 Documentation Quality

**Identifier:** D4

**Purpose**
Assess how understandable, usable, installable, and adoptable the repository is, on the basis of the
documentation it provides to prospective users and contributors.

**Research question**
*RQ-D4: Does the repository provide the documentation a prospective user or contributor needs in
order to understand, install, use, and contribute to the project?*

**Why it matters for OSS health and adoption**
Documentation is the dominant determinant of *adoption cost*. A technically excellent but
undocumented project transfers its entire learning burden onto every adopting team, and that cost is
paid repeatedly, by each adopter, indefinitely. Documentation quality is also one of the few
dimensions observable *without* a long activity history, which makes it disproportionately valuable
when assessing young repositories where the time-series dimensions cannot yet yield a stable signal.
Finally, it is a credible proxy for maintainer intent: projects documented for outside use are
projects that expect outside users.

**Relationship to the base paper**
**Not supported — extension.** Documentation is an artifact-presence and content-property assessment,
not an event count accumulating over time, and therefore falls outside the indicator family the base
paper models. This dimension is one of the clearest coverage extensions in the framework, and it
exists because the base paper's question (*can health indicators be predicted?*) is narrower than
ours (*should this repository be adopted?*).

**Relationship to our project research gap**
"Documentation Assessment" is an explicitly declared component in `README.md`. It is a primary input
to Adoption Readiness (§5.2), where its influence is expected to be greater than in general health
assessment, since documentation bears more directly on adoption cost than on project survival.

**Classification:** Core health dimension (adoption-facing).

---

### 3.5 Governance

**Identifier:** D5

**Purpose**
Assess the repository's governance practices — whether processes for contribution, decision-making,
licensing, and community conduct are explicitly defined and visibly followed.

**Research question**
*RQ-D5: Does the project define and follow explicit, discoverable processes for contribution,
decision-making, licensing, and community conduct?*

**Why it matters for OSS health and adoption**
Governance determines three things no other dimension captures. First, **legal usability**: a
repository without a clear license is not adoptable at any level of technical health, which makes
this the one dimension capable of producing an absolute veto rather than merely a low score. Second,
**process predictability**: documented contribution processes tell a prospective contributor what
will happen to their work, which is a precondition for the community renewal measured in D2. Third,
and most importantly for long-horizon assessment, **transferability**: governance that is written
down survives the departure of the person who wrote it, whereas tacit governance leaves with its
holder. Two projects with identical activity profiles can therefore have very different survival
prospects depending on whether their process is externalised.

**Relationship to the base paper**
**Not supported — extension.** Governance is a policy and process property evidenced by repository
artifacts and conventions, not a time-series indicator, and lies outside the base paper's scope.

**Relationship to our project research gap**
Governance is a necessary input to organisational adoption decisions, which the base paper does not
address, and it supplies risk evidence of a categorically different kind from the activity-derived
signals — structural rather than behavioural. Its inclusion is part of what makes the framework a
decision-support instrument rather than a health monitor.

**Classification:** Core health dimension (adoption-facing).

---

### 3.6 Repository Maturity & Quality

**Identifier:** D6

**Purpose**
Capture repository and project maturity and development context — repository structure, project
size, length of development history, and evolution pattern — as an interpretive context for the
other dimensions.

**Research question**
*RQ-D6: What is the repository's maturity and development context, and how should that context
condition the interpretation of the other dimensions?*

**Why it matters for OSS health and adoption**
Identical observations carry different meanings in different contexts. Two contributors and three
commits a month is an unremarkable profile for a focused six-month-old utility and an alarming one
for a decade-old framework with wide downstream dependency; a stable low commit rate can indicate
either neglect or a mature project that has reached feature completeness. Without a maturity
context, the framework cannot distinguish these cases, and both comparison and risk assessment would
produce systematically wrong readings for young repositories and for stable mature ones.

**Why this is context and not a scored component**
Assigning maturity a weight in the index would make repository *age and size* directly reward score.
That is not defensible: age is not a virtue, and size is not quality. Maturity's proper role is to
condition how the other dimensions are read — as a stratification and interpretation variable —
rather than to contribute score of its own. Per the Step 1A specification, **no weight is assigned to
D6**, and promotion to a direct RHI component may occur only if a later validation step produces
positive evidence that maturity carries health information not already captured by the other
dimensions.

**Relationship to the base paper**
**Methodological only.** The base paper's forecasting approach inherently requires sufficient
historical depth for a series to be modelled at all, so history length functions there as a
*precondition of applicability* rather than as a scored health property. We adopt the same stance:
maturity governs whether, and how confidently, the other assessments — particularly the
forecast-based D7 — can be produced.

**Relationship to our project research gap**
D6 protects the validity of our extension. It gates whether Sustainability can be reported with
confidence for a given repository, and it enables the like-for-like stratification that Repository
Comparison (§5.1) requires in order not to produce misleading rankings.

**Classification:** Supporting / context dimension. **No weight assigned in Step 1A.**

---

### 3.7 Sustainability

**Identifier:** D7

**Purpose**
Assess whether the repository appears capable of remaining active, maintained, and viable over the
long term — a forward-looking judgement, as distinct from the current-state assessments in D1–D5.

**Research question**
*RQ-D7: Given the repository's observed health trajectory, is it likely to remain active and
maintained over a defined future horizon?*

**Why it matters for OSS health and adoption**
Adoption is a forward commitment: a team choosing a dependency is not buying its present state but
its future maintenance. Current-state health is a snapshot, and snapshots systematically mislead at
turning points — a project already in decline can present strong current-state values for a
considerable period after its trajectory has turned. Distinguishing *healthy now* from *likely to
remain healthy* is the single most decision-relevant transformation the system performs, and it is
the dimension to which the base paper's method contributes most directly.

**Relationship to the base paper**
**Strongly supported methodologically; the construct is our extension.** This dimension is where the
project's *reproduction* of the base paper is located: forecasting the future values of health
indicators from historical GitHub data using hyperparameter-optimized learners is exactly the
mechanism required to produce a defensible forward-looking judgement, and it is the base paper's core
contribution. The extension lies in composition and interpretation — the base paper predicts
indicators individually and makes no claim that they compose into a single "sustainability"
construct. That composition, and its translation into an adoption-relevant statement, are ours.

**Relationship to our project research gap**
"Sustainability Analysis" is a declared component in `README.md`. D7 is the join point between the
reproduced predictive core and the extended decision-support layer, and it is therefore the most
important single dimension for the project's research narrative.

**Dependency note (carried to later steps).** D7 is *temporally derived*: it consumes the historical
series of D1–D3 rather than introducing independent observations. If D7 and its own inputs both
contribute to the RHI, the same evidence is counted twice, with the forward-looking signal implicitly
weighted more heavily than intended. Resolving this — by structural separation, by weighting, or by
reporting D7 alongside rather than inside the index — is a required decision in the index-construction
step and is deliberately left open here.

**Classification:** Core health dimension (forward-looking / temporal).

---

## 4. Derived Assessments

Derived assessments are **computed from** the dimensions in §3. They introduce no new observations of
their own; their entire content is a transformation of dimensional evidence. No formulas, weights,
normalization schemes, or thresholds are defined in this step.

### 4.1 Repository Health Index (RHI)

**Identifier:** DA1

**Role**
The RHI is the project's unified health score: a single interpretable value integrating the health
dimensions selected for inclusion, intended to make repositories summarisable and comparable without
requiring the reader to interpret every dimension individually. It is a **decision instrument
constructed from measurements**, not a measurement in itself.

**Provenance — stated explicitly**
The RHI is **our proposed integration**. It does not exist in the base paper, which predicts
individual health indicators and makes no claim about combining them into a composite index. Any
statement in this project describing the RHI as derived from, validated by, or present in the base
paper would be incorrect and must not be made.

**Design constraints it must satisfy (stated as requirements, not as a formula)**
Recording these now constrains the later design and is itself part of the Step 1A contribution:

1. **Decomposability** — any RHI value must be attributable back to the dimensional evidence that
   produced it. A score a user cannot interrogate cannot support a decision.
2. **Comparability** — values must be meaningful across repositories of differing size, age, and
   domain, or the comparison component in §5.1 is invalid.
3. **Robustness to missing evidence** — some dimensions will be unobservable for some repositories,
   and absence of evidence must not be silently equivalent to evidence of poor health.
4. **Resistance to single-dimension domination** — no one dimension may be able to carry the index,
   or the index measures that dimension rather than health.
5. **Non-redundancy** — dimensions that are strongly dependent (notably D7 and its D1–D3 inputs, and
   D3a with D3b) must not contribute the same evidence twice.
6. **Validity evidence** — the index must be *evaluated* against something external, not merely
   asserted to be reasonable.

**Deliberately deferred to later steps:** which dimensions participate; the weighting scheme and its
justification; normalization; whether the RHI is a single scalar, a dimensional profile, or both; and
any banding or thresholds. **None of these are decided in Step 1A.**

**Classification:** Derived assessment.

### 4.2 Risk Assessment

**Identifier:** DA2

**Role**
Risk assessment identifies specific, named conditions that threaten a repository's continued
viability or make it costly to depend on, each traced to the dimensional evidence that supports it.
Its output is a set of *identified conditions with evidence*, not a number that competes with the RHI.

**Why risk is derived and not an independent weighted dimension**
Risk is not a separate observational channel. The same evidence that causes a repository to score
poorly on D1, D2, or D3 *is* the risk — a growing issue backlog is not evidence of risk in addition to
being poor issue health; it is the same observation described in decision terms. Adding risk as a
further weighted term in the index would therefore count that evidence twice and silently amplify the
influence of whichever dimensions happen to feed the risk conditions. Risk is also **categorically
different** from a health score in a way that matters practically: health is a graded quantity, while
risks are discrete conditions that are present or absent, are individually actionable, and can be
decisive on their own — a repository with an otherwise excellent profile and no license is not
"slightly less adoptable". Collapsing such conditions into a weighted average would destroy exactly
the information that makes them useful.

**Candidate risk evidence categories** (named in the project requirements; **not** operationalised
here — no conditions, thresholds, or severities are defined in Step 1A):

| Candidate risk condition | Primary evidential dimension(s) |
|---|---|
| Inactive or absent maintainers | D2, D1 |
| Contributor concentration / insufficient diversity | D2 |
| Growing unresolved issue backlog | D3b |
| Stalled or unreviewed contribution queue | D3a |
| Declining development activity trend | D1, D7 |
| Governance or licensing gaps | D5 |
| Documentation gaps affecting adoptability | D4 |
| Further conditions established by later research | — |

**Deliberately deferred to later steps:** the precise definition of each condition; detection criteria
and thresholds; severity assignment; aggregation into an overall risk statement; and whether risk
modifies the RHI or is reported strictly alongside it. **None of these are decided in Step 1A.**

**Classification:** Derived assessment.

---

## 5. Decision-Support Components

These components consume the dimensions and derived assessments and present them to a user in
decision terms. None are implemented, designed, or specified in Step 1A.

### 5.1 Repository Comparison

**Identifier:** DS1

**Role**
Compare two or more repositories on health, sustainability, and risk, so that a choice between
candidate dependencies can be made on evidence rather than on reputation or popularity.

**Framework requirements it inherits**
Comparison is where a composite index provides most value and also where it is most hazardous: a
scalar invites ranking, and ranking implies a precision the underlying construct does not possess.
Two constraints follow from this framework. First, comparison must be **stratified by maturity
context (D6)**, since comparing a young project against a mature one on uncontextualised values
mainly measures the age difference. Second, comparison must expose the **dimensional profile**
alongside any scalar, because two repositories with equal RHI values may differ entirely in
composition — and that difference, not the tie, is the decision-relevant information.

**Base-paper relationship:** Not covered — extension.

**Project relationship:** Follows from the platform's stated decision-support purpose in `README.md`.

**Classification:** Decision support.

### 5.2 Adoption Readiness

**Identifier:** DS2

**Role**
Provide an overall assessment of whether a repository is suitable to adopt as a dependency or
technology choice.

**Why this is distinct from the RHI**
*"Is this project healthy?"* and *"should we adopt it?"* are different questions with different
answers. A healthy, active, well-governed project may still be unsuitable for a given adopter —
because its license is incompatible with the adopter's intended use, because it has no usable
documentation, or because it lacks release discipline. Conversely, a project with modest activity may
be entirely adoptable if it is stable, documented, and clearly licensed. Adoption readiness therefore
draws on the same evidence as the RHI but weights it toward adopter-facing concerns (D4, D5) and
treats certain risk conditions as vetoes rather than deductions. Maintaining this distinction is a
deliberate design position of the framework, not an implementation detail.

**Base-paper relationship:** Not covered — extension.

**Project relationship:** Corresponds to "AI-Based Adoption Recommendations" in `README.md` and is the
practical endpoint of the whole pipeline.

**Classification:** Decision support.

### 5.3 AI-Assisted Insights

**Identifier:** DS3

**Role**
Explain, in natural language, what the computed health results mean: which dimensions drive the
outcome, which risks were identified and on what evidence, what the sustainability outlook implies,
and what a maintainer or adopter could do about it.

**Boundary constraint — recorded now to bind later design**
The AI layer is an **explanation layer over computed evidence, never a scoring layer**. It must not
produce, adjust, override, or substitute for any dimension value, RHI value, risk condition, or
sustainability judgement, and every statement it makes must be attributable to computed evidence.
Allowing generated text to influence scores would make results unreproducible and would forfeit the
empirical basis inherited from the base paper — which is the project's principal claim to research
validity. This constraint is stated in Step 1A precisely so that it constrains the design rather than
being negotiated later under implementation pressure.

**Base-paper relationship:** Not covered — extension.

**Project relationship:** Corresponds to the AI-assisted elements of `README.md`. **Not implemented in
this step.**

**Classification:** Decision support.

---

## 6. Overall Conceptual Framework

### 6.1 Assessment pipeline

```
                        +---------------------------+
                        |     GitHub Repository     |
                        |   (observable evidence)   |
                        +---------------------------+
                                     |
                                     v
        +-------------------------------------------------------+
        |                   HEALTH DIMENSIONS                   |
        |                                                       |
        |   CORE                                                |
        |     D1  Development Activity                          |
        |     D2  Contributor & Community Health                |
        |     D3  Maintenance Efficiency                        |
        |           D3a Pull Request Health                     |
        |           D3b Issue Health                            |
        |     D4  Documentation Quality                         |
        |     D5  Governance                                    |
        |     D7  Sustainability      (forward-looking)         |
        |                                                       |
        |   SUPPORTING / CONTEXT                                |
        |     D6  Repository Maturity & Quality  (no weight)    |
        +-------------------------------------------------------+
                                     |
                                     v
        +-------------------------------------------------------+
        |      HEALTH METRICS   (to be defined in Step 1B)      |
        |   every metric attaches to exactly one dimension      |
        +-------------------------------------------------------+
                                     |
                                     v
        +-------------------------------------------------------+
        |     RHI  -  Repository Health Index   [DERIVED]       |
        |   composition, weighting, normalization: NOT Step 1A  |
        +-------------------------------------------------------+
                                     |
                     +---------------+---------------+
                     |                               |
                     v                               v
        +--------------------------+   +----------------------------+
        |  SUSTAINABILITY  (D7)    |   |  RISK ASSESSMENT  [DERIVED]|
        |  forward-looking outlook |   |  evidence-traced conditions|
        |  (base-paper method)     |   |  NOT a weighted dimension  |
        +--------------------------+   +----------------------------+
                     |                               |
                     +---------------+---------------+
                                     v
        +-------------------------------------------------------+
        |            REPOSITORY COMPARISON  [DECISION]          |
        |     stratified by D6; profile shown, not just score   |
        +-------------------------------------------------------+
                                     |
                                     v
        +-------------------------------------------------------+
        |             ADOPTION READINESS  [DECISION]            |
        |    "should we adopt?" is not "is it healthy?"         |
        +-------------------------------------------------------+
                                     |
                                     v
        +-------------------------------------------------------+
        |       AI-ASSISTED DECISION SUPPORT  [DECISION]        |
        |    explanation over computed evidence - never scoring |
        +-------------------------------------------------------+
```

### 6.2 How D6 and D7 attach to the pipeline

The linear pipeline above is the primary flow. Two dimensions relate to it in a non-linear way and are
shown here separately so the main diagram stays readable:

```
   D6 (Maturity & Quality) ......> conditions the interpretation of
                                   D1..D5, D7, RHI and Comparison
                                   (context input; contributes no score)

   D1, D2, D3 history .........> D7 (Sustainability) via forecasting
                                   -> reproduction of the base paper's method
                                   -> see the non-redundancy note in 3.7 and 4.1(5)
```

### 6.3 Reproduction / extension overlay

```
   REPRODUCTION (base paper)      : indicator time series  ->  forecast  (feeds D7)
   EXTENSION    (this project)    : D4, D5 coverage
                                    + RHI integration
                                    + derived risk
                                    + comparison
                                    + adoption readiness
                                    + AI explanation
```

---

## 7. Research Boundary for Step 1A

Step 1A defines **what is being assessed and why**. It does not define **how anything is measured or
computed**. The following are intentionally *not* decided in this step, and any later document that
decides them must cite this framework as its source of constructs:

| Not decided in Step 1A | Reason it is deferred |
|---|---|
| **Exact metrics** for any dimension | Metrics must be chosen to fit the defined constructs, not the reverse (§1.2). Step 1B. |
| **Formulas** of any kind | Cannot be specified before metrics exist. |
| **Weights** for dimensions or the RHI | Weighting is a validity claim and requires evidence, not assertion. Explicitly includes the prohibition on assigning a weight to D6. |
| **Normalization** schemes | Depends on metric scales and distributions, which are not yet known. |
| **Thresholds and bands** (healthy / at-risk / unhealthy) | Require empirical distributions from real repositories. |
| **Risk detection criteria and severities** | Conditions are named in §4.2 but deliberately not operationalised. |
| **ML algorithms and hyperparameter-optimization setup** | Reproduction target from the base paper; belongs to the modelling step, and its exact configuration must be verified against the paper first (§2.6). |
| **Datasets and repository sampling strategy** | Requires the metric definitions to know what must be collected. |
| **GitHub API data collection** | Implementation; also constrained by the metrics not yet defined. |
| **Backend APIs, database schema, frontend** | Implementation; carries no research content at this stage. |
| **AI / LLM integration** | Deferred entirely; its boundary constraint is recorded in §5.3 but nothing is designed or implemented. |

**No implementation code, schema, configuration, or interface was produced in Step 1A, and no source
files outside `docs/research/` were created or modified.**

---

## 8. Traceability Table

Role values are restricted to: **Core Health Dimension**, **Supporting Dimension**, **Derived
Assessment**, **Decision Support**.

Step values: **Step 1A** = defined in this document; **Step 1B** = metric definition (the next step);
**Post-1B** = later steps not yet numbered in the current project plan.

| Component | Role | Base Paper Support | Project Requirement | Step |
|---|---|---|---|---|
| D1 Development Activity | Core Health Dimension | Strong — canonical member of the modelled indicator family | RHI + Sustainability Analysis (`README.md`); Step 1A dimension 1 | Defined Step 1A; metrics Step 1B |
| D2 Contributor & Community Health | Core Health Dimension | Strong for volume; Partial for contribution distribution (extension) | Contributor Analytics (`README.md`); Step 1A dimension 2 | Defined Step 1A; metrics Step 1B |
| D3 Maintenance Efficiency | Core Health Dimension | Partial — counts inherited, "efficiency" construct is ours | Risk Evaluation (`README.md`); Step 1A dimension 3 | Defined Step 1A; metrics Step 1B |
| D3a Pull Request Health | Core Health Dimension (sub-component of D3) | Partial — PR volume inherited; review timeliness is extension | Step 1A dimension 3 (PR Health) | Defined Step 1A; metrics Step 1B |
| D3b Issue Health | Core Health Dimension (sub-component of D3) | Partial — issue counts inherited; backlog dynamics is extension | Step 1A dimension 3 (Issue Health); "increasing unresolved issues" risk evidence | Defined Step 1A; metrics Step 1B |
| D4 Documentation Quality | Core Health Dimension | None — extension beyond base paper | Documentation Assessment (`README.md`); Step 1A dimension 4 | Defined Step 1A; metrics Step 1B |
| D5 Governance | Core Health Dimension | None — extension beyond base paper | Step 1A dimension 5; adoption/legal usability | Defined Step 1A; metrics Step 1B |
| D6 Repository Maturity & Quality | Supporting Dimension | Methodological only — history depth as a precondition, not a scored property | Step 1A dimension 6; **explicitly no weight assigned** | Defined Step 1A; context metrics Step 1B; possible promotion only Post-1B on evidence |
| D7 Sustainability | Core Health Dimension (forward-looking) | Strong methodologically (forecasting) — construct composition is our extension | Sustainability Analysis (`README.md`); Step 1A dimension 7 | Defined Step 1A; metrics Step 1B; modelling Post-1B |
| DA1 Repository Health Index (RHI) | Derived Assessment | **None — our proposed integration, not present in the base paper** | RHI (`README.md`); Step 1A component 9 | Role defined Step 1A; composition, weighting, normalization Post-1B |
| DA2 Risk Assessment | Derived Assessment | None — extension beyond base paper | Risk Evaluation (`README.md`); Step 1A component 8 | Role and evidence sources defined Step 1A; criteria and severities Post-1B |
| DS1 Repository Comparison | Decision Support | None — extension beyond base paper | Step 1A component 10 | Role defined Step 1A; design Post-1B |
| DS2 Adoption Readiness | Decision Support | None — extension beyond base paper | AI-Based Adoption Recommendations (`README.md`); Step 1A component 11 | Role defined Step 1A; design Post-1B |
| DS3 AI-Assisted Insights | Decision Support | None — extension beyond base paper | AI-assisted elements (`README.md`); Step 1A component 12 | Role and boundary constraint defined Step 1A; design and implementation Post-1B |

---

**End of Step 1A.** The conceptual framework is fixed. Metric definition (Step 1B) has not been
started, and no metrics, formulas, weights, normalization, thresholds, models, datasets, or
implementation artifacts are established by this document.
