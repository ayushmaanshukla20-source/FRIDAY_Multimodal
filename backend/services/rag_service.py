import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.core.config import settings
from backend.core.logging import logger
from backend.services.document_service import document_service
from backend.services.embedding_service import embedding_service
from backend.services.safety_service import safety_service

class RAGService:
    def __init__(self):
        self.collection_name = "friday_knowledge_base"
        self._client = None
        self._collection = None
        self._init_store()

    def _init_store(self):
        try:
            os.makedirs(settings.vector_store_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=settings.vector_store_dir,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB initialized with collection '{self.collection_name}'. Current count: {self._collection.count()}")
        except Exception as e:
            logger.warning(f"ChromaDB persistent client error: {e}. Initializing in-memory ephemeral client.")
            try:
                self._client = chromadb.EphemeralClient()
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as ex:
                logger.error(f"Critical failure initializing vector store: {ex}")
                self._collection = None

    def index_document(self, doc_id: str, doc_name: str, file_path: str) -> int:
        """
        Parses, chunks, embeds, and stores a document in the vector store.
        Returns the number of indexed chunks.
        """
        if self._collection is None:
            raise RuntimeError("Vector store collection is not available.")

        chunks = document_service.parse_document(file_path)
        if not chunks:
            return 0

        ids = [f"{doc_id}_{c.chunk_index}" for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = [
            {
                "document_id": doc_id,
                "document_name": doc_name,
                "page": c.page if c.page is not None else 1,
                "chunk_index": c.chunk_index
            }
            for c in chunks
        ]

        # Generate embeddings
        embeddings = embedding_service.embed_batch(texts)

        # Upsert into ChromaDB
        self._collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        logger.info(f"Successfully indexed document '{doc_name}' ({doc_id}) with {len(chunks)} chunks.")
        return len(chunks)

    def query(self, query_text: str, top_k: int = 4, document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant knowledge chunks.
        """
        if self._collection is None or self._collection.count() == 0:
            return []

        query_embedding = embedding_service.embed_text(query_text)
        where_filter = None
        if document_ids and len(document_ids) == 1:
            where_filter = {"document_id": document_ids[0]}
        elif document_ids and len(document_ids) > 1:
            where_filter = {"document_id": {"$in": document_ids}}

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self._collection.count()),
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            logger.warning(f"Error querying vector store: {e}")
            return []

        formatted = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for i, doc in enumerate(docs):
                meta = metas[i] if i < len(metas) else {}
                dist = dists[i] if i < len(dists) else 0.0
                score = round(max(0.0, 1.0 - dist), 3)

                formatted.append({
                    "chunk_id": f"{meta.get('document_id', 'unknown')}_{meta.get('chunk_index', i)}",
                    "document_id": str(meta.get("document_id", "")),
                    "document_name": str(meta.get("document_name", "Document")),
                    "content": doc,
                    "page": meta.get("page", 1),
                    "section": meta.get("section", None),
                    "score": score
                })
        return formatted

    def delete_document(self, doc_id: str) -> bool:
        """Deletes all chunks belonging to a document from ChromaDB."""
        if self._collection is None:
            return False
        try:
            self._collection.delete(where={"document_id": doc_id})
            logger.info(f"Deleted vector chunks for document_id {doc_id}.")
            return True
        except Exception as e:
            logger.error(f"Error deleting vector chunks for {doc_id}: {e}")
            return False

    def build_grounded_context(self, query: str, top_k: int = 4, document_ids: Optional[List[str]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Retrieves top relevant chunks and formats them into an untrusted-isolated context block with citations.
        """
        matches = self.query(query, top_k=top_k, document_ids=document_ids)
        if not matches:
            return "", []

        citations = []
        context_parts = []
        for match in matches:
            # Sanitize content against prompt injection
            safe_content = safety_service.sanitize_untrusted_text(match["content"])
            doc_name = match["document_name"]
            page = match["page"]
            score = match["score"]

            citations.append({
                "document_id": match["document_id"],
                "document_name": doc_name,
                "snippet": safe_content[:150] + ("..." if len(safe_content) > 150 else ""),
                "page": page,
                "section": match["section"],
                "score": score
            })

            context_parts.append(
                f"[Source: {doc_name} | Page: {page} | Relevance: {score}]\n{safe_content}"
            )

        grounded_context = (
            "\n<untrusted_knowledge_base_context>\n"
            + "\n\n---\n\n".join(context_parts)
            + "\n</untrusted_knowledge_base_context>\n"
        )
        return grounded_context, citations

rag_service = RAGService()
