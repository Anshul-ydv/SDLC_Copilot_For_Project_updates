# chat structure
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from app.services.rag_service import rag_service
from app.database import get_db
from app import models
from datetime import datetime
import json
import asyncio
from fastapi.responses import FileResponse
from app.services.pdf_service import generate_pdf_from_text
import os

router = APIRouter()

# --- Pydantic Schemas --- for the document

class MessageSchema(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class SessionSchema(BaseModel):
    id: str
    title: str
    role: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class CreateSessionRequest(BaseModel):
    user_id: str
    role: str
    title: str

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    role: str
    query: str
    task_type: Optional[str] = None
    context_files: Optional[list[str]] = []

class ChatResponse(BaseModel):
    response: str
    source_documents: list[str]
    session_id: str

# --- API Endpoints --- diff diff sessions

@router.get("/sessions", response_model=List[SessionSchema])
async def get_sessions(user_id: str, db: Session = Depends(get_db)):
    return db.query(models.ChatSession).filter(models.ChatSession.user_id == user_id).order_by(models.ChatSession.created_at.desc()).all()

@router.get("/sessions/{session_id}/messages", response_model=List[MessageSchema])
async def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    return db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.created_at.asc()).all()

@router.post("/sessions", response_model=SessionSchema)
async def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    db_session = models.ChatSession(
        title=request.title,
        role=request.role,
        user_id=request.user_id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.post("/query", response_model=ChatResponse)
async def process_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main endpoint for chatting and document generation (Legacy Non-Streaming).
    """
    try:
        user_msg = models.ChatMessage(session_id=request.session_id, role="user", content=request.query)
        db.add(user_msg)
        
        rag_response = rag_service.generate_answer(request.query, request.role, request.task_type)

        bot_msg = models.ChatMessage(session_id=request.session_id, role="assistant", content=rag_response)
        db.add(bot_msg)
        db.commit()

        return ChatResponse(
            response=rag_response,
            source_documents=request.context_files if request.context_files else ["None"],
            session_id=request.session_id
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/stream")
async def process_chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Streaming endpoint for real-time document generation.
    """
    async def event_generator():
        full_response = []
        try:
            # 1. Save User Message
            user_msg = models.ChatMessage(session_id=request.session_id, role="user", content=request.query)
            db.add(user_msg)
            db.commit()

            # 2. Iterate through RAG Service Stream
            for chunk in rag_service.stream_answer(request.query, request.role, request.task_type):
                full_response.append(chunk)
                yield chunk

            # 3. Save Assistant Response after completion
            final_content = "".join(full_response)
            bot_msg = models.ChatMessage(session_id=request.session_id, role="assistant", content=final_content)
            db.add(bot_msg)
            db.commit()

        except Exception as e:
            db.rollback()
            yield f"Error in stream: {str(e)}"

    return StreamingResponse(event_generator(), media_type="text/plain")

class PDFRequest(BaseModel):
    content: str
    filename: Optional[str] = "SDLC_Document.pdf"

@router.post("/generate-pdf")
async def generate_pdf_endpoint(request: PDFRequest):
    try:
        file_path = generate_pdf_from_text(request.content, request.filename)
        return FileResponse(
            path=file_path,
            filename=request.filename,
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
