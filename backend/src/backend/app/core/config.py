"""Utilities for FastAPI application configuration."""

from __future__ import annotations

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from ... import constants


def apply_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=constants.DEFAULT_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def default_metadata() -> dict[str, str]:
    return {
        "title": constants.API_TITLE,
        "version": constants.API_VERSION,
    }


