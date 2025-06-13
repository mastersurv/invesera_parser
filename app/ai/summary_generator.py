from openai import AsyncOpenAI
from app.config import settings


class SummaryGenerator:
    """AI-powered summary generator using OpenAI API."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def generate_summary(self, title: str, content: str) -> str:
        """Generate summary for article content using AI."""
        if not settings.openai_api_key:
            return "Summary generation unavailable: API key not configured"
        
        try:
            prompt = self._create_prompt(title, content)
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates concise summaries of Wikipedia articles. Provide clear, informative summaries in Russian language."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def _create_prompt(self, title: str, content: str) -> str:
        """Create prompt for AI summary generation."""
        truncated_content = content[:3000] if len(content) > 3000 else content
        
        return f"""
        Создай краткое содержание для статьи Википедии:
        
        Название: {title}
        
        Содержание:
        {truncated_content}
        
        Требования к резюме:
        - Объем: 3-5 предложений
        - Язык: русский
        - Стиль: информативный и понятный
        - Включи основные факты и ключевую информацию
        """ 