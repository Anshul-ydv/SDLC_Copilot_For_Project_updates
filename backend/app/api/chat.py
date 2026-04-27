from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from sqlalchemy.orm import Session
from app.services.rag_service import rag_service
from app.database import get_db
from app import models
from datetime import datetime
from app.services.pdf_service import generate_pdf_from_text
from app.utils.security_utils import validate_query_safety, sanitize_query
from app.utils.rbac_utils import validate_task_access, Permission, get_role_capabilities
from app.utils.auth_utils import get_current_user
from collections import defaultdict
import os

router = APIRouter()

active_sessions: dict[str, bool] = defaultdict(bool)


class MessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    role: str
    content: str
    created_at: datetime


class SessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: str
    role: str
    user_id: str
    created_at: datetime


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
async def get_sessions(user_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Verify user can only access their own sessions
    if current_user.get("sub") != user_id:
        raise HTTPException(status_code=403, detail="Access denied: You can only view your own sessions")
    
    return db.query(models.ChatSession).filter(
        models.ChatSession.user_id == user_id,
        models.ChatSession.deleted_at.is_(None)
    ).order_by(models.ChatSession.created_at.desc()).all()


@router.get("/sessions/{session_id}/messages", response_model=List[MessageSchema])
async def get_session_messages(session_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Verify session ownership
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != current_user.get("sub"):
        raise HTTPException(status_code=403, detail="Access denied: This session does not belong to you")
    
    return db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.created_at.asc()).all()


@router.post("/sessions", response_model=SessionSchema)
async def create_session(request: CreateSessionRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Verify user can only create sessions for themselves
    if current_user.get("sub") != request.user_id:
        raise HTTPException(status_code=403, detail="Access denied: You can only create sessions for yourself")
    
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
async def delete_session(session_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Soft delete a chat session (sets deleted_at timestamp)."""
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify session ownership
    if session.user_id != current_user.get("sub"):
        raise HTTPException(status_code=403, detail="Access denied: This session does not belong to you")
    
    try:
        # Soft delete: set deleted_at timestamp instead of removing from DB
        session.deleted_at = datetime.now()
        db.commit()
        return {"status": "success", "message": "Session deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=ChatResponse)
async def process_chat(request: ChatRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Main endpoint for chatting and document generation."""
    try:
        # Verify session ownership
        session = db.query(models.ChatSession).filter(models.ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.user_id != current_user.get("sub"):
            raise HTTPException(status_code=403, detail="Access denied: This session does not belong to you")
        
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty or whitespace only")
        
        # Validate query safety (prompt injection prevention)
        is_safe, error_msg = validate_query_safety(request.query)
        if not is_safe:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Sanitize query
        sanitized_query = sanitize_query(request.query)
        
        # Validate RBAC access for task type
        is_allowed, rbac_message, permission = validate_task_access(request.role, request.task_type)
        if not is_allowed:
            # Return polite refusal as 200 response instead of 403 error
            user_msg = models.ChatMessage(session_id=request.session_id, role="user", content=sanitized_query)
            db.add(user_msg)
            
            bot_msg = models.ChatMessage(session_id=request.session_id, role="assistant", content=rbac_message)
            db.add(bot_msg)
            db.commit()

            return ChatResponse(
                response=rbac_message,
                source_documents=["None"],
                session_id=request.session_id
            )
        
        user_msg = models.ChatMessage(session_id=request.session_id, role="user", content=sanitized_query)
        db.add(user_msg)
        
        rag_response = rag_service.generate_answer(sanitized_query, request.role, request.session_id, request.task_type)
        
        # Add RBAC note for partial access
        if permission == Permission.PARTIAL and rbac_message:
            rag_response = f"{rbac_message}\n\n{rag_response}"

        bot_msg = models.ChatMessage(session_id=request.session_id, role="assistant", content=rag_response)
        db.add(bot_msg)
        db.commit()

        return ChatResponse(
            response=rag_response,
            source_documents=request.context_files if request.context_files else ["None"],
            session_id=request.session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query/stream")
async def process_chat_stream(request: ChatRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Streaming endpoint for real-time document generation with rate limiting."""
    
    # Verify session ownership
    session = db.query(models.ChatSession).filter(models.ChatSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != current_user.get("sub"):
        raise HTTPException(status_code=403, detail="Access denied: This session does not belong to you")

    if active_sessions[request.session_id]:
        raise HTTPException(
            status_code=429,
            detail="A query is already in progress for this session. Please wait for it to complete."
        )

    async def event_generator():
        full_response = []
        try:
            active_sessions[request.session_id] = True
            
            # Validate query safety (prompt injection prevention)
            is_safe, error_msg = validate_query_safety(request.query)
            if not is_safe:
                yield f"Error: {error_msg}"
                return
            
            # Validate RBAC access for task type
            is_allowed, rbac_message, permission = validate_task_access(request.role, request.task_type)
            if not is_allowed:
                yield f"Access Denied: {rbac_message}"
                return
            
            # Sanitize query
            sanitized_query = sanitize_query(request.query)

            user_msg = models.ChatMessage(session_id=request.session_id, role="user", content=sanitized_query)
            db.add(user_msg)
            db.commit()
            
            # Add RBAC note for partial access
            if permission == Permission.PARTIAL and rbac_message:
                yield f"{rbac_message}\n\n"

            for chunk in rag_service.stream_answer(sanitized_query, request.role, request.session_id, request.task_type):
                full_response.append(chunk)
                yield chunk

            final_content = "".join(full_response)
            bot_msg = models.ChatMessage(session_id=request.session_id, role="assistant", content=final_content)
            db.add(bot_msg)
            db.commit()

        except Exception as e:
            db.rollback()
            yield f"Error in stream: {str(e)}"
        finally:
            active_sessions[request.session_id] = False

    return StreamingResponse(event_generator(), media_type="text/plain")


@router.post("/generate-pdf")
async def generate_pdf_endpoint(request: PDFRequest):
    try:
        file_path = generate_pdf_from_text(request.content, request.filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail=f"PDF file was not created at {file_path}")
        
        return FileResponse(
            path=file_path,
            filename=request.filename,
            media_type="application/pdf"
        )
    except Exception as e:
        import traceback
        error_detail = f"PDF generation error: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/role-capabilities")
async def get_role_capabilities_endpoint(role: str):
    """Get all capabilities for a specific role."""
    try:
        capabilities = get_role_capabilities(role)
        return {
            "role": role,
            "capabilities": capabilities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
