import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.core.config import settings
from backend.core.database import _db_connected
from backend.models.document import Document
from backend.schemas.documents import DocumentResponse, DocumentListResponse
from backend.services.rag_service import rag_service
from backend.core.logging import logger

router = APIRouter(prefix="/api/documents", tags=["Knowledge Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".markdown", ".csv", ".json", ".py", ".html"}
_fallback_documents = {}

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Uploads, parses, chunks, and indexes a knowledge document into RAG vector store.
    """
    filename = file.filename or "uploaded_file.txt"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        allowed_str = ", ".join(ALLOWED_EXTENSIONS)
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed types: {allowed_str}")

    doc_id = str(uuid.uuid4())
    safe_filename = f"{doc_id}_{Path(filename).name}"
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = Path(settings.upload_dir) / safe_filename

    # Stream and validate size in 1 MB chunks (efficient for up to 1 GB files)
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    file_size = 0
    chunk_size = 1024 * 1024  # 1 MB chunk buffer

    try:
        with open(file_path, "wb") as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > max_bytes:
                    f.close()
                    if file_path.exists():
                        os.remove(file_path)
                    limit_label = f"{settings.max_upload_size_mb // 1024} GB" if settings.max_upload_size_mb >= 1024 else f"{settings.max_upload_size_mb} MB"
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds maximum upload limit of {limit_label}."
                    )
                f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        logger.error(f"Error saving uploaded file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    # Ingest and Index in Vector Store
    chunk_count = 0
    status = "indexed"
    error_msg = None

    try:
        chunk_count = rag_service.index_document(
            doc_id=doc_id,
            doc_name=filename,
            file_path=str(file_path)
        )
    except Exception as e:
        status = "failed"
        error_msg = str(e)
        logger.error(f"Failed to index document '{filename}': {e}")

    # Save to MySQL if connected, else fallback
    now_iso = datetime.now(timezone.utc).isoformat()
    if _db_connected:
        try:
            from backend.core.database import _SessionLocal
            if _SessionLocal:
                with _SessionLocal() as db:
                    doc = Document(
                        id=doc_id,
                        filename=filename,
                        file_path=str(file_path),
                        file_size=file_size,
                        file_type=ext.replace(".", ""),
                        chunk_count=chunk_count,
                        status=status,
                        error_message=error_msg
                    )
                    db.add(doc)
                    db.commit()
        except Exception as e:
            logger.error(f"Error saving document record to MySQL: {e}")

    _fallback_documents[doc_id] = {
        "id": doc_id,
        "filename": filename,
        "file_path": str(file_path),
        "file_size": file_size,
        "file_type": ext.replace(".", ""),
        "chunk_count": chunk_count,
        "status": status,
        "error_message": error_msg,
        "created_at": now_iso
    }

    return DocumentResponse(
        id=doc_id,
        filename=filename,
        file_size=file_size,
        file_type=ext.replace(".", ""),
        chunk_count=chunk_count,
        status=status,
        error_message=error_msg,
        created_at=now_iso
    )

@router.get("", response_model=DocumentListResponse)
def list_documents():
    """Lists all uploaded documents with indexing telemetry."""
    docs = []
    if _db_connected:
        try:
            from backend.core.database import _SessionLocal
            if _SessionLocal:
                with _SessionLocal() as db:
                    records = db.query(Document).order_by(Document.created_at.desc()).all()
                    for r in records:
                        docs.append(DocumentResponse(
                            id=r.id,
                            filename=r.filename,
                            file_size=r.file_size,
                            file_type=r.file_type,
                            chunk_count=r.chunk_count,
                            status=r.status,
                            error_message=r.error_message,
                            created_at=r.created_at.isoformat() if r.created_at else ""
                        ))
                    return DocumentListResponse(documents=docs, total_count=len(docs))
        except Exception as e:
            logger.warning(f"Error fetching documents from MySQL: {e}")

    # Fallback
    for doc in _fallback_documents.values():
        docs.append(DocumentResponse(**doc))
    return DocumentListResponse(documents=docs, total_count=len(docs))

@router.delete("/{document_id}")
def delete_document(document_id: str):
    """Deletes a document, its local file, and all associated vectors in ChromaDB."""
    deleted = False

    # Remove from ChromaDB vector store
    rag_service.delete_document(document_id)

    # Remove from MySQL
    if _db_connected:
        try:
            from backend.core.database import _SessionLocal
            if _SessionLocal:
                with _SessionLocal() as db:
                    doc = db.query(Document).filter(Document.id == document_id).first()
                    if doc:
                        # Remove file
                        if os.path.exists(doc.file_path):
                            try:
                                os.remove(doc.file_path)
                            except Exception:
                                pass
                        db.delete(doc)
                        db.commit()
                        deleted = True
        except Exception as e:
            logger.error(f"Error deleting document {document_id} from MySQL: {e}")

    # Remove from fallback
    if document_id in _fallback_documents:
        fdoc = _fallback_documents.pop(document_id)
        if os.path.exists(fdoc.get("file_path", "")):
            try:
                os.remove(fdoc["file_path"])
            except Exception:
                pass
        deleted = True

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"status": "success", "message": f"Document {document_id} and associated vectors successfully expunged."}
