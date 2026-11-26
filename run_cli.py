"""
Multi-Vital Early Warning System (MVEWS) - Command Line Interface
================================================================
Run simulations, test filtering, scoring, trends, and escalation directly in the terminal.

Usage:
    python run_cli.py --scenario sepsis
    python run_cli.py --scenario noise_artifacts --filter-window 5
    python run_cli.py --csv data/sample_sepsis_case.csv
    python run_cli.py --test-manual --hr 125 --rr 26 --spo2 91 --temp 38.8 --sbp 92 --dbp 58
"""

import sys
import os
import argparse
import time
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform.startswith("win"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from core.vitals_filter import VitalMedianFilter
from core.scoring_engine import ScoringEngine
from core.trend_analyzer import TrendAnalyzer
from core.predictor import VitalPredictor
from core.escalation import EscalationProtocol
from core.patient_simulator import PatientSimulator, SCENARIO_DESCRIPTIONS


def run_manual_test(hr, rr, spo2, temp, sbp, dbp):
    print("=" * 70)
    print("  MULTI-VITAL EARLY WARNING SCORE & ESCALATION ANALYSIS")
    print("=" * 70)
    print(f"Input Vitals: HR={hr} bpm, RR={rr}/min, SpO2={spo2}%, Temp={temp}°C, BP={sbp}/{dbp} mmHg\n")

    # 1. Scoring
    scores = ScoringEngine.evaluate(hr=hr, rr=rr, spo2=spo2, temp=temp, sbp=sbp, dbp=dbp)
    print(f"[1] CLINICAL SCORING (NEWS2 / MVEWS)")
    print(f"    - Heart Rate Score:        {scores.hr_score}")
    print(f"    - Respiratory Rate Score:  {scores.rr_score}")
    print(f"    - Oxygen Saturation Score: {scores.spo2_score}")
    print(f"    - Temperature Score:       {scores.temp_score}")
    print(f"    - Systolic BP Score:       {scores.sbp_score}")
    print(f"    ---------------------------------------")
    print(f"    TOTAL EARLY WARNING SCORE: {scores.total_score} (Risk Level: {scores.risk_level})")
    print(f"    Mean Arterial Pressure:    {scores.map_value} mmHg")
    print(f"    Shock Index:               {scores.shock_index} ({scores.shock_risk})\n")

    # 2. Prediction
    predictor = VitalPredictor()
    pred = predictor.predict(hr=hr, rr=rr, spo2=spo2, temp=temp, sbp=sbp, dbp=dbp, current_score=scores.total_score)
    print(f"[2] PREDICTIVE MACHINE LEARNING (2-4 Hour Horizon)")
    print(f"    - Deterioration Probability: {pred.deterioration_probability * 100:.1f}%")
    print(f"    - Risk Classification:       {pred.risk_category}")
    print(f"    - Forecasted EWS at +2h:     {pred.predicted_ews_2h:.1f} pts")
    print(f"    - Sepsis Risk Score:         {pred.sepsis_risk_score:.0f}%")
    print(f"    - Shock Decompensation Risk: {pred.shock_decompensation_risk:.0f}%\n")

    # 3. Escalation
    vital_summary = {"hr": f"{hr} bpm", "rr": f"{rr}/min", "spo2": f"{spo2}%", "temp": f"{temp}°C", "bp": f"{sbp}/{dbp} mmHg"}
    esc = EscalationProtocol.determine_escalation(
        total_score=scores.total_score,
        has_extreme_trigger=scores.has_extreme_trigger,
        trajectory_status="Static Evaluation",
        predicted_category=pred.risk_category,
        vital_summary=vital_summary
    )
    print(f"[3] CLINICAL ESCALATION PROTOCOL")
    print(f"    - Escalation Status:         {esc.level_name}")
    print(f"    - Target Clinical Response:  {esc.clinical_response}")
    print(f"    - Response Time Window:      {esc.target_response_time}")
    print(f"    - Monitoring Frequency:      {esc.monitoring_frequency}")
    print("\n[4] SBAR CLINICAL HANDOFF REPORT:")
    print(esc.sbar_report)
    print("=" * 70)


def run_scenario_stream(scenario: str, filter_window: int = 5, steps: int = 30):
    print("=" * 70)
    print(f"  STREAMING SCENARIO: {scenario.upper()} (Median Filter Window: {filter_window})")
    print(f"  {SCENARIO_DESCRIPTIONS.get(scenario, '')}")
    print("=" * 70)

    sim = PatientSimulator(scenario=scenario, seed=42)
    df = sim.generate_trajectory(n_points=steps, time_step_minutes=5.0)

    v_filter = VitalMedianFilter(window_size=filter_window)
    trend_analyzer = TrendAnalyzer(sample_interval_minutes=5.0)
    predictor = VitalPredictor()

    history = []

    print(f"{'Time':>6} | {'Raw HR':>6} -> {'Filt HR':>7} | {'Raw SpO2':>8} -> {'Filt SpO2':>9} | {'Raw BP':>7} -> {'Filt BP':>7} | {'EWS':>3} | {'Trend':>14} | {'Escalation'}")
    print("-" * 105)

    for i in range(len(df)):
        row = df.iloc[i]
        raw_vitals = {
            "hr": float(row["hr"]), "rr": float(row["rr"]),
            "spo2": float(row["spo2"]), "temp": float(row["temp"]),
            "sbp": float(row["sbp"]), "dbp": float(row["dbp"])
        }
        filt_vitals = v_filter.filter_sample(raw_vitals)

        scores = ScoringEngine.evaluate(
            hr=filt_vitals["hr"], rr=filt_vitals["rr"], spo2=filt_vitals["spo2"],
            temp=filt_vitals["temp"], sbp=filt_vitals["sbp"], dbp=filt_vitals["dbp"]
        )

        history.append({
            "step": i,
            "hr": filt_vitals["hr"], "rr": filt_vitals["rr"], "spo2": filt_vitals["spo2"],
            "temp": filt_vitals["temp"], "sbp": filt_vitals["sbp"], "dbp": filt_vitals["dbp"],
            "total_score": scores.total_score
        })

        hist_df = pd.DataFrame(history)
        trend = trend_analyzer.analyze_history(hist_df, window_samples=12)
        pred = predictor.predict(
            hr=filt_vitals["hr"], rr=filt_vitals["rr"], spo2=filt_vitals["spo2"],
            temp=filt_vitals["temp"], sbp=filt_vitals["sbp"], dbp=filt_vitals["dbp"],
            current_score=scores.total_score, vital_slopes=trend.vital_slopes,
            score_velocity=trend.score_velocity
        )

        esc = EscalationProtocol.determine_escalation(
            total_score=scores.total_score,
            has_extreme_trigger=scores.has_extreme_trigger,
            trajectory_status=trend.trajectory_status,
            predicted_category=pred.risk_category,
            vital_summary=filt_vitals
        )

        t_min = f"{i * 5}m"
        raw_bp_s = f"{raw_vitals['sbp']:.0f}"
        filt_bp_s = f"{filt_vitals['sbp']:.0f}"
        
        print(f"{t_min:>6} | {raw_vitals['hr']:>6.1f} -> {filt_vitals['hr']:>7.1f} | {raw_vitals['spo2']:>8.1f} -> {filt_vitals['spo2']:>9.1f} | {raw_bp_s:>7} -> {filt_bp_s:>7} | {scores.total_score:>3} | {trend.trajectory_status:>14} | {esc.level_name}")

    print("=" * 105)


def run_csv_batch(csv_path: str, filter_window: int = 5):
    if not os.path.exists(csv_path):
        print(f"Error: File not found {csv_path}")
        return

    print(f"Processing CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    v_filter = VitalMedianFilter(window_size=filter_window)
    filtered_df = v_filter.filter_dataframe(df)

    scores = []
    levels = []
    for _, row in filtered_df.iterrows():
        res = ScoringEngine.evaluate(
            hr=row["hr_filtered"], rr=row["rr_filtered"], spo2=row["spo2_filtered"],
            temp=row["temp_filtered"], sbp=row["sbp_filtered"], dbp=row["dbp_filtered"]
        )
        scores.append(res.total_score)
        levels.append(res.risk_level)

    filtered_df["mvews_score"] = scores
    filtered_df["risk_tier"] = levels

    out_path = csv_path.replace(".csv", "_processed_mvews.csv")
    filtered_df.to_csv(out_path, index=False)
    print(f"Processed {len(filtered_df)} records successfully. Saved output to:\n -> {out_path}")
    print("\nSummary of Escalation Tiers:")
    print(filtered_df["risk_tier"].value_counts().to_string())


def main():
    parser = argparse.ArgumentParser(description="Multi-Vital Early Warning System CLI")
    parser.add_argument("--scenario", type=str, default="sepsis", choices=["sepsis", "respiratory", "shock", "noise_artifacts", "stable"])
    parser.add_argument("--steps", type=int, default=25, help="Simulation steps to display")
    parser.add_argument("--filter-window", type=int, default=5, help="Window size for median filter")
    parser.add_argument("--csv", type=str, help="Process external patient CSV dataset")
    parser.add_argument("--test-manual", action="store_true", help="Run single manual patient test")
    parser.add_argument("--hr", type=float, default=115.0)
    parser.add_argument("--rr", type=float, default=26.0)
    parser.add_argument("--spo2", type=float, default=92.0)
    parser.add_argument("--temp", type=float, default=38.7)
    parser.add_argument("--sbp", type=float, default=96.0)
    parser.add_argument("--dbp", type=float, default=58.0)

    args = parser.parse_args()

    if args.test_manual:
        run_manual_test(args.hr, args.rr, args.spo2, args.temp, args.sbp, args.dbp)
    elif args.csv:
        run_csv_batch(args.csv, filter_window=args.filter_window)
    else:
        run_scenario_stream(args.scenario, filter_window=args.filter_window, steps=args.steps)


if __name__ == "__main__":
    main()
