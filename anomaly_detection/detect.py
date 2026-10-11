"""Scoring and anomaly detection engine: evaluates telemetry windows and emits AnomalyEvent.

Features:
- Dual-model support: PyTorch LSTM Autoencoder and scikit-learn Isolation Forest baseline.
- Produces structured AnomalyEvent with timestamp, overall anomaly score, threshold,
  and ranked list of the most affected sensors with deviation directions.
- Comprehensive evaluation function calculating Precision, Recall, and F1-Score per fault type,
  displaying a side-by-side model comparison table.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import torch
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anomaly_detection.preprocessing import TelemetryPreprocessor
from anomaly_detection.models.autoencoder import LSTMAutoencoder
from anomaly_detection.models.isolation_forest import IsolationForestDetector

SAVED_MODELS_DIR = Path(__file__).resolve().parent / "saved_models"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


class SensorDeviation(BaseModel):
    """Detailed attribution for an individual deviating sensor."""
    sensor_id: str
    reconstruction_error: float
    current_value: float
    z_score: float
    direction: str  # "HIGH" or "LOW"


class AnomalyEvent(BaseModel):
    """Structured operational alarm event emitted upon anomaly detection."""
    event_id: str
    timestamp: datetime
    is_anomaly: bool
    score: float
    threshold: float
    model_name: str
    affected_sensors: List[SensorDeviation] = Field(default_factory=list)
    top_sensor_names: List[str] = Field(default_factory=list)
    fault_label: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnomalyDetector:
    """Evaluates telemetry windows and produces structured AnomalyEvent alerts."""

    def __init__(
        self,
        ae_path: Optional[Path] = None,
        iso_path: Optional[Path] = None,
        scaler_path: Optional[Path] = None
    ):
        self.ae_path = ae_path or (SAVED_MODELS_DIR / "lstm_autoencoder.pt")
        self.iso_path = iso_path or (SAVED_MODELS_DIR / "isolation_forest.pkl")
        self.scaler_path = scaler_path or (SAVED_MODELS_DIR / "scaler.pkl")

        self.preprocessor: Optional[TelemetryPreprocessor] = None
        self.ae_model: Optional[LSTMAutoencoder] = None
        self.iso_model: Optional[IsolationForestDetector] = None
        self.ae_threshold: float = 1.085
        self.features: List[str] = []
        self.seq_len: int = 30

        self._load_models()

    def _load_models(self) -> None:
        """Load trained preprocessor, LSTM Autoencoder, and Isolation Forest models."""
        if self.scaler_path.exists():
            self.preprocessor = TelemetryPreprocessor.load(self.scaler_path)
            self.features = self.preprocessor.feature_cols

        if self.ae_path.exists():
            ckpt = torch.load(self.ae_path, map_location="cpu")
            self.ae_threshold = float(ckpt.get("threshold", 1.085))
            self.seq_len = int(ckpt.get("seq_len", 30))
            self.features = ckpt.get("features", self.features)
            self.ae_model = LSTMAutoencoder(input_dim=len(self.features), seq_len=self.seq_len)
            self.ae_model.load_state_dict(ckpt["model_state_dict"])
            self.ae_model.eval()

        if self.iso_path.exists():
            self.iso_model = IsolationForestDetector.load(self.iso_path)

    def detect_lstm(self, df_window: pd.DataFrame, fault_label: Optional[str] = None) -> AnomalyEvent:
        """Run LSTM Autoencoder anomaly detection on a telemetry window."""
        now = datetime.now(timezone.utc)
        event_id = f"AE-EVT-{int(now.timestamp() * 1000) % 1000000}"

        if self.ae_model is None or self.preprocessor is None:
            raise RuntimeError("LSTM Autoencoder model or scaler not loaded. Run train.py first.")

        # Preprocess features
        features = [f for f in self.features if f in df_window.columns]
        scaled = self.preprocessor.transform(df_window[features])

        # Ensure sequence length dimension
        if len(scaled) < self.seq_len:
            pad_size = self.seq_len - len(scaled)
            scaled = np.pad(scaled, ((pad_size, 0), (0, 0)), mode="edge")
        else:
            scaled = scaled[-self.seq_len:]

        x_tensor = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            overall_err, sensor_errs = self.ae_model.compute_reconstruction_error(x_tensor)
            overall_score = float(overall_err[0].item())
            sensor_scores = sensor_errs[0].cpu().numpy()

        is_anomaly = overall_score > self.ae_threshold
        deviations: List[SensorDeviation] = []

        # Sensor attribution
        for idx, feat in enumerate(features):
            err = float(sensor_scores[idx])
            val = float(df_window[feat].iloc[-1])
            mean = float(self.preprocessor.scaler.mean_[idx])
            scale = float(self.preprocessor.scaler.scale_[idx])
            z_score = (val - mean) / (scale if scale > 0 else 1.0)

            if err > (self.ae_threshold * 0.75) or abs(z_score) > 2.0:
                deviations.append(
                    SensorDeviation(
                        sensor_id=feat,
                        reconstruction_error=round(err, 4),
                        current_value=round(val, 4),
                        z_score=round(float(z_score), 2),
                        direction="HIGH" if z_score > 0 else "LOW",
                    )
                )

        deviations.sort(key=lambda d: d.reconstruction_error, reverse=True)
        top_sensor_names = [d.sensor_id for d in deviations[:5]]

        return AnomalyEvent(
            event_id=event_id,
            timestamp=now,
            is_anomaly=is_anomaly,
            score=round(overall_score, 4),
            threshold=round(self.ae_threshold, 4),
            model_name="LSTM_Autoencoder",
            affected_sensors=deviations,
            top_sensor_names=top_sensor_names,
            fault_label=fault_label,
            metadata={"window_size": len(df_window)},
        )

    def detect_isolation_forest(self, df_window: pd.DataFrame, fault_label: Optional[str] = None) -> AnomalyEvent:
        """Run Isolation Forest anomaly detection on a telemetry window."""
        now = datetime.now(timezone.utc)
        event_id = f"IF-EVT-{int(now.timestamp() * 1000) % 1000000}"

        if self.iso_model is None or self.preprocessor is None:
            raise RuntimeError("Isolation Forest model or scaler not loaded. Run train.py first.")

        features = [f for f in self.features if f in df_window.columns]
        scaled = self.preprocessor.transform(df_window[features])

        if len(scaled) < self.seq_len:
            pad_size = self.seq_len - len(scaled)
            scaled = np.pad(scaled, ((pad_size, 0), (0, 0)), mode="edge")
        else:
            scaled = scaled[-self.seq_len:]

        # Reshape to (1, seq_len * num_features)
        x_in = scaled.reshape(1, -1)
        is_anom_arr, score_arr = self.iso_model.score(x_in)
        is_anomaly = bool(is_anom_arr[0])
        score = float(score_arr[0])

        # Sensor deviation attribution via individual feature z-scores
        latest_vec = scaled[-1]
        deviations = []
        for idx, feat in enumerate(features):
            z_score = float(latest_vec[idx])
            val = float(df_window[feat].iloc[-1])
            if abs(z_score) > 2.0:
                deviations.append(
                    SensorDeviation(
                        sensor_id=feat,
                        reconstruction_error=round(abs(z_score), 4),
                        current_value=round(val, 4),
                        z_score=round(z_score, 2),
                        direction="HIGH" if z_score > 0 else "LOW",
                    )
                )

        deviations.sort(key=lambda d: d.reconstruction_error, reverse=True)
        top_sensor_names = [d.sensor_id for d in deviations[:5]]

        return AnomalyEvent(
            event_id=event_id,
            timestamp=now,
            is_anomaly=is_anomaly,
            score=round(score, 4),
            threshold=0.5,
            model_name="Isolation_Forest",
            affected_sensors=deviations,
            top_sensor_names=top_sensor_names,
            fault_label=fault_label,
            metadata={"window_size": len(df_window)},
        )


def evaluate_models() -> None:
    """Evaluate Isolation Forest vs LSTM Autoencoder on benchmark datasets and print comparison table."""
    detector = AnomalyDetector()
    csv_files = list(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("[WARNING] No benchmark CSV files found in data/raw/. Run load_tep_dataset.py first.")
        return

    print("=" * 75)
    print("      EVALUATION: ISOLATION FOREST vs LSTM AUTOENCODER      ")
    print("=" * 75)
    print(f"Evaluating across {len(csv_files)} benchmark datasets in {RAW_DATA_DIR.name}...\n")

    window_size = 30
    step = 5

    # Storage for per-dataset metric tracking:
    # {model: {dataset_name: {'tp': int, 'fp': int, 'tn': int, 'fn': int}}}
    results: Dict[str, Dict[str, Dict[str, int]]] = {
        "Isolation_Forest": {},
        "LSTM_Autoencoder": {}
    }

    for csv_file in sorted(csv_files):
        df = pd.read_csv(csv_file)
        fault_name = csv_file.stem.replace("tep_", "").upper()
        # True label is anomaly if not NORMAL
        is_ground_truth_anomaly = "NORMAL" not in fault_name

        for model_name in ["Isolation_Forest", "LSTM_Autoencoder"]:
            if fault_name not in results[model_name]:
                results[model_name][fault_name] = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}

        # Slide windows across dataset
        for i in range(0, len(df) - window_size + 1, step):
            window = df.iloc[i : i + window_size]

            # 1. Isolation Forest prediction
            evt_iso = detector.detect_isolation_forest(window, fault_label=fault_name)
            pred_iso = evt_iso.is_anomaly
            if is_ground_truth_anomaly:
                if pred_iso:
                    results["Isolation_Forest"][fault_name]["tp"] += 1
                else:
                    results["Isolation_Forest"][fault_name]["fn"] += 1
            else:
                if pred_iso:
                    results["Isolation_Forest"][fault_name]["fp"] += 1
                else:
                    results["Isolation_Forest"][fault_name]["tn"] += 1

            # 2. LSTM Autoencoder prediction
            evt_ae = detector.detect_lstm(window, fault_label=fault_name)
            pred_ae = evt_ae.is_anomaly
            if is_ground_truth_anomaly:
                if pred_ae:
                    results["LSTM_Autoencoder"][fault_name]["tp"] += 1
                else:
                    results["LSTM_Autoencoder"][fault_name]["fn"] += 1
            else:
                if pred_ae:
                    results["LSTM_Autoencoder"][fault_name]["fp"] += 1
                else:
                    results["LSTM_Autoencoder"][fault_name]["tn"] += 1

    # Print Comparison Table
    header = f"{'Model':<18} | {'Operating Mode':<18} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}"
    divider = "-" * len(header)
    print(header)
    print(divider)

    for model_name in ["Isolation_Forest", "LSTM_Autoencoder"]:
        total_tp, total_fp, total_tn, total_fn = 0, 0, 0, 0

        for fault_mode, counts in results[model_name].items():
            tp, fp, tn, fn = counts["tp"], counts["fp"], counts["tn"], counts["fn"]
            total_tp += tp
            total_fp += fp
            total_tn += tn
            total_fn += fn

            if "NORMAL" in fault_mode:
                # For normal baseline, specificity / false alarm rate is key
                precision = tn / (tn + fn) if (tn + fn) > 0 else 1.0
                recall = tn / (tn + fp) if (tn + fp) > 0 else 1.0
            else:
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

            print(
                f"{model_name:<18} | {fault_mode:<18} | {precision * 100:>8.2f}% | {recall * 100:>8.2f}% | {f1 * 100:>8.2f}%"
            )

        # Overall aggregate
        overall_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        overall_rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        overall_f1 = (
            (2 * overall_prec * overall_rec / (overall_prec + overall_rec))
            if (overall_prec + overall_rec) > 0
            else 0.0
        )
        print(
            f"{model_name + ' (Overall)':<18} | {'ALL DATASETS':<18} | {overall_prec * 100:>8.2f}% | {overall_rec * 100:>8.2f}% | {overall_f1 * 100:>8.2f}%"
        )
        print(divider)

    # Demonstrate live sample AnomalyEvent inspection
    print("\n" + "=" * 75)
    print("           SAMPLE LIVE ANOMALY EVENT INSPECTION           ")
    print("=" * 75)
    sample_fault_file = RAW_DATA_DIR / "tep_fault_idv04.csv"
    if sample_fault_file.exists():
        df_fault = pd.read_csv(sample_fault_file)
        # Take a window from late in the fault run
        window_sample = df_fault.iloc[-35:]
        evt = detector.detect_lstm(window_sample, fault_label="IDV(4)")
        print(f"Event ID        : {evt.event_id}")
        print(f"Timestamp       : {evt.timestamp.isoformat()}")
        print(f"Model           : {evt.model_name}")
        print(f"Anomaly Detected: {evt.is_anomaly}")
        print(f"Score / Limit   : {evt.score:.4f} (Threshold: {evt.threshold:.4f})")
        print(f"Top Sensors     : {evt.top_sensor_names}")
        print("Sensor Deviations Breakdown:")
        for dev in evt.affected_sensors[:4]:
            print(f"  - {dev.sensor_id:<12}: Error={dev.reconstruction_error:.4f}, Z-score={dev.z_score:>+5.2f} ({dev.direction})")
    print("=" * 75)


if __name__ == "__main__":
    evaluate_models()
