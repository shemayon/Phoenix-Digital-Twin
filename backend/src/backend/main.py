"""CLI launcher for the FastAPI application."""

from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
