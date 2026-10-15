-- NoiseFit PM Portfolio — Synthetic SQL Analysis
-- IMPORTANT: This dataset is fictional and does not represent Noise internal data.

-- Q1. Overall sync outcome rate
SELECT outcome,
       COUNT(*) AS events,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct
FROM sync_events
GROUP BY outcome
ORDER BY events DESC;

-- Q2. Sync failure rate by device model
SELECT d.device_model,
       COUNT(*) AS total_syncs,
       SUM(CASE WHEN s.outcome IN ('failed','partial') THEN 1 ELSE 0 END) AS problem_syncs,
       ROUND(100.0 * SUM(CASE WHEN s.outcome IN ('failed','partial') THEN 1 ELSE 0 END) / COUNT(*), 2) AS problem_rate_pct
FROM sync_events s
JOIN devices d ON s.device_id = d.device_id
GROUP BY d.device_model
ORDER BY problem_rate_pct DESC;

-- Q3. Failure reason distribution
SELECT failure_reason,
       COUNT(*) AS failures,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM sync_events WHERE outcome <> 'success'), 2) AS share_pct
FROM sync_events
WHERE outcome <> 'success'
GROUP BY failure_reason
ORDER BY failures DESC;

-- Q4. Median sync duration for successful syncs (SQLite percentile approximation)
WITH ordered AS (
  SELECT duration_seconds,
         ROW_NUMBER() OVER (ORDER BY duration_seconds) AS rn,
         COUNT(*) OVER () AS n
  FROM sync_events
  WHERE outcome='success'
)
SELECT AVG(duration_seconds) AS median_success_sync_seconds
FROM ordered
WHERE rn IN ((n+1)/2, (n+2)/2);

-- Q5. Users with repeated sync problems
SELECT d.user_id,
       COUNT(*) AS problem_syncs
FROM sync_events s
JOIN devices d ON s.device_id=d.device_id
WHERE s.outcome IN ('failed','partial')
GROUP BY d.user_id
HAVING COUNT(*) >= 3
ORDER BY problem_syncs DESC;

-- Q6. Sync-related support burden
SELECT category,
       COUNT(*) AS tickets,
       ROUND(100.0 * AVG(resolved),2) AS resolution_rate_pct
FROM support_tickets
GROUP BY category
ORDER BY tickets DESC;

-- Q7. Users with sync problems vs app engagement
WITH problem_users AS (
  SELECT DISTINCT d.user_id
  FROM sync_events s
  JOIN devices d ON s.device_id=d.device_id
  WHERE s.outcome IN ('failed','partial')
)
SELECT
  CASE WHEN p.user_id IS NULL THEN 'No sync problem' ELSE 'Sync problem' END AS cohort,
  COUNT(DISTINCT u.user_id) AS users,
  ROUND(AVG(session_counts.sessions),2) AS avg_sessions
FROM users u
LEFT JOIN problem_users p ON u.user_id=p.user_id
LEFT JOIN (
  SELECT user_id, COUNT(*) AS sessions
  FROM app_sessions
  GROUP BY user_id
) session_counts ON u.user_id=session_counts.user_id
GROUP BY cohort;

-- Q8. Sync Center usage (product analytics simulation)
SELECT COUNT(*) AS sync_center_sessions,
       COUNT(DISTINCT user_id) AS unique_users
FROM app_sessions
WHERE entry_point='sync_center';

-- Q9. Support tickets by platform
SELECT u.platform,
       t.category,
       COUNT(*) AS tickets
FROM support_tickets t
JOIN users u ON t.user_id=u.user_id
GROUP BY u.platform,t.category
ORDER BY u.platform,tickets DESC;

-- Q10. Workout engagement by users experiencing sync problems
WITH problem_users AS (
  SELECT DISTINCT d.user_id
  FROM sync_events s
  JOIN devices d ON s.device_id=d.device_id
  WHERE s.outcome IN ('failed','partial')
)
SELECT
  CASE WHEN p.user_id IS NULL THEN 'No sync problem' ELSE 'Sync problem' END AS cohort,
  COUNT(w.workout_id) AS workouts,
  ROUND(AVG(w.duration_minutes),2) AS avg_workout_minutes
FROM workouts w
LEFT JOIN problem_users p ON w.user_id=p.user_id
GROUP BY cohort;
