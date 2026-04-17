from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, field_validator
from typing import Optional, List
from sqlalchemy.orm import Session
from app.services.rag_service import rag_service
from app.database import get_db
from app import models
from datetime import datetime
from app.services.pdf_service import generate_pdf_from_text

router = APIRouter()


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
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        """Validate query length between 3 and 4000 characters."""
        query_stripped = v.strip()
        if not query_stripped:
            raise ValueError('Query cannot be empty or whitespace only')
        if len(query_stripped) < 3:
            raise ValueError('Query must be at least 3 characters long')
        if len(query_stripped) > 4000:
            raise ValueError('Query must not exceed 4000 characters')
        return v


class ChatResponse(BaseModel):
    response: str
    source_documents: list[str]
    session_id: str


class PDFRequest(BaseModel):
    content: str
    filename: Optional[str] = "SDLC_Document.pdf"


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


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session and all its messages."""
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        db.delete(session)
        db.commit()
        return {"status": "success", "message": "Session deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=ChatResponse)
async def process_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main endpoint for chatting and document generation."""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty or whitespace only")
        
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
    """Streaming endpoint for real-time document generation."""
    async def event_generator():
        full_response = []
        try:
            user_msg = models.ChatMessage(session_id=request.session_id, role="user", content=request.query)
            db.add(user_msg)
            db.commit()

            for chunk in rag_service.stream_answer(request.query, request.role, request.task_type):
                full_response.append(chunk)
                yield chunk

            final_content = "".join(full_response)
            bot_msg = models.ChatMessage(session_id=request.session_id, role="assistant", content=final_content)
            db.add(bot_msg)
            db.commit()

        except Exception as e:
            db.rollback()
            yield f"Error in stream: {str(e)}"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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
