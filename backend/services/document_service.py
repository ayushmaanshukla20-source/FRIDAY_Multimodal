import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from pypdf import PdfReader
import docx
from backend.core.logging import logger

class DocumentChunk:
    def __init__(self, text: str, page: Optional[int] = None, section: Optional[str] = None, chunk_index: int = 0):
        self.text = text.strip()
        self.page = page
        self.section = section
        self.chunk_index = chunk_index

class DocumentService:
    @staticmethod
    def parse_document(file_path: str) -> List[DocumentChunk]:
        """
        Parses PDF, DOCX, TXT, and Markdown files into raw text chunks with page information.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext == ".pdf":
            return DocumentService._parse_pdf(path)
        elif ext in [".docx", ".doc"]:
            return DocumentService._parse_docx(path)
        elif ext in [".txt", ".md", ".markdown", ".csv", ".json", ".py", ".html"]:
            return DocumentService._parse_text(path)
        else:
            # Fallback to plain text read
            return DocumentService._parse_text(path)

    @staticmethod
    def _parse_pdf(path: Path, max_pages: int = 300) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        try:
            reader = PdfReader(str(path))
            total_pages = min(len(reader.pages), max_pages)
            for page_idx in range(total_pages):
                page = reader.pages[page_idx]
                text = page.extract_text() or ""
                if text.strip():
                    page_chunks = DocumentService.chunk_text(text, chunk_size=600, overlap=100)
                    for c in page_chunks:
                        chunks.append(DocumentChunk(text=c, page=page_idx + 1, chunk_index=len(chunks)))
                        if len(chunks) >= 1500:
                            break
                if len(chunks) >= 1500:
                    break
        except Exception as e:
            logger.error(f"Error parsing PDF {path}: {e}")
        return chunks

    @staticmethod
    def _parse_docx(path: Path) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        try:
            doc = docx.Document(str(path))
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            text_chunks = DocumentService.chunk_text(full_text, chunk_size=600, overlap=100)
            for i, c in enumerate(text_chunks[:1500]):
                chunks.append(DocumentChunk(text=c, page=1, chunk_index=i))
        except Exception as e:
            logger.error(f"Error parsing DOCX {path}: {e}")
        return chunks

    @staticmethod
    def _parse_text(path: Path, max_chars: int = 5_000_000) -> List[DocumentChunk]:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(max_chars)
        except Exception as e:
            logger.error(f"Error reading text file {path}: {e}")
            content = ""

        chunks: List[DocumentChunk] = []
        text_chunks = DocumentService.chunk_text(content, chunk_size=600, overlap=100)
        for i, c in enumerate(text_chunks[:1500]):
            chunks.append(DocumentChunk(text=c, page=1, chunk_index=i))
        return chunks

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        """Splits text into overlapping chunks."""
        text = text.strip()
        if not text:
            return []
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            # Try to break on whitespace or newline if possible
            if end < len(text):
                last_space = chunk.rfind(" ")
                last_newline = chunk.rfind("\n")
                break_point = max(last_space, last_newline)
                if break_point > chunk_size // 2:
                    chunk = text[start:start + break_point]
                    start = start + break_point + 1
                else:
                    start = end - overlap
            else:
                start = end

            if chunk.strip():
                chunks.append(chunk.strip())
        return chunks

document_service = DocumentService()
