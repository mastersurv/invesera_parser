from typing import Optional, List
from loguru import logger

from app.repositories.article_repository import ArticleRepository
from app.parsers.wikipedia_parser import WikipediaParser
from app.ai.summary_generator import SummaryGenerator
from app.schemas import ArticleCreate, SummaryResponse
from app.models import Article
from app.config import settings


class ArticleService:
    """Service for managing articles, parsing, and summary generation."""
    
    def __init__(
        self,
        article_repository: ArticleRepository,
        summary_generator: SummaryGenerator
    ):
        self.article_repository = article_repository
        self.summary_generator = summary_generator
    
    async def parse_and_save_article(self, url: str) -> Article:
        """Parse article and save to database with recursive parsing."""
        if not WikipediaParser.is_wikipedia_url(url):
            raise ValueError("URL must be a Wikipedia article URL")
        
        existing_article = await self.article_repository.get_by_url(url)
        if existing_article:
            return existing_article
        
        async with WikipediaParser() as parser:
            root_article = await self._parse_recursive(parser, url, depth=0, parent_id=None)
        
        if root_article:
            await self._generate_summary_for_root_article(root_article)
        
        return root_article
    
    async def get_article_summary(self, url: str) -> Optional[SummaryResponse]:
        """Get article summary by URL."""
        article = await self.article_repository.get_by_url(url)
        if not article:
            return None
        
        return SummaryResponse(
            url=article.url,
            title=article.title,
            summary=article.summary,
            summary_generated=article.summary_generated
        )
    
    async def _parse_recursive(
        self,
        parser: WikipediaParser,
        url: str,
        depth: int,
        parent_id: Optional[int]
    ) -> Optional[Article]:
        """Recursively parse article and its linked articles."""
        if depth > settings.max_recursion_depth:
            return None
        
        existing_article = await self.article_repository.get_by_url(url)
        if existing_article:
            return existing_article
        
        try:
            logger.info(f"Parsing article at depth {depth}: {url}")
            title, content, links = await parser.parse_article(url)
            
            article_data = ArticleCreate(
                url=url,
                title=title,
                content=content,
                depth_level=depth,
                parent_id=parent_id
            )
            
            article = await self.article_repository.create(article_data)
            
            if depth < settings.max_recursion_depth:
                await self._parse_child_articles(parser, links, depth + 1, article.id)
            
            return article
        
        except Exception as e:
            logger.error(f"Error parsing article {url}: {str(e)}")
            return None
    
    async def _parse_child_articles(
        self,
        parser: WikipediaParser,
        links: List[str],
        depth: int,
        parent_id: int
    ) -> None:
        """Parse child articles from links."""
        for link in links[:5]:
            if await self.article_repository.exists_by_url(link):
                continue
            
            try:
                await self._parse_recursive(parser, link, depth, parent_id)
            except Exception as e:
                logger.error(f"Error parsing child article {link}: {str(e)}")
                continue
    
    async def _generate_summary_for_root_article(self, article: Article) -> None:
        """Generate summary for root article."""
        if article.depth_level == 0 and not article.summary_generated:
            try:
                logger.info(f"Generating summary for article: {article.title}")
                summary = await self.summary_generator.generate_summary(
                    article.title, 
                    article.content
                )
                await self.article_repository.update_summary(article.id, summary)
                logger.info(f"Summary generated for article: {article.title}")
            except Exception as e:
                logger.error(f"Error generating summary for {article.title}: {str(e)}")
    
    async def generate_pending_summaries(self) -> int:
        """Generate summaries for articles that don't have them yet."""
        articles = await self.article_repository.get_root_articles_without_summary()
        count = 0
        
        for article in articles:
            try:
                summary = await self.summary_generator.generate_summary(
                    article.title, 
                    article.content
                )
                await self.article_repository.update_summary(article.id, summary)
                count += 1
                logger.info(f"Summary generated for article: {article.title}")
            except Exception as e:
                logger.error(f"Error generating summary for {article.title}: {str(e)}")
        
        return count 