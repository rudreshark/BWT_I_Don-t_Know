### 🐺 SKÖLL

AI-Based Insider Threat Detection Using Behavioral Drift


---

### Overview

SKÖLL is an AI-powered insider threat detection system designed to identify malicious intent before data exfiltration occurs.
It continuously monitors user behavior, detects behavioral drift, and triggers automated security responses in real time.

The system is designed for high-security environments and aligns with the Digital Personal Data Protection (DPDP) Act 2026.


---

### Problem Statement

Detecting stealthy “low-and-slow” insider threats that bypass traditional security mechanisms through subtle, long-term behavioral drift.


---

### The Issue

Traditional security systems fail to detect insider threats that:

Operate gradually over long periods

Appear legitimate at each individual step

Avoid triggering rule-based alerts



---

### The Risk

By 2026, organizations may face ₹250 Crore penalties under the DPDP Act if they fail to:

Detect internal data misuse

Prevent insider-driven data leaks

Maintain proper audit trails



---

### The Gap

Existing security tools are too rigid:

They cannot differentiate between legitimate behavior changes (role change, promotion)

And malicious insider actions (data theft, source code exfiltration)



---

### Proposed Solution

SKÖLL – Behavioral Drift–Based Insider Threat Detection

SKÖLL is an AI-powered monitoring shield, built using Trae, that detects insider threats by analyzing behavioral drift over time instead of relying on static rules.


---

### Core Concept

Continuous monitoring of developer activity

Long-term behavioral baseline learning

Detection of subtle deviations using statistical drift analysis

Automated action before data loss occurs



---

### Methodology

Component	     Description

Baseline Window	     90-day historical user behavior
Observation Window	Current 7-day activity
Drift Measurement	KL-Divergence
Learning Model	    LSTM Neural Networks
Risk Output	    Trust Score (0–100)



---

### System Architecture (Logical Flow)

User / Developer Activity Logs
            ↓
LSTM Behavioral Modeling
            ↓
KL-Divergence Drift Analysis
            ↓
Real-Time Trust Score Engine
            ↓
Automated Kill-Switch
            ↓
Audit Logs & DPDP Compliance Reports


---

### Key Features

🔍 LSTM Behavioral Profiling

Learns the unique behavioral fingerprint of each user

Adapts naturally to gradual role or workload changes


### 📊 Real-Time Trust Score

Trust Score ranges from 0–100

Displayed live on the admin dashboard


### 🚨 Automated Kill-Switch

Instantly revokes Git / SSH / system permissions

Triggered when high-risk behavioral drift is detected


### 📑 DPDP Audit Logs

One-click compliance reporting

Designed for regulatory verification



---

### Trust Score Interpretation

Trust Score Range	System Action

80–100	        Secure – Normal Operation
50–79	        Warning – Under Monitoring
Below 50	Critical – Access Revoked



---

### User Interfaces (Mocked)

IDE Sidebar

Displays live Trust Score (example: 85% Secure)


### Drift Visualization

Green Line → Baseline behavior

Red Line → Current drift trend


### Lock Screen Overlay

Access Denied  
Unusual Behavioral Drift Detected


---

### Roles

Security Administrator

Monitor Trust Scores

Configure drift thresholds

Review incidents and audit logs


### Standard User

Normal, authorized behavior baseline


### Anomalous User

Simulated insider threat behavior



---

### Repository Structure

/src        → AI models and detection logic  
/data       → Simulated employee activity logs  
/ui         → Admin monitoring dashboard  
/reports    → DPDP 2026 audit and incident logs


---

### Technology Stack

Python

LSTM Neural Networks

KL-Divergence

Behavioral Analytics

Trae Platform



---

### Hackathon Demonstration Flow

1. Train baseline behavior using 90-day simulated data


2. Introduce anomalous activity


3. Observe gradual behavioral drift


4. Trust Score drops below threshold


5. Automated access revocation


6. Generate DPDP audit report




---

### Impact

Detects insider threats before execution

Prevents regulatory penalties

Reduces false positives

Scales across enterprise and government systems



---

### Conclusion

SKÖLL transforms insider threat detection from reactive to predictive by identifying behavioral intent, not just violations.
It unifies AI, automation, and compliance into a single intelligent security layer.


---

### About

SKÖLL — An AI sentinel guarding organizations against insider threats through behavioral intelligence.

🐺🛡️


---
