import pytest
from unittest.mock import AsyncMock, patch, Mock

from app.ai.summary_generator import SummaryGenerator


class TestSummaryGenerator:
    """Tests for SummaryGenerator."""
    
    @pytest.fixture
    def summary_generator(self):
        """Create SummaryGenerator instance."""
        return SummaryGenerator()
    
    @pytest.fixture
    def sample_article_data(self):
        """Sample article data for testing."""
        return {
            "title": "Test Article", 
            "content": "This is a test article with some content that needs to be summarized."
        }
    
    @patch('app.config.settings')
    async def test_generate_summary_no_api_key(self, mock_settings, summary_generator, sample_article_data):
        """Test summary generation when no API key is configured."""
        mock_settings.openai_api_key = ""
        
        result = await summary_generator.generate_summary(
            sample_article_data["title"], 
            sample_article_data["content"]
        )
        
        assert "API key not configured" in result
    
    @patch('app.ai.summary_generator.AsyncOpenAI')
    @patch('app.config.settings')
    async def test_generate_summary_success(
        self, mock_settings, mock_openai_class, summary_generator, sample_article_data
    ):
        """Test successful summary generation."""
        mock_settings.openai_api_key = "test-api-key"
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Краткое содержание статьи."
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        result = await summary_generator.generate_summary(
            sample_article_data["title"],
            sample_article_data["content"]
        )
        
        assert result == "Краткое содержание статьи."
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('app.ai.summary_generator.AsyncOpenAI')
    @patch('app.config.settings')
    async def test_generate_summary_api_error(
        self, mock_settings, mock_openai_class, summary_generator, sample_article_data
    ):
        """Test summary generation with API error."""
        mock_settings.openai_api_key = "test-api-key"
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        result = await summary_generator.generate_summary(
            sample_article_data["title"],
            sample_article_data["content"]
        )
        
        assert "Error generating summary" in result
        assert "API Error" in result
    
    @patch('app.ai.summary_generator.AsyncOpenAI')
    @patch('app.config.settings')
    async def test_generate_summary_long_content(
        self, mock_settings, mock_openai_class, summary_generator
    ):
        """Test summary generation with very long content gets truncated."""
        mock_settings.openai_api_key = "test-api-key"
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Краткое содержание."
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        long_content = "A" * 5000
        
        result = await summary_generator.generate_summary("Test Title", long_content)
        
        assert result == "Краткое содержание."
        
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        user_message = messages[1]["content"]
        
        assert len([c for c in user_message if c == "A"]) <= 3000
    
    def test_create_prompt(self, summary_generator):
        """Test prompt creation for AI."""
        title = "Test Article"
        content = "Test content for the article."
        
        prompt = summary_generator._create_prompt(title, content)
        
        assert title in prompt
        assert content in prompt
        assert "Краткое содержание" in prompt
        assert "русский" in prompt
        assert "3-5 предложений" in prompt
    
    def test_create_prompt_long_content_truncation(self, summary_generator):
        """Test prompt creation truncates long content."""
        title = "Test Article"
        long_content = "A" * 5000
        
        prompt = summary_generator._create_prompt(title, long_content)
        
        content_in_prompt = prompt.split("Содержание:")[1].split("Требования")[0].strip()
        assert len(content_in_prompt) <= 3000 