from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.claude import chat_with_context

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    message: str
    history: list[dict] = []  # [{"role": "user"|"assistant", "content": "..."}]


@router.post("")
def chat(body: ChatMessage):
    response = chat_with_context(body.message, body.history)
    return {"response": response}
