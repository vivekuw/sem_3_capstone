"""Unit and integration tests for Phase 10: Evaluation & Benchmark framework."""

import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.metrics import (
    compute_classification_metrics,
    compute_top_k_accuracy,
    compute_mean_reciprocal_rank,
)
from evaluation.eval_anomalies import evaluate_anomaly_detectors
from evaluation.eval_root_cause import evaluate_root_cause_accuracy
from evaluation.eval_ablation import run_ablation_experiments
from evaluation.eval_faithfulness import run_faithfulness_evaluation


def test_classification_metrics_computation():
    """Verify classification metrics accurately compute TP, FP, FN, TN, precision, recall, and F1."""
    y_true = [0, 0, 1, 1, 1, 0, 1, 0]
    y_pred = [0, 0, 1, 1, 0, 0, 1, 1]

    metrics = compute_classification_metrics(y_true, y_pred)
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "accuracy" in metrics
    assert "false_alarm_rate" in metrics

    # TP = 3, FP = 1, FN = 1, TN = 3
    assert metrics["true_positives"] == 3
    assert metrics["false_positives"] == 1
    assert metrics["false_negatives"] == 1
    assert metrics["true_negatives"] == 3

    assert metrics["precision"] == round(3 / 4, 4)
    assert metrics["recall"] == round(3 / 4, 4)
    assert metrics["f1"] == round(3 / 4, 4)


def test_top_k_and_mrr_metrics():
    """Verify Top-1, Top-3, and MRR calculations."""
    ground_truth = ["UNIT_REACTOR", "UNIT_FEED", "UNIT_STRIPPER"]
    predictions = [
        ["UNIT_REACTOR", "UNIT_FEED", "UNIT_CONDENSER"],     # Rank 1 hit
        ["UNIT_CONDENSER", "UNIT_FEED", "UNIT_REACTOR"],     # Rank 2 hit
        ["UNIT_SEPARATOR", "UNIT_FEED", "UNIT_CONDENSER"],   # Missed
    ]

    top1 = compute_top_k_accuracy(ground_truth, predictions, k=1)
    top2 = compute_top_k_accuracy(ground_truth, predictions, k=2)
    top3 = compute_top_k_accuracy(ground_truth, predictions, k=3)
    mrr = compute_mean_reciprocal_rank(ground_truth, predictions)

    assert top1 == round(1 / 3, 4)
    assert top2 == round(2 / 3, 4)
    assert top3 == round(2 / 3, 4)

    # MRR = (1/1 + 1/2 + 0) / 3 = 1.5 / 3 = 0.5
    assert mrr == 0.5


def test_eval_anomalies_execution_and_schema():
    """Verify evaluate_anomaly_detectors produces expected columns and non-empty results."""
    df = evaluate_anomaly_detectors()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2  # LSTM AE and IF
    for col in ["Model", "Precision", "Recall", "F1-Score", "Accuracy", "Detection Delay (sec)"]:
        assert col in df.columns
        assert df[col].notna().all()


def test_eval_root_cause_accuracy_schema():
    """Verify evaluate_root_cause_accuracy calculates accuracy across all TEP test cases."""
    df = evaluate_root_cause_accuracy()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 10
    for col in ["Fault ID", "Ground Truth Unit", "Predicted Rank 1", "Confidence", "Top-1 Correct"]:
        assert col in df.columns

    # High accuracy overall
    assert df["Top-1 Correct"].mean() >= 0.70
    assert df["Top-3 Correct"].mean() >= 0.90


def test_ablation_study_knowledge_graph_lift():
    """Verify ablation study correctly quantifies lift provided by the Knowledge Graph."""
    df = run_ablation_experiments()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5

    full_row = df.loc[df["Short Name"] == "Full Model"].iloc[0]
    no_kg_row = df.loc[df["Short Name"] == "No KG (Ablation)"].iloc[0]

    # Full model with KG must outperform purely statistical time-series model
    assert full_row["Top-1 Accuracy"] > no_kg_row["Top-1 Accuracy"]
    assert full_row["MRR"] > no_kg_row["MRR"]


def test_faithfulness_evaluation_grounding():
    """Verify faithfulness check enforces grounding and detects ungrounded claims."""
    df = run_faithfulness_evaluation()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 10
    for col in ["Fault ID", "Faithfulness Score", "Faithful (Pass >= 0.85)"]:
        assert col in df.columns

    # Majority of reports must pass strict grounding
    assert df["Faithful (Pass >= 0.85)"].mean() >= 0.80
