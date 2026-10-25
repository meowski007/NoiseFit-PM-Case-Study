# NoiseFit Sync Reliability — Sync Center
### Product Management & Business Analysis Case Study

> **IMPORTANT PORTFOLIO DISCLOSURE**  
> **This is an independent product and business analysis case study, not a real client engagement.** The KPI dataset is synthetic and is used to demonstrate analytical and measurement methods. Sync Center is a proposed feature, and the A/B test plan does not establish a completed experiment or measured business impact. Never infer that this project represents an official engagement or communication from Noise (Nexxbase Technologies), boAt, Google/Fitbit, or Samsung.

---

## Executive Summary

Wearable fitness trackers depend entirely on dependable data synchronization. When users complete workouts or record sleep, they expect seamless data availability on their mobile companion app. This independent case study investigates synchronization reliability across wearable ecosystems, identifies synchronization failure as the primary driver of customer churn, and engineers a comprehensive business analysis and product requirements specification for **NoiseFit Sync Center**.

Sync Center replaces silent failure with a deterministic, transparent four-stage recovery engine:

$$\textbf{Detect} \longrightarrow \textbf{Explain} \longrightarrow \textbf{Recover} \longrightarrow \textbf{Confirm}$$

This repository contains the complete, recruiter-ready **Business Analysis & Product Management documentation suite**, complete with qualitative review coding, RICE prioritization, a formal BRD, 10 Gherkin user stories, a detailed use case, process maps, a mathematical KPI framework, a bidirectional traceability matrix, synthetic SQL analytics, and an experimentation plan.

---

## Research status

To ensure complete transparency during internship and product management interviews, this repository maintains strict factual boundaries:
- **Review Mining:** 426 Google Play store reviews were collected and coded across four wearable companion apps (NoiseFit: 96, boAt Crest: 131, Fitbit: 101, Samsung Health: 98).
- **Opportunity Prioritization:** RICE prioritization was used to evaluate candidate problem areas, ranking synchronization reliability as the #1 strategic priority (Score: 4.08).
- **Product Artifacts Authored:** The persona (*Aarav*), Jobs to be Done (JTBD), Business Requirements Document (BRD), 10 agile user stories with 32 Gherkin acceptance criteria, 7 core KPI specifications, an 8-screen vector UX prototype, and an A/B experimentation plan were authored.
- **Synthetic Telemetry Baseline:** The KPI telemetry dataset (`noisefit_synthetic.db`, 8,307 sync events, 900 support tickets) is **synthetic**, created to demonstrate relational SQL analytics and measurement modeling.
- **Experimentation Status:** The A/B testing plan is a proposed statistical validation protocol; **no A/B test has been executed on live production traffic, and no experimental results exist.**
- **User Interviews:** Primary 1-on-1 qualitative user interviews have **not been conducted** ($N = 0$). Standardized research kits, screeners, and interview guides are created and ready for execution under [`product/research/`](./product/research/).
- **Usability Testing:** Prototype usability tests have **not been conducted** ($N = 0$). Standardized usability task protocols and scorecards are created under [`product/usability/`](./product/usability/).
- **Simulated Stakeholder Reviews:** Any stakeholder reviews included in this repository ([`product/reviews/simulated-stakeholder-review.md`](./product/reviews/simulated-stakeholder-review.md)) are **AI-simulated peer critiques**, not feedback from real engineers, designers, or corporate managers.
- **Platform Separation:** **SyncOps Assistant** is a separate, functional educational reliability platform (`syncops-assistant/`). It is **not** the proposed NoiseFit "Sync Center" consumer mobile companion feature.

---

## Portfolio Navigation Guide

For recruiters, hiring managers, and interviewers, this repository can be explored along the natural eight-step product management journey:

1. **Problem Discovery:** Start with empirical customer evidence in [`01_Research/`](./01_Research/) and the 426 coded reviews in [`research/evidence_register.csv`](./research/evidence_register.csv).
2. **Prioritization:** Review the opportunity-level RICE scoring in [`02_Prioritization/`](./02_Prioritization/) and trade-offs in [`product/trade-off-log.md`](./product/trade-off-log.md).
3. **Requirements & Scope:** Inspect the formal Business Requirements Document in [`docs/BRD.md`](./docs/BRD.md) and 10 Gherkin user stories in [`docs/USER_STORIES.md`](./docs/USER_STORIES.md).
4. **Proposed UX & Recovery Journey:** Walk through the 8-screen vector prototype in [`prototype/prototype_reference.md`](./prototype/prototype_reference.md) and [`05_UX/SVG_Screens/`](./05_UX/SVG_Screens/).
5. **Metrics & Experimentation:** Evaluate the 7 core KPIs in [`docs/KPI_AND_METRICS.md`](./docs/KPI_AND_METRICS.md), synthetic SQL in [`sql/analysis_queries.sql`](./sql/analysis_queries.sql), and the statistical A/B test plan in [`product/experimentation/ab-test-plan.md`](./product/experimentation/ab-test-plan.md).
6. **Research & Usability Validation:** Review continuous discovery kits ready for deployment in [`product/research/`](./product/research/) and [`product/usability/`](./product/usability/).
7. **Technical Implementation:** Inspect the separate, functional **SyncOps Assistant** platform in [`syncops-assistant/`](../syncops-assistant/) and its release notes in [`product/release/release-notes.md`](./product/release/release-notes.md).
8. **Next Steps & Strategy:** Explore the Now/Next/Later roadmap in [`product/roadmap-and-backlog.md`](./product/roadmap-and-backlog.md) and the ConTech PM statement in [`product/company-fit/construction-tech-pm-statement.md`](./product/company-fit/construction-tech-pm-statement.md).

---

## Product Management Master Deliverable Suite

| Deliverable Area | Artifact Name & Link | Core Purpose & Scope | Status |
|---|---|---|---|
| **Master Index** | [`product/README.md`](./product/README.md) | Comprehensive overview and navigation matrix for all PM portfolio artifacts. | Master Guide |
| **Strategy & Backlog** | [`product/roadmap-and-backlog.md`](./product/roadmap-and-backlog.md) | Now/Next/Later strategic roadmap linked to the 7 KPIs; prioritized MoSCoW/RICE backlog. | Proposed Roadmap |
| **Decisions & Scoping** | [`product/trade-off-log.md`](./product/trade-off-log.md) | 6 deep product decisions detailing context, options, sacrifices, and reversal conditions. | Proposed Decisions |
| **Risk Governance** | [`product/risks-and-blockers.md`](./product/risks-and-blockers.md) | Enterprise register tracking 16 product, engineering, data, privacy, and UX risks. | Active Governance |
| **User Research** | [`product/research/research-plan-and-recruiting.md`](./product/research/research-plan-and-recruiting.md) | Unbiased screener, recruitment script, consent model, and participant tracking sheet ($N=5\text{--}8$). | Ready for Execution |
|  | [`product/research/interview-guide.md`](./product/research/interview-guide.md) | 8 open-ended, non-leading behavioral questions with neutral follow-up probes. | Ready for Execution |
|  | [`product/research/research-notes-template.md`](./product/research/research-notes-template.md) | Standardized note-taking form separating verbatim quotes from researcher interpretations. | Reusable Template |
|  | [`product/research/affinity-mapping-template.md`](./product/research/affinity-mapping-template.md) | Inductive thematic synthesis matrix with contradiction audit and PRD implications. | Reusable Template |
|  | [`product/research/research-summary-template.md`](./product/research/research-summary-template.md) | One-page executive research summary brief with honest $N=0$ participant accounting. | Reusable Template |
| **Usability Testing** | [`product/usability/usability-test-plan.md`](./product/usability/usability-test-plan.md) | Test plan with think-aloud script, 5 realistic tasks, assistance tiers, and stop rules. | Ready for Execution |
|  | [`product/usability/usability-results-template.md`](./product/usability/usability-results-template.md) | Task observation scorecard and executive usability metrics summary table. | Reusable Template |
| **Experimentation** | [`product/experimentation/ab-test-plan.md`](./product/experimentation/ab-test-plan.md) | 21-section statistical A/B test plan: power formula, worked $n=356$ sample size, guardrails. | Proposed Plan |
| **Telemetry & Funnel** | [`product/analytics/funnel-and-events.md`](./product/analytics/funnel-and-events.md) | 5-stage funnel telemetry specs, JSON event schemas, and drop-off analysis questions. | Telemetry Spec |
|  | [`product/analytics/funnel-queries.sql`](./product/analytics/funnel-queries.sql) | 10 verified SQLite queries on synthetic data + proposed event-level funnel queries. | Verified SQL |
| **Release & Demo** | [`product/release/release-notes.md`](./product/release/release-notes.md) | Verified release notes for SyncOps Assistant documenting backend, API, RAG, and UI capabilities. | Verified Platform |
|  | [`product/release/demo-script.md`](./product/release/demo-script.md) | Time-boxed 3-minute video recording script connecting discovery, SyncOps, and prototype. | Presentation Script |
| **Quality & UAT** | [`product/qa/bug-report-template.md`](./product/qa/bug-report-template.md) | Standard PM/QA bug report template with defined severity levels and illustrative BLE defect. | Reusable Template |
|  | [`product/qa/uat-plan.md`](./product/qa/uat-plan.md) | Comprehensive User Acceptance Testing plan covering 6 test scenarios and exit criteria. | Planned Protocol |
| **Peer Review** | [`product/reviews/simulated-stakeholder-review.md`](./product/reviews/simulated-stakeholder-review.md) | AI-simulated critiques from Staff Mobile Engineer, Product Designer, and Senior PM. | Simulated Review |
|  | [`product/reviews/changelog.md`](./product/reviews/changelog.md) | Audit changelog separating created files, modified files, and proposed changes. | Active Log |
| **Product Sense** | [`product/product-sense/sync-experience-teardown.md`](./product/product-sense/sync-experience-teardown.md) | One-page teardown of commercial wearable synchronization mechanics based on public docs. | Product Teardown |
| **Interview Prep** | [`product/interview-prep/product-case-practice.md`](./product/interview-prep/product-case-practice.md) | 5 full product-case interview frameworks with clarifying questions and model answers. | Interview Prep |
|  | [`product/interview-prep/project-interview-questions.md`](./product/interview-prep/project-interview-questions.md) | 10 tough defense questions covering review mining, RICE, synthetic data, and A/B testing. | Interview Prep |
| **Industry Alignment** | [`product/company-fit/construction-tech-pm-statement.md`](./product/company-fit/construction-tech-pm-statement.md) | 200–300-word statement scaffold connecting IoT sync reliability to construction tech. | Reusable Scaffold |

---

| Deliverable | File Path | Scope & Focus |
|---|---|---|
| **Business Requirements Document (BRD)** | [`docs/BRD.md`](./docs/BRD.md) | Business problem, objectives, scope boundaries, stakeholder RACI, `BR-01` to `BR-06`, `FR-01` to `FR-10`, and `NFR-01` to `NFR-05`. |
| **User Stories & Acceptance Criteria** | [`docs/USER_STORIES.md`](./docs/USER_STORIES.md) | 10 user stories for persona *Aarav* with MoSCoW priorities, FR/KPI mappings, and 32 Given/When/Then Gherkin criteria. |
| **Detailed Use Case (UC-01)** | [`docs/USE_CASES.md`](./docs/USE_CASES.md) | Comprehensive primary use case: *Recover from a Failed Sync* with happy path, 3 alternate flows, 6 exception flows, and 5 business rules. |
| **Process Maps & Workflows** | [`docs/PROCESS_MAPS.md`](./docs/PROCESS_MAPS.md) | Visual state transitions, decision logic, cross-functional swimlanes, and step-by-step Miro / Lucidchart reconstruction guide. |
| **KPI & Metrics Framework** | [`docs/KPI_AND_METRICS.md`](./docs/KPI_AND_METRICS.md) | Mathematical formulas, operational definitions, and target benchmarks (`[ASSUMPTION]`) for 7 core synchronization KPIs. |
| **Requirements Traceability Matrix** | [`docs/TRACEABILITY_MATRIX.md`](./docs/TRACEABILITY_MATRIX.md) | Bidirectional forward/backward traceability linking customer review evidence to BRs, FRs, stories, ACs, KPIs, and validation methods. |
| **Interview Preparation & Defense** | [`docs/INTERVIEW_PREPARATION.md`](./docs/INTERVIEW_PREPARATION.md) | 5 core interview questions with deep BA model answers, disclaimers, and Junior BA (AI/GenAI) skill alignment. |
| **Assumptions & Open Questions** | [`docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md`](./docs/ASSUMPTIONS_AND_OPEN_QUESTIONS.md) | 9-part governance register separating verified facts, proposed decisions, explicit assumptions, missing data, and stakeholder questions. |

### Supporting Repository Deliverables
- **Evidence Register:** [`research/evidence_register.csv`](./research/evidence_register.csv) — 426 coded Google Play reviews.
- **Traceability Matrix CSV:** [`requirements/requirements_traceability.csv`](./requirements/requirements_traceability.csv) — Structured CSV matrix.
- **Standalone Process Maps:**
  - Flowchart: [`process-maps/sync_center_flow.mmd`](./process-maps/sync_center_flow.mmd)
  - Swimlanes: [`process-maps/sync_center_swimlanes.mmd`](./process-maps/sync_center_swimlanes.mmd)
- **KPI Data Dictionary:** [`metrics/KPI_data_dictionary.md`](./metrics/KPI_data_dictionary.md) — Telemetry schema and derived metric dictionary.
- **A/B Experimentation Plan:** [`experimentation/AB_TEST_PLAN.md`](./experimentation/AB_TEST_PLAN.md) — Statistical hypothesis testing and rollout protocol.
- **Prototype Screen Reference:** [`prototype/prototype_reference.md`](./prototype/prototype_reference.md) — 8 SVG prototype screen specifications.
- **SQL Analytics Script:** [`sql/analysis_queries.sql`](./sql/analysis_queries.sql) — 10 SQL queries analyzing synthetic telemetry.

---

## Resume-Ready CV Bullets

> **For Junior Business Analyst, Junior BA (AI/GenAI), and Product Analyst Applications:**

- **Analyzed 426 competitor Google Play reviews using sentiment analysis and RICE prioritization to identify wearable synchronization failure as the primary user churn driver.**
- **Authored comprehensive BRD, FRD, 10 user stories with Gherkin acceptance criteria, and bidirectional traceability matrix mapping user pain points to functional requirements.**
- **Designed 4-stage Sync Center workflow, A/B test validation plan, and synthetic SQL telemetry schema to model sync recovery and support burden KPIs.**

---

## 01 — Research & Problem Framing

### Objective
Understand recurring user pain points in NoiseFit and benchmark them against competing wearable companion applications.

### Review Dataset (426 Google Play Reviews)
The empirical research dataset contains **426 coded Google Play reviews** sampled across four products and all five rating tiers:
- **NoiseFit:** 96 reviews (22 × 1★, 20 × 2★, 20 × 3★, 15 × 4★, 19 × 5★)
- **boAt Crest:** 131 reviews (23 × 1★, 20 × 2★, 20 × 3★, 20 × 4★, 48 × 5★)
- **Google Health (Fitbit):** 101 reviews (27 × 1★, 15 × 2★, 19 × 3★, 20 × 4★, 20 × 5★)
- **Samsung Health:** 98 reviews (25 × 1★, 20 × 2★, 19 × 3★, 15 × 4★, 19 × 5★)

### NoiseFit Thematic Coding & Key Signals
- **Sync / Data:** **22 reviews (22.9%)** — 11 rated 1–2★ (50.0% severe dissatisfaction).
- **Features / Functionality:** 21 reviews (21.9%) — Only 1 rated 1–2★ (primarily feature requests).
- **Connectivity (Bluetooth):** 16 reviews (16.7%) — 7 rated 1–2★ (disconnection and unpairing friction).
- **Accuracy:** 10 reviews (10.4%) — 4 rated 1–2★.
- **Tracking:** 8 reviews (8.3%) — 4 rated 1–2★.

**Key Analytical Finding:** While "Features/Functionality" generated high volume, low-rating complaints were overwhelmingly concentrated in **Sync/Data and Connectivity (42.9% of all 1–2★ reviews)**. This proved that synchronization unreliability is the primary driver of negative reviews and app abandonment.

*Original Research Files:* See [`01_Research/`](./01_Research/) and [`research/evidence_register.csv`](./research/evidence_register.csv).

---

## 02 — Opportunity Prioritization (RICE)

Multiple candidate opportunity areas were evaluated using an auditable RICE framework:

$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

| Opportunity Area | Reach (1–10) | Impact (0.25–3) | Confidence (0–1) | Effort (1–10) | RICE Score | Rank |
|---|---|---|---|---|---|---|
| **Reliable Sync & Recovery** | **8** | **3 (Massive)** | **0.85** | **5** | **4.08** | **#1** |
| **Bluetooth Connection Recovery** | 7 | 3 (Massive) | 0.80 | 5 | 3.36 | #2 |
| **App Performance & Stability** | 7 | 2 (High) | 0.75 | 6 | 1.75 | #3 |
| **Health / Workout Data Accuracy** | 6 | 3 (Massive) | 0.65 | 7 | 1.67 | #4 |
| **Workout Tracking Depth** | 6 | 2 (High) | 0.65 | 6 | 1.30 | #5 |
| **Pricing Transparency** | 4 | 1 (Medium) | 0.80 | 3 | 1.07 | #6 |
| **Customization & Watch Faces** | 7 | 1 (Medium) | 0.60 | 7 | 0.60 | #7 |

*Note: RICE scores reflect portfolio analytical assumptions to structure prioritization, not internal company metrics.*

*Original Prioritization Files:* See [`02_Prioritization/`](./02_Prioritization/).

---

## 03 — Product Definition & User Persona

### Target User Persona
- **Persona Name:** *Aarav — The Everyday Wearable User*
- **Profile:** Young, smartphone-dependent Noise smartwatch user who checks steps, sleep, and workouts daily.
- **Primary Goal:** Dependably track health routines without having to repeatedly troubleshoot Bluetooth or unpair the watch.
- **Frustration Trigger:** Opening the companion app to find broken step streaks or missing sleep logs without any explanation.

### Jobs-to-be-Done (JTBD)
> *"When I use my Noise wearable throughout the day, I want my data to reliably appear in NoiseFit and clearly know when something has failed, so that I can trust my activity and health records."*

### User Journey
$$\text{Wear} \longrightarrow \text{Connect} \longrightarrow \text{Sync} \longrightarrow \text{Discover Problem} \longrightarrow \text{Recover} \longrightarrow \text{Confirm} \longrightarrow \text{Continue}$$

*Original Definition Files:* See [`03_Product_Definition/`](./03_Product_Definition/).

---

## 04 — Product Requirements Document (PRD)

The proposed MVP provides:
1. Real-time sync status card on the home dashboard.
2. Last successful sync timestamp.
3. Category-level completeness breakdown (Steps, Sleep, Heart Rate, Workouts).
4. Plain-language root-cause explanations (BLE disconnect, OS background kill, timeout).
5. One-tap targeted retry (differential packet recovery).
6. Guided Bluetooth reconnection flow.
7. Explicit confirmation screen showing restored categories and timestamp.
8. Automated customer support escalation with pre-packaged diagnostic logs after 3 failures.

*Original PRD Files:* See [`04_PRD/`](./04_PRD/) and [`docs/BRD.md`](./docs/BRD.md).

---

## 05 — UX Prototype & Screen Specifications

The UX prototype models an 8-screen recovery flow following the 4-stage model:

```mermaid
flowchart LR
    S1["1. Dashboard\n(Healthy / Partial)"] --> S2["2. Sync Center\n(Syncing / Overview)"]
    S2 --> S3["3. Partial Sync\n(Category Breakdown)"]
    S3 --> S4["4. Sync Details\n(Plain Diagnosis)"]
    S4 --> S5["5. Bluetooth Recovery\n(Guided Reconnect)"]
    S4 --> S6["6. Recovering\n(Progress State)"]
    S5 --> S6
    S6 --> S7["7. Sync Complete\n(Verified Confirmation)"]
    S7 --> S8["8. Sync History\n(Audit Trail)"]
```

- **Vector SVG Screens:** [`05_UX/SVG_Screens/`](./05_UX/SVG_Screens/)
- **Visual Mockup:** [`05_UX/NoiseFit_Sync_Center_Prototype_Visual.png`](./05_UX/NoiseFit_Sync_Center_Prototype_Visual.png)
- **Editable Prototype Slides:** [`05_UX/NoiseFit_Sync_Center_Editable_Prototype.pptx`](./05_UX/NoiseFit_Sync_Center_Editable_Prototype.pptx)
- **Figma Wireframe Specifications:** [`05_UX/Figma_Wireframe_Spec.xlsx`](./05_UX/Figma_Wireframe_Spec.xlsx)
- **Prototype Documentation:** [`prototype/prototype_reference.md`](./prototype/prototype_reference.md)

---

## 06 — Synthetic SQL Analytics

A synthetic relational database (`noisefit_synthetic.db`) with 8,307 sync events and 900 support tickets was constructed to simulate product telemetry analysis:

### Key Analytical Insights (Synthetic Data)
- **Overall Sync Outcome (Q1):** 70.93% success (5,892), 16.11% failed (1,338), 12.96% partial (1,077). Total problem rate is **29.07%**.
- **Model Distribution (Q2):** Failure rate is evenly distributed (~27%–30%) across models (Voyage: 30.08%, Pulse 2: 29.99%, Force Plus: 29.77%), indicating app/OS-level rather than single-hardware failure.
- **Root Causes (Q3):** Firmware mismatch (21.45%), background restriction (20.41%), Bluetooth disconnected (19.79%), timeout (19.75%), server timeout (18.59%).
- **Support Burden (Q6):** Sync (319 tickets) and Connectivity (215 tickets) represent **59.3% of total customer support volume** (534/900).

*Original SQL Files:* Preserved in [`06_SQL/`](./06_SQL/) and query catalog in [`sql/README.md`](./sql/README.md).

---

## 07 — Experimentation & A/B Validation

- **Experiment Design:** Control ($A$ — Existing sync experience) vs. Treatment ($B$ — Sync Center MVP).
- **Primary Metric:** Sync Recovery Rate within 15 minutes (Target: $\ge 60\%$, $+30\text{pp lift}$ `[ASSUMPTION]`).
- **Secondary Metrics:** Median Time to Recover ($<60\text{s}$ `[ASSUMPTION]`), Missing-data session rate, Support contact rate.
- **Guardrail Metrics:** App crash rate ($\le +0.05\%$), 24h battery drain ($<1.0\%$).
- **Experimentation Protocol:** See [`experimentation/AB_TEST_PLAN.md`](./experimentation/AB_TEST_PLAN.md).
- **Case Study Presentation Deck:** See [`07_Presentation/NoiseFit_PM_Case_Study.pptx`](./07_Presentation/NoiseFit_PM_Case_Study.pptx).

---

## 08 — Go-to-Market (GTM) & Rollout Strategy

- **Target Segment:** Active Noise wearable users experiencing delayed or missing activity data.
- **Positioning:** *A clearer, more dependable way to understand and recover from wearable sync problems.*
- **Core Message:** *Know when your data is synced. Recover when it isn't.*
- **Value Pillars:** Reliable · Simple · Transparent.
- **Launch Touchpoints:** In-app educational cards, contextual failure notifications, self-service Help Center guides.

*Original Finalization Files:* See [`08_Finalization/`](./08_Finalization/).

---

## Skills Demonstrated

| Competency Area | Tools & Frameworks Applied | Concrete Portfolio Evidence |
|---|---|---|
| **Requirements Elicitation** | Qualitative Review Mining, Coded Taxonomies | 426 Google Play reviews categorized across 10 themes in [`research/evidence_register.csv`](./research/evidence_register.csv). |
| **Requirements Documentation** | Formal BRD, Functional Specs, NFRs | Complete BRD (`BR-01`–`BR-06`, `FR-01`–`FR-10`, `NFR-01`–`NFR-05`) in [`docs/BRD.md`](./docs/BRD.md). |
| **Agile User Stories** | MoSCoW Prioritization, Gherkin (Given/When/Then) | 10 user stories with 32 testable Gherkin scenarios in [`docs/USER_STORIES.md`](./docs/USER_STORIES.md). |
| **Use Case Modeling** | Detailed Behavioral Specifications, Business Rules | End-to-end `UC-01` specification with 6 exception flows in [`docs/USE_CASES.md`](./docs/USE_CASES.md). |
| **Process Modeling** | Flowcharts, Cross-Functional Swimlanes, Miro Guide | Valid Mermaid diagrams and Miro reproduction guide in [`docs/PROCESS_MAPS.md`](./docs/PROCESS_MAPS.md). |
| **KPI & Metric Design** | Mathematical Formulations, Attribution Windows | 7 rigorous KPI specifications and SQL derivations in [`docs/KPI_AND_METRICS.md`](./docs/KPI_AND_METRICS.md). |
| **Traceability & Governance** | Bidirectional RTM, Forward/Backward Orphan Checks | Unbroken matrix and risk register in [`docs/TRACEABILITY_MATRIX.md`](./docs/TRACEABILITY_MATRIX.md). |
| **Product Analytics (SQL)** | SQLite, Window Functions, Cohort Segmentation | 10 analysis queries on 8,307 events in [`sql/analysis_queries.sql`](./sql/analysis_queries.sql). |
| **Experimentation** | A/B Test Design, Power Analysis, Sample Sizing | Statistical protocol and phased rollout plan in [`experimentation/AB_TEST_PLAN.md`](./experimentation/AB_TEST_PLAN.md). |
| **UI/UX Wireframing** | Information Architecture, Design Systems | 8 vector SVG screens and Figma spec in [`prototype/prototype_reference.md`](./prototype/prototype_reference.md). |

---

## Repository Structure

```text
NoiseFit-PM-Case-Study/
│
├── README.md                                  # Executive summary & portfolio master index
│
├── product/                                   # Product Management Artifact Suite (Upgraded)
│   ├── README.md                              # Master PM navigation matrix & portfolio index
│   ├── roadmap-and-backlog.md                 # Now/Next/Later roadmap & prioritized RICE backlog
│   ├── trade-off-log.md                       # 6 architectural & product trade-off records
│   ├── risks-and-blockers.md                  # Comprehensive risk & blocker register (16 risks)
│   ├── research/                              # Continuous discovery & user research kit
│   │   ├── research-plan-and-recruiting.md    # Screener, recruiting scripts, consent protocol
│   │   ├── interview-guide.md                 # 8 non-leading behavioral questions & probes
│   │   ├── research-notes-template.md         # Observation form separating quotes from insights
│   │   ├── affinity-mapping-template.md       # Thematic clustering & contradiction audit
│   │   └── research-summary-template.md       # One-page executive research brief (N=0 honest)
│   ├── usability/                             # Prototype usability testing kit
│   │   ├── usability-test-plan.md             # 5 realistic tasks covering the 4-stage journey
│   │   └── usability-results-template.md      # Quantitative task scorecard & metrics summary
│   ├── experimentation/                       # A/B experimentation upgrade
│   │   └── ab-test-plan.md                    # 21-section statistical plan (n=356 sample derivation)
│   ├── analytics/                             # Funnel analytics & telemetry
│   │   ├── funnel-and-events.md               # 5-stage funnel telemetry specs & JSON schemas
│   │   └── funnel-queries.sql                 # 10 runnable SQLite queries on synthetic telemetry
│   ├── release/                               # Product operations & presentation
│   │   ├── release-notes.md                   # Verified release notes for SyncOps Assistant
│   │   └── demo-script.md                     # Time-boxed 3-minute video presentation script
│   ├── qa/                                    # Quality assurance & delivery
│   │   ├── bug-report-template.md             # PM/QA bug report standard with illustrative BLE bug
│   │   └── uat-plan.md                        # User Acceptance Testing plan (6 test scenarios)
│   ├── reviews/                               # Governance & peer review
│   │   ├── simulated-stakeholder-review.md    # AI-simulated critiques (Eng, Design, PM)
│   │   └── changelog.md                       # Master portfolio governance changelog
│   ├── product-sense/                         # Commercial product teardowns
│   │   └── sync-experience-teardown.md        # Commercial wearable teardown (Fitbit/Google Health)
│   ├── interview-prep/                        # Interview defense & mastery
│   │   ├── product-case-practice.md           # 5 full product-case frameworks & model answers
│   │   └── project-interview-questions.md     # 10 likely project defense questions & model answers
│   └── company-fit/                           # Strategic vertical alignment
│       └── construction-tech-pm-statement.md  # 256-word ConTech PM internship statement scaffold
│
├── docs/                                      # Comprehensive Business Analysis documentation
│   ├── README.md                              # BA documentation index & recruiter guide
│   ├── BRD.md                                 # Business Requirements Document (BRD-NF-001)
│   ├── USER_STORIES.md                        # 10 User Stories with Gherkin Acceptance Criteria
│   ├── USE_CASES.md                           # Detailed Use Case Specification (UC-01)
│   ├── PROCESS_MAPS.md                        # Process modeling & Miro/Lucidchart guide
│   ├── KPI_AND_METRICS.md                     # KPI framework & mathematical formulations
│   ├── TRACEABILITY_MATRIX.md                 # Bidirectional traceability & orphan audits
│   ├── INTERVIEW_PREPARATION.md               # 5 defense questions & Junior BA (AI) alignment
│   └── ASSUMPTIONS_AND_OPEN_QUESTIONS.md      # 9-part governance register & risk log
│
├── research/
│   └── evidence_register.csv                  # 426 coded Google Play reviews
│
├── requirements/
│   └── requirements_traceability.csv          # Structured CSV traceability matrix
│
├── process-maps/
│   ├── sync_center_flow.mmd                   # Standalone Mermaid flowchart (Detect->Confirm)
│   └── sync_center_swimlanes.mmd              # Standalone Mermaid cross-functional swimlanes
│
├── metrics/
│   └── KPI_data_dictionary.md                 # Telemetry relational schema & derived metrics
│
├── experimentation/
│   └── AB_TEST_PLAN.md                        # Statistical A/B testing plan & rollout protocol
│
├── prototype/
│   └── prototype_reference.md                 # Prototype screen specifications & UI asset index
│
├── sql/
│   ├── README.md                              # Query catalog & schema documentation
│   └── analysis_queries.sql                   # 10 standalone SQL analysis queries
│
├── 01_Research/                               # Original qualitative research & reviews
├── 02_Prioritization/                         # Original RICE opportunity prioritization
├── 03_Product_Definition/                     # Original persona, journey & concept
├── 04_PRD/                                    # Original Product Requirements Document
├── 05_UX/                                     # Original Figma wireframe spec, PPTX & SVG screens
├── 06_SQL/                                    # Original synthetic SQLite database & ZIP
├── 07_Presentation/                           # Original 15-slide executive presentation
└── 08_Finalization/                           # Original GTM strategy & quality control
```
