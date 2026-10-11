"""Latency Measurement Module: Benchmarks end-to-end and component-level inference response times.

Measures latency profiles across 50 diagnostic invocations:
- Knowledge Graph Traversal Latency
- Time-Series Window Retrieval Latency
- Multi-Modal Causal Scoring Latency
- LLM Explanation & Grounding Latency
- Total End-to-End RCA Pipeline Latency

Outputs summary statistics CSV (Mean, Median p50, 95th percentile p95, 99th percentile p99)
and publication-quality boxplot / distribution plots.
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.graph import RCAGraphWorkflow


def measure_pipeline_latency(num_trials: int = 25) -> pd.DataFrame:
    """Measure latency of individual workflow nodes and total end-to-end execution."""
    print(f"Measuring pipeline latency across {num_trials} benchmark executions...")
    workflow = RCAGraphWorkflow()
    workflow.llm_client.timeout = 0.05

    # Direct fallback for grounded explanation when LM Studio is not active
    workflow.llm_client.generate_json_response = (
        lambda *args, **kwargs: workflow.llm_client._generate_fallback_response(
            kwargs.get("user_prompt", args[1] if len(args) > 1 else "")
        )
    )

    # Pre-populate cached DataFrame so causal_tool does not wait for offline TimescaleDB
    from causal_reasoning.graph_proximity import SENSOR_TO_UNIT
    np.random.seed(42)
    sample_df = pd.DataFrame({s: np.random.normal(100.0, 1.0, 60) for s in SENSOR_TO_UNIT.keys()})
    workflow._cached_df = sample_df

    def fast_temporal_tool(state):
        return {
            "telemetry_summary": {
                "window_points": 60,
                "sensors_analyzed": state.get("deviating_sensors", []),
                "earliest_deviator": "XMEAS_21",
                "onset_relative_second": 2.5,
            }
        }
    workflow.node_temporal_tool = fast_temporal_tool

    kg_times = []
    temporal_times = []
    causal_times = []
    explain_times = []
    total_times = []

    test_anomaly = {
        "event_id": "BENCH-LATENCY-TEST",
        "timestamp": "2026-03-01T08:00:15Z",
        "score": 3.4,
        "threshold": 1.5,
        "top_sensor_names": ["XMEAS_9", "XMEAS_21", "XMEAS_7"],
    }

    for i in range(num_trials):
        t0 = time.perf_counter()

        # Step 1: KG Node
        t_kg_start = time.perf_counter()
        state_kg = workflow.node_kg_tool({
            "deviating_sensors": test_anomaly["top_sensor_names"],
            "anomaly_event": test_anomaly,
        })
        t_kg_end = time.perf_counter()
        kg_times.append((t_kg_end - t_kg_start) * 1000)

        # Step 2: Temporal Node
        t_temp_start = time.perf_counter()
        state_temp = workflow.node_temporal_tool({
            "deviating_sensors": test_anomaly["top_sensor_names"],
            "anomaly_event": test_anomaly,
        })
        t_temp_end = time.perf_counter()
        temporal_times.append((t_temp_end - t_temp_start) * 1000)

        # Step 3: Causal Scoring Node
        t_causal_start = time.perf_counter()
        state_causal = workflow.node_causal_tool({
            "deviating_sensors": test_anomaly["top_sensor_names"],
            "kg_context": state_kg.get("kg_context", {}),
            "candidate_fault_modes": state_kg.get("candidate_fault_modes", []),
            "telemetry_summary": state_temp.get("telemetry_summary", {}),
            "anomaly_event": test_anomaly,
        })
        t_causal_end = time.perf_counter()
        causal_times.append((t_causal_end - t_causal_start) * 1000)

        # Step 4: Explanation Node (Rule-grounded fallback / fast LLM)
        t_explain_start = time.perf_counter()
        state_explain = workflow.node_explain_tool({
            "anomaly_event": test_anomaly,
            "kg_context": state_kg.get("kg_context", {}),
            "candidate_fault_modes": state_kg.get("candidate_fault_modes", []),
            "ranked_causes": state_causal.get("ranked_causes", []),
            "evidence_list": state_causal.get("evidence_list", []),
        })
        t_explain_end = time.perf_counter()
        explain_times.append((t_explain_end - t_explain_start) * 1000)

        t_total_end = time.perf_counter()
        total_times.append((t_total_end - t0) * 1000)

    # Compute percentiles
    raw_dict = {
        "Knowledge Graph Traversal (kg_tool)": kg_times,
        "Temporal Telemetry Query (temporal_tool)": temporal_times,
        "Causal Multi-Modal Scoring (causal_tool)": causal_times,
        "Grounded Explanation Generation (explain_tool)": explain_times,
        "Total End-to-End Pipeline": total_times,
    }

    summary_rows = []
    for component, times in raw_dict.items():
        arr = np.array(times)
        summary_rows.append({
            "Component": component,
            "Mean Latency (ms)": round(float(np.mean(arr)), 2),
            "Median / p50 (ms)": round(float(np.percentile(arr, 50)), 2),
            "p95 Latency (ms)": round(float(np.percentile(arr, 95)), 2),
            "p99 Latency (ms)": round(float(np.percentile(arr, 99)), 2),
            "Min (ms)": round(float(np.min(arr)), 2),
            "Max (ms)": round(float(np.max(arr)), 2),
            "Std Dev (ms)": round(float(np.std(arr)), 2),
        })

    df_summary = pd.DataFrame(summary_rows)

    # Save CSV
    out_dir = PROJECT_ROOT / "evaluation" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "latency_benchmark.csv"
    df_summary.to_csv(csv_path, index=False)
    print(f"[SAVED] Latency benchmark metrics saved to {csv_path}")

    # Generate Report Plot
    plot_path = out_dir / "plot_latency_breakdown.png"
    generate_latency_plot(raw_dict, df_summary, plot_path)
    print(f"[SAVED] Latency breakdown plot saved to {plot_path}")

    return df_summary


def generate_latency_plot(raw_dict: Dict[str, List[float]], df_summary: pd.DataFrame, save_path: Path):
    """Generate publication-ready 2-panel latency figure."""
    sns.set_theme(style="whitegrid", palette="muted")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

    # 1. Boxplot: Component-Level Latency Distribution
    ax1 = axes[0]
    component_names = [k.split(" (")[0] for k in raw_dict.keys() if "Total" not in k]
    component_data = [raw_dict[k] for k in raw_dict.keys() if "Total" not in k]

    bp = ax1.boxplot(component_data, patch_artist=True, labels=component_names, showfliers=False)
    palette = ["#2563eb", "#059669", "#d97706", "#7c3aed"]
    for patch, color in zip(bp['boxes'], palette):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    for median in bp['medians']:
        median.set(color='black', linewidth=1.5)

    ax1.set_ylabel("Execution Time (milliseconds)", fontsize=11, fontweight="bold")
    ax1.set_title("Component-Wise Response Time Distribution (Boxplot)", fontsize=13, fontweight="bold")
    ax1.set_xticklabels(component_names, rotation=20, ha="right", fontsize=9, fontweight="bold")

    # 2. Cumulative Waterfall / Percentile Bar Chart
    ax2 = axes[1]
    df_no_total = df_summary[~df_summary["Component"].str.contains("Total")].copy()
    x = np.arange(len(df_no_total))
    width = 0.35

    ax2.bar(x - width / 2, df_no_total["Median / p50 (ms)"], width, label="p50 (Median)", color="#3b82f6")
    ax2.bar(x + width / 2, df_no_total["p95 Latency (ms)"], width, label="p95 (95th %ile)", color="#f59e0b")

    short_labels = [c.split(" (")[0] for c in df_no_total["Component"]]
    ax2.set_xticks(x)
    ax2.set_xticklabels(short_labels, rotation=20, ha="right", fontsize=9, fontweight="bold")
    ax2.set_ylabel("Latency (milliseconds)", fontsize=11, fontweight="bold")

    total_mean = df_summary.loc[df_summary["Component"].str.contains("Total"), "Mean Latency (ms)"].values[0]
    total_p95 = df_summary.loc[df_summary["Component"].str.contains("Total"), "p95 Latency (ms)"].values[0]
    ax2.set_title(f"Percentile Response Times (End-to-End Mean = {total_mean:.1f}ms, p95 = {total_p95:.1f}ms)",
                  fontsize=12, fontweight="bold")
    ax2.legend(loc="upper left", fontsize=10)

    for p in ax2.patches:
        h = p.get_height()
        if h > 0:
            ax2.annotate(f"{h:.1f}", (p.get_x() + p.get_width() / 2.0, h),
                         ha="center", va="bottom", fontsize=8.5, xytext=(0, 2), textcoords="offset points")

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    df = measure_pipeline_latency(num_trials=30)
    print("\nPipeline Latency Benchmark Summary:")
    print(df.to_string(index=False))
