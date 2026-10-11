"""LSTM Autoencoder for multivariate anomaly detection in PyTorch."""

import torch
import torch.nn as nn
from typing import Tuple


class LSTMEncoder(nn.Module):
    """Encodes a sequence into a latent embedding vector."""

    def __init__(self, input_dim: int, hidden_dim: int = 64, latent_dim: int = 24, num_layers: int = 2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0
        )
        self.fc = nn.Linear(hidden_dim, latent_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch_size, seq_len, input_dim)
        _, (hn, _) = self.lstm(x)
        # hn[-1]: (batch_size, hidden_dim)
        latent = self.fc(hn[-1])
        return latent


class LSTMDecoder(nn.Module):
    """Decodes latent embedding back to reconstructed sequence."""

    def __init__(self, latent_dim: int, hidden_dim: int = 64, output_dim: int = 22, seq_len: int = 30, num_layers: int = 2):
        super().__init__()
        self.seq_len = seq_len
        self.fc = nn.Linear(latent_dim, hidden_dim)
        self.lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0
        )
        self.output_layer = nn.Linear(hidden_dim, output_dim)

    def forward(self, latent: torch.Tensor) -> torch.Tensor:
        # latent: (batch_size, latent_dim)
        rep = self.fc(latent).unsqueeze(1).repeat(1, self.seq_len, 1)
        out, _ = self.lstm(rep)
        reconstruction = self.output_layer(out)
        return reconstruction


class LSTMAutoencoder(nn.Module):
    """End-to-end LSTM Autoencoder model."""

    def __init__(
        self,
        input_dim: int = 22,
        hidden_dim: int = 64,
        latent_dim: int = 24,
        seq_len: int = 30,
        num_layers: int = 2
    ):
        super().__init__()
        self.input_dim = input_dim
        self.seq_len = seq_len
        self.encoder = LSTMEncoder(input_dim, hidden_dim, latent_dim, num_layers)
        self.decoder = LSTMDecoder(latent_dim, hidden_dim, input_dim, seq_len, num_layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction

    def compute_reconstruction_error(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute mean squared error overall and per-sensor.
        Returns:
            overall_error: (batch_size,)
            sensor_errors: (batch_size, input_dim)
        """
        recon = self.forward(x)
        squared_diff = (x - recon) ** 2
        # Average over sequence length
        sensor_errors = torch.mean(squared_diff, dim=1)  # (batch_size, input_dim)
        overall_error = torch.mean(sensor_errors, dim=1)  # (batch_size,)
        return overall_error, sensor_errors
