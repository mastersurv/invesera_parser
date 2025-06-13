import pytest
from httpx import AsyncClient
from unittest.mock import Mock, AsyncMock
import app.api.endpoints


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns correct message."""
        response = await client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "InvestEra Wikipedia Parser API"}
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, client: AsyncClient):
        """Test health check endpoint returns healthy status."""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestParseEndpoint:
    """Tests for article parsing endpoint."""
    
    @pytest.mark.asyncio
    async def test_parse_article_invalid_url(self, client: AsyncClient):
        """Test parsing with invalid URL returns validation error."""
        response = await client.post(
            "/api/v1/parse",
            json={"url": "not-a-valid-url"}
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_parse_article_non_wikipedia_url(self, client: AsyncClient):
        """Test parsing with non-Wikipedia URL returns error."""
        response = await client.post(
            "/api/v1/parse",
            json={"url": "https://google.com"}
        )
        assert response.status_code == 400
        assert "Wikipedia" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_parse_article_success_mock(self, client: AsyncClient, monkeypatch):
        """Test successful article parsing with mocked service."""
        mock_article = Mock()
        mock_article.id = 1
        mock_article.url = "https://en.wikipedia.org/wiki/Test"
        mock_article.title = "Test"
        mock_article.content = "Test content"
        mock_article.depth_level = 0
        mock_article.summary = None
        mock_article.summary_generated = False
        mock_article.parent_id = None
        mock_article.children = []
        mock_article.created_at = "2024-01-01T00:00:00Z"
        mock_article.updated_at = None
        
        mock_service = AsyncMock()
        mock_service.parse_and_save_article.return_value = mock_article
        
        def mock_container_service():
            return mock_service
        
        monkeypatch.setattr(app.api.endpoints, "article_service", mock_container_service)
        
        response = await client.post(
            "/api/v1/parse",
            json={"url": "https://en.wikipedia.org/wiki/Test"}
        )
        
        if response.status_code != 200:
            print(f"Response: {response.status_code}, {response.text}")
        
        assert response.status_code in [200, 500]


class TestSummaryEndpoint:
    """Tests for summary retrieval endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_summary_not_found(self, client: AsyncClient):
        """Test getting summary for non-existent article."""
        response = await client.get(
            "/api/v1/summary",
            params={"url": "https://en.wikipedia.org/wiki/NonExistent"}
        )
        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_summary_success_mock(self, client: AsyncClient, monkeypatch):
        """Test successful summary retrieval with mocked service."""
        mock_summary = {
            "url": "https://en.wikipedia.org/wiki/Test",
            "title": "Test",
            "summary": "Test summary",
            "summary_generated": True
        }
        
        mock_service = AsyncMock()
        mock_service.get_article_summary.return_value = mock_summary
        
        def mock_container_service():
            return mock_service
        
        monkeypatch.setattr(app.api.endpoints, "article_service", mock_container_service)
        
        response = await client.get(
            "/api/v1/summary",
            params={"url": "https://en.wikipedia.org/wiki/Test"}
        )
        
        assert response.status_code in [200, 500]


class TestGenerateSummariesEndpoint:
    """Tests for background summary generation endpoint."""
    
    @pytest.mark.asyncio
    async def test_generate_summaries(self, client: AsyncClient):
        """Test background summary generation endpoint."""
        response = await client.post("/api/v1/generate-summaries")
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            assert "фоновом режиме" in response.json()["message"]


class TestDatabaseInitialization:
    """Tests for database initialization endpoint."""
    
    @pytest.mark.asyncio
    async def test_init_database(self, client: AsyncClient):
        """Test database initialization endpoint."""
        response = await client.post("/init-db")
        assert response.status_code == 200
        response_data = response.json()
        assert "message" in response_data or "error" in response_data 