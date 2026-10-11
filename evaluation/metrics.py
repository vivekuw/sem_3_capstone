"""Comprehensive evaluation metrics for Root Cause Analysis and Anomaly Detection.

Includes:
- Binary classification metrics: Precision, Recall, F1, Accuracy, False Alarm Rate (FAR)
- Ranking metrics: Top-1 Accuracy, Top-k Accuracy, Mean Reciprocal Rank (MRR)
- Operational metrics: Detection Delay, Hallucination Rate, Faithfulness Score
"""

from typing import List, Dict, Any, Union
import numpy as np


def compute_classification_metrics(
    y_true: Union[List[int], np.ndarray],
    y_pred: Union[List[int], np.ndarray],
) -> Dict[str, float]:
    """Compute binary anomaly detection precision, recall, F1, accuracy, and FAR.

    Args:
        y_true: Ground truth binary labels (0 = normal, 1 = anomaly).
        y_pred: Predicted binary labels (0 = normal, 1 = anomaly).

    Returns:
        Dict with precision, recall, f1, accuracy, and false_alarm_rate (FAR).
    """
    y_true_arr = np.array(y_true, dtype=int)
    y_pred_arr = np.array(y_pred, dtype=int)

    tp = int(np.sum((y_true_arr == 1) & (y_pred_arr == 1)))
    fp = int(np.sum((y_true_arr == 0) & (y_pred_arr == 1)))
    fn = int(np.sum((y_true_arr == 1) & (y_pred_arr == 0)))
    tn = int(np.sum((y_true_arr == 0) & (y_pred_arr == 0)))

    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * (precision * recall) / (precision + recall)) if (precision + recall) > 0 else 0.0
    accuracy = float((tp + tn) / len(y_true_arr)) if len(y_true_arr) > 0 else 0.0
    far = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "false_alarm_rate": round(far, 4),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
    }


def compute_top_k_accuracy(
    ground_truth_causes: List[str],
    ranked_predictions: List[List[str]],
    k: int = 3,
) -> float:
    """Compute Top-k root-cause diagnosis accuracy.

    Args:
        ground_truth_causes: List of ground-truth unit/fault labels (e.g. ['UNIT_REACTOR', ...]).
        ranked_predictions: List of ranked prediction candidate lists (e.g. [['UNIT_REACTOR', 'UNIT_FEED'], ...]).
        k: Cutoff rank (e.g. 1 or 3).

    Returns:
        Fraction of cases where ground truth is present in top-k predictions.
    """
    if not ground_truth_causes or not ranked_predictions:
        return 0.0

    hits = 0
    total = min(len(ground_truth_causes), len(ranked_predictions))

    for i in range(total):
        gt = str(ground_truth_causes[i]).strip().upper()
        preds = [str(p).strip().upper() for p in ranked_predictions[i][:k]]
        if gt in preds:
            hits += 1

    return round(float(hits / total), 4)


def compute_mean_reciprocal_rank(
    ground_truth_causes: List[str],
    ranked_predictions: List[List[str]],
) -> float:
    """Compute Mean Reciprocal Rank (MRR) across root-cause diagnoses.

    MRR = (1 / N) * sum(1 / rank_i) where rank_i is the 1-based index of the true cause.
    If the true cause is not in predictions, reciprocal rank is 0.
    """
    if not ground_truth_causes or not ranked_predictions:
        return 0.0

    reciprocal_ranks = []
    total = min(len(ground_truth_causes), len(ranked_predictions))

    for i in range(total):
        gt = str(ground_truth_causes[i]).strip().upper()
        preds = [str(p).strip().upper() for p in ranked_predictions[i]]
        if gt in preds:
            rank = preds.index(gt) + 1  # 1-indexed
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    return round(float(np.mean(reciprocal_ranks)), 4)
