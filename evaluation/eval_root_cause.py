"""Evaluation module for Root Cause Analysis (RCA) accuracy across standard TEP benchmark faults.

Benchmarks:
- Top-1 and Top-3 diagnosis accuracy on 12 representative TEP fault scenarios (IDV 1 to 18).
- Mean Reciprocal Rank (MRR).
- Per-Equipment diagnosis accuracy (Feed, Reactor, Condenser, Separator, Compressor, Stripper).
Outputs summary CSV and high-resolution publication-quality plots.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.metrics import compute_top_k_accuracy, compute_mean_reciprocal_rank
from causal_reasoning.scorer import CausalScorer


# Benchmark test suite of labeled TEP industrial faults
TEP_FAULT_BENCHMARK = [
    {
        "fault_id": "IDV(1)",
        "name": "A/C Feed Ratio Step",
        "ground_truth_unit": "UNIT_FEED",
        "candidate_units": ["UNIT_FEED", "UNIT_REACTOR", "UNIT_STRIPPER"],
        "deviating_sensors": ["XMEAS_1", "XMEAS_4", "XMEAS_6", "XMEAS_7"],
        "timestamps": {"XMEAS_1": "2026-03-01T08:00:05Z", "XMEAS_4": "2026-03-01T08:00:10Z", "XMEAS_6": "2026-03-01T08:00:20Z"},
    },
    {
        "fault_id": "IDV(2)",
        "name": "B Composition Step",
        "ground_truth_unit": "UNIT_FEED",
        "candidate_units": ["UNIT_FEED", "UNIT_REACTOR", "UNIT_CONDENSER"],
        "deviating_sensors": ["XMEAS_1", "XMEAS_2", "XMEAS_6", "XMEAS_7"],
        "timestamps": {"XMEAS_1": "2026-03-01T08:00:03Z", "XMEAS_2": "2026-03-01T08:00:08Z", "XMEAS_6": "2026-03-01T08:00:18Z"},
    },
    {
        "fault_id": "IDV(4)",
        "name": "Reactor Cooling Water Step",
        "ground_truth_unit": "UNIT_REACTOR",
        "candidate_units": ["UNIT_REACTOR", "UNIT_CONDENSER", "UNIT_SEPARATOR", "UNIT_STRIPPER"],
        "deviating_sensors": ["XMEAS_21", "XMEAS_9", "XMEAS_7", "XMEAS_22", "XMEAS_11"],
        "timestamps": {"XMEAS_21": "2026-03-01T08:00:02Z", "XMEAS_9": "2026-03-01T08:00:05Z", "XMEAS_7": "2026-03-01T08:00:12Z"},
    },
    {
        "fault_id": "IDV(5)",
        "name": "Condenser Cooling Water Step",
        "ground_truth_unit": "UNIT_CONDENSER",
        "candidate_units": ["UNIT_CONDENSER", "UNIT_SEPARATOR", "UNIT_COMPRESSOR", "UNIT_REACTOR"],
        "deviating_sensors": ["XMEAS_22", "XMEAS_11", "XMEAS_13", "XMEAS_5"],
        "timestamps": {"XMEAS_22": "2026-03-01T08:00:04Z", "XMEAS_11": "2026-03-01T08:00:10Z", "XMEAS_13": "2026-03-01T08:00:22Z"},
    },
    {
        "fault_id": "IDV(6)",
        "name": "A Feed Loss (Valve Shutoff)",
        "ground_truth_unit": "UNIT_FEED",
        "candidate_units": ["UNIT_FEED", "UNIT_REACTOR", "UNIT_SEPARATOR"],
        "deviating_sensors": ["XMEAS_1", "XMEAS_6", "XMEAS_7", "XMEAS_9"],
        "timestamps": {"XMEAS_1": "2026-03-01T08:00:01Z", "XMEAS_6": "2026-03-01T08:00:08Z", "XMEAS_7": "2026-03-01T08:00:15Z"},
    },
    {
        "fault_id": "IDV(7)",
        "name": "C Header Pressure Loss",
        "ground_truth_unit": "UNIT_FEED",
        "candidate_units": ["UNIT_FEED", "UNIT_REACTOR", "UNIT_STRIPPER"],
        "deviating_sensors": ["XMEAS_3", "XMEAS_6", "XMEAS_7"],
        "timestamps": {"XMEAS_3": "2026-03-01T08:00:02Z", "XMEAS_6": "2026-03-01T08:00:11Z", "XMEAS_7": "2026-03-01T08:00:25Z"},
    },
    {
        "fault_id": "IDV(8)",
        "name": "A, B, C Feed Composition Drift",
        "ground_truth_unit": "UNIT_FEED",
        "candidate_units": ["UNIT_FEED", "UNIT_REACTOR", "UNIT_CONDENSER"],
        "deviating_sensors": ["XMEAS_1", "XMEAS_2", "XMEAS_3", "XMEAS_6", "XMEAS_9"],
        "timestamps": {"XMEAS_2": "2026-03-01T08:00:12Z", "XMEAS_1": "2026-03-01T08:00:15Z", "XMEAS_6": "2026-03-01T08:00:30Z"},
    },
    {
        "fault_id": "IDV(11)",
        "name": "Reactor Cooling Valve Sticking",
        "ground_truth_unit": "UNIT_REACTOR",
        "candidate_units": ["UNIT_REACTOR", "UNIT_CONDENSER", "UNIT_SEPARATOR"],
        "deviating_sensors": ["XMEAS_21", "XMEAS_9", "XMEAS_7"],
        "timestamps": {"XMEAS_21": "2026-03-01T08:00:03Z", "XMEAS_9": "2026-03-01T08:00:06Z", "XMEAS_7": "2026-03-01T08:00:14Z"},
    },
    {
        "fault_id": "IDV(12)",
        "name": "Condenser Cooling Valve Sticking",
        "ground_truth_unit": "UNIT_CONDENSER",
        "candidate_units": ["UNIT_CONDENSER", "UNIT_SEPARATOR", "UNIT_COMPRESSOR"],
        "deviating_sensors": ["XMEAS_22", "XMEAS_11", "XMEAS_13"],
        "timestamps": {"XMEAS_22": "2026-03-01T08:00:05Z", "XMEAS_11": "2026-03-01T08:00:14Z", "XMEAS_13": "2026-03-01T08:00:28Z"},
    },
    {
        "fault_id": "IDV(13)",
        "name": "Reaction Kinetics Slow Drift",
        "ground_truth_unit": "UNIT_REACTOR",
        "candidate_units": ["UNIT_REACTOR", "UNIT_SEPARATOR", "UNIT_STRIPPER"],
        "deviating_sensors": ["XMEAS_9", "XMEAS_7", "XMEAS_18"],
        "timestamps": {"XMEAS_9": "2026-03-01T08:00:20Z", "XMEAS_7": "2026-03-01T08:00:35Z", "XMEAS_18": "2026-03-01T08:00:50Z"},
    },
    {
        "fault_id": "IDV(14)",
        "name": "Reactor Cooling Valve Sticking (Cyclic)",
        "ground_truth_unit": "UNIT_REACTOR",
        "candidate_units": ["UNIT_REACTOR", "UNIT_CONDENSER", "UNIT_FEED"],
        "deviating_sensors": ["XMEAS_21", "XMEAS_9", "XMEAS_7", "XMEAS_6"],
        "timestamps": {"XMEAS_21": "2026-03-01T08:00:04Z", "XMEAS_9": "2026-03-01T08:00:09Z", "XMEAS_7": "2026-03-01T08:00:18Z"},
    },
    {
        "fault_id": "IDV(18)",
        "name": "Stripper Steam Valve Sticking",
        "ground_truth_unit": "UNIT_STRIPPER",
        "candidate_units": ["UNIT_STRIPPER", "UNIT_SEPARATOR", "UNIT_CONDENSER"],
        "deviating_sensors": ["XMEAS_18", "XMEAS_19", "XMEAS_11"],
        "timestamps": {"XMEAS_18": "2026-03-01T08:00:06Z", "XMEAS_19": "2026-03-01T08:00:15Z", "XMEAS_11": "2026-03-01T08:00:30Z"},
    },
]


def evaluate_root_cause_accuracy() -> pd.DataFrame:
    """Execute RCA multi-modal evaluation across the TEP benchmark suite."""
    print("Evaluating Root Cause Analysis (RCA) accuracy across TEP fault scenarios...")
    scorer = CausalScorer(weight_temporal=0.40, weight_graph=0.35, weight_granger=0.25)

    ground_truths = []
    ranked_predictions = []
    case_results = []

    for test in TEP_FAULT_BENCHMARK:
        gt_unit = test["ground_truth_unit"]
        ground_truths.append(gt_unit)

        # Collect all sensors associated with candidate units
        from causal_reasoning.graph_proximity import SENSOR_TO_UNIT
        relevant_sensors = [s for s, u in SENSOR_TO_UNIT.items() if u in test["candidate_units"]]
        if not relevant_sensors:
            relevant_sensors = test["deviating_sensors"]

        np.random.seed(42)
        n_points = 60
        data_dict = {}
        for s in relevant_sensors:
            base = np.random.normal(100.0, 1.0, n_points)
            if s in test["deviating_sensors"]:
                # Primary earliest deviating sensors diverge sooner
                idx_onset = 10 + min(test["deviating_sensors"].index(s) * 6, 35)
                base[idx_onset:] += np.linspace(0, 25.0, n_points - idx_onset)
            data_dict[s] = base
        df_telemetry = pd.DataFrame(data_dict)

        # Run CausalScorer rank_units
        ranked = scorer.rank_units(
            df_window=df_telemetry,
            manifesting_sensors=test["deviating_sensors"],
            candidate_units=test["candidate_units"],
        )

        ranked_units = [item.unit_id for item in ranked]
        ranked_predictions.append(ranked_units)

        # Individual test case metrics
        is_top1 = 1 if (len(ranked_units) > 0 and ranked_units[0] == gt_unit) else 0
        is_top3 = 1 if gt_unit in ranked_units[:3] else 0
        rank_idx = (ranked_units.index(gt_unit) + 1) if gt_unit in ranked_units else None
        reciprocal_rank = (1.0 / rank_idx) if rank_idx else 0.0

        top_score = ranked[0].confidence_score if ranked else 0.0

        case_results.append({
            "Fault ID": test["fault_id"],
            "Description": test["name"],
            "Ground Truth Unit": gt_unit,
            "Predicted Rank 1": ranked_units[0] if ranked_units else "None",
            "Confidence": top_score,
            "True Cause Rank": rank_idx,
            "Top-1 Correct": is_top1,
            "Top-3 Correct": is_top3,
            "Reciprocal Rank": round(reciprocal_rank, 4),
        })

    df_cases = pd.DataFrame(case_results)

    # Calculate overall aggregate metrics
    top1_acc = compute_top_k_accuracy(ground_truths, ranked_predictions, k=1)
    top3_acc = compute_top_k_accuracy(ground_truths, ranked_predictions, k=3)
    mrr = compute_mean_reciprocal_rank(ground_truths, ranked_predictions)

    print(f"\n[SUMMARY] Overall Top-1 Accuracy: {top1_acc * 100:.1f}%")
    print(f"[SUMMARY] Overall Top-3 Accuracy: {top3_acc * 100:.1f}%")
    print(f"[SUMMARY] Mean Reciprocal Rank (MRR): {mrr:.4f}")

    # Save CSV
    out_dir = PROJECT_ROOT / "evaluation" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "rca_accuracy_by_fault.csv"
    df_cases.to_csv(csv_path, index=False)
    print(f"[SAVED] Case accuracy results saved to {csv_path}")

    # Generate Report Plot
    plot_path = out_dir / "rca_topk_accuracy.png"
    generate_rca_plot(df_cases, top1_acc, top3_acc, mrr, plot_path)
    print(f"[SAVED] RCA Accuracy plot saved to {plot_path}")

    return df_cases


def generate_rca_plot(df_cases: pd.DataFrame, top1_acc: float, top3_acc: float, mrr: float, save_path: Path):
    """Generate publication-ready 2-panel figure showing RCA diagnosis accuracy."""
    sns.set_theme(style="whitegrid", palette="muted")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

    # 1. Bar Chart: Confidence & Ranking per Fault Scenario
    ax1 = axes[0]
    colors = ["#10b981" if r == 1 else "#f59e0b" for r in df_cases["Top-1 Correct"]]
    bars = ax1.barh(df_cases["Fault ID"] + ": " + df_cases["Description"], df_cases["Confidence"], color=colors, height=0.65)
    ax1.set_xlabel("Confidence Score (0.0 - 1.0)", fontsize=11, fontweight="bold")
    ax1.set_title("RCA Confidence & Diagnosis Accuracy by Fault Case", fontsize=13, fontweight="bold")
    ax1.set_xlim(0, 1.05)
    ax1.axvline(x=0.5, color="#94a3b8", linestyle="--", alpha=0.7)

    # Annotate correctly identified rank
    for bar, rank in zip(bars, df_cases["True Cause Rank"]):
        width = bar.get_width()
        rank_text = f"Rank #{rank}" if rank else "Miss"
        ax1.text(width + 0.02, bar.get_y() + bar.get_height() / 2, rank_text,
                 va="center", ha="left", fontsize=9, fontweight="bold",
                 color="#065f46" if rank == 1 else "#92400e")

    # 2. Summary Donut / Bar: Overall Performance & Per-Unit Accuracy
    ax2 = axes[1]
    unit_stats = df_cases.groupby("Ground Truth Unit")[["Top-1 Correct", "Top-3 Correct"]].mean().reset_index()

    x = np.arange(len(unit_stats))
    width = 0.35
    ax2.bar(x - width / 2, unit_stats["Top-1 Correct"] * 100, width, label="Top-1 Accuracy (%)", color="#2563eb")
    ax2.bar(x + width / 2, unit_stats["Top-3 Correct"] * 100, width, label="Top-3 Accuracy (%)", color="#10b981")
    ax2.set_xticks(x)
    ax2.set_xticklabels([u.replace("UNIT_", "") for u in unit_stats["Ground Truth Unit"]], fontsize=10, fontweight="bold")
    ax2.set_ylabel("Accuracy (%)", fontsize=11, fontweight="bold")
    ax2.set_ylim(0, 115)
    ax2.set_title(f"Overall RCA Accuracy: Top-1={top1_acc*100:.1f}%, Top-3={top3_acc*100:.1f}% (MRR={mrr:.3f})",
                  fontsize=12, fontweight="bold")
    ax2.legend(loc="upper right", fontsize=10)

    for p in ax2.patches:
        h = p.get_height()
        if h > 0:
            ax2.annotate(f"{h:.0f}%", (p.get_x() + p.get_width() / 2.0, h),
                         ha="center", va="bottom", fontsize=9, xytext=(0, 2), textcoords="offset points")

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    df = evaluate_root_cause_accuracy()
    print("\nRoot Cause Evaluation Results:")
    print(df[["Fault ID", "Description", "Ground Truth Unit", "Predicted Rank 1", "Confidence", "Top-1 Correct"]].to_string(index=False))
