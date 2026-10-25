# PM & QA Bug Report Template — Defect Tracking Standard

> **DOCUMENT CONTROL & QA GOVERNANCE**  
> **Project:** NoiseFit Sync Reliability — Sync Center  
> **Artifact:** Standardized Bug Report Specification & Illustrative Example  
> **Status:** Reusable QA Engineering Standard  
> **Linked Artifacts:** [UAT Plan](./uat-plan.md) · [10 User Stories](../../docs/USER_STORIES.md) · [SyncOps Release Notes](../release/release-notes.md)

---

## 1. Defect Severity & Priority Classification Standards

To ensure consistent defect triage across product management, engineering, and QA leads, defects are evaluated along two orthogonal dimensions: **Severity** (technical impact) and **Priority** (business urgency).

### Severity Levels (Technical Impact)
- **SEV1 — Critical (Blocker):** Catastrophic system failure. Core application crashes on launch, causes irrecoverable health data loss, corrupts local database, or drains $>5.0\%$ battery per hour. No workaround exists. Blocks release.
- **SEV2 — Major (High):** Major functional breakdown. A primary feature (e.g., One-Tap Retry or Bluetooth reconnection) fails for a significant user cohort. A painful workaround exists (e.g., manual phone reboot). Must fix before general availability.
- **SEV3 — Minor (Medium):** Non-critical functional defect or edge-case failure. Feature operates incorrectly under rare conditions (e.g., incorrect timestamp formatting after timezone change), but core recovery remains functional.
- **SEV4 — Trivial (Low / Cosmetic):** Minor visual polish flaw, typographic error, micro-copy misalignment, or slight color discrepancy that does not impede task completion.

### Priority Levels (Business Urgency)
- **P0:** Immediate hotfix / sprint blocker. Work commences immediately; halts deployment pipeline.
- **P1:** High priority. Must be addressed in current sprint or release candidate.
- **P2:** Medium priority. Scheduled for subsequent sprint cycle.
- **P3:** Low priority. Placed in backlog for future polish.

---

## 2. Reusable Bug Report Template (Blank Form)

```markdown
### Bug Report: [BUG-ID] — [Short, Descriptive Imperative Title]

- **Bug ID:** `BUG-NF-XXXX`
- **Report Date:** `YYYY-MM-DD`
- **Reporter / QA Engineer:** `[Name / Role]`
- **Assigned Component / Module:** `[e.g., BLE Radio Manager / Sync Center UI / Local SQLite Database]`
- **Assigned Owner:** `[e.g., Hypothetical Mobile Engineering Lead]`
- **Environment:**
  - Device Model: `[e.g., Google Pixel 7 / Samsung Galaxy S23 / iPhone 14]`
  - Operating System Build: `[e.g., Android 14.0 Build UP1A.231005.007]`
  - Application Version / Commit: `[e.g., v4.2.0-rc2 (Commit: abc1234)]`
  - Smartwatch Firmware Version: `[e.g., v1.0.42_BLE]`
- **Associated Requirement / Story:** `[e.g., US-04 (Scenario 04.3) / FR-05]`
- **Severity Level:** `[ ] SEV1 (Critical)  [ ] SEV2 (Major)  [ ] SEV3 (Minor)  [ ] SEV4 (Trivial)`
- **Priority Level:** `[ ] P0  [ ] P1  [ ] P2  [ ] P3`
- **Reproducibility Rate:** `[ ] 100% (Deterministic)  [ ] ~75% (Frequent)  [ ] Intermittent (<25%)`

#### Preconditions:
1. `[Precondition 1: e.g., Smartwatch paired via BLE]`
2. `[Precondition 2: e.g., Host smartphone has Bluetooth disabled in OS quick settings]`

#### Steps to Reproduce:
1. `[Step 1]`
2. `[Step 2]`
3. `[Step 3]`

#### Expected Result:
`[Clear, unambiguous statement of what should have occurred according to the PRD/acceptance criteria]`

#### Actual Result:
`[Precise, factual description of what actually occurred on the device]`

#### Workaround (if known):
`[Steps user can take to bypass the defect, if any]`

#### Supporting Evidence & Diagnostic Logs:
- Screenshot / Video Link: `[Attachment link]`
- Device Logcat / Console Extract:
  ```text
  [Insert relevant log snippet with timestamps and error codes]
  ```

#### Suspected Root Cause:
`[Engineering hypothesis on what component or logic branch failed]`

#### Verification & Retest Status:
- Status: `[ ] New  [ ] Triaged  [ ] In Progress  [ ] Fixed in Build ___  [ ] Verified & Closed`
- Retest Date: `[YYYY-MM-DD]` | Retested By: `[Name]`
```

---

## 3. Filled-In Example (Illustrative Quality Defect)

> **GOVERNANCE DISCLOSURE:**  
> **ILLUSTRATIVE EXAMPLE — NOT A VERIFIED DEFECT.**  
> The example below is an illustrative quality report demonstrating how a Senior PM or QA Lead documents complex asynchronous BLE edge-case bugs. It does not represent an actual defect logged in production software.

```markdown
### Bug Report: BUG-NF-0104 — Rapid consecutive taps on "Retry Sync" trigger duplicate BLE socket allocation and app freeze

- **Bug ID:** `BUG-NF-0104`
- **Report Date:** `2026-10-26`
- **Reporter / QA Engineer:** `[Hypothetical: Mobile QA Lead]`
- **Assigned Component / Module:** `Mobile BLE Connection Manager (Android Client)`
- **Assigned Owner:** `[Hypothetical: Android Engineering Lead]`
- **Environment:**
  - Device Model: Samsung Galaxy S22 (SM-S901B)
  - Operating System Build: Android 14 (OneUI 6.0)
  - Application Version / Commit: NoiseFit Companion v4.2.0-rc1 (Commit: 8f2a1b9)
  - Smartwatch Firmware Version: Noise ColorFit Pro 4 Firmware v2.1.8
- **Associated Requirement / Story:** `US-04 (Scenario 04.1) / FR-05 / NFR-01`
- **Severity Level:** **SEV2 (Major)**
- **Priority Level:** **P1**
- **Reproducibility Rate:** **100% (Deterministic when tapped $\ge 3$ times in under 1 second)**

#### Preconditions:
1. Smartwatch is connected via BLE with simulated partial sync state (Steps synced, Sleep delayed).
2. User is on Screen 04 ("Sync Details — Failure").

#### Steps to Reproduce:
1. Tap the primary "Retry Sync" button rapidly three times in rapid succession (<500ms between taps).
2. Observe UI state transition and Android system logcat.

#### Expected Result (Per US-04, Scenario 04.1):
The primary "Retry Sync" CTA button must immediately disable upon the first tap, enter an unclickable loading state, and render the "Recovering" screen (Screen 06) with a single active BLE socket. Subsequent taps should be ignored.

#### Actual Result:
The CTA button remains clickable for ~400ms before navigating to Screen 06. The mobile app initiates three simultaneous asynchronous BLE GATT connection handshakes (`gatt.connect()`). The Android OS Bluetooth daemon detects socket conflict, logs error code `GATT_STACK_BUSY_8`, freezes the UI thread for 4.2 seconds, and forces the application into an Application Not Responding (ANR) crash dialog.

#### Workaround:
Force-quit the companion app from the Android recent apps menu, toggle Bluetooth off and on, and relaunch the app.

#### Supporting Evidence & Diagnostic Logs:
- Video Attachment: `evidence/bug_0104_anr_freeze.mp4`
- Android Logcat Extract:
  ```text
  2026-10-26 14:15:02.104 2841-2910/com.noisefit.app W/BluetoothGatt: connect() - device: DC:54:75:A1:02:11, auto: false
  2026-10-26 14:15:02.215 2841-2910/com.noisefit.app W/BluetoothGatt: connect() - socket already allocated! Overlapping handshake requested.
  2026-10-26 14:15:02.320 2841-2910/com.noisefit.app E/BluetoothGatt: GATT_CONN_FAIL: status 8 (GATT_STACK_BUSY)
  2026-10-26 14:15:06.520 1204-1245/system_server E/ActivityManager: ANR in com.noisefit.app (com.noisefit.app/.ui.SyncCenterActivity)
  Reason: Input dispatching timed out (Waiting to send non-key event because the focused window has not finished processing the previous input)
  ```

#### Suspected Root Cause:
The `onClick` listener on the "Retry Sync" button in `SyncDetailsFragment.kt` executes asynchronous network dispatch without immediately setting `button.isEnabled = false` on the main UI thread. Multiple coroutines launch concurrently and conflict on the shared singleton `BleGattManager`.

#### Proposed Fix:
1. Implement immediate atomic UI disabling: Set `button.isEnabled = false` and show spinner synchronously on the first touch event.
2. In `BleGattManager.kt`, enforce mutex lock on `connectGatt()` to reject redundant connection requests while a handshake is in flight.

#### Verification & Retest Status:
- Status: `Triaged`
- Target Milestone: Sprint 14 Hotfix
```

---

## 4. Beginner-Friendly Explainer

### What this artifact does
This document establishes the official Bug Reporting Standard for the product. It defines technical severity levels (SEV1–SEV4), business priority tiers (P0–P3), provides a reusable blank template, and includes an illustrative filled-in defect report modeling an asynchronous BLE socket crash.

### Why it matters
Product Managers work closely with QA and engineering leads to triage bugs during release crunch. Writing precise reproduction steps, distinguishing expected vs. actual outcomes, and providing raw diagnostic logs saves engineering hours and proves that you understand technical root causes.

### How to use it
- Use the blank template whenever you discover unexpected behavior during prototype or code testing.
- Fill out every field systematically before assigning the ticket to an engineering lead.
- Reference the illustrative bug report in interviews to explain how you handle race conditions and UI-thread deadlocks.

### What I can honestly claim in an interview
- **Can claim:** You established this PM/QA bug tracking standard, defined severity/priority criteria, and drafted an illustrative technical defect report demonstrating deep knowledge of BLE race conditions and Android ANR handling.
- **Cannot claim:** You cannot claim that `BUG-NF-0104` was logged by a real customer on production servers; it is prominently labeled as an illustrative engineering example.
