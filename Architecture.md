# SKÖLL: System Architecture & Operational Workflow

SKÖLL operates as a proactive security layer that monitors behavioral patterns within a development environment to identify intent-based threats.

🏗️ Technical Architecture
The system is built on a modular pipeline designed for real-time analysis and response:

1. Data Ingestion Layer
   - Collects logs across multiple dimensions: File I/O, CLI command history, and Git activity.
   - Imports datasets "in one go" using Python’s bulk-loading utilities for high-velocity analysis.

2. AI Analysis Layer (The Brain)
   - Temporal Profiling: A Long Short-Term Memory (LSTM) network establishes a "digital fingerprint" of normal operations.
   - Drift Calculation: The system utilizes Kullback–Leibler (KL) Divergence to measure the statistical distance between current behavior and the established baseline.

3. Response Layer
   - Risk Scoring: Assigns a real-time "Trust Score" (0-100) to every active session.
   - Automated Mitigation: Triggers a "Kill-Switch" to revoke permissions when behavior deviates beyond the safety threshold.



--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🔄 Operational Workflow (Demo Scenario)

To demonstrate the system’s capabilities, the workflow is divided into three distinct organizational perspectives:

I. Security Administration (The Watcher)
The administrator monitors the central command console. This role oversees the live telemetry of all users and manages the DPDP 2026 Audit Logs. When a drift is detected, the administrator confirms the automated lockout and reviews the incident report.

II. Baseline Operations (Standard Behavior)
Represents the "Safe User" profile. This workflow involves standard development tasks—editing source code, committing to established branches, and accessing relevant documentation. The system maintains a high trust score for this profile.

III. Malicious Drift (The Insider)
Represents the "Threat" profile. This workflow simulates a "low-and-slow" attack. The user gradually begins to access sensitive system files (e.g., `.env`, `/ssh_keys`) and executes unusual administrative commands. The system visualizes the "Red" drift line pulling away from the baseline in real-time.



--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 📁 Directory Logic
- `/src`: Detection logic and KL-Divergence mathematical implementation.
- `/data`: Storage for multi-user behavioral log spreadsheets.
- `/ui`: Real-time monitoring interface for the Security Administrator.
- `/reports`: Automatically generated PDF logs for DPDP 2026 regulatory compliance.


--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# System Architecture Flow
The SKÖLL engine processes data through five core stages to detect and mitigate insider threats in real-time:

|Developer Logs| ----> |Trae API| ----> |LSTM Temporal Profiler| ----> |KL Divergence Scoring| ----> |Automated Response| 


1. Developer Logs: Captures raw activity data, including file edits, CLI command history, and Git commits.

2. Trae API: Acts as the integration bridge, streaming normalized log data into the analysis pipeline.

3. LSTM Temporal Profiler: A neural network that profiles user behavior over time to establish a unique operational baseline.

4. KL Divergence Scoring: Calculates the statistical shift (drift) between current actions and the established profile.

5. Automated Response: Triggers the security kill-switch to revoke access if the drift score indicates high risk.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
