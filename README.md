# NoiseFit PM Case Study — Sync Center

A Product Management case study exploring how NoiseFit could improve the reliability and transparency of wearable data synchronization.

This project covers the complete PM workflow:

**Research → Problem Framing → Prioritization → Product Definition → PRD → UX → SQL → Experimentation → GTM**

---

## Product

### NoiseFit Sync Center

A proposed experience that helps users understand whether their wearable data has successfully synchronized with the NoiseFit app and recover quickly when synchronization fails.

### Core concept

**Detect → Explain → Recover → Confirm**

The concept focuses on making synchronization failures visible and actionable rather than leaving users uncertain about whether their data was successfully transferred.

> This is an independent portfolio case study and is not an internal Noise product proposal.

---

# 01 — Research

## Objective

Understand recurring user pain points in NoiseFit and compare them with competing wearable applications.

### Products reviewed

- NoiseFit
- boAt Crest
- Google Health (Fitbit)
- Samsung Health

### Review dataset

The research dataset contains **426 Google Play reviews** sampled across the four products and multiple rating levels.

The NoiseFit sample contains:

- 22 × 1-star
- 20 × 2-star
- 20 × 3-star
- 15 × 4-star
- 19 × 5-star

### NoiseFit themes

The analysis identified recurring themes including:

- Sync / Data
- Features / Functionality
- Connectivity
- Accuracy
- Tracking
- Pricing / Monetization
- Battery / Performance
- UI / UX
- Privacy / Permissions
- Support / Service

### Key research signal

Within the NoiseFit sample, **Sync/Data** was the most frequent coded theme, followed by **Features/Functionality** and **Connectivity**.

Cross-brand analysis was used to distinguish potentially NoiseFit-specific signals from broader wearable-app problems.

> The review dataset is a portfolio research sample and should not be interpreted as representative of the complete NoiseFit user base.

### Research files

See [`01_Research`](./01_Research/) for:

- Review analysis
- Qualitative synthesis
- Cross-brand analysis
- Evidence bank
- Problem framing

---

# 02 — Prioritization

Multiple opportunity areas were evaluated using a RICE-style framework.

The prioritization considered:

- Reach
- Impact
- Confidence
- Effort

### Selected opportunity

**Reliable Sync & Recovery**

### Working product question

> How might we make NoiseFit's sync experience more reliable and transparent, so users can understand whether their wearable data has successfully reached the app and recover quickly when synchronization fails?

The RICE calculations are **portfolio assumptions**, not Noise internal metrics.

See [`02_Prioritization`](./02_Prioritization/).

---

# 03 — Product Definition

## Target user

A young, smartphone-dependent wearable user who regularly checks activity, sleep and workout information.

### Jobs To Be Done

> When I use my Noise wearable throughout the day, I want my data to reliably appear in NoiseFit and clearly know when something has failed, so that I can trust my activity and health records.

### User journey

**Wear → Connect → Sync → Discover problem → Recover → Confirm → Continue**

The product definition translates the research signal into a focused product opportunity.

See [`03_Product_Definition`](./03_Product_Definition/).

---

# 04 — PRD

## Product: NoiseFit Sync Center

The proposed MVP provides:

1. Sync status
2. Last successful sync timestamp
3. Data completeness by category
4. Failure explanations
5. Retry functionality
6. Guided Bluetooth recovery
7. Success confirmation
8. Support escalation

### Product principles

- Transparent
- Actionable
- Recoverable
- Confirmable

### Key metrics

- Sync recovery rate
- Percentage of sessions with missing data
- Median time to successful sync
- Repeat sync failures
- Support contacts related to synchronization
- Retention among affected users

See [`04_PRD`](./04_PRD/).

---

# 05 — UX

The UX concept follows the same recovery model:

**Detect → Explain → Recover → Confirm**

### Prototype flow

1. Dashboard
2. Sync Center
3. Partial Sync
4. Sync Details / Failure
5. Reconnect Watch
6. Recovering
7. Sync Complete
8. Sync History

The repository includes:

- UX specification
- Editable prototype
- Prototype visual
- SVG screen references

See [`05_UX`](./05_UX/).

> The UI is a proposed portfolio concept and is not a representation of the current NoiseFit application interface.

---

# 06 — SQL

A synthetic SQL dataset was created to demonstrate how a PM could investigate synchronization reliability and its relationship with engagement and support burden.

### Example analyses

- Overall sync outcome
- Sync failure rate by device
- Failure reasons
- Successful sync duration
- Repeated synchronization problems
- Support burden
- Engagement with and without sync problems
- Sync Center usage
- Platform-level support patterns
- Workout engagement by sync cohort

### Important

The SQL dataset is **synthetic**.

It does not represent Noise internal data, production telemetry, or proprietary company information.

See [`06_SQL`](./06_SQL/).

---

# 07 — Experimentation & Presentation

The case study includes an experimentation framework comparing:

### Control

Existing synchronization experience.

### Treatment

NoiseFit Sync Center.

### Primary metric

**Sync recovery rate**

### Secondary metrics

- Time to successful sync
- Missing-data rate
- Retry success
- Support contacts

### Guardrails

- App crashes
- Battery impact

The complete case study presentation is available in [`07_Presentation`](./07_Presentation/).

---

# 08 — GTM & Finalization

The proposed launch strategy focuses on existing Noise wearable users who regularly interact with activity, sleep and workout data and experience uncertainty when information is delayed or missing.

### Positioning

> A clearer, more dependable way to understand and recover from sync problems.

### Core message

**Know when your data is synced. Recover when it isn't.**

### Value pillars

**Reliable · Simple · Transparent**

The GTM plan also considers:

- In-app education
- Contextual notifications
- Help Center support
- Post-recovery feedback
- Controlled rollout by device / OS
- Telemetry → Support → Feedback → Fixes → Release

See [`08_Finalization`](./08_Finalization/).

---

# Case Study Summary

| Stage | Output |
|---|---|
| Research | Review analysis + competitor context |
| Problem | Sync reliability and transparency |
| Prioritization | RICE-style opportunity prioritization |
| Product Definition | Persona + journey + solution concept |
| PRD | Sync Center requirements |
| UX | 8-screen recovery flow |
| SQL | Synthetic product analytics |
| Experiment | Control vs Sync Center |
| GTM | Positioning + rollout strategy |
| Presentation | End-to-end PM case study |

---

# Repository Structure

```text
NoiseFit-PM-Case-Study/
│
├── 01_Research/
│   ├── Review analysis
│   └── Qualitative synthesis
│
├── 02_Prioritization/
│   └── Opportunity prioritization
│
├── 03_Product_Definition/
│   └── Persona, journey & solution
│
├── 04_PRD/
│   └── NoiseFit Sync Center PRD
│
├── 05_UX/
│   ├── UX specification
│   ├── Editable prototype
│   ├── Prototype visual
│   └── SVG screen references
│
├── 06_SQL/
│   └── Synthetic SQL portfolio
│
├── 07_Presentation/
│   └── PM case study presentation
│
└── 08_Finalization/
    ├── GTM strategy
    └── Final PM quality control
