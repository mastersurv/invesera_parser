import pytest
from unittest.mock import AsyncMock, patch
from bs4 import BeautifulSoup

from app.parsers.wikipedia_parser import WikipediaParser


class TestWikipediaParser:
    """Tests for WikipediaParser."""
    
    @pytest.fixture
    def parser(self):
        """Create WikipediaParser instance."""
        return WikipediaParser()
    
    def test_is_wikipedia_url_valid(self, parser):
        """Test valid Wikipedia URL detection."""
        valid_urls = [
            "https://en.wikipedia.org/wiki/Python_(programming_language)",
            "https://ru.wikipedia.org/wiki/Тест",
            "http://en.wikipedia.org/wiki/Test"
        ]
        
        for url in valid_urls:
            assert WikipediaParser.is_wikipedia_url(url) is True
    
    def test_is_wikipedia_url_invalid(self, parser):
        """Test invalid Wikipedia URL detection."""
        invalid_urls = [
            "https://google.com",
            "https://en.wikipedia.org/wiki/File:Test.jpg",
            "https://example.com/wiki/Test",
            "not-a-url"
        ]
        
        for url in invalid_urls:
            assert WikipediaParser.is_wikipedia_url(url) is False
    
    def test_is_valid_wikipedia_link_valid(self, parser):
        """Test valid Wikipedia link detection."""
        valid_links = [
            "/wiki/Test",
            "/wiki/Python_(programming_language)",
            "/wiki/Test_Article"
        ]
        
        for link in valid_links:
            assert parser._is_valid_wikipedia_link(link) is True
    
    def test_is_valid_wikipedia_link_invalid(self, parser):
        """Test invalid Wikipedia link detection."""
        invalid_links = [
            "/wiki/File:Test.jpg",
            "/wiki/Category:Test",
            "/wiki/Talk:Test",
            "/wiki/User:Test",
            "/wiki/Template:Test",
            "https://example.com",
            "/not-wiki/Test"
        ]
        
        for link in invalid_links:
            assert parser._is_valid_wikipedia_link(link) is False
    
    @patch('aiohttp.ClientSession.get')
    async def test_parse_article_success(self, mock_get, parser):
        """Test successful article parsing."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = """
        <html>
            <body>
                <h1 class="firstHeading">Test Article</h1>
                <div id="mw-content-text">
                    <p>This is a test paragraph with more than 50 characters for testing purposes.</p>
                    <p>Another paragraph with sufficient content for the test to pass validation.</p>
                    <a href="/wiki/Valid_Link">Valid Link</a>
                    <a href="/wiki/File:Invalid.jpg">Invalid Link</a>
                </div>
            </body>
        </html>
        """
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with parser:
            title, content, links = await parser.parse_article("https://en.wikipedia.org/wiki/Test")
        
        assert title == "Test Article"
        assert "test paragraph" in content.lower()
        assert len(links) > 0
        assert "https://en.wikipedia.org/wiki/Valid_Link" in links
    
    @patch('aiohttp.ClientSession.get')
    async def test_parse_article_404(self, mock_get, parser):
        """Test parsing article that returns 404."""
        mock_response = AsyncMock()
        mock_response.status = 404
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with parser:
            with pytest.raises(ValueError) as exc_info:
                await parser.parse_article("https://en.wikipedia.org/wiki/NonExistent")
        
        assert "404" in str(exc_info.value)
    
    async def test_parse_article_without_context_manager(self, parser):
        """Test parsing article without async context manager raises error."""
        with pytest.raises(RuntimeError) as exc_info:
            await parser.parse_article("https://en.wikipedia.org/wiki/Test")
        
        assert "context manager" in str(exc_info.value)
    
    def test_extract_title_with_element(self, parser):
        """Test title extraction with valid element."""
        
        html = '<h1 class="firstHeading">Test Title</h1>'
        soup = BeautifulSoup(html, 'lxml')
        
        title = parser._extract_title(soup)
        assert title == "Test Title"
    
    def test_extract_title_without_element(self, parser):
        """Test title extraction without valid element."""
        
        html = '<h1>Not the right class</h1>'
        soup = BeautifulSoup(html, 'lxml')
        
        title = parser._extract_title(soup)
        assert title == "Unknown Title"
    
    def test_extract_content_with_paragraphs(self, parser):
        """Test content extraction with valid paragraphs."""
        
        html = '''
        <div id="mw-content-text">
            <p>This is a long enough paragraph that should be included in the content.</p>
            <p>Another paragraph with sufficient length for inclusion in the final result.</p>
            <p>Short</p>
        </div>
        '''
        soup = BeautifulSoup(html, 'lxml')
        
        content = parser._extract_content(soup)
        assert "long enough paragraph" in content
        assert "Another paragraph" in content
        assert "Short" not in content
    
    def test_extract_content_without_div(self, parser):
        """Test content extraction without content div."""
        
        html = '<p>Some paragraph</p>'
        soup = BeautifulSoup(html, 'lxml')
        
        content = parser._extract_content(soup)
        assert content == "" 