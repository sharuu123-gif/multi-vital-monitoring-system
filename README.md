# Multi-Vital Early Warning System (MVEWS) with Deterioration Prediction

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Clinical Standard](https://img.shields.io/badge/Clinical%20Standard-NEWS2%20%2F%20RCP-red.svg)](https://www.rcplondon.ac.uk/projects/outputs/national-early-warning-score-news-2)
[![Smart Healthcare](https://img.shields.io/badge/Domain-Smart%20Healthcare%20%26%20ICU-purple.svg)]()

A clinical-grade, intelligent physiological monitoring and decision-support system designed for Intensive Care Units (ICU), emergency departments, and hospital step-down wards.

The system ingests continuous multi-vital telemetry (**Heart Rate [HR], Respiratory Rate [RR], Oxygen Saturation [SpO₂], Temperature [Temp], and Blood Pressure [SBP/DBP]**), eliminates spurious motion artifacts via **online Median Filtering**, calculates standardized **clinical Early Warning Scores (NEWS2 / MVEWS)**, tracks physiological **trajectory and score velocity (trend)**, predicts acute clinical deterioration within 2–4 hours using **Machine Learning**, and triggers tiered **Clinical Escalation Protocols** with automated **SBAR communication handoffs**.

---

## 🏗️ System Architecture

```
[ Continuous Patient Vitals ]
  HR, RR, SpO₂, Temp, SBP, DBP
               │
               ▼
┌─────────────────────────────────┐
│   Online Median Filter (1D)     │  <-- Window Size: 3-11 samples
│  Outlier & Artifact Suppression │  <-- Rejects sensor disconnects, motion spikes
└──────────────┬──────────────────┘
               │
       Cleaned Vital Stream
               │
       ┌───────┴────────────────────────┐
       ▼                                ▼
┌───────────────────────┐   ┌───────────────────────────┐
│ Clinical Score Engine │   │   Trend & Slope Engine    │
│  NEWS2 / MVEWS Rules  │   │  Linear Regression Slopes │
│  MAP & Shock Index    │   │  Score Velocity (pts/hr)  │
└──────────┬────────────┘   └─────────────┬─────────────┘
           │                              │
           └──────────────┬───────────────┘
                          ▼
┌────────────────────────────────────────────────────────┐
│     Predictive Machine Learning Engine (2h-4h)        │
│  - Deterioration Probability (Gradient Boosting)       │
│  - 2-Hour Forecasted EWS (Random Forest Regressor)     │
│  - Syndromic Risks: Sepsis, Shock, Respiratory Failure │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│             Clinical Escalation Engine                 │
│  Level 0: Routine Monitoring (12h cycle)               │
│  Level 1: Low Risk (4-6h nurse assessment)             │
│  Level 2: Urgent Ward Doctor Review (30-60 min)        │
│  Level 3: CRITICAL / Emergency Team (MET / RRT / ICU)  │
│  ----------------------------------------------------  │
│  Automated Clinical SBAR Communication Report          │
└────────────────────────────────────────────────────────┘
```

---

## 💡 Core Features

### 1. Robust Online Median Filtering
- Suppresses high-frequency sensor disconnects, patient movement artifacts, and loose lead dips.
- Uses physiological sanity boundary clamping (`20-260 bpm` for HR, `40-100%` for SpO₂, etc.).
- Eliminates ICU false alarms while preserving authentic, sustained clinical decompensations.

### 2. Standardized Multi-Vital Scoring Engine
- Implements Royal College of Physicians **NEWS2 (National Early Warning Score 2)**.
- Sub-scores computed for HR, RR, SpO₂, Body Temperature, and Systolic BP.
- Computes advanced hemodynamic indices:
  - **Mean Arterial Pressure (MAP)**: $\text{MAP} = \frac{2 \times \text{DBP} + \text{SBP}}{3}$
  - **Shock Index (SI)**: $\text{SI} = \frac{\text{HR}}{\text{SBP}}$ (Identifies occult hypovolemic / septic shock early).
- Detects single-parameter extreme red flags (score 3 in any single vital).

### 3. Multi-Window Physiological Trend Analysis
- Multi-sample linear regression slopes:
  - $\Delta \text{HR}/\Delta t$ (bpm/hour)
  - $\Delta \text{RR}/\Delta t$ (breaths/min/hour)
  - $\Delta \text{SpO}_2/\Delta t$ (%/hour)
  - $\Delta \text{SBP}/\Delta t$ (mmHg/hour)
- **Score Velocity ($\Delta \text{EWS}/\Delta t$)**: Flags rapid deterioration even before absolute score reaches emergency thresholds.
- Trajectory classifications: `Rapidly Deteriorating`, `Deteriorating`, `Stable`, `Improving`.

### 4. Machine Learning Predictive Deterioration Engine
- **Classification Model**: Calibrated `GradientBoostingClassifier` forecasting acute deterioration probability ($0\% - 100\%$) in the next 2 to 4 hours.
- **Regression Model**: `RandomForestRegressor` projecting estimated EWS score at $+2\text{h}$.
- **Syndromic Profiling**:
  - **Sepsis / SIRS Syndrome Risk Score** (qSOFA criteria integration)
  - **Hemodynamic Shock Risk Index**
  - **Acute Hypoxemic Respiratory Failure Risk**

### 5. Multi-Tier Clinical Escalation Protocol
| Escalation Tier | Score Criteria | Clinical Response Team | Maximum Response Time | Monitoring Frequency |
|---|---|---|---|---|
| **Level 0: Routine** | Score 0 | Ward Nurse | Next scheduled round | 12-hourly |
| **Level 1: Low Risk** | Score 1–4 | Registered Nurse | Within 2–4 hours | 4–6 hourly |
| **Level 2: Urgent Review** | Score 5–6 OR Single Red Vital | Ward Resident / Registrar | Within 30–60 minutes | 1-hourly / Telemetry |
| **Level 3: Critical Alert** | Score $\ge 7$ OR Rapid Velocity | Medical Emergency Team (MET) / ICU | **IMMEDIATE (< 15 min)** | Continuous Telemetry |

### 6. Automated Clinical SBAR Handoff Report
Generates structured **Situation, Background, Assessment, Recommendation (SBAR)** documentation ready for copy/export during emergency escalations.

---

## 🚀 Quickstart Guide

### 1. Installation
Clone or extract the repository, and install the dependencies:
```bash
cd multi_vital_early_warning_system
pip install -r requirements.txt
```

### 2. Launch the Interactive Web Dashboard
Run the one-click launcher:
```bash
python run_dashboard.py
```
*Alternatively, run with Streamlit directly:*
```bash
streamlit run web/app.py
```
Open your browser at `http://localhost:8501`.

#### What you can do in the Dashboard:
- **Live Telemetry Stream**: Test 5 realistic clinical scenarios (*Sepsis Decompensation*, *Acute Respiratory Failure*, *Hemorrhagic Shock*, *Sensor Artifact Spikes*, and *Stable Ward Patient*).
- **Raw vs. Filtered Signal Graphs**: Toggle interactive Plotly charts showing real-time median filter spike suppression.
- **Predictive Gauge**: Watch the real-time AI decompensation probability gauge and syndromic risk bars.
- **Escalation & Actions**: Review mandatory hospital actions and download the SBAR report.
- **Manual Vital Sandbox**: Adjust sliders for HR, RR, SpO2, Temp, BP to simulate any custom edge case.
- **Batch CSV Analysis**: Upload external telemetry CSV files or analyze pre-loaded ICU datasets.

---

### 3. Command Line Interface (CLI)

#### Run a Simulation Stream in Terminal:
```bash
python run_cli.py --scenario sepsis --steps 20
```

#### Test Noise Rejection with Median Filter:
```bash
python run_cli.py --scenario noise_artifacts --filter-window 5
```

#### Evaluate a Single Patient Snapshot:
```bash
python run_cli.py --test-manual --hr 128 --rr 28 --spo2 90 --temp 39.1 --sbp 86 --dbp 52
```

#### Batch Process an External Telemetry CSV:
```bash
python run_cli.py --csv data/sample_sepsis_case.csv
```

---

### 4. Run Verification Unit Tests
```bash
python run_evaluation.py
```

---

## 📂 Project Directory Structure

```
multi_vital_early_warning_system/
├── core/
│   ├── __init__.py
│   ├── vitals_filter.py        # Online & batch 1D Median Filter & artifact suppression
│   ├── scoring_engine.py       # NEWS2 / MVEWS scoring, MAP, Shock Index
│   ├── trend_analyzer.py       # Multi-window slopes & score velocity
│   ├── predictor.py            # Gradient Boosting & Random Forest ML models
│   ├── escalation.py           # Level 0-3 clinical escalation & SBAR generator
│   └── patient_simulator.py    # Realistic patient telemetry scenario streams
├── data/
│   ├── sample_icu_telemetry.csv
│   ├── sample_sepsis_case.csv
│   ├── sample_shock_case.csv
│   └── generate_samples.py
├── models/
│   ├── train_model.py          # Synthetic dataset generator & model calibration
│   ├── vital_classifier.joblib # Saved deterioration classifier
│   └── vital_regressor.joblib  # Saved 2h score regressor
├── tests/
│   ├── test_filter.py
│   ├── test_scoring.py
│   └── test_escalation.py
├── web/
│   └── app.py                  # Streamlit clinical dashboard
├── README.md                   # Comprehensive technical & clinical documentation
├── requirements.txt            # Python dependencies
├── run_dashboard.py            # One-click dashboard runner
├── run_cli.py                  # CLI simulation and analysis tool
└── run_evaluation.py           # Unit test verification suite
```

---

## 📜 Clinical Disclaimer
*This system is designed as an investigative and educational clinical decision-support prototype conforming to Royal College of Physicians NEWS2 guidelines. It does not replace professional clinical judgment or certified medical devices in clinical practice.*
