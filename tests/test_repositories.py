import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.article_repository import ArticleRepository
from app.schemas import ArticleCreate


class TestArticleRepository:
    """Tests for ArticleRepository."""
    
    @pytest.fixture
    def repository(self, db_session: AsyncSession):
        """Create ArticleRepository with test session."""
        return ArticleRepository(db_session)
    
    @pytest.fixture
    def sample_article_data(self):
        """Create sample article data for testing."""
        return ArticleCreate(
            url="https://en.wikipedia.org/wiki/Test",
            title="Test Article",
            content="This is test content for the article.",
            depth_level=0,
            parent_id=None
        )
    
    async def test_create_article(self, repository, sample_article_data):
        """Test creating a new article."""
        article = await repository.create(sample_article_data)
        
        assert article.id is not None
        assert article.url == sample_article_data.url
        assert article.title == sample_article_data.title
        assert article.content == sample_article_data.content
        assert article.depth_level == sample_article_data.depth_level
        assert article.summary_generated is False
    
    async def test_get_by_url_existing(self, repository, sample_article_data):
        """Test getting article by URL for existing article."""
        created_article = await repository.create(sample_article_data)
        
        found_article = await repository.get_by_url(sample_article_data.url)
        
        assert found_article is not None
        assert found_article.id == created_article.id
        assert found_article.url == sample_article_data.url
    
    async def test_get_by_url_not_existing(self, repository):
        """Test getting article by URL for non-existing article."""
        article = await repository.get_by_url("https://en.wikipedia.org/wiki/NonExistent")
        
        assert article is None
    
    async def test_get_by_id_existing(self, repository, sample_article_data):
        """Test getting article by ID for existing article."""
        created_article = await repository.create(sample_article_data)
        
        found_article = await repository.get_by_id(created_article.id)
        
        assert found_article is not None
        assert found_article.id == created_article.id
        assert found_article.url == sample_article_data.url
    
    async def test_get_by_id_not_existing(self, repository):
        """Test getting article by ID for non-existing article."""
        article = await repository.get_by_id(99999)
        
        assert article is None
    
    async def test_exists_by_url_existing(self, repository, sample_article_data):
        """Test checking existence of article by URL for existing article."""
        await repository.create(sample_article_data)
        
        exists = await repository.exists_by_url(sample_article_data.url)
        
        assert exists is True
    
    async def test_exists_by_url_not_existing(self, repository):
        """Test checking existence of article by URL for non-existing article."""
        exists = await repository.exists_by_url("https://en.wikipedia.org/wiki/NonExistent")
        
        assert exists is False
    
    async def test_update_summary(self, repository, sample_article_data):
        """Test updating article summary."""
        article = await repository.create(sample_article_data)
        test_summary = "This is a test summary."
        
        await repository.update_summary(article.id, test_summary)
        
        updated_article = await repository.get_by_id(article.id)
        assert updated_article.summary == test_summary
        assert updated_article.summary_generated is True
    
    async def test_get_root_articles_without_summary(self, repository):
        """Test getting root articles without summary."""
        root_data = ArticleCreate(
            url="https://en.wikipedia.org/wiki/Root",
            title="Root Article",
            content="Root content",
            depth_level=0,
            parent_id=None
        )
        
        child_data = ArticleCreate(
            url="https://en.wikipedia.org/wiki/Child",
            title="Child Article", 
            content="Child content",
            depth_level=1,
            parent_id=1
        )
        
        root_article = await repository.create(root_data)
        await repository.create(child_data)
        
        articles = await repository.get_root_articles_without_summary()
        
        assert len(articles) == 1
        assert articles[0].id == root_article.id
        assert articles[0].depth_level == 0
        assert articles[0].parent_id is None
    
    async def test_create_child_article(self, repository, sample_article_data):
        """Test creating child article with parent relationship."""
        parent_article = await repository.create(sample_article_data)
        
        child_data = ArticleCreate(
            url="https://en.wikipedia.org/wiki/Child",
            title="Child Article",
            content="Child content",
            depth_level=1,
            parent_id=parent_article.id
        )
        
        child_article = await repository.create(child_data)
        
        assert child_article.parent_id == parent_article.id
        assert child_article.depth_level == 1
        
        parent_with_children = await repository.get_by_id(parent_article.id)
        assert len(parent_with_children.children) == 1
        assert parent_with_children.children[0].id == child_article.id 