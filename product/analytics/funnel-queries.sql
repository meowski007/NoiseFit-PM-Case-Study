-- ==============================================================================
-- NoiseFit PM Portfolio — Funnel & Post-Launch Health SQL Analytics
-- File: product/analytics/funnel-queries.sql
-- Database Dialect: SQLite 3.x
-- 
-- IMPORTANT PORTFOLIO DISCLOSURE:
-- ALL TABLES AND DATA REFERENCED IN PART 1 ARE SYNTHETIC (noisefit_synthetic.db).
-- THEY WERE CONSTRUCTED TO DEMONSTRATE PRODUCT ANALYTICS, SQL FLUENCY, AND
-- TELEMETRY DERIVATIONS. THEY DO NOT REPRESENT GENUINE CORPORATE DATA FROM NOISE.
-- PART 2 CONTAINS PROPOSED QUERIES FOR A FUTURE EVENT TELEMETRY PIPELINE.
-- ==============================================================================

-- ==============================================================================
-- PART 1: RUNNABLE QUERIES OVER EXISTING SYNTHETIC RELATIONAL SCHEMA
-- Tables Used: users, devices, sync_events, app_sessions, support_tickets, workouts
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Q1. Baseline Sync Outcome & Problem Rate (KPI-01: Sync Success Rate)
-- Purpose: Calculate overall proportion of success, failure, and partial syncs.
-- Business Context: In synthetic telemetry, establishes the 29.07% baseline problem rate.
-- ------------------------------------------------------------------------------
SELECT 
    outcome,
    COUNT(*) AS event_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct
FROM sync_events
GROUP BY outcome
ORDER BY event_count DESC;

-- ------------------------------------------------------------------------------
-- Q2. Post-Failure Recovery Transition (KPI-02: Recovery Rate Proxy)
-- Purpose: Measures what proportion of failed or partial sync attempts are immediately
--          followed by a successful sync on the same device.
-- Note: Evaluates chronological transitions using window function LAG().
-- ------------------------------------------------------------------------------
WITH ordered_syncs AS (
    SELECT 
        sync_id,
        device_id,
        event_time,
        outcome,
        LAG(outcome) OVER (PARTITION BY device_id ORDER BY event_time) AS prev_outcome,
        LAG(event_time) OVER (PARTITION BY device_id ORDER BY event_time) AS prev_event_time
    FROM sync_events
)
SELECT 
    COUNT(*) AS total_subsequent_attempts,
    SUM(CASE WHEN prev_outcome IN ('failed', 'partial') THEN 1 ELSE 0 END) AS attempts_following_problem,
    SUM(CASE WHEN prev_outcome IN ('failed', 'partial') AND outcome = 'success' THEN 1 ELSE 0 END) AS recovered_attempts,
    ROUND(100.0 * SUM(CASE WHEN prev_outcome IN ('failed', 'partial') AND outcome = 'success' THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN prev_outcome IN ('failed', 'partial') THEN 1 ELSE 0 END), 0), 2) AS immediate_recovery_rate_pct
FROM ordered_syncs;

-- ------------------------------------------------------------------------------
-- Q3. Median Sync Duration for Healthy Events (KPI-03: Time to Recover Baseline)
-- Purpose: Calculates the P50 median sync duration in seconds for successful events.
-- Note: SQLite lacks a native MEDIAN() aggregate - it uses ROW_NUMBER() CTE approximation.
-- ------------------------------------------------------------------------------
WITH ordered_durations AS (
    SELECT 
        duration_seconds,
        ROW_NUMBER() OVER (ORDER BY duration_seconds) AS row_num,
        COUNT(*) OVER () AS total_count
    FROM sync_events
    WHERE outcome = 'success' AND duration_seconds IS NOT NULL
)
SELECT 
    ROUND(AVG(duration_seconds), 2) AS median_healthy_sync_duration_seconds
FROM ordered_durations
WHERE row_num IN ((total_count + 1) / 2, (total_count + 2) / 2);

-- ------------------------------------------------------------------------------
-- Q4. Chronic Repeat Failure Concentration (KPI-04: Repeat Failure Rate)
-- Purpose: Identify the cohort of users who logged >= 3 failed or partial sync events.
-- Business Context: Chronic friction users represent acute customer churn risk.
-- ------------------------------------------------------------------------------
WITH user_failure_counts AS (
    SELECT 
        d.user_id,
        COUNT(*) AS problem_sync_count
    FROM sync_events s
    JOIN devices d ON s.device_id = d.device_id
    WHERE s.outcome IN ('failed', 'partial')
    GROUP BY d.user_id
)
SELECT 
    COUNT(CASE WHEN problem_sync_count >= 3 THEN 1 END) AS chronic_failure_users,
    COUNT(*) AS total_users_with_problems,
    ROUND(100.0 * COUNT(CASE WHEN problem_sync_count >= 3 THEN 1 END) / COUNT(*), 2) AS chronic_problem_user_share_pct
FROM user_failure_counts;

-- ------------------------------------------------------------------------------
-- Q5. Support Ticket Volume by Category (KPI-05: Support Burden Baseline)
-- Purpose: Quantifies customer support tickets driven by sync and connectivity.
-- Business Context: Proves that sync issues account for nearly 60% of support costs.
-- ------------------------------------------------------------------------------
SELECT 
    category,
    COUNT(*) AS ticket_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM support_tickets), 2) AS ticket_share_pct,
    ROUND(100.0 * AVG(resolved), 2) AS resolution_rate_pct
FROM support_tickets
GROUP BY category
ORDER BY ticket_count DESC;

-- ------------------------------------------------------------------------------
-- Q6. Sync Center Entry Point Utilization (KPI-07: Adoption Simulation)
-- Purpose: Measures traffic flow into the simulated 'sync_center' entry point.
-- ------------------------------------------------------------------------------
SELECT 
    entry_point,
    COUNT(*) AS session_count,
    COUNT(DISTINCT user_id) AS unique_users,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM app_sessions), 2) AS traffic_share_pct
FROM app_sessions
GROUP BY entry_point
ORDER BY session_count DESC;

-- ------------------------------------------------------------------------------
-- Q7. Sync Failure Rate by Smartwatch Hardware Model
-- Purpose: Determines whether sync unreliability is hardware-specific or app-wide.
-- Analytical Finding: Even distribution (~27-30%) proves app/protocol-level defect.
-- ------------------------------------------------------------------------------
SELECT 
    d.device_model,
    COUNT(*) AS total_syncs,
    SUM(CASE WHEN s.outcome IN ('failed', 'partial') THEN 1 ELSE 0 END) AS problem_syncs,
    ROUND(100.0 * SUM(CASE WHEN s.outcome IN ('failed', 'partial') THEN 1 ELSE 0 END) / COUNT(*), 2) AS failure_rate_pct
FROM sync_events s
JOIN devices d ON s.device_id = d.device_id
GROUP BY d.device_model
ORDER BY failure_rate_pct DESC;

-- ------------------------------------------------------------------------------
-- Q8. Diagnostic Root-Cause Breakdown
-- Purpose: Identifies the relative frequency of primary failure classifications.
-- ------------------------------------------------------------------------------
SELECT 
    COALESCE(failure_reason, 'unclassified') AS failure_reason,
    COUNT(*) AS failure_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM sync_events WHERE outcome <> 'success'), 2) AS failure_share_pct
FROM sync_events
WHERE outcome <> 'success'
GROUP BY failure_reason
ORDER BY failure_count DESC;

-- ------------------------------------------------------------------------------
-- Q9. Support Ticket Categories Segmented by Mobile Operating System
-- Purpose: Compares iOS vs. Android customer support burden.
-- ------------------------------------------------------------------------------
SELECT 
    u.platform,
    t.category,
    COUNT(*) AS ticket_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY u.platform), 2) AS platform_category_share_pct
FROM support_tickets t
JOIN users u ON t.user_id = u.user_id
GROUP BY u.platform, t.category
ORDER BY u.platform, ticket_count DESC;

-- ------------------------------------------------------------------------------
-- Q10. Engagement Impact: Average Sessions for Affected vs. Unaffected Users
-- Purpose: Tests whether users experiencing sync failures exhibit lower engagement.
-- ------------------------------------------------------------------------------
WITH problem_users AS (
    SELECT DISTINCT d.user_id
    FROM sync_events s
    JOIN devices d ON s.device_id = d.device_id
    WHERE s.outcome IN ('failed', 'partial')
),
user_session_counts AS (
    SELECT user_id, COUNT(*) AS session_count
    FROM app_sessions
    GROUP BY user_id
)
SELECT 
    CASE WHEN p.user_id IS NOT NULL THEN 'Experienced Sync Problem' ELSE 'Zero Sync Problems' END AS cohort,
    COUNT(u.user_id) AS total_users,
    ROUND(AVG(COALESCE(s.session_count, 0)), 2) AS avg_app_sessions_per_user
FROM users u
LEFT JOIN problem_users p ON u.user_id = p.user_id
LEFT JOIN user_session_counts s ON u.user_id = s.user_id
GROUP BY cohort;


-- ==============================================================================
-- PART 2: PROPOSED EVENT-LEVEL FUNNEL ANALYTICS QUERIES (FUTURE EVENT SCHEMA)
-- Expected Table: sync_funnel_events
-- Schema: (event_id, sync_id, user_id, event_name, event_time, properties_json)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Expected Schema Definition for Future Event Store:
-- CREATE TABLE sync_funnel_events (
--     event_id TEXT PRIMARY KEY,
--     sync_id TEXT NOT NULL,
--     user_id TEXT NOT NULL,
--     event_name TEXT NOT NULL CHECK(event_name IN (
--         'sync_failure_detected',
--         'sync_center_opened',
--         'sync_diagnosis_viewed',
--         'sync_retry_started',
--         'sync_recovery_confirmed'
--     )),
--     event_time TEXT NOT NULL,
--     properties JSON
-- );
-- ------------------------------------------------------------------------------

-- ------------------------------------------------------------------------------
-- PF-01. Five-Stage End-to-End Funnel Conversion & Drop-Off
-- Purpose: Computes user conversion across all 5 stages of the recovery funnel.
-- ------------------------------------------------------------------------------
/*
WITH stage_counts AS (
    SELECT 
        COUNT(DISTINCT CASE WHEN event_name = 'sync_failure_detected' THEN user_id END) AS stage1_detect_users,
        COUNT(DISTINCT CASE WHEN event_name = 'sync_center_opened' THEN user_id END) AS stage2_open_users,
        COUNT(DISTINCT CASE WHEN event_name = 'sync_diagnosis_viewed' THEN user_id END) AS stage3_diagnose_users,
        COUNT(DISTINCT CASE WHEN event_name = 'sync_retry_started' THEN user_id END) AS stage4_retry_users,
        COUNT(DISTINCT CASE WHEN event_name = 'sync_recovery_confirmed' THEN user_id END) AS stage5_confirmed_users
    FROM sync_funnel_events
    WHERE event_time >= datetime('now', '-14 days')
)
SELECT 
    stage1_detect_users,
    stage2_open_users,
    ROUND(100.0 * stage2_open_users / NULLIF(stage1_detect_users, 0), 2) AS detect_to_open_pct,
    stage3_diagnose_users,
    ROUND(100.0 * stage3_diagnose_users / NULLIF(stage2_open_users, 0), 2) AS open_to_diagnose_pct,
    stage4_retry_users,
    ROUND(100.0 * stage4_retry_users / NULLIF(stage3_diagnose_users, 0), 2) AS diagnose_to_retry_pct,
    stage5_confirmed_users,
    ROUND(100.0 * stage5_confirmed_users / NULLIF(stage4_retry_users, 0), 2) AS retry_to_confirm_pct,
    ROUND(100.0 * stage5_confirmed_users / NULLIF(stage1_detect_users, 0), 2) AS total_funnel_conversion_pct
FROM stage_counts;
*/

-- ------------------------------------------------------------------------------
-- PF-02. Funnel Drop-Off Analysis by Diagnostic Category
-- Purpose: Determines which failure mode experiences the highest diagnostic abandonment.
-- ------------------------------------------------------------------------------
/*
SELECT 
    json_extract(properties, '$.diagnostic_category') AS diagnostic_category,
    COUNT(DISTINCT sync_id) AS total_diagnoses_viewed,
    COUNT(DISTINCT CASE WHEN event_name = 'sync_retry_started' THEN sync_id END) AS retries_initiated,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN event_name = 'sync_retry_started' THEN sync_id END) / 
          COUNT(DISTINCT sync_id), 2) AS diagnosis_to_retry_rate_pct
FROM sync_funnel_events
WHERE event_name IN ('sync_diagnosis_viewed', 'sync_retry_started')
GROUP BY diagnostic_category
ORDER BY total_diagnoses_viewed DESC;
*/

-- ------------------------------------------------------------------------------
-- SYNTHETIC DATA — ILLUSTRATIVE ANALYSIS ONLY
-- The runnable queries in Part 1 execute against the synthetic SQLite portfolio
-- database. The queries in Part 2 reflect the intended future event instrumentation.
-- Neither establishes production client performance or real consumer metrics.
-- ==============================================================================
