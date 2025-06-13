import aiohttp
from bs4 import BeautifulSoup
from typing import List, Set, Tuple
import re
from urllib.parse import urljoin, urlparse


class WikipediaParser:
    """Parser for extracting content from Wikipedia articles."""
    
    def __init__(self):
        self.session = None
        self.base_url = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def parse_article(self, url: str) -> Tuple[str, str, List[str]]:
        """Parse Wikipedia article and extract title, content, and links."""
        if not self.session:
            raise RuntimeError("Parser must be used as async context manager")
        
        parsed_url = urlparse(url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, timeout=timeout, headers=headers) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to fetch article: {response.status}")
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'lxml')
                
                title = self._extract_title(soup)
                content = self._extract_content(soup)
                links = self._extract_links(soup)
                
                return title, content, links
        
        except Exception as e:
            raise ValueError(f"Error parsing article {url}: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title."""
        title_element = soup.find('h1', {'class': 'firstHeading'})
        return title_element.get_text().strip() if title_element else "Unknown Title"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content."""
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return ""
        
        paragraphs = content_div.find_all('p')
        content_parts = []
        
        for paragraph in paragraphs:
            text = paragraph.get_text().strip()
            if text and len(text) > 50:
                content_parts.append(text)
        
        return "\n\n".join(content_parts[:10])
    
    def _extract_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract Wikipedia article links from content."""
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            return []
        
        links = []
        seen_links: Set[str] = set()
        
        for link in content_div.find_all('a', href=True):
            href = link.get('href')
            
            if self._is_valid_wikipedia_link(href):
                full_url = urljoin(self.base_url, href)
                
                if full_url not in seen_links:
                    seen_links.add(full_url)
                    links.append(full_url)
                    
                    if len(links) >= 10:
                        break
        
        return links
    
    def _is_valid_wikipedia_link(self, href: str) -> bool:
        """Check if link is a valid Wikipedia article link."""
        if not href or not href.startswith('/wiki/'):
            return False
        
        invalid_patterns = [
            ':', '#', 'File:', 'Category:', 'Template:', 'Help:', 'Special:', 
            'Talk:', 'User:', 'Wikipedia:', 'Portal:', 'MediaWiki:'
        ]
        
        return not any(pattern in href for pattern in invalid_patterns)
    
    @staticmethod
    def is_wikipedia_url(url: str) -> bool:
        """Check if URL is a Wikipedia URL."""
        parsed = urlparse(url)
        return 'wikipedia.org' in parsed.netloc and '/wiki/' in parsed.path 