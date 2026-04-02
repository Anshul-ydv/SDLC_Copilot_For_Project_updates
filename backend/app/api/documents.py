# API endpoints for document upload and retrieval
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
import shutil
import os
from app.services.rag_service import rag_service
from app.database import get_db
from app.models import Document

router = APIRouter()

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Endpoint to upload PDF, DOCX, or CSV files for RAG with metadata tracking."""
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Gather metadata
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file.filename)[1].lstrip(".").lower()

        # Persist metadata in the Document table
        doc_record = Document(
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext,
            status="uploaded",
            metadata_json={"content_type": file.content_type},
        )
        db.add(doc_record)
        db.commit()

        # Trigger the RAG chunking and DB storing
        rag_service.process_file(file_path, file.filename)

        # Mark as indexed after successful processing
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
async def list_documents(db: Session = Depends(get_db)):
    """Returns a list of uploaded reference documents with metadata."""
    docs = db.query(Document).order_by(Document.upload_date.desc()).all()
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

