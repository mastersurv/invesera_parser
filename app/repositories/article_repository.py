from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models import Article
from app.schemas import ArticleCreate


class ArticleRepository:
    """Repository for managing articles in database."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, article_data: ArticleCreate) -> Article:
        """Create a new article in database."""
        article = Article(**article_data.model_dump())
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return article
    
    async def get_by_url(self, url: str) -> Optional[Article]:
        """Get article by URL."""
        result = await self.session.execute(
            select(Article).where(Article.url == url)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, article_id: int) -> Optional[Article]:
        """Get article by ID with children."""
        result = await self.session.execute(
            select(Article)
            .options(selectinload(Article.children))
            .where(Article.id == article_id)
        )
        return result.scalar_one_or_none()
    
    async def get_root_articles_without_summary(self) -> List[Article]:
        """Get root articles that don't have summary generated."""
        result = await self.session.execute(
            select(Article).where(
                Article.parent_id.is_(None),
                Article.summary_generated == False
            )
        )
        return result.scalars().all()
    
    async def update_summary(self, article_id: int, summary: str) -> None:
        """Update article summary."""
        await self.session.execute(
            update(Article)
            .where(Article.id == article_id)
            .values(summary=summary, summary_generated=True)
        )
        await self.session.commit()
    
    async def exists_by_url(self, url: str) -> bool:
        """Check if article exists by URL."""
        result = await self.session.execute(
            select(Article.id).where(Article.url == url)
        )
        return result.scalar_one_or_none() is not None 