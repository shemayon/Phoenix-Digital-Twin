"""FastAPI application entrypoint for the digital twin MVP."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .. import constants
from .api.routes import chat as chat_router
from .api.routes import idsl as idsl_router
from .api.routes import twin as twin_router
from .core.config import apply_cors, default_metadata
from .idsl.repository import IDSLRepository
from .services.chatbot import GeminiChatService
from .services.simulator import SimPyDigitalTwinSimulator


def _create_app() -> FastAPI:
    app = FastAPI(**default_metadata())
    apply_cors(app)
    templates = Jinja2Templates(directory=str(constants.PACKAGE_DIR / "templates"))

    @app.on_event("startup")
    async def load_ids_payload() -> None:  # noqa: D401 - FastAPI hook
        repo = IDSLRepository()
        repo.load_from_excel(constants.SAMPLE_DATA_PATH)
        app.state.ids_repo = repo

        simulator = SimPyDigitalTwinSimulator(repo)
        await simulator.start()
        app.state.simulator = simulator

        chat_service = GeminiChatService(repo, simulator)
        app.state.chat_service = chat_service

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "dashboard.html", {"request": request})

    @app.get("/health")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(idsl_router.router)
    app.include_router(twin_router.router)
    app.include_router(chat_router.router)

    @app.on_event("shutdown")
    async def shutdown_simulator() -> None:  # noqa: D401
        simulator: SimPyDigitalTwinSimulator | None = getattr(app.state, "simulator", None)
        if simulator is not None:
            await simulator.stop()

    return app


app = _create_app()


