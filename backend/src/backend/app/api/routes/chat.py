"""Chat endpoints that proxy to the Gemini-style assistant."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ...models.chat import ChatRequest, ChatResponse
from ..deps import get_chat_service


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, service = Depends(get_chat_service)) -> ChatResponse:
    return service.generate_response(request)


