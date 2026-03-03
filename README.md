
🐺 SKÖLL

AI-Based Insider Threat Detection Using Behavioral Drift


---

### Overview

SKÖLL is an AI-powered insider threat detection system designed to identify malicious intent before data exfiltration occurs.
It continuously monitors user behavior, detects behavioral drift, and triggers automated security responses in real time.

The system is built for high-security environments and aligns with the Digital Personal Data Protection (DPDP) Act 2026.


---

### Problem

Insider threats are:

Trusted by default

Slow and subtle

Difficult to detect using rule-based systems


Traditional security tools react after data loss occurs.
Under the DPDP Act 2026, delayed detection leads to legal, financial, and reputational damage.


---

### Solution

SKÖLL introduces predictive insider threat detection by:

Learning normal user behavior using AI

Continuously measuring behavioral deviations

Automatically stopping high-risk sessions


This enables organizations to detect intent, not just violations.


---

### Core Innovation

Behavioral Drift Detection Engine

User activity is modeled using LSTM neural networks

Live actions are compared with historical baselines

KL-Divergence measures statistical deviation

Drift severity is converted into a Trust Score


This approach detects low-and-slow insider attacks that evade traditional security systems.


---

### System Architecture

User Activity Logs
        ↓
Behavioral Modeling (LSTM)
        ↓
Drift Analysis (KL-Divergence)
        ↓
Trust Score Engine
        ↓
Automated Kill-Switch & Audit Logs


---

### Automated Kill-Switch

When behavioral drift exceeds a defined risk threshold:

User session is immediately locked

Permissions are revoked

Incident is logged for compliance review


⏱️ Zero manual delay. Zero data exposure.


---

### Trust Score

Each session receives a Trust Score (0–100) based on:

Behavioral consistency

Drift intensity

Historical user profile


### Trust Score	System  Action

80–100. 	 Normal operation
50–79	         Monitored
Below 50	 Automatic lockout



---

### Roles

Security Administrator

Real-time dashboard monitoring

Threshold and policy configuration

Incident and audit review


### Standard User

Normal, authorized behavior baseline


### Anomalous User

Simulated insider threat behavior



---

### DPDP Act 2026 Compliance

SKÖLL directly supports DPDP requirements by:

Continuous internal access monitoring

Rapid automated response

Incident traceability

Audit-ready compliance reports


All events are logged for regulatory verification.


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

AI-based Behavioral Analytics

Trae (Pro – Hackathon Access)



---

### Hackathon Demonstration Flow

1. Train baseline user behavior


2. Inject anomalous activity


3. Observe behavioral drift increase


4. Trigger automated kill-switch


5. Display generated compliance report




---

### Impact

Prevents insider data breaches before execution

Reduces DPDP compliance risk

Minimizes false positives through adaptive learning

Scales across enterprise and government systems



---

### Conclusion

SKÖLL transforms insider threat detection from reactive to predictive by identifying behavioral intent.
It delivers early warning, automated protection, and legal compliance in a single intelligent system.


---

### About

SKÖLL is an AI sentinel that hunts insider threats through behavioral intelligence.

🐺🛡️


---
