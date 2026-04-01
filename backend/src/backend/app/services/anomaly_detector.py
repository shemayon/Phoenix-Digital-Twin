import torch
import torch.nn as nn
import numpy as np
from collections import deque
from typing import List, Optional

class LSTMAutoencoder(nn.Module):
    """Simple LSTM Autoencoder for Anomaly Detection."""
    def __init__(self, input_dim: int, hidden_dim: int):
        super(LSTMAutoencoder, self).__init__()
        self.encoder = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.decoder = nn.LSTM(hidden_dim, input_dim, batch_first=True)
        
    def forward(self, x):
        # x: [batch, seq_len, input_dim]
        _, (h, _) = self.encoder(x)
        # h: [1, batch, hidden_dim]
        
        # Repeat hidden state for decoder
        seq_len = x.shape[1]
        h_repeated = h.repeat(seq_len, 1, 1).permute(1, 0, 2)
        
        output, _ = self.decoder(h_repeated)
        return output

class AnomalyDetector:
    """LSTM-based anomaly detection engine."""
    def __init__(self, tag_names: List[str], window_size: int = 30):
        self.tag_names = tag_names
        self.window_size = window_size
        self.input_dim = len(tag_names)
        self.hidden_dim = 16
        
        # Initialize model with stable random seed
        torch.manual_seed(42)
        self.model = LSTMAutoencoder(self.input_dim, self.hidden_dim)
        self.model.eval()
        
        # Buffers for time-series data
        self.buffers = {tag: deque(maxlen=window_size) for tag in tag_names}
        
    def add_data_point(self, data: dict):
        """Add a new telemetry point for all tags."""
        for tag in self.tag_names:
            val = data.get(tag, 0.0)
            self.buffers[tag].append(val)
            
    def is_ready(self) -> bool:
        """True if we have enough data for a full window."""
        return all(len(b) >= self.window_size for b in self.buffers.values())
        
    def detect_anomaly(self) -> float:
        """
        Inference call. Returns an anomaly score (0.0 to 1.0).
        Score is based on reconstruction error.
        """
        if not self.is_ready():
            return 0.0
            
        # Prepare input tensor [1, window_size, input_dim]
        data = []
        for i in range(self.window_size):
            row = [self.buffers[tag][i] for tag in self.tag_names]
            data.append(row)
            
        # Normalize (simple z-score or min-max would be better in production)
        # For this prototype, we'll just center around 0.
        input_tensor = torch.FloatTensor(data).unsqueeze(0)
        
        with torch.no_grad():
            reconstruction = self.model(input_tensor)
            # Calculate MSE reconstruction error
            error = torch.mean((input_tensor - reconstruction) ** 2).item()
            
        # Map error to 0-1 scale. 
        # Baseline noise error for random weights is usually small.
        # Spikes (anomalies) will cause large reconstruction failure.
        score = min(1.0, error * 10.0) 
        return score
