from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    type: str  # chat, vision, embedding, audio, image
    is_active: bool

class ModelListResponse(BaseModel):
    models: List[ModelInfo]
    active_llm: str
    active_embedding: str
    active_vision: str

class MultimodalAnalyseRequest(BaseModel):
    prompt: Optional[str] = "Analyze this input and describe its key elements in detail, Boss."
    image_base64: Optional[str] = None
    file_path: Optional[str] = None
    analysis_type: str = "general"  # general, ocr, code, diagram, screen

class MultimodalAnalyseResponse(BaseModel):
    analysis: str
    modality: str
    status: str = "success"
    extracted_text: Optional[str] = None

class ViewerAction(BaseModel):
    action: str  # rotate, zoom, wireframe, reset, load, hierarchy, procedural
    target: Optional[str] = None
    params: Dict[str, Any] = {}

class ViewerCommandRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=500)

class ViewerCommandResponse(BaseModel):
    parsed: bool
    command: str
    actions: List[ViewerAction]
    message: str

class DesktopExecuteRequest(BaseModel):
    action: str = Field(..., description="Action type: open_app, open_url, system_info")
    target: str = Field(..., description="Application name, URL, or tool identifier")
    confirmed: bool = Field(False, description="User confirmation flag for destructive or safety operations")

class DesktopExecuteResponse(BaseModel):
    success: bool
    action: str
    target: str
    output: str
    requires_confirmation: bool = False

class AudioTranscribeRequest(BaseModel):
    audio_base64: Optional[str] = None
    file_path: Optional[str] = None

class AudioTranscribeResponse(BaseModel):
    text: str
    success: bool
    language: Optional[str] = "en"

class AudioSpeakRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

class AudioSpeakResponse(BaseModel):
    audio_url: Optional[str] = None
    audio_base64: Optional[str] = None
    success: bool

class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    aspect_ratio: str = "1:1"

class ImageGenerateResponse(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    prompt: str
    success: bool
    message: str

class SpotifySearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=255)
    search_type: str = "track"  # track, artist, playlist, album

class SpotifyItem(BaseModel):
    name: str
    artist: Optional[str] = None
    url: str
    uri: Optional[str] = None
    image_url: Optional[str] = None

class SpotifySearchResponse(BaseModel):
    query: str
    items: List[SpotifyItem]
    is_authenticated: bool
    message: str

class SpotifyPlayRequest(BaseModel):
    query: Optional[str] = None
    track: Optional[str] = None
    artist: Optional[str] = None

class SpotifyPlaylistRequest(BaseModel):
    playlist_name: str
