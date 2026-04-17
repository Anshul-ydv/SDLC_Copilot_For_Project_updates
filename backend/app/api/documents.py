from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
import shutil
import os
from app.services.rag_service import rag_service
from app.services.feedback_service import get_feedback_service
from app.database import get_db
from app.models import Document, DocumentFeedback
from pydantic import BaseModel

router = APIRouter()

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class FeedbackRequest(BaseModel):
    rating: str
    feedback_text: str = None
    doc_type: str = None
    user_id: str = None


class FeedbackResponse(BaseModel):
    id: str
    document_id: str
    rating: str
    feedback_text: str = None
    ai_improvement_suggestions: str = None
    doc_type: str = None
    created_at: str = None


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...), 
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Endpoint to upload PDF, DOCX, or CSV files for RAG with metadata tracking."""
    try:
        file_ext = os.path.splitext(file.filename)[1].lstrip(".").lower()
        allowed_extensions = {'pdf', 'docx', 'csv', 'doc', 'txt'}
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type '.{file_ext}' not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        existing_doc = db.query(Document).filter(
            Document.filename == file.filename,
            Document.session_id == session_id
        ).first()
        if existing_doc:
            raise HTTPException(
                status_code=400,
                detail=f"Document '{file.filename}' has already been uploaded to this session"
            )
        
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)
        
        MAX_FILE_SIZE = 20 * 1024 * 1024
        if file_size > MAX_FILE_SIZE:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum limit of 20 MB"
            )

        doc_record = Document(
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext,
            status="uploaded",
            metadata_json={"content_type": file.content_type},
            session_id=session_id
        )
        db.add(doc_record)
        db.commit()

        try:
            rag_service.process_file(file_path, file.filename)
        except Exception as e:
            db.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

        doc_record.status = "indexed"
        db.commit()

        return {
            "id": doc_record.id,
            "filename": file.filename,
            "file_size": file_size,
            "file_type": file_ext,
            "status": "Successfully uploaded and indexed in knowledge base",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_documents(session_id: str = None, db: Session = Depends(get_db)):
    """Returns a list of uploaded reference documents with metadata."""
    query = db.query(Document)
    if session_id:
        query = query.filter(Document.session_id == session_id)
        
    docs = query.order_by(Document.upload_date.desc()).all()
    return {
        "documents": [
            {
                "id": d.id,
                "filename": d.filename,
                "file_size": d.file_size,
                "file_type": d.file_type,
                "upload_date": d.upload_date.isoformat() if d.upload_date else None,
                "status": d.status,
            }
            for d in docs
        ]
    }


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document and its associated file."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
            
        db.delete(doc)
        db.commit()
        return {"status": "success", "message": "Document deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/feedback")
async def submit_feedback(
    document_id: str,
    feedback: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit QA feedback (thumbs up/down) for a document."""
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        existing_feedback = db.query(DocumentFeedback).filter(
            DocumentFeedback.document_id == document_id,
            DocumentFeedback.user_id == feedback.user_id
        ).first()
        
        ai_suggestions = None
        
        if feedback.rating == "thumbs_down":
            try:
                with open(doc.file_path, 'r', encoding='utf-8') as f:
                    doc_content = f.read()
            except:
                doc_content = "Document content could not be read"
            
            feedback_service = get_feedback_service()
            doc_type = feedback.doc_type or "Unknown"
            
            ai_suggestions = feedback_service.generate_improvement_suggestions(
                doc_content,
                doc_type,
                feedback.feedback_text or ""
            )
        
        if existing_feedback:
            existing_feedback.rating = feedback.rating
            existing_feedback.feedback_text = feedback.feedback_text
            existing_feedback.ai_improvement_suggestions = ai_suggestions
            existing_feedback.doc_type = feedback.doc_type
            db.commit()
            feedback_id = existing_feedback.id
        else:
            new_feedback = DocumentFeedback(
                document_id=document_id,
                user_id=feedback.user_id,
                rating=feedback.rating,
                feedback_text=feedback.feedback_text,
                ai_improvement_suggestions=ai_suggestions,
                doc_type=feedback.doc_type or "Unknown"
            )
            db.add(new_feedback)
            db.commit()
            feedback_id = new_feedback.id
        
        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id,
            "rating": feedback.rating,
            "ai_suggestions": ai_suggestions if feedback.rating == "thumbs_down" else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")


@router.get("/{document_id}/feedback")
async def get_feedback(document_id: str, db: Session = Depends(get_db)):
    """Retrieve all feedback for a document."""
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        feedbacks = db.query(DocumentFeedback).filter(
            DocumentFeedback.document_id == document_id
        ).order_by(DocumentFeedback.created_at.desc()).all()
        
        return {
            "document_id": document_id,
            "filename": doc.filename,
            "feedback_count": len(feedbacks),
            "feedbacks": [
                {
                    "id": f.id,
                    "rating": f.rating,
                    "feedback_text": f.feedback_text,
                    "ai_improvement_suggestions": f.ai_improvement_suggestions,
                    "doc_type": f.doc_type,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in feedbacks
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/feedback/summary")
async def get_feedback_summary(document_id: str, db: Session = Depends(get_db)):
    """Get a summary of feedback for a document."""
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        feedbacks = db.query(DocumentFeedback).filter(
            DocumentFeedback.document_id == document_id
        ).all()
        
        thumbs_up = sum(1 for f in feedbacks if f.rating == "thumbs_up")
        thumbs_down = sum(1 for f in feedbacks if f.rating == "thumbs_down")
        
        latest_improvement_suggestions = None
        latest_feedback_with_suggestions = db.query(DocumentFeedback).filter(
            DocumentFeedback.document_id == document_id,
            DocumentFeedback.ai_improvement_suggestions.isnot(None)
        ).order_by(DocumentFeedback.created_at.desc()).first()
        
        if latest_feedback_with_suggestions:
            latest_improvement_suggestions = latest_feedback_with_suggestions.ai_improvement_suggestions
        
        return {
            "document_id": document_id,
            "filename": doc.filename,
            "summary": {
                "thumbs_up": thumbs_up,
                "thumbs_down": thumbs_down,
                "total_ratings": thumbs_up + thumbs_down,
                "quality_score": f"{(thumbs_up / (thumbs_up + thumbs_down) * 100):.1f}%" if (thumbs_up + thumbs_down) > 0 else "No ratings"
            },
            "latest_improvement_suggestions": latest_improvement_suggestions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
