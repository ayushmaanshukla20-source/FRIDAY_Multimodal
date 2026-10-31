from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Citation(BaseModel):
    document_id: str
    document_name: str
    snippet: str
    page: Optional[int] = None
    section: Optional[str] = None
    score: Optional[float] = None

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000, description="User prompt or query")
    conversation_id: Optional[str] = Field(None, description="Existing conversation UUID")
    use_rag: bool = Field(True, description="Whether to ground response in indexed RAG documents")
    support_mode: bool = Field(False, description="Whether Emotional Support Mode is activated")
    modality: str = Field("text", description="Input modality (text, image, audio, document)")
    file_path: Optional[str] = Field(None, description="Optional path to attached file for multimodal context")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image for multimodal vision analysis")
    task_type: Optional[str] = Field(None, description="Specialized student task: ocr_notes, analyze_diagram, solve_problem, generate_quiz")

class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    reply: Optional[str] = None
    citations: List[Citation] = []
    modality: str = "text"
    status: str = "success"
    viewer_actions: Optional[List[Dict[str, Any]]] = None

class MessageDetail(BaseModel):
    id: str
    role: str
    content: str
    modality: str
    citations: Optional[List[Citation]] = None
    metadata_json: Optional[str] = None
    created_at: str

class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0

class ConversationDetail(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[MessageDetail] = []
