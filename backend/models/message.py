import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.models.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    modality = Column(String(30), default="text")  # text, image, document, audio, video, multimodal
    citations = Column(Text, nullable=True)  # JSON-encoded string
    metadata_json = Column(Text, nullable=True)  # JSON-encoded metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    conversation = relationship("Conversation", back_populates="messages")
