from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
import json
from datetime import datetime

from app.database import get_db
from app.models import Document
from app.services.mcp_pipeline import mcp_pipeline
from app.services.mcp_document_generator import mcp_doc_generator, mcp_giver_agent
from app.services.pdf_service import generate_pdf_from_text
from langchain_community.document_loaders import PyPDFLoader, CSVLoader, Docx2txtLoader

router = APIRouter()

UPLOAD_DIR = "uploaded_docs"
MCP_OUTPUT_DIR = "/tmp/mcp_outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MCP_OUTPUT_DIR, exist_ok=True)


def extract_document_text(file_path: str, filename: str) -> str:
    try:
        if filename.endswith(".pdf"):
            documents = PyPDFLoader(file_path).load()
        elif filename.endswith(".csv"):
            documents = CSVLoader(file_path).load()
        elif filename.endswith((".doc", ".docx")):
            documents = Docx2txtLoader(file_path).load()
        elif filename.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {filename}")
        return "\n\n".join([doc.page_content for doc in documents])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from document: {str(e)}")


@router.post("/process")
async def process_document_with_mcp(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    output_format: str = Form("docx"),
    delivery_mode: str = Form("download"),
    db: Session = Depends(get_db)
):
    """Process a document through the MCP multi-agent pipeline and return the processed output."""
    try:
        file_ext = os.path.splitext(file.filename)[1].lstrip(".").lower()
        allowed_extensions = {'pdf', 'docx', 'doc', 'csv', 'txt'}
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type '.{file_ext}' not supported. Allowed: {', '.join(allowed_extensions)}"
            )

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)

        MAX_FILE_SIZE = 50 * 1024 * 1024
        if file_size > MAX_FILE_SIZE:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds 50 MB limit for MCP processing"
            )
        
        doc_record = Document(
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_ext,
            status="processing",
            metadata_json={"mcp_pipeline": True, "content_type": file.content_type},
            session_id=session_id
        )
        db.add(doc_record)
        db.commit()

        document_content = extract_document_text(file_path, file.filename)

        session_output_dir = os.path.join(MCP_OUTPUT_DIR, session_id)
        os.makedirs(session_output_dir, exist_ok=True)

        unified_payload = mcp_pipeline.process_document(
            document_content=document_content,
            filename=file.filename,
            output_dir=session_output_dir
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = os.path.splitext(file.filename)[0]

        if output_format == "docx":
            output_filename = f"{base_filename}_MCP_processed_{timestamp}.docx"
            output_path = os.path.join(session_output_dir, output_filename)
            mcp_doc_generator.generate_document(unified_payload, output_path)

        elif output_format == "pdf":
            docx_filename = f"{base_filename}_MCP_processed_{timestamp}.docx"
            mcp_doc_generator.generate_document(unified_payload, os.path.join(session_output_dir, docx_filename))

            output_filename = f"{base_filename}_MCP_processed_{timestamp}.pdf"
            output_path = os.path.join(session_output_dir, output_filename)
            summary = f"""# MCP Pipeline Processing Results

Document: {file.filename}
Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Requirements: {len(unified_payload.get('requirements', []))}
- Tables: {len(unified_payload.get('table_map', []))}
- Business Rules: {len(unified_payload.get('business_rules', []))}
- Process Flows: {len(unified_payload.get('flows', []))}
- Change Requests: {len(unified_payload.get('change_requests', []))}

## Validation Status
Status: {'PASSED' if unified_payload.get('validation_summary', {}).get('passed', False) else 'FAILED'}
Warnings: {len(unified_payload.get('validation_summary', {}).get('warnings', []))}
Errors: {len(unified_payload.get('validation_summary', {}).get('errors', []))}

For detailed results, please download the DOCX version.
"""
            generate_pdf_from_text(summary, output_filename)

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported output format: {output_format}")
        
        delivery_confirmation = mcp_giver_agent.deliver_document(
            document_path=output_path,
            delivery_mode=delivery_mode
        )

        doc_record.status = "processed"
        doc_record.metadata_json.update({
            "mcp_output_path": output_path,
            "mcp_output_format": output_format,
            "mcp_delivery": delivery_confirmation
        })
        db.commit()
        
        return {
            "status": "success",
            "message": "Document processed successfully through MCP pipeline",
            "document_id": doc_record.id,
            "input_file": file.filename,
            "output_file": output_filename,
            "output_path": output_path,
            "output_format": output_format,
            "pipeline_summary": {
                "requirements_extracted": len(unified_payload.get('requirements', [])),
                "tables_analyzed": len(unified_payload.get('table_map', [])),
                "business_rules": len(unified_payload.get('business_rules', [])),
                "process_flows": len(unified_payload.get('flows', [])),
                "change_requests": len(unified_payload.get('change_requests', [])),
                "validation_passed": unified_payload.get('validation_summary', {}).get('passed', False)
            },
            "delivery": delivery_confirmation,
            "intermediate_files": {
                "reader_output": os.path.join(session_output_dir, "reader_output.json"),
                "requirements": os.path.join(session_output_dir, "s1_requirements.json"),
                "table_schemas": os.path.join(session_output_dir, "s2_table_schemas.json"),
                "business_logic": os.path.join(session_output_dir, "s3_business_logic.json"),
                "change_requests": os.path.join(session_output_dir, "s4_change_requests.json"),
                "validation": os.path.join(session_output_dir, "s5_validation.json"),
                "unified_payload": os.path.join(session_output_dir, "unified_payload.json")
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"MCP pipeline error: {str(e)}")


@router.get("/download/{session_id}/{filename}")
async def download_mcp_output(session_id: str, filename: str):
    """Download a processed MCP output file."""
    file_path = os.path.join(MCP_OUTPUT_DIR, session_id, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')


@router.get("/intermediate/{session_id}/{file_type}")
async def get_intermediate_output(session_id: str, file_type: str):
    """Get intermediate JSON outputs from the MCP pipeline."""
    file_mapping = {
        "reader": "reader_output.json",
        "requirements": "s1_requirements.json",
        "tables": "s2_table_schemas.json",
        "business_logic": "s3_business_logic.json",
        "change_requests": "s4_change_requests.json",
        "validation": "s5_validation.json",
        "unified": "unified_payload.json"
    }
    if file_type not in file_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Must be one of: {', '.join(file_mapping.keys())}"
        )
    file_path = os.path.join(MCP_OUTPUT_DIR, session_id, file_mapping[file_type])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Intermediate file not found: {file_type}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading intermediate file: {str(e)}")


@router.get("/status/{document_id}")
async def get_mcp_processing_status(document_id: str, db: Session = Depends(get_db)):
    """Get the processing status of an MCP pipeline job."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": document_id,
        "filename": doc.filename,
        "status": doc.status,
        "file_size": doc.file_size,
        "file_type": doc.file_type,
        "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
        "metadata": doc.metadata_json
    }
