# KPI Data Dictionary & Telemetry Schema

> **DOCUMENT CONTROL & CLASSIFICATION**  
> **Project:** NoiseFit Sync Reliability — Sync Center  
> **Document ID:** DD-NF-001  
> **Version:** 1.0  
> **Classification:** Independent Portfolio Case Study  
> **Status:** Proposed Data Architecture Specification  
> **Date:** October 16, 2026  
> **Telemetry Source:** Synthetic SQL Portfolio Schema (`noisefit_synthetic.db`)

---

## 1. Overview & Data Architecture

This document establishes the official data dictionary supporting the **7 Core Key Performance Indicators** for the NoiseFit Sync Center initiative. It defines both the entity-relationship schemas used for operational telemetry logging and the analytical field derivations required for BI reporting and A/B test analysis.

### Telemetry Entity Relationship Overview

```
 [users] 1 ────────── ∞ [devices]
    │                        │
    │ 1                      │ 1
    │                        │
    ∞                        ∞
 [app_sessions]         [sync_events]
    │
    │ 1
    │
    ∞
 [support_tickets]
```

---

## 2. Telemetry Relational Tables

### 2.1. Table: `sync_events`
Captures every distinct synchronization attempt initiated by the mobile client or background scheduler.

| Column Name | Data Type | Nullable | Constraints / Enum | Description | Business Metric Mapping |
|---|---|---|---|---|---|
| `sync_id` | `INTEGER` | No | Primary Key | Unique autoincrementing sync transaction ID | Event count |
| `device_id` | `INTEGER` | No | FK → `devices.device_id` | Identifier of the smartwatch peripheral | Device segmentation |
| `event_time` | `TEXT` | No | ISO8601 Timestamp | UTC timestamp of sync initiation | Time window filtering |
| `outcome` | `TEXT` | No | `'success'`, `'failed'`, `'partial'` | Technical outcome of synchronization attempt | KPI-01, KPI-02 |
| `duration_seconds`| `INTEGER` | Yes | $\ge 0$ | Total elapsed duration from handshake to socket close | KPI-03 (Time to Recover) |
| `failure_reason` | `TEXT` | Yes | `'firmware_mismatch'`, `'background_restriction'`, `'bluetooth_disconnected'`, `'timeout'`, `'server_timeout'` | Diagnostic classification of failed/partial sync | Root cause distribution |

### 2.2. Table: `devices`
Maintains hardware model specifications and activation records.

| Column Name | Data Type | Nullable | Constraints / Enum | Description | Business Metric Mapping |
|---|---|---|---|---|---|
| `device_id` | `INTEGER` | No | Primary Key | Unique hardware device instance identifier | Granular device joins |
| `user_id` | `INTEGER` | No | FK → `users.user_id` | Owning registered user account identifier | User cohort mapping |
| `device_model` | `TEXT` | No | `'Voyage'`, `'Pulse 2'`, `'Force Plus'`, `'ColorFit Pro'`, `'Thrive'`, `'Icon 2'` | Commercial smartwatch model line | KPI segmentation |
| `activation_date`| `TEXT` | No | ISO8601 Date | Date watch was initially paired with NoiseFit | Cohort lifecycle analysis |

### 2.3. Table: `users`
Captures user profile demographic and platform attributes.

| Column Name | Data Type | Nullable | Constraints / Enum | Description | Business Metric Mapping |
|---|---|---|---|---|---|
| `user_id` | `INTEGER` | No | Primary Key | Anonymized user account identifier | Unique user counting |
| `age_band` | `TEXT` | Yes | `'18-24'`, `'25-34'`, `'35-44'`, `'45+'` | Age bracket for demographic segmentation | User persona validation |
| `platform` | `TEXT` | No | `'android'`, `'ios'` | Smartphone operating system family | OS failure segmentation |
| `signup_date` | `TEXT` | No | ISO8601 Date | User account registration date | User retention analysis |

### 2.4. Table: `app_sessions`
Tracks foreground application launches and user navigation entry points.

| Column Name | Data Type | Nullable | Constraints / Enum | Description | Business Metric Mapping |
|---|---|---|---|---|---|
| `session_id` | `INTEGER` | No | Primary Key | Unique session identifier | Session frequency |
| `user_id` | `INTEGER` | No | FK → `users.user_id` | Identifier of user initiating session | Active user counting |
| `session_time` | `TEXT` | No | ISO8601 Timestamp | Timestamp of session start | Session activity timeline |
| `entry_point` | `TEXT` | No | `'dashboard'`, `'sync_center'`, `'notification'`, `'workout'` | Surface through which user entered the app | KPI-07 (Adoption Rate) |

### 2.5. Table: `support_tickets`
Logs customer inquiries submitted to the support desk.

| Column Name | Data Type | Nullable | Constraints / Enum | Description | Business Metric Mapping |
|---|---|---|---|---|---|
| `ticket_id` | `INTEGER` | No | Primary Key | Unique ticket reference number | Support volume count |
| `user_id` | `INTEGER` | No | FK → `users.user_id` | Identifier of customer submitting ticket | Ticket submitter linkage |
| `created_at` | `TEXT` | No | ISO8601 Timestamp | Creation timestamp of the support ticket | Incident window matching |
| `category` | `TEXT` | No | `'sync'`, `'connectivity'`, `'features'`, `'accuracy'`, `'other'` | Topic categorization of customer grievance | KPI-05 (Support Tickets) |
| `resolved` | `INTEGER` | No | `0` (Open), `1` (Resolved) | Final resolution status flag | Support resolution efficiency |

### 2.6. Table: `workouts`
Logs exercise records transferred from wearables.

| Column Name | Data Type | Nullable | Constraints / Enum | Description | Business Metric Mapping |
|---|---|---|---|---|---|
| `workout_id` | `INTEGER` | No | Primary Key | Unique workout session identifier | Workout record count |
| `user_id` | `INTEGER` | No | FK → `users.user_id` | Identifier of user performing exercise | Activity engagement |
| `workout_date` | `TEXT` | No | ISO8601 Date | Date of physical activity | Engagement timeline |
| `workout_type` | `TEXT` | No | `'running'`, `'cycling'`, `'walking'`, `'hiit'` | Exercise classification | Activity segmentation |
| `duration_minutes`| `INTEGER` | No | $>0$ | Workout duration | Workout depth metric |
| `calories` | `INTEGER` | No | $\ge 0$ | Total active kilocalories burned | Health telemetry integrity |

---

## 3. KPI Derived Metrics Dictionary

| KPI ID | Metric Name | Mathematical Formula | Aggregation Granularity | Target Benchmark |
|---|---|---|---|---|
| **KPI-01** | **Sync Success Rate** | $\frac{\text{COUNT}(\text{outcome} = \text{'success'})}{\text{COUNT}(*)} \times 100$ | Hourly / Daily / Device | $>85.0\%$ `[ASSUMPTION]` |
| **KPI-02** | **Recovery Rate** | $\frac{\text{COUNT}(\text{Recovered Sessions within 15 min})}{\text{COUNT}(\text{Failed or Partial Sync Sessions})} \times 100$ | Daily / Weekly | $>60.0\%$ `[ASSUMPTION]` |
| **KPI-03** | **Time to Recover** | $\text{MEDIAN}(\text{timestamp}_{\text{success}} - \text{timestamp}_{\text{failure}})$ | Daily / Weekly | $<60\text{ seconds}$ `[ASSUMPTION]` |
| **KPI-04** | **Repeat Failure Rate** | $\frac{\text{COUNT}(\text{Distinct Users with } \ge 3 \text{ Failures in 7d})}{\text{COUNT}(\text{Distinct Users with } \ge 1 \text{ Failure in 7d})} \times 100$ | 7-Day Rolling Window | $<15.0\%$ `[ASSUMPTION]` |
| **KPI-05** | **Sync Support Ticket Volume** | $\frac{\text{COUNT}(\text{Tickets WHERE category IN ('sync','connectivity')})}{\text{COUNT}(\text{Total Active Users})} \times 1,000$ | Weekly / Monthly | $-25.0\%$ Relative Reduction `[ASSUMPTION]` |
| **KPI-06** | **Self-Service Resolution Rate** | $\frac{\text{COUNT}(\text{Recovered via Sync Center without Ticket in 24h})}{\text{COUNT}(\text{Sync Center Engaged Failure Sessions})} \times 100$ | Weekly / Monthly | $>70.0\%$ `[ASSUMPTION]` |
| **KPI-07** | **Sync Center Adoption Rate** | $\frac{\text{COUNT}(\text{DISTINCT } user\_id \text{ entering Sync Center post-failure})}{\text{COUNT}(\text{DISTINCT } user\_id \text{ experiencing sync failure})} \times 100$ | Weekly / Monthly | $>40.0\%$ `[ASSUMPTION]` |
