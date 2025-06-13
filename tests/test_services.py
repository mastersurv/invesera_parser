import pytest
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.article_service import ArticleService
from app.repositories.article_repository import ArticleRepository
from app.ai.summary_generator import SummaryGenerator
from app.models import Article
from app.schemas import ArticleCreate


class TestArticleService:
    """Tests for ArticleService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock article repository."""
        return AsyncMock(spec=ArticleRepository)
    
    @pytest.fixture
    def mock_summary_generator(self):
        """Create mock summary generator."""
        return AsyncMock(spec=SummaryGenerator)
    
    @pytest.fixture
    def article_service(self, mock_repository, mock_summary_generator):
        """Create ArticleService with mocked dependencies."""
        return ArticleService(mock_repository, mock_summary_generator)
    
    @pytest.fixture
    def sample_article(self):
        """Create sample article for testing."""
        article = Mock(spec=Article)
        article.id = 1
        article.url = "https://en.wikipedia.org/wiki/Test"
        article.title = "Test Article"
        article.content = "Test content"
        article.depth_level = 0
        article.summary = None
        article.summary_generated = False
        article.parent_id = None
        return article
    
    async def test_get_article_summary_found(
        self, article_service, mock_repository, sample_article
    ):
        """Test getting summary for existing article."""
        sample_article.summary = "Test summary"
        sample_article.summary_generated = True
        mock_repository.get_by_url.return_value = sample_article
        
        result = await article_service.get_article_summary(sample_article.url)
        
        assert result is not None
        assert result.url == sample_article.url
        assert result.title == sample_article.title
        assert result.summary == sample_article.summary
        assert result.summary_generated == sample_article.summary_generated
    
    async def test_get_article_summary_not_found(
        self, article_service, mock_repository
    ):
        """Test getting summary for non-existent article."""
        mock_repository.get_by_url.return_value = None
        
        result = await article_service.get_article_summary("https://example.com")
        
        assert result is None
    
    async def test_parse_and_save_article_invalid_url(self, article_service):
        """Test parsing invalid URL raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await article_service.parse_and_save_article("https://google.com")
        
        assert "Wikipedia" in str(exc_info.value)
    
    async def test_parse_and_save_article_existing(
        self, article_service, mock_repository, sample_article
    ):
        """Test parsing existing article returns cached version."""
        mock_repository.get_by_url.return_value = sample_article
        
        result = await article_service.parse_and_save_article(sample_article.url)
        
        assert result == sample_article
        mock_repository.get_by_url.assert_called_once_with(sample_article.url)
    
    @patch('app.services.article_service.WikipediaParser')
    async def test_parse_and_save_article_new(
        self, mock_parser_class, article_service, mock_repository, 
        mock_summary_generator, sample_article
    ):
        """Test parsing new article creates and saves it."""
        mock_parser = AsyncMock()
        mock_parser_class.return_value.__aenter__.return_value = mock_parser
        mock_parser.parse_article.return_value = (
            "Test Title", "Test Content", ["https://en.wikipedia.org/wiki/Link1"]
        )
        
        mock_repository.get_by_url.return_value = None
        mock_repository.exists_by_url.return_value = False
        mock_repository.create.return_value = sample_article
        mock_repository.update_summary.return_value = None
        
        mock_summary_generator.generate_summary.return_value = "Generated summary"
        
        with patch('app.parsers.wikipedia_parser.WikipediaParser.is_wikipedia_url', return_value=True):
            result = await article_service.parse_and_save_article(sample_article.url)
        
        assert result == sample_article
        mock_repository.create.assert_called_once()
        mock_summary_generator.generate_summary.assert_called_once()
    
    async def test_generate_pending_summaries(
        self, article_service, mock_repository, mock_summary_generator
    ):
        """Test generating summaries for pending articles."""
        articles = [Mock(id=1, title="Test1", content="Content1")]
        mock_repository.get_root_articles_without_summary.return_value = articles
        mock_summary_generator.generate_summary.return_value = "Generated summary"
        mock_repository.update_summary.return_value = None
        
        count = await article_service.generate_pending_summaries()
        
        assert count == 1
        mock_summary_generator.generate_summary.assert_called_once()
        mock_repository.update_summary.assert_called_once_with(1, "Generated summary") 