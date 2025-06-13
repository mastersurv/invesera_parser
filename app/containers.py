from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_async_session
from app.repositories.article_repository import ArticleRepository
from app.services.article_service import ArticleService
from app.ai.summary_generator import SummaryGenerator


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""
    
    config = providers.Configuration()
    
    db_session = providers.Resource(get_async_session)
    
    article_repository = providers.Factory(
        ArticleRepository,
        session=db_session
    )
    
    summary_generator = providers.Singleton(SummaryGenerator)
    
    article_service = providers.Factory(
        ArticleService,
        article_repository=article_repository,
        summary_generator=summary_generator
    ) 