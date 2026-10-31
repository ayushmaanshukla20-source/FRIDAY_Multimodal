from fastapi import APIRouter
from backend.schemas.documents import KnowledgeQueryRequest, KnowledgeQueryResponse, KnowledgeChunkResult
from backend.services.rag_service import rag_service

router = APIRouter(prefix="/api/knowledge", tags=["RAG Knowledge Search"])

@router.post("/query", response_model=KnowledgeQueryResponse)
def query_knowledge_base(request: KnowledgeQueryRequest):
    """
    Performs direct semantic search across the knowledge base vector index.
    """
    results = rag_service.query(
        query_text=request.query,
        top_k=request.top_k,
        document_ids=request.document_ids
    )

    chunks = [
        KnowledgeChunkResult(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            document_name=r["document_name"],
            content=r["content"],
            page=r.get("page"),
            section=r.get("section"),
            score=r.get("score", 0.0)
        )
        for r in results
    ]

    return KnowledgeQueryResponse(
        query=request.query,
        results=chunks,
        count=len(chunks)
    )
