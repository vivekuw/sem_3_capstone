"""Training script for anomaly detection models on normal baseline plant telemetry.

Fits the scaler strictly on NORMAL data, trains an LSTM Autoencoder in PyTorch,
computes empirical reconstruction error threshold, trains an Isolation Forest baseline,
and persists all trained artifacts to anomaly_detection/saved_models/.
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from anomaly_detection.preprocessing import TelemetryPreprocessor
from anomaly_detection.models.autoencoder import LSTMAutoencoder
from anomaly_detection.models.isolation_forest import IsolationForestDetector

SAVED_MODELS_DIR = Path(__file__).resolve().parent / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)


def load_normal_training_data() -> pd.DataFrame:
    """Load baseline normal data from data/raw/ or generate if not found."""
    raw_csv = PROJECT_ROOT / "data" / "raw" / "tep_normal_baseline.csv"
    if raw_csv.exists():
        print(f"[INFO] Loading normal baseline dataset from {raw_csv} ...")
        df = pd.read_csv(raw_csv)
        if "fault_label" in df.columns:
            df = df[df["fault_label"] == "NORMAL"]
        return df

    # Fallback to generating 4 hours of baseline
    from ingestion.load_tep_dataset import generate_benchmark_run
    print("[INFO] Generating normal baseline training series...")
    df = generate_benchmark_run(num_samples=720, fault_type="NORMAL")
    return df


def train_lstm_autoencoder(
    X_train_seq: np.ndarray,
    input_dim: int,
    seq_len: int = 30,
    epochs: int = 15,
    batch_size: int = 32,
    lr: float = 1e-3,
    device: str = "cpu",
) -> LSTMAutoencoder:
    """Train PyTorch LSTM Autoencoder on normal sequence windows."""
    print(f"[INFO] Training LSTM Autoencoder on {len(X_train_seq)} sequences (seq_len={seq_len}, dim={input_dim})...")
    model = LSTMAutoencoder(input_dim=input_dim, seq_len=seq_len).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    criterion = nn.MSELoss()

    tensor_x = torch.tensor(X_train_seq, dtype=torch.float32)
    dataset = TensorDataset(tensor_x)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        for (batch_x,) in loader:
            batch_x = batch_x.to(device)
            optimizer.zero_grad()
            recon = model(batch_x)
            loss = criterion(recon, batch_x)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(batch_x)

        avg_loss = total_loss / len(X_train_seq)
        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch [{epoch:>2}/{epochs}] - Reconstruction MSE: {avg_loss:.6f}")

    return model


def run_training_pipeline() -> None:
    """Execute end-to-end training pipeline for both anomaly detection models."""
    print("=" * 60)
    print("       PHASE 4: ANOMALY DETECTION MODEL TRAINING        ")
    print("=" * 60)

    # 1. Load NORMAL data only
    df_normal = load_normal_training_data()
    print(f"[INFO] Normal baseline dataset shape: {df_normal.shape}")

    # 2. Fit Scaler strictly on Normal data
    preprocessor = TelemetryPreprocessor()
    scaled_data = preprocessor.fit_transform(df_normal)
    preprocessor.save(SAVED_MODELS_DIR / "scaler.pkl")
    print(f"[INFO] Fitted and saved Scaler for {len(preprocessor.feature_cols)} sensors.")

    feature_dim = scaled_data.shape[1]
    seq_len = 30

    # 3. Sliding Windows
    X_windows = TelemetryPreprocessor.create_sliding_windows(scaled_data, window_size=seq_len, step_size=1)
    print(f"[INFO] Created {len(X_windows)} sliding windows of shape ({seq_len}, {feature_dim}).")

    # 4. Train LSTM Autoencoder
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ae_model = train_lstm_autoencoder(X_windows, input_dim=feature_dim, seq_len=seq_len, epochs=15, device=device)

    # Compute empirical anomaly threshold (99th percentile of normal reconstruction loss)
    ae_model.eval()
    with torch.no_grad():
        tensor_x = torch.tensor(X_windows, dtype=torch.float32).to(device)
        overall_err, _ = ae_model.compute_reconstruction_error(tensor_x)
        threshold = float(np.percentile(overall_err.cpu().numpy(), 99.0))
        print(f"[INFO] Computed 99th-percentile Normal Reconstruction Threshold: {threshold:.6f}")

    # Save LSTM Autoencoder weights and metadata
    torch.save(
        {
            "model_state_dict": ae_model.state_dict(),
            "threshold": threshold,
            "input_dim": feature_dim,
            "seq_len": seq_len,
            "features": preprocessor.feature_cols,
        },
        SAVED_MODELS_DIR / "lstm_autoencoder.pt",
    )
    print("[INFO] Saved PyTorch weights to saved_models/lstm_autoencoder.pt")

    # 5. Train Baseline Isolation Forest
    print("[INFO] Fitting Isolation Forest baseline on normal windows...")
    iso_forest = IsolationForestDetector(contamination=0.01, random_state=42)
    iso_forest.fit(X_windows)
    iso_forest.save(SAVED_MODELS_DIR / "isolation_forest.pkl")
    print("[INFO] Saved Isolation Forest baseline to saved_models/isolation_forest.pkl")

    print("\n[SUCCESS] Model training complete. All models saved in saved_models/.")


if __name__ == "__main__":
    run_training_pipeline()
