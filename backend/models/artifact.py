import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from backend.models.base import Base

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artifact_type = Column(String(50), nullable=False)  # image, audio, model_3d, code, analysis
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
