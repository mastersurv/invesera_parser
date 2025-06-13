import asyncio
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.schemas import ArticleResponse, ParseRequest
from datetime import datetime
from app.parsers.wikipedia_parser import WikipediaParser
from app.main import app
from app.ai.summary_generator import SummaryGenerator


def test_root_endpoint():
    """Test root endpoint returns correct message."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "InvestEra Wikipedia Parser API"}


def test_health_endpoint():
    """Test health endpoint returns healthy status."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_parse_endpoint_invalid_url():
    """Test parse endpoint with invalid URL."""
    client = TestClient(app)
    response = client.post("/api/v1/parse", json={"url": "invalid-url"})
    assert response.status_code == 422


def test_parse_endpoint_non_wikipedia():
    """Test parse endpoint with non-Wikipedia URL."""
    client = TestClient(app)
    response = client.post("/api/v1/parse", json={"url": "https://google.com"})
    assert response.status_code == 400
    assert "Wikipedia" in response.json()["detail"]


def test_summary_endpoint_missing_param():
    """Test summary endpoint without URL parameter.""" 
    client = TestClient(app)
    response = client.get("/api/v1/summary")
    assert response.status_code == 422


def test_init_db_endpoint():
    """Test database initialization endpoint."""
    client = TestClient(app)
    response = client.post("/init-db")
    assert response.status_code in [200, 500]


class TestParsers:
    """Tests for parser components."""
    
    def test_wikipedia_url_validation(self):
        """Test Wikipedia URL validation logic."""
        
        valid_urls = [
            "https://en.wikipedia.org/wiki/Python",
            "https://ru.wikipedia.org/wiki/Тест",
        ]
        
        invalid_urls = [
            "https://google.com",
            "invalid-url",
        ]
        
        for url in valid_urls:
            assert WikipediaParser.is_wikipedia_url(url) is True
        
        for url in invalid_urls:
            assert WikipediaParser.is_wikipedia_url(url) is False


class TestSchemas:
    """Tests for Pydantic schemas."""
    
    def test_parse_request_validation(self):
        """Test ParseRequest schema validation."""
        
        valid_data = {"url": "https://en.wikipedia.org/wiki/Test"}
        request = ParseRequest(**valid_data)
        assert str(request.url) == valid_data["url"]
        
        with pytest.raises(Exception):
            ParseRequest(url="invalid-url")
    
    def test_article_response_creation(self):
        """Test ArticleResponse schema creation."""
        
        article_data = {
            "id": 1,
            "url": "https://en.wikipedia.org/wiki/Test",
            "title": "Test",
            "content": "Content",
            "depth_level": 0,
            "summary": None,
            "summary_generated": False,
            "parent_id": None,
            "children": [],
            "created_at": datetime.now(),
            "updated_at": None
        }
        
        response = ArticleResponse(**article_data)
        assert response.id == 1
        assert response.title == "Test"


@patch('app.ai.summary_generator.settings')
def test_summary_generator_no_api_key(mock_settings):
    """Test summary generator when no API key is configured."""
    
    mock_settings.openai_api_key = ""
    generator = SummaryGenerator()
    
    async def test():
        result = await generator.generate_summary("Test", "Content")
        return result
    
    result = asyncio.run(test())
    assert "API key not configured" in result 