# Synthetic SQL Analytics — Query Catalog & Schema

> **DISCLAIMER:** All data and tables referenced here are **synthetic** and were created strictly for this portfolio business analysis case study. They do not represent internal product telemetry, proprietary databases, or actual metrics from Noise or any competitor.

---

## 1. Overview & Purpose

In this case study, synthetic SQL analytics simulate how a Business Analyst or Product Analyst interrogates product telemetry to:
1. Diagnose baseline failure rates and device concentration.
2. Characterize root causes (e.g., Bluetooth dropouts vs. background OS kills).
3. Measure user impact, including repeat failures and support volume.
4. Define baseline metrics and measurable targets for the proposed **Sync Center** feature.

The complete SQLite database (`noisefit_synthetic.db`) and CSV table exports are preserved in the original archive at [`06_SQL/NoiseFit_SQL_Portfolio.zip`](../06_SQL/NoiseFit_SQL_Portfolio.zip). The standalone query script is provided directly in [`sql/analysis_queries.sql`](./analysis_queries.sql) for rapid review.

---

## 2. Synthetic Schema Definition

The synthetic telemetry model comprises six relational tables:

| Table Name | Description | Row Count | Primary Key | Key Foreign Keys |
|---|---|---|---|---|
| `users` | User demographic and platform metadata | 1,200 | `user_id` | — |
| `devices` | Smartwatch device models and activation dates | 1,500 | `device_id` | `user_id` → `users.user_id` |
| `sync_events` | Granular synchronization attempts and outcomes | 8,307 | `sync_id` | `device_id` → `devices.device_id` |
| `workouts` | User workout sessions recorded on wearables | 4,500 | `workout_id` | `user_id` → `users.user_id` |
| `support_tickets` | Inbound customer support inquiries by category | 900 | `ticket_id` | `user_id` → `users.user_id` |
| `app_sessions` | Companion app foreground sessions and entry points | 9,000 | `session_id` | `user_id` → `users.user_id` |

---

## 3. Query Catalog

The analysis script [`analysis_queries.sql`](./analysis_queries.sql) executes 10 core business and product questions:

| Query ID | Business Question | Telemetry Tables Used | Key Analytical Finding (Synthetic) |
|---|---|---|---|
| **Q1** | What is the overall sync outcome distribution? | `sync_events` | 70.93% success (5,892), 16.11% failed (1,338), 12.96% partial (1,077). Overall problem rate is 29.07%. |
| **Q2** | Which smartwatch models have elevated failure rates? | `sync_events`, `devices` | Failure rate is evenly distributed (~27%–30%) across models (Voyage: 30.08%, Pulse 2: 29.99%, Force Plus: 29.77%), indicating app/OS-level rather than single-hardware failure. |
| **Q3** | What are the primary failure reasons? | `sync_events` | Firmware mismatch (21.45%), background restriction (20.41%), Bluetooth disconnected (19.79%), timeout (19.75%), server timeout (18.59%). |
| **Q4** | What is the median sync duration for successful events? | `sync_events` | Median duration is 75 seconds. |
| **Q5** | Which users experience chronic (≥3) sync failures? | `sync_events`, `devices` | Identifies cohort of repeat-failure users at acute risk of churn. |
| **Q6** | What proportion of support tickets are sync-related? | `support_tickets` | Sync (319 tickets, 52.35% resolution) and Connectivity (215 tickets, 51.16%) represent 59.3% of total ticket volume (534/900). |
| **Q7** | Does sync failure correlate with lower app engagement? | `users`, `sync_events`, `devices`, `app_sessions` | Measures session frequency among affected vs. unaffected cohorts (~7.5 sessions/user). |
| **Q8** | How is the proposed Sync Center entry point utilized? | `app_sessions` | Evaluates adoption and traffic flow into `entry_point = 'sync_center'`. |
| **Q9** | Do support categories vary between iOS and Android? | `support_tickets`, `users` | Compares platform-specific support burdens. |
| **Q10** | How does workout recording differ across sync cohorts? | `workouts`, `sync_events`, `devices` | Evaluates impact of data-sync drops on health engagement. |

---

## 4. Key Takeaways for Business Analysis

1. **Quantified Problem Size:** In the synthetic dataset, nearly 3 out of 10 sync attempts (29.07%) fail or partially fail, mirroring the qualitative review findings where Sync/Data was the #1 user complaint (22.9% of NoiseFit reviews).
2. **Support Cost Driver:** Sync and connectivity issues drive nearly 60% of support contacts, proving that improving self-service sync recovery directly impacts operational support costs.
3. **Target Setting Baseline:** These synthetic baseline values inform the measurable targets and acceptance criteria defined in [`docs/BRD.md`](../docs/BRD.md) and [`docs/KPI_AND_METRICS.md`](../docs/KPI_AND_METRICS.md).
