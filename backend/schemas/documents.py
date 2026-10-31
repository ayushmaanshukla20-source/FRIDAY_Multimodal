from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    file_type: str
    chunk_count: int
    status: str
    error_message: Optional[str] = None
    created_at: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total_count: int

class KnowledgeQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(4, ge=1, le=20)
    document_ids: Optional[List[str]] = None

class KnowledgeChunkResult(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    content: str
    page: Optional[int] = None
    section: Optional[str] = None
    score: float

class KnowledgeQueryResponse(BaseModel):
    query: str
    results: List[KnowledgeChunkResult]
    count: int
