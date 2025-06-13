from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class ArticleBase(BaseModel):
    """Base article schema."""
    
    url: str
    title: str
    content: str
    depth_level: int = 0


class ArticleCreate(ArticleBase):
    """Schema for creating an article."""
    
    parent_id: Optional[int] = None


class ArticleResponse(ArticleBase):
    """Schema for article response."""
    
    id: int
    summary: Optional[str] = None
    summary_generated: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    parent_id: Optional[int] = None
    # children: List["ArticleResponse"] = []  # Временно отключено из-за async проблем
    
    class Config:
        from_attributes = True


class ParseRequest(BaseModel):
    """Schema for parsing request."""
    
    url: HttpUrl


class SummaryResponse(BaseModel):
    """Schema for summary response."""
    
    url: str
    title: str
    summary: Optional[str] = None
    summary_generated: bool = False


ArticleResponse.model_rebuild() 