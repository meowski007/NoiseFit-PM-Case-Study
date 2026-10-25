# Three-Minute Executive Video Demo Script

> **DOCUMENT CONTROL & PRESENTATION SPECIFICATION**  
> **Project:** NoiseFit Sync Reliability Case Study & Linked SyncOps Assistant  
> **Artifact:** Time-Boxed 3-Minute Video Recording Script  
> **Total Duration:** Exactly 3 Minutes (180 Seconds)  
> **Target Audience:** PM Hiring Managers, Group PMs, and Technical Recruiters  
> **Recording Setup:** Single Laptop Screen Capture (OBS / Loom / QuickTime) with Voiceover  
> **Pre-Recording Command:** Ensure Streamlit (`streamlit run dashboard/app.py`) is open on `localhost:8501`, vector SVG screens are open in browser tabs, and `README.md` is visible.

---

## 1. Master Recording Timeline & Script Breakdown

| Timestamp | Screen / Visual Shot | Physical Action to Perform | Spoken Talking Points (Verbatim Script) | What the Viewer Should Notice | Evidence Captured in Video | Built vs. Proposed Status |
|---|---|---|---|---|---|---|
| **0:00 – 0:20**<br>(20s) | Repository Master Index ([`README.md`](../../README.md)) | Show repository root; highlight disclosure banner and executive summary. | *"Hi! I'm excited to share my Product Management case study on wearable synchronization reliability. In the digital health space, when data synchronization fails silently, users assume hardware defect or data loss, driving churn. In this project, I investigated synchronization unreliability across wearable ecosystems and engineered a four-stage recovery engine: Detect, Explain, Recover, and Confirm."* | Clear, professional repo layout; prominent portfolio disclosure establishing academic/independent context. | Bidirectional traceability matrix and document control. | **Verified Documentation** |
| **0:20 – 0:55**<br>(35s) | Research Register & RICE Spreadsheet ([`research/evidence_register.csv`](../../research/evidence_register.csv)) | Scroll through 426 coded reviews in Excel/CSV, then show RICE table in `README.md`. | *"Rather than relying on intuition, I mined and coded 426 Google Play reviews across NoiseFit, boAt, Fitbit, and Samsung Health. Within NoiseFit, Sync and Data issues accounted for 22.9% of all feedback, with 50% representing severe 1- and 2-star complaints. I applied an auditable RICE prioritization framework, where Reliable Sync & Recovery scored Rank 1 with 4.08, proving that fixing sync reliability protects core retention far more than adding cosmetic features."* | Stratified sampling across 5 rating tiers; empirical ranking separating feature requests from acute churn drivers. | 426 coded reviews; mathematical RICE score derivation. | **Empirical Research & Prioritization** |
| **0:55 – 1:45**<br>(50s) | Live **SyncOps Assistant** Streamlit Dashboard (`localhost:8501`) | Navigate between Overview, Incidents, Forecast, and RAG Triage tabs. Run a live RAG search: *"How do I resolve BLE buffer overflow?"* | *"To model the backend reliability required for high-scale sync platforms, I built SyncOps Assistant. It's a functional FastAPI and Streamlit platform powered by deterministic synthetic telemetry. Here on the dashboard, you see real-time calculation of all seven customer-experience KPIs, including a 70.9% sync success baseline and median time to recover. In the triage tab, our grounded TF-IDF RAG engine searches 13 SRE runbooks, providing exact markdown citations and enforcing strict refusal guardrails if an inquiry lacks relevant operational runbooks."* | Functional UI updating dynamically; sub-second RAG search returning verifiable section citations and runbook links. | Real-time 7-KPI calculation; RAG retrieval engine with citation provenance. | **Verified Functional Software** (Separate SRE Platform) |
| **1:45 – 2:25**<br>(40s) | NoiseFit 8-Screen UX Prototype ([`05_UX/SVG_Screens/`](../../05_UX/SVG_Screens/)) | Click through vector screens: `screen_01_Dashboard.svg` $\rightarrow$ `screen_03_Partial_Sync.svg` $\rightarrow$ `screen_04_Sync_Details.svg` $\rightarrow$ `screen_07_Sync_Complete.svg`. | *"For the consumer mobile experience, I designed an 8-screen vector prototype for our target persona, Aarav. Instead of a silent spinner, the dashboard surfaces a partial sync card. Tapping it opens Sync Center, breaking down Steps, Heart Rate, and Sleep. The user receives plain-language explanations—like Bluetooth interruption—and can tap a single differential retry that requests only missing sleep packets. Finally, the confirmation screen gives explicit peace of mind with verified timestamps."* | Clean 8pt design system; high-contrast WCAG 2.1 AA badges; seamless 4-stage transition from detection to confirmation. | 8 vector SVG prototype screens; Figma wireframe specifications. | **Proposed UX Design Concept** (Prototype) |
| **2:25 – 2:50**<br>(25s) | Upgraded A/B Test Plan ([`product/experimentation/ab-test-plan.md`](../experimentation/ab-test-plan.md)) | Highlight statistical power formula ($n=356$) and guardrail metrics table. | *"To validate this feature safely, I authored a comprehensive A/B experimentation plan. For our primary metric—Sync Recovery Rate within 15 minutes—I used a two-proportion z-test to calculate that we need 356 failure incidents per variant for 80% power at 95% confidence. The rollout includes non-negotiable guardrails on app crash rate and battery drain, with an emergency kill-switch protocol."* | Formal statistical sample sizing; pre-defined decision tree; guardrail metrics preventing unmonitored rollout. | Mathematical sample-size derivation; 5-phase rollout schedule. | **Proposed Experiment Design** (Unexecuted) |
| **2:50 – 3:00**<br>(10s) | Product Roadmap & Research Kit ([`product/roadmap-and-backlog.md`](../roadmap-and-backlog.md)) | Show Now/Next/Later roadmap and research kits. Conclude video. | *"All research and usability kits are ready for execution with 5 to 8 users. This portfolio reflects my end-to-end approach to product management: grounded discovery, quantitative rigor, technical fluency, and empathetic UX. Thank you!"* | Cohesive Now/Next/Later roadmap; professional closing. | Complete PM artifact suite. | **Active Portfolio Standard** |

---

## 2. Pre-Recording Technical Checklist

Before hitting "Record", ensure your workstation is set up:
- [ ] **FastAPI Backend Running:** In terminal 1: `uvicorn app.main:app --port 8000` inside `syncops-assistant/`.
- [ ] **Streamlit Running:** In terminal 2: `streamlit run dashboard/app.py` inside `syncops-assistant/`. Browser opened at `http://localhost:8501`.
- [ ] **Browser Tabs Prepared in Order:**
  - Tab 1: Root [`README.md`](../../README.md) (on GitHub or local markdown preview).
  - Tab 2: [`research/evidence_register.csv`](../../research/evidence_register.csv) (or Excel spreadsheet).
  - Tab 3: Streamlit Operations Cockpit (`http://localhost:8501`).
  - Tab 4: Vector SVG screen [`05_UX/SVG_Screens/screen_01_Dashboard.svg`](../../05_UX/SVG_Screens/screen_01_Dashboard.svg).
  - Tab 5: Vector SVG screen [`05_UX/SVG_Screens/screen_04_Sync_Details.svg`](../../05_UX/SVG_Screens/screen_04_Sync_Details.svg).
  - Tab 6: Vector SVG screen [`05_UX/SVG_Screens/screen_07_Sync_Complete.svg`](../../05_UX/SVG_Screens/screen_07_Sync_Complete.svg).
  - Tab 7: [`product/experimentation/ab-test-plan.md`](../experimentation/ab-test-plan.md).
- [ ] **Audio Check:** Test microphone input levels; eliminate background fan noise.
- [ ] **Resolution:** Set screen recording resolution to standard 1080p ($1920 \times 1080$).

---

## 3. Beginner-Friendly Explainer

### What this artifact does
This script is a second-by-second presentation plan for recording a 3-minute video portfolio walkthrough. It details exactly what to click, what to show on screen, and what words to speak, ensuring a smooth, highly professional delivery.

### Why it matters
Hiring managers often spend less than two minutes reviewing an internship application. A tight, polished 3-minute video demonstration proves communication skills, executive presence, and product passion far faster than a 50-page document.

### How to use it
- Rehearse the script with a stopwatch 2–3 times to get comfortable with the pacing.
- Use Loom or OBS to record your screen and voice in one continuous take.
- Embed the resulting video link at the top of your portfolio README and LinkedIn post.

### What I can honestly claim in an interview
- **Can claim:** You designed, timed, and recorded a 3-minute executive walkthrough showcasing the empirical review analysis, live SyncOps platform, UX prototype, and statistical experiment plan.
- **Cannot claim:** You cannot claim that the mobile Sync Center screens are running on a real smartphone. Emphasize that SyncOps Assistant is a functional reliability tool, while Sync Center is a proposed UX prototype.
