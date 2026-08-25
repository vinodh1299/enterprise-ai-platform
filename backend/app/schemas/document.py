from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class DocumentChunkResponse(BaseModel):
    """
    Pydantic schema for returning document chunk data.
    """
    id: int
    chunk_index: int
    page_number: int
    content: str
    metadata_json: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    """
    Pydantic schema for returning document metadata.
    """
    id: int
    filename: str
    original_name: str
    file_type: str
    file_size: int
    owner_id: int
    uploaded_at: datetime
    total_chunks: int = 0

    model_config = ConfigDict(from_attributes=True)


class SearchResult(BaseModel):
    """
    Schema for vector search results.
    """
    chunk_id: int
    document_id: int
    filename: str
    page_number: int
    content: str
    similarity_score: float
