from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Article(Base):
    """Article model for storing Wikipedia articles."""
    
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    depth_level = Column(Integer, nullable=False, default=0)
    summary = Column(Text, nullable=True)
    summary_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    parent_id = Column(Integer, ForeignKey("articles.id"), nullable=True)
    parent = relationship("Article", remote_side=[id], back_populates="children")
    children = relationship("Article", back_populates="parent") 