# Assumptions, Data Boundaries & Open Questions

> **DOCUMENT CONTROL & CLASSIFICATION**  
> **Project:** NoiseFit Sync Reliability — Sync Center  
> **Document ID:** AOQ-NF-001  
> **Version:** 1.0  
> **Classification:** Independent Portfolio Case Study  
> **Status:** Open Governance & Risk Register  
> **Date:** October 16, 2026

---

## 1. Architectural Integrity & Boundaries

A rigorous Business Analysis portfolio must maintain complete transparency regarding what is empirically verified, what is modeled through portfolio assumptions, and what requires production engineering validation.

This document systematically partitions project knowledge into nine distinct governance sections:

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     VERIFIED FACTS (A)          │       │    PROPOSED DECISIONS (B)       │
│  • 426 Review Dataset           │       │  • Sync Center 4-Stage Flow     │
│  • Coded Themes & Ratings       │       │  • One-Tap Targeted Retry       │
│  • RICE Prioritization          │       │  • 3-Attempt Escalation Cap     │
└─────────────────────────────────┘       └─────────────────────────────────┘
                 │                                         │
                 ▼                                         ▼
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│   EXPLICIT ASSUMPTIONS (C)      │       │     MISSING EVIDENCE (D)        │
│  • Target KPI Values            │       │  • Proprietary Firmware Logs    │
│  • BLE Buffer Sizes             │       │  • Internal Noise Churn Data    │
│  • 15-Minute Recovery Window    │       │  • Production Telemetry DB      │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

---

## 2. Section A: Verified Project Facts

The following facts represent verified, reproducible data within this repository:

1. **Review Dataset Scope:** Exactly **426 public Google Play reviews** were collected and analyzed across four wearable companion apps:
   - **NoiseFit:** 96 reviews (22 × 1★, 20 × 2★, 20 × 3★, 15 × 4★, 19 × 5★)
   - **boAt Crest:** 131 reviews (23 × 1★, 20 × 2★, 20 × 3★, 20 × 4★, 48 × 5★)
   - **Google Health (Fitbit):** 101 reviews (27 × 1★, 15 × 2★, 19 × 3★, 20 × 4★, 20 × 5★)
   - **Samsung Health:** 98 reviews (25 × 1★, 20 × 2★, 19 × 3★, 15 × 4★, 19 × 5★)
2. **NoiseFit Qualitative Thematic Distribution:**
   - **Sync / Data:** 22 reviews (**22.9%** share; 11 rated 1–2★)
   - **Features / Functionality:** 21 reviews (21.9% share; only 1 rated 1–2★)
   - **Connectivity (Bluetooth):** 16 reviews (16.7% share; 7 rated 1–2★)
   - **Accuracy:** 10 reviews (10.4% share; 4 rated 1–2★)
   - **Tracking:** 8 reviews (8.3% share; 4 rated 1–2★)
   - **Pricing / Monetization:** 7 reviews (7.3% share; 7 rated 1–2★)
   - **Battery / Performance:** 5 reviews (5.2% share; 3 rated 1–2★)
   - **UI / UX:** 5 reviews (5.2% share; 1 rated 1–2★)
   - **Privacy / Permissions:** 1 review (1.0% share; 1 rated 1–2★)
   - **Support / Service:** 1 review (1.0% share; 1 rated 1–2★)
3. **RICE Opportunity Prioritization:**
   - Reliable Sync & Recovery ranked **#1** with a RICE score of **4.08** (Reach: 8, Impact: 3, Confidence: 0.85, Effort: 5).
4. **User Persona & JTBD:**
   - Persona: *Aarav — The Everyday Wearable User* (young, smartphone-dependent Noise smartwatch owner).
   - Core JTBD: *"When I use my Noise wearable throughout the day, I want my data to reliably appear in NoiseFit and clearly know when something has failed, so that I can trust my activity and health records."*
5. **UX Prototype Assets:**
   - 8 verified prototype screens provided as vector assets in [`05_UX/SVG_Screens/`](../05_UX/SVG_Screens/) and specified in [`05_UX/Figma_Wireframe_Spec.xlsx`](../05_UX/Figma_Wireframe_Spec.xlsx).
6. **Synthetic SQL Telemetry Dataset:**
   - Relational database (`noisefit_synthetic.db`) containing 6 tables: `users` (1,200), `devices` (1,500), `sync_events` (8,307), `workouts` (4,500), `support_tickets` (900), and `app_sessions` (9,000).

---

## 3. Section B: Proposed Design Decisions

The following solutions represent proposed product specifications designed to solve the identified user friction:

1. **Four-Stage Sync Center Architecture:** Structuring recovery around **Detect $\rightarrow$ Explain $\rightarrow$ Recover $\rightarrow$ Confirm** rather than relying on silent background retries.
2. **Contextual Status Surfacing:** Replacing ambiguous spinners with an explicit sync status card on the main dashboard, displaying relative timestamps (e.g., "Synced 2 min ago").
3. **Differential Category Retry:** Designing the retry action to request *only* failed or delayed categories (e.g., resending sleep packets without re-transmitting steps).
4. **Retry Threshold Ceiling:** Enforcing a strict maximum of **3 consecutive automated retry attempts** before escalating to customer support, preventing battery exhaustion and customer frustration.
5. **Automated Diagnostic Packaging:** Automatically attaching non-PII technical telemetry (device model, firmware version, OS version, last 5 BLE error codes) to pre-populated customer support tickets.

---

## 4. Section C: Explicit Assumptions

All targets and operational thresholds marked `[ASSUMPTION]` require empirical validation in a production environment:

1. `[ASSUMPTION]` **Target KPI Values:**
   - Sync Success Rate Target: $>85.0\%$ (baseline: 70.93% synthetic).
   - Recovery Rate Target: $\ge 60.0\%$ (baseline: ~30.0% unguided).
   - Time to Recover Target: $<60.0\text{ seconds}$ (baseline: 75s healthy sync, >180s manual reinstall).
   - Repeat Failure Rate Target: $<15.0\%$.
   - Support Ticket Reduction: $-25.0\%$ relative decrease in sync-related tickets.
   - Self-Service Resolution Rate: $>70.0\%$.
   - Sync Center Adoption Rate: $>40.0\%$ among failure-affected cohorts.
2. `[ASSUMPTION]` **Recovery Window Duration:** Defined as **15 minutes** post-initial failure for immediate recovery attribution.
3. `[ASSUMPTION]` **Hardware Flash Memory Capacity:** Smartwatch peripherals are assumed to cache at least 7 days of raw sensor packets during prolonged phone disconnection.
4. `[ASSUMPTION]` **OS Bluetooth API Capabilities:** Android 10+ and iOS 14+ native Bluetooth APIs provide programmatic error state callbacks (e.g., GATT status codes) with sufficient fidelity to distinguish radio-off from peripheral out-of-range.
5. `[ASSUMPTION]` **Battery Guardrail Ceiling:** Mobile companion app background polling consumes $<1.0\%$ total device battery per 24-hour cycle.

---

## 5. Section D: Missing Evidence & Data Boundaries

The following information could not be derived from public reviews or synthetic modeling:

1. **Internal Telemetry Baselines:** Actual production sync success rates, daily BLE error code distributions, and crash metrics across the genuine NoiseFit active user base.
2. **Customer Support Cost Accounting:** Internal cost-per-ticket metrics, average handling time (AHT), and first-contact resolution (FCR) data for the Noise customer operations team.
3. **Proprietary Hardware Specifications:** Exact Bluetooth Low Energy chipset models, MTU buffer limits, and firmware sleep cycle timers across legacy Noise smartwatch models.
4. **True User Churn Attribution:** Exact 30-day cohort retention data linking sync failures directly to account deactivations or device returns.

---

## 6. Open Questions for Cross-Functional Stakeholders

---

### E. Questions for Engineering (Firmware & Mobile)
1. **BLE Throughput & MTU Size:** What is the maximum negotiated MTU size supported across legacy vs. modern Noise smartwatch firmware? Does packet fragmentation cause timeout failures during large multi-day sync transfers?
2. **Android 14 Background Service Restrictions:** How will Sync Center maintain background polling without triggering aggressive OEM battery killer kills (e.g., Xiaomi MIUI, Samsung OneUI, OnePlus OxygenOS)?
3. **Firmware Buffer Overflow:** If a watch remains disconnected for greater than 7 days, does the firmware drop the oldest records or stop recording new workouts?
4. **Socket Teardown Latency:** When a timeout occurs, does the client BLE stack cleanly release the GATT peripheral socket, or does it leave ghost connections preventing immediate retry?

---

### F. Questions for Product Management
1. **Feature Gating & Rollout Strategy:** Should Sync Center be released as a universal app feature immediately, or restricted initially to specific flagship models (e.g., ColorFit Pro 4, Noise Voyage)?
2. **Offline Mode Value Proposition:** If the user has no internet connection, should Sync Center still confirm local watch-to-phone transfer, even if cloud dashboard backup is queued?
3. **Notification Thresholds:** At what point of sync delay should an active push notification be fired to avoid notification fatigue?

---

### G. Questions for Data & Analytics
1. **Event Pipeline Backpressure:** Can the analytics ingest pipeline handle high-frequency burst events (`sync_initiated`, `sync_completed`) from millions of active devices during morning peak hours (6:00 AM – 9:00 AM)?
2. **A/B Experiment User Allocation:** Should experimentation cohorts be randomized at the `user_id` level or the `device_model` level to avoid spillover effects across multi-device owners?
3. **Attribution Modeling:** What exact session timeout threshold (15 min vs. 30 min) maximizes correlation between self-service recovery and long-term 30-day retention?

---

### H. Questions for Customer Support Operations
1. **CRM Payload Ingestion:** Does the existing ticketing platform (e.g., Zendesk, Freshdesk) support direct API ingestion of encrypted JSON technical diagnostic attachments?
2. **Tier-2 Routing Rules:** Can tickets pre-populated by Sync Center with $\ge 3$ verified failures bypass tier-1 triage and route directly to specialized hardware/firmware support desks?
3. **Customer Re-contact Windows:** What percentage of users who experience sync issues call phone support rather than submitting in-app tickets?

---

### I. Questions for Further User Research & Usability Testing
1. **Diagnostic Copy Comprehension:** In usability testing, do non-technical users understand phrases like "Bluetooth connection interrupted", or do they prefer simpler analogies like "Watch is too far from phone"?
2. **Confirmation Screen Behavior:** Do users prefer an explicit confirmation modal that requires a tap on "Done", or an unobtrusive auto-dismissing toast banner?
3. **Partial Sync Mental Model:** When 3 out of 4 categories sync (e.g., Steps synced, Sleep delayed), do users perceive the app as functional or broken? Does highlighting partial sync increase trust or induce unnecessary anxiety?
