"""Master evaluation orchestrator for Phase 10: Explainable Industrial AI RCA Capstone.

Runs the entire experimental evaluation suite:
1. Anomaly Detection Benchmark (LSTM Autoencoder vs Isolation Forest)
2. Root Cause Analysis Benchmark (Top-1, Top-3, MRR across labeled TEP faults)
3. Ablation Study (Full Model vs No Knowledge Graph vs No Granger Causality)
4. Pipeline Latency Measurement (Component response times & percentiles p50, p95, p99)
5. Faithfulness & Hallucination Resistance Check

Saves all summary tables as CSV in `evaluation/results/` and generates 5 high-resolution
report-ready figures for the final capstone thesis.
"""

import sys
import io
import time
from pathlib import Path
import pandas as pd

# Ensure UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.eval_anomalies import evaluate_anomaly_detectors
from evaluation.eval_root_cause import evaluate_root_cause_accuracy
from evaluation.eval_ablation import run_ablation_experiments
from evaluation.eval_latency import measure_pipeline_latency
from evaluation.eval_faithfulness import run_faithfulness_evaluation


def run_complete_evaluation_suite():
    """Execute all benchmark suites sequentially and summarize findings."""
    print("=" * 80)
    print("[*] EXPLAINABLE INDUSTRIAL AI ROOT-CAUSE AGENT - MASTER EVALUATION SUITE")
    print("    Benchmarking Tennessee Eastman Process (TEP) Performance & Faithfulness")
    print("=" * 80)

    start_total = time.time()
    results_dir = PROJECT_ROOT / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # 1. Anomaly Detection
    print("\n[STAGE 1/5] Running Anomaly Detection Model Evaluation...")
    t0 = time.time()
    df_anomalies = evaluate_anomaly_detectors()
    print(f"[OK] Anomaly detection evaluation complete in {time.time() - t0:.2f}s")

    # 2. Root Cause Analysis
    print("\n[STAGE 2/5] Running Root Cause Analysis (RCA) Accuracy Evaluation...")
    t0 = time.time()
    df_rca = evaluate_root_cause_accuracy()
    print(f"[OK] Root cause accuracy evaluation complete in {time.time() - t0:.2f}s")

    # 3. Ablation Study
    print("\n[STAGE 3/5] Running Multi-Modal Ablation Study (Knowledge Graph Lift)...")
    t0 = time.time()
    df_ablation = run_ablation_experiments()
    print(f"[OK] Ablation study complete in {time.time() - t0:.2f}s")

    # 4. Latency Measurement
    print("\n[STAGE 4/5] Running Inference Latency & Percentile Benchmarking...")
    t0 = time.time()
    df_latency = measure_pipeline_latency(num_trials=25)
    print(f"[OK] Latency benchmarking complete in {time.time() - t0:.2f}s")

    # 5. Faithfulness & Grounding Check
    print("\n[STAGE 5/5] Running Explanation Faithfulness & Hallucination Verification...")
    t0 = time.time()
    df_faithfulness = run_faithfulness_evaluation()
    total_time = time.time() - start_total

    # =========================================================================
    # Executive Summary Printout
    # =========================================================================
    print("\n" + "=" * 80)
    print(f"[*] MASTER EVALUATION COMPLETED IN {total_time:.2f} SECONDS")
    print("=" * 80)

    print("\n1. ANOMALY DETECTION BENCHMARK:")
    print(df_anomalies[["Model", "Precision", "Recall", "F1-Score", "Detection Delay (sec)"]].to_string(index=False))

    top1 = df_rca["Top-1 Correct"].mean() * 100
    top3 = df_rca["Top-3 Correct"].mean() * 100
    mrr = df_rca["Reciprocal Rank"].mean()
    print(f"\n2. ROOT CAUSE ACCURACY ON TEP FAULTS:")
    print(f"   - Top-1 Accuracy: {top1:.1f}%")
    print(f"   - Top-3 Accuracy: {top3:.1f}%")
    print(f"   - Mean Reciprocal Rank (MRR): {mrr:.4f}")

    print("\n3. ABLATION STUDY COMPARISON (Knowledge Graph Lift):")
    print(df_ablation[["Short Name", "Top-1 Accuracy", "Top-3 Accuracy", "MRR", "Delta vs Full (Top-1)"]].to_string(index=False))

    total_p50 = df_latency.loc[df_latency["Component"].str.contains("Total"), "Median / p50 (ms)"].values[0]
    total_p95 = df_latency.loc[df_latency["Component"].str.contains("Total"), "p95 Latency (ms)"].values[0]
    print(f"\n4. LATENCY BENCHMARK:")
    print(f"   - End-to-End Pipeline Median (p50): {total_p50:.1f} ms")
    print(f"   - End-to-End Pipeline 95th Percentile (p95): {total_p95:.1f} ms")

    avg_faith = df_faithfulness["Faithfulness Score"].mean()
    pass_rate = df_faithfulness["Faithful (Pass >= 0.85)"].mean() * 100
    print(f"\n5. FAITHFULNESS & GROUNDING (LLM Hallucination Resistance):")
    print(f"   - Evidence Grounding Score: {avg_faith:.3f} / 1.000")
    print(f"   - Hallucination-Free Pass Rate: {pass_rate:.1f}%")

    print("\n" + "-" * 80)
    print("[ARTIFACTS] GENERATED ARTIFACTS IN evaluation/results/:")
    for f in sorted(results_dir.glob("*")):
        if f.is_file() and not f.name.startswith("."):
            size_kb = f.stat().st_size / 1024
            print(f"   - {f.name:<35} ({size_kb:.1f} KB)")
    print("-" * 80 + "\n")


if __name__ == "__main__":
    run_complete_evaluation_suite()
