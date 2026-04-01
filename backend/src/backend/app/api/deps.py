"""Common FastAPI dependencies."""

from __future__ import annotations

from fastapi import Request

from ..idsl.repository import IDSLRepository
from ..services.chatbot import GeminiChatService
from ..services.simulator import SimPyDigitalTwinSimulator


def get_ids_repo(request: Request) -> IDSLRepository:
    repo: IDSLRepository | None = getattr(request.app.state, "ids_repo", None)
    if repo is None:
        raise RuntimeError("IDSL repository not initialised; ensure startup hook ran.")
    return repo


def get_simulator(request: Request) -> SimPyDigitalTwinSimulator:
    simulator: SimPyDigitalTwinSimulator | None = getattr(request.app.state, "simulator", None)
    if simulator is None:
        raise RuntimeError("Simulator not initialised; ensure startup hook ran.")
    return simulator


def get_chat_service(request: Request) -> GeminiChatService:
    service: GeminiChatService | None = getattr(request.app.state, "chat_service", None)
    if service is None:
        raise RuntimeError("Chat service not initialised; ensure startup hook ran.")
    return service



