"""Static configuration values for the MVP backend.

These values are hard-coded for the proof of concept and should be moved to
environment variables or a secrets store before production use.
"""

from __future__ import annotations

from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
BACKEND_DIR = SRC_DIR.parent
ROOT_DIR = BACKEND_DIR.parent


import os

# ---------------------------------------------------------------------------
# External service configuration
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCVkJ-VH9xkKaywf7vyMW7Qjw87m1VfqkQ")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


# ---------------------------------------------------------------------------
# Data + simulation settings
# ---------------------------------------------------------------------------
SAMPLE_DATA_PATH = ROOT_DIR / "Sample data.xlsx"
SIMULATION_TICK_SECONDS = 1.0
SIMULATION_ACCELERATION_FACTOR = 1.0  # Real-time: 1 tick = 1 real second
IDSL_REFRESH_SECONDS = 5.0


# ---------------------------------------------------------------------------
# API / App settings
# ---------------------------------------------------------------------------
API_TITLE = "Digital Twin IDSL API"
API_VERSION = "0.1.0"
DEFAULT_CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
]


