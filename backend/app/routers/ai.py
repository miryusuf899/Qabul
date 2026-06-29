from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import DbSession
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai_service import handle_ai_chat

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(payload: AIChatRequest, db: DbSession) -> AIChatResponse:
    return await handle_ai_chat(db, payload)
