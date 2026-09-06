from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SourceCitation(BaseModel):
    id: str
    source: str
    page: Optional[int] = 1
    content_snippet: str
    metadata: Dict[str, Any] = {}

class QueryRequest(BaseModel):
    question: str = Field(..., description="User's technical IT support question", min_length=2)
    top_k: Optional[int] = Field(default=4, description="Number of context chunks to retrieve", ge=1, le=10)
    image_data: Optional[str] = Field(default=None, description="Optional base64 encoded image or visual log input")

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation]
    retrieved_count: int
    model_used: str

class HealthResponse(BaseModel):
    status: str
    vector_store_status: str
    collection_count: int
    ollama_model: str
