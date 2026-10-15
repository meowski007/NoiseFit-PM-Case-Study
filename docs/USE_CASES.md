# Detailed Use Case Specification — NoiseFit Sync Center

> **DOCUMENT CONTROL & CLASSIFICATION**  
> **Project:** NoiseFit Sync Reliability — Sync Center  
> **Document ID:** UC-NF-001  
> **Version:** 1.0  
> **Classification:** Independent Portfolio Case Study  
> **Primary Use Case:** UC-01: Recover from a Failed Sync  
> **Date:** October 16, 2026

---

## 1. Use Case Overview

| Attribute | Details |
|---|---|
| **Use Case ID** | **UC-01** |
| **Use Case Name** | **Recover from a Failed or Partial Synchronization** |
| **Primary Actor** | **Aarav — The Everyday Wearable User** |
| **Supporting Actors / Systems** | • **NoiseFit Mobile App (Client Experience)**<br>• **Noise Smartwatch Device (BLE Peripheral)**<br>• **Sync Center Engine & State Manager**<br>• **Support & Telemetry Backend Services** |
| **Goal in Context** | Enable a wearable user who encounters a stalled, delayed, or failed data sync to quickly diagnose the root cause, initiate self-service recovery, and verify that all health/activity data has reached the app without unpairing or contacting support. |
| **Trigger** | Automatic trigger upon failed/partial sync event, OR user manually opens Sync Center from the dashboard status card after noticing missing activity data. |
| **Scope** | Client Mobile Application & Local BLE Peripheral Subsystem. |

---

## 2. Stakeholders and Interests

- **Wearable User (Aarav):** Wants immediate access to daily steps, sleep, and workout records without performing repetitive, technical troubleshooting.
- **Product Management:** Seeks to protect 7-day user retention, increase sync success rates, and drive feature adoption.
- **Customer Support Operations:** Aims to eliminate preventable tier-1 sync complaints, reducing overall support ticket queues.
- **Engineering / QA:** Needs deterministic client state transitions, predictable battery/network consumption, and reproducible error logs.

---

## 3. Preconditions & Assumptions

### Preconditions
1. User has the NoiseFit companion application installed on an iOS (14+) or Android (10+) smartphone.
2. Smartwatch has previously been paired and registered with the user account.
3. Smartwatch has accumulated unsynchronized activity, sleep, or workout packets in its local buffer.
4. A synchronization attempt has occurred and returned a non-success status (`failed`, `partial`, or `timeout`).

### Assumptions
1. `[ASSUMPTION]` Smartwatch hardware maintains internal non-volatile memory capable of holding at least 7 days of historical health data without overwriting.
2. `[ASSUMPTION]` The mobile companion app has background BLE polling permissions enabled by the host operating system.
3. `[ASSUMPTION]` Bluetooth radio status and connection state can be queried by the mobile client via native OS APIs within $\le 200\text{ ms}$.

---

## 4. Main Success Scenario (Happy Path)

The primary success flow rigorously follows the four core Sync Center principles:

$$\textbf{Stage 1: Detect} \longrightarrow \textbf{Stage 2: Explain} \longrightarrow \textbf{Stage 3: Recover} \longrightarrow \textbf{Stage 4: Confirm}$$

| Step | Actor | System Action / Process Description |
|---|---|---|
| **1 (Detect)** | **App** | Background sync cycle terminates with missing workout and sleep packets. Sync Center State Manager flags sync state as `Partial Sync`. |
| **2 (Detect)** | **App** | Updates Dashboard status card: renders amber warning badge and label: *"Partial Sync • 2 of 4 data types synced"*. |
| **3 (Detect)** | **User** | Opens NoiseFit app, notices the status badge, and taps *"View sync status"*. |
| **4 (Explain)** | **App** | Navigates to **Sync Center** screen. Displays granular breakdown of categories: Steps (Synced), Heart Rate (Synced), Sleep (Delayed), Workouts (Failed). |
| **5 (Explain)** | **User** | Taps on the flagged "Sleep — Delayed" row. |
| **6 (Explain)** | **App** | Opens **Sync Details — Failure** screen. Inspects client error log (Code 133: BLE Packet Drop) and renders plain-language diagnosis: *"Smartwatch connection momentarily dropped during sleep packet transfer."* Surfaces last successful sync time and primary CTA: **[Retry Sync]**. |
| **7 (Recover)** | **User** | Verifies watch is on wrist and taps **[Retry Sync]**. |
| **8 (Recover)** | **App** | Transitions to **Recovering** screen. Displays animated progress spinner: *"Reconnecting to watch and resuming transfer..."*. Initializes 45-second recovery timer. |
| **9 (Recover)** | **App** | Client BLE engine re-establishes socket connection with peripheral, verifies packet sequence numbers, and streams remaining sleep and workout buffers. |
| **10 (Confirm)** | **App** | Receives all expected packets, performs CRC checksum validation, and updates local database cache. |
| **11 (Confirm)** | **App** | Transitions to **Sync Complete** screen. Renders green checkmark, celebrates restoration: *"All data categories are up to date"*, displays exact restored metrics and current timestamp. |
| **12 (Confirm)** | **User** | Taps **[Done]**. |
| **13 (Confirm)** | **App** | Navigates back to main Dashboard. Updates dashboard summary cards with recovered sleep score and workout calories. Emits `sync_recovered_success` telemetry event to analytics backend. |

---

## 5. Alternate Flows

### Alternate Flow 1 (AF-1): Guided Bluetooth Reconnection Flow
- **At Step 6:** System detects that the host smartphone's Bluetooth radio is switched off, OR device GATT connection is severed.
- **6.A1:** App displays diagnosis: *"Bluetooth is disconnected. NoiseFit cannot communicate with your smartwatch."* Surfaces CTA: **[Reconnect Watch]**.
- **6.A2:** User taps **[Reconnect Watch]**.
- **6.A3:** App launches **Bluetooth Recovery** screen, prompting user to enable Bluetooth or bring watch into 1-meter proximity.
- **6.A4:** If Bluetooth is disabled, app triggers native OS permission dialog: *"Allow NoiseFit to turn on Bluetooth"*. User accepts.
- **6.A5:** App automatically scans for peripheral UUID, establishes BLE bond, and flows directly to **Step 8 (Recovering)**.

### Alternate Flow 2 (AF-2): User Re-enters Sync Center via Direct Push Notification
- **At Step 1:** App detects background sync failure while running in background.
- **1.A1:** System fires high-priority local push notification: *"Sync incomplete: Your sleep data is ready to transfer. Tap to recover."*
- **1.A2:** User taps notification, bypassing the dashboard and landing immediately on **Step 4 (Sync Center)**.

### Alternate Flow 3 (AF-3): Partial Sync Auto-Resolution
- **At Step 8:** During recovery, the watch successfully transfers sleep data, but workout data requires an extended sync buffer.
- **8.A1:** App updates category badge for Sleep to *Synced*, while maintaining Workout as *Syncing*.
- **8.A2:** App notifies user: *"Sleep data restored. Finalizing workout transfer..."* without restarting the entire cycle.

---

## 6. Exception Flows

### Exception Flow 1 (EF-1): Diagnostic Information Unavailable (Graceful Fallback)
- **At Step 6:** The low-level BLE stack returns an undefined vendor error (`UNKNOWN_ERR_0xFF`).
- **6.E1:** System applies **Business Rule BR-R01 (No False Diagnostics)**. Instead of showing empty text or raw hex codes, app renders standardized fallback: *"Temporary sync interruption. Your data is safely stored on your watch."*
- **6.E2:** App displays standard recovery options: **[Retry Sync]** and **[Troubleshooting Tips]**.

### Exception Flow 2 (EF-2): Smartwatch Out of Range / Battery Depleted
- **At Step 9:** App attempts BLE handshake, but smartwatch does not acknowledge advertisement packets within 15 seconds.
- **9.E1:** App pauses recovery and prompts user: *"Unable to locate watch. Ensure your watch is powered on and within arm's reach."*
- **9.E2:** User checks watch. If battery is dead, user places watch on charger and cancels flow. Unsynchronized data remains cached in app state.

### Exception Flow 3 (EF-3): Missing Operating System Permissions
- **At Step 7:** User taps [Retry Sync], but the host OS has revoked Nearby Devices (Android 12+) or Location permissions.
- **7.E1:** App renders permission recovery modal: *"Nearby devices permission is required for Bluetooth syncing."*
- **7.E2:** User taps **[Open Settings]**, granting required permission, and returns to app to resume Step 8.

### Exception Flow 4 (EF-4): Recovery Timeout (45-Second Expiry)
- **At Step 9:** The BLE stream hangs or drops mid-packet. The 45-second recovery watchdog timer expires.
- **9.E3:** App halts transfer socket, increments internal session retry counter (`retry_count = 1`), and displays: *"Sync timed out. Connection was unstable."*
- **9.E4:** App renders **[Try Again]** CTA with suggestion: *"Toggle Bluetooth or move away from Wi-Fi interference."*

### Exception Flow 5 (EF-5): Repeated Failures Exceed Threshold (Support Escalation)
- **At Step 9.E3:** User attempts retry, and it fails for the 3rd consecutive time (`retry_count >= 3`).
- **9.E5:** System applies **Business Rule BR-R02 (Retry Ceiling & Escalation)**. The app terminates automatic retry loops.
- **9.E6:** Screen renders dedicated escalation view: *"We couldn't restore sync automatically. Let our technical team investigate."*
- **9.E7:** App provides primary CTA: **[Send Diagnostic Log to Support]**.
- **9.E8:** User taps CTA. App bundles technical metadata (device model, firmware version, OS version, last 5 BLE error codes) into an encrypted JSON payload, pre-fills a tier-2 support ticket, and provides user with a reference ticket number.

### Exception Flow 6 (EF-6): User Cancellation
- **At any step:** User taps the "Back" arrow or background dismisses Sync Center.
- **X.E1:** App safely aborts ongoing non-critical BLE scans to conserve battery.
- **X.E2:** App preserves pending sync state in local cache. Dashboard status card remains in `Partial Sync` mode until the next scheduled sync or user re-entry.

---

## 7. Business Rules

| Rule ID | Rule Name | Description & Enforcement |
|---|---|---|
| **BR-R01** | **No False Positives** | The system must NEVER display a successful sync message or update dashboard metrics unless the full category payload has been received and verified via CRC checksum. |
| **BR-R02** | **Retry Threshold Ceiling** | Maximum consecutive automated retries per session is strictly capped at **3 attempts**. After 3 failures, system must route user to support escalation to prevent battery drain and user rage. |
| **BR-R03** | **Battery Protection Guardrail** | Recovery BLE polling must terminate after **45 seconds** if no packet handshake is received. Background retry intervals must adhere to exponential back-off (2m, 5m, 15m). |
| **BR-R04** | **Differential Sync Preservation** | Retry actions must only query missing data blocks. Previously verified categories (e.g., Steps) must never be re-requested or overwritten during recovery. |
| **BR-R05** | **Zero Health PII in Logs** | Diagnostic error packages sent to customer support or analytics must contain zero user biometric data (heart rates, step totals, GPS tracks). Only technical BLE stack traces are permitted. |

---

## 8. Postconditions

### Success Postconditions
1. All pending activity, sleep, and workout data are safely written to local SQLite database and synchronized with cloud profile.
2. Dashboard sync status updates to *"Up to date"*, with timestamp refreshed to current time.
3. User session retry counter is reset to 0.
4. Telemetry event `sync_success` logged with duration and payload metrics.

### Failure Postconditions
1. Incomplete categories remain marked as `Failed` or `Delayed`.
2. Existing local health data is preserved without corruption.
3. Retry attempt counter is incremented and logged in telemetry.
4. Support ticket reference is displayed if escalation threshold was crossed.

---

## 9. Traceability & Engineering Validation Points

- **Related Business Requirements:** `BR-01, BR-02, BR-03, BR-04, BR-05, BR-06`
- **Related Functional Requirements:** `FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-09, FR-10`
- **Related User Stories:** `US-01, US-02, US-03, US-04, US-05, US-06, US-07, US-08, US-09`
- **Related KPIs:** `KPI-01 (Sync Success Rate), KPI-02 (Recovery Rate), KPI-03 (Time to Recover), KPI-05 (Support Volume)`

### Engineering Validation Gate (Requires Tech Lead Sign-off):
> `[ENGINEERING VALIDATION REQUIRED]`
> 1. Exact BLE MTU size negotiation (typically 23 to 512 bytes) and packet streaming throughput under low signal (RSSI < -85 dBm).
> 2. Android 14 foreground service types (`dataSync` / `connectedDevice`) compliance to prevent background process termination.
> 3. Support API endpoint latency and payload schema for automated diagnostic package transmission.
