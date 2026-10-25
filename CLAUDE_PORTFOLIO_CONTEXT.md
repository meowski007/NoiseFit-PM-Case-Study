# NoiseFit PM Case Study & SyncOps Platform — Claude Context Brief

> **INSTRUCTIONS FOR CLAUDE:**
> You are helping a student candidate applying for **Product Management (PM) Intern / Associate Product Manager (APM)** and **Product Analyst** roles.
> Use the verified facts, numbers, and guardrails in this document to update resumes, prepare interview answers, and critique case studies.
> **DO NOT** invent metrics, customer interviews, production deployments, or corporate affiliations.

---

## 1. Project Overview & Architecture

The candidate built a two-part portfolio centered on synchronization reliability across consumer IoT devices and cloud platforms:

1. **NoiseFit Sync Reliability Case Study (`NoiseFit-PM-Case-Study`):**
   - Independent product management and business analysis case study proposing **NoiseFit Sync Center**, a mobile companion feature replacing silent sync failures with a 4-stage recovery engine:
     $$\textbf{Detect} \longrightarrow \textbf{Explain} \longrightarrow \textbf{Recover} \longrightarrow \textbf{Confirm}$$
   - **Repository:** `https://github.com/meowski007/NoiseFit-PM-Case-Study` (Branch: `fix/honesty-and-clarity`)
2. **SyncOps Assistant (`syncops-assistant`):**
   - A separate, functional backend educational reliability platform built with FastAPI, SQLite, Pandera, Scikit-Learn, Statsmodels, and React/Streamlit.
   - Inspired by the same 4-stage reliability mental model, but designed for Site Reliability Engineers (SREs) and Data Platform leads.
   - **Repository:** `https://github.com/meowski007/syncops-assistant` (Branch: `fix/honesty-and-clarity`)

---

## 2. Non-Negotiable Factual Guardrails (Strict Honesty)

When writing resume bullets or interview responses, adhere strictly to these boundaries:
- **Independent Portfolio:** Not an official engagement with Noise (Nexxbase Technologies), boAt, Google/Fitbit, Samsung, Apple, or Amgen.
- **Review Mining ($N=426$):** 426 Google Play reviews mined across 4 companion apps (NoiseFit: 96, boAt Crest: 131, Fitbit: 101, Samsung Health: 98). Purposive quota sampling across 5 rating tiers.
- **Complaint Theme, Not Churn:** Reviews measure customer complaints and dissatisfaction, not measured account churn. Sync/Data was the #1 low-rating complaint theme (42.9% of all 1–2★ reviews).
- **RICE Prioritization:** Score **4.08** ranked Reliable Sync as the top opportunity. Inputs are analytical judgments, proven robust under $\pm 0.15$ Confidence sensitivity testing.
- **Synthetic Telemetry Baseline:** All telemetry datasets (`noisefit_synthetic.db` with 8,307 events; `syncops.db` with 5,000 clean events) are **100% synthetic models** for SQL and ETL demonstration.
- **Zero Live Interviews ($N=0$):** Primary 1-on-1 qualitative interviews have not been conducted. Standardized interview guides and screeners are planned templates.
- **Zero Usability Tests ($N=0$):** Prototype testing has not been run. The prototype is a static 8-screen UX specification (SVG screens, PPTX, Excel wireframe spec). No Figma file or clickable prototype exists yet.
- **Unexecuted A/B Test:** The 21-section A/B test plan is a designed statistical protocol ($n=356$ sample size derivation), not executed on live production users.
- **Simulated Stakeholder Reviews:** Reviews from engineers/designers are AI-simulated peer critiques.
- **Platform Distinction:** SyncOps Assistant is a separate backend platform demo, not the consumer mobile feature.
- **Two Triage Modes in SyncOps:**
  1. `/triage/rag`: **Retrieval-only** via sublinear TF-IDF and cosine similarity with refusal guardrails. **No generative LLM call**.
  2. `/triage`: Autonomous OpenAI tool-calling agent querying SQLite and reading Markdown SOPs, with an offline deterministic rule-based fallback.

---

## 3. Verified Technical Verification Numbers

All figures below have been executed and verified in local runs:
- **Automated Test Suite:** 88 passed, 0 failed in pytest (covering API, KPIs, Data Quality, Walk-Forward Forecasting, RAG Guardrails, Mocked LLM Tool-Calling).
- **Tool Versions:** Python 3.12.10, Node.js v24.22.1, npm 11.19.1, Git 2.56.0.
- **SyncOps Database:** 20,000 raw ingested rows, 5,000 clean validated rows, 300 distinct customers across 5 device cohorts, 5 incidents, 244 support tickets.
- **ETL Pipeline:** Idempotent 5-stage Pandera pipeline with HMAC-SHA256 customer ID masking and dead-letter quarantine.
- **Time-Series Forecasting Backtesting:** Chronological walk-forward validation (rolling origin):
  - Daily Failure Rate: Exponential Smoothing champion (MAE 0.968, RMSE 1.068, sMAPE 16.10%) vs. Seasonal Naive (MAE 1.098).
  - Daily Incident Volume: Naive Baseline champion (MAE 1.000) on sparse integer events.
- **RAG Evaluation Benchmark (25 Curated SRE Questions):**
  - Mean Reciprocal Rank (MRR): 0.880
  - Hit@1: 84.0% | Hit@3: 88.0% | Hit@5: 96.0%
  - Citation Validity Rate: 100.0%
  - Refusal Threshold: Cosine similarity $< 0.08$.

---

## 4. Resume-Ready CV Bullets (Google XYZ Format)

Use these verified bullet points for PM Intern, APM, and Product Analyst resumes:

### For Product Management Intern / APM Roles:
- **Analyzed 426 competitor Google Play reviews** using qualitative coding and an auditable RICE framework (Score: 4.08), identifying synchronization failure as the primary negative feedback driver (42.9% of 1–2★ reviews).
- **Authored comprehensive PRD, BRD, and 10 agile user stories** with 32 testable Gherkin acceptance criteria, a bidirectional traceability matrix, and a Now/Next/Later roadmap linked to 7 core reliability KPIs.
- **Designed 8 static vector UX specifications** modeling a 4-stage recovery workflow ($\text{Detect} \rightarrow \text{Explain} \rightarrow \text{Recover} \rightarrow \text{Confirm}$), introducing differential retries to eliminate silent failures.
- **Engineered a 21-section statistical A/B test plan**, deriving a required sample size of $n=356$ failure incidents per variant (80% power, $\alpha=0.05$) with non-negotiable crash and battery guardrails.

### For Technical PM / Product Analyst Roles:
- **Modeled 5-stage funnel telemetry and analyzed an 8,307-event synthetic database** using 10 relational SQL queries to evaluate sync failure distributions and support ticket root causes.
- **Architected data governance and ETL pipeline in SyncOps Assistant**, enforcing Pandera schema contracts, dead-letter quarantine, and HMAC-SHA256 PII masking across 5,000 telemetry events.
- **Built and evaluated a grounded RAG knowledge engine** using sublinear TF-IDF vectorization over 13 Markdown runbooks, achieving an 0.880 MRR and 84% Hit@1 with refusal guardrails.

---

## 5. Master Deliverables Index (Where Artifacts Live)

- **Master Portfolio Navigation:** [`product/README.md`](./product/README.md)
- **Product Strategy & Backlog:** [`product/roadmap-and-backlog.md`](./product/roadmap-and-backlog.md)
- **Trade-Off Decision Log:** [`product/trade-off-log.md`](./product/trade-off-log.md) (6 architectural trade-offs)
- **Risk & Blocker Register:** [`product/risks-and-blockers.md`](./product/risks-and-blockers.md) (16 enterprise risks)
- **Research Protocol (Planned):** [`product/research/research-plan-and-recruiting.md`](./product/research/research-plan-and-recruiting.md)
- **Usability Plan (Planned):** [`product/usability/usability-test-plan.md`](./product/usability/usability-test-plan.md)
- **Canonical A/B Test Plan:** [`product/experimentation/ab-test-plan.md`](./product/experimentation/ab-test-plan.md)
- **Funnel Telemetry & SQL:** [`product/analytics/funnel-and-events.md`](./product/analytics/funnel-and-events.md) & [`product/analytics/funnel-queries.sql`](./product/analytics/funnel-queries.sql)
- **QA Standards & UAT:** [`product/qa/bug-report-template.md`](./product/qa/bug-report-template.md) & [`product/qa/uat-plan.md`](./product/qa/uat-plan.md)
- **Interview Defense Guide:** [`product/interview-prep/project-interview-questions.md`](./product/interview-prep/project-interview-questions.md) (10 tough defense Q&As)
- **Commercial Teardown:** [`product/product-sense/sync-experience-teardown.md`](./product/product-sense/sync-experience-teardown.md)
- **Vertical Fit:** [`product/company-fit/construction-tech-pm-statement.md`](./product/company-fit/construction-tech-pm-statement.md)
