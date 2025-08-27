"""
News Data Provider
Fetches financial news from various free sources
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import aiohttp
from config.settings import NEWS_SOURCES


class NewsProvider:
    """Financial news data provider"""
    
    def __init__(self):
        self.sources = NEWS_SOURCES
        self.last_update = None
        
    def get_market_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get latest market news from multiple sources"""
        all_news = []
        
        for source_name, rss_url in self.sources.items():
            try:
                news = self._fetch_rss_feed(rss_url, source_name, limit // len(self.sources))
                all_news.extend(news)
            except Exception as e:
                print(f"Error fetching news from {source_name}: {e}")
                continue
        
        # Sort by publication date (newest first)
        all_news.sort(key=lambda x: x.get('published', datetime.min), reverse=True)
        
        self.last_update = datetime.now()
        return all_news[:limit]
    
    def _fetch_rss_feed(self, url: str, source: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch news from RSS feed"""
        try:
            feed = feedparser.parse(url)
            news_items = []
            
            for entry in feed.entries[:limit]:
                # Parse publication date
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                
                # Extract summary/description
                summary = ""
                if hasattr(entry, 'summary'):
                    # Remove HTML tags from summary
                    soup = BeautifulSoup(entry.summary, 'html.parser')
                    summary = soup.get_text().strip()
                
                news_item = {
                    'title': entry.get('title', ''),
                    'summary': summary,
                    'link': entry.get('link', ''),
                    'source': source,
                    'published': published or datetime.now(),
                    'author': entry.get('author', ''),
                    'tags': [tag.term for tag in entry.get('tags', [])]
                }
                
                news_items.append(news_item)
            
            return news_items
            
        except Exception as e:
            raise Exception(f"Error fetching RSS feed {url}: {str(e)}")
    
    async def get_news_async(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Asynchronously fetch news from multiple sources"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for source_name, rss_url in self.sources.items():
                task = self._fetch_rss_async(session, rss_url, source_name, limit // len(self.sources))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_news = []
            for result in results:
                if isinstance(result, list):
                    all_news.extend(result)
                elif isinstance(result, Exception):
                    print(f"Error in async news fetch: {result}")
            
            # Sort by publication date
            all_news.sort(key=lambda x: x.get('published', datetime.min), reverse=True)
            
            self.last_update = datetime.now()
            return all_news[:limit]
    
    async def _fetch_rss_async(self, session: aiohttp.ClientSession, url: str, source: str, limit: int) -> List[Dict[str, Any]]:
        """Asynchronously fetch RSS feed"""
        try:
            async with session.get(url, timeout=10) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                news_items = []
                for entry in feed.entries[:limit]:
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    
                    summary = ""
                    if hasattr(entry, 'summary'):
                        soup = BeautifulSoup(entry.summary, 'html.parser')
                        summary = soup.get_text().strip()
                    
                    news_item = {
                        'title': entry.get('title', ''),
                        'summary': summary,
                        'link': entry.get('link', ''),
                        'source': source,
                        'published': published or datetime.now(),
                        'author': entry.get('author', ''),
                        'tags': [tag.term for tag in entry.get('tags', [])]
                    }
                    
                    news_items.append(news_item)
                
                return news_items
                
        except Exception as e:
            return []
    
    def search_news(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for news containing specific keywords"""
        all_news = self.get_market_news(limit * 2)  # Get more to filter
        
        query_lower = query.lower()
        filtered_news = []
        
        for news in all_news:
            title_lower = news.get('title', '').lower()
            summary_lower = news.get('summary', '').lower()
            
            if query_lower in title_lower or query_lower in summary_lower:
                filtered_news.append(news)
                
                if len(filtered_news) >= limit:
                    break
        
        return filtered_news
    
    def get_trending_topics(self) -> List[Dict[str, Any]]:
        """Extract trending topics from news headlines"""
        news = self.get_market_news(50)
        
        # Simple keyword extraction (can be improved with NLP)
        word_count = {}
        for item in news:
            title = item.get('title', '').lower()
            words = title.split()
            
            for word in words:
                # Filter out common words and short words
                if len(word) > 3 and word not in ['market', 'stock', 'shares', 'trading', 'price', 'close', 'open']:
                    word_count[word] = word_count.get(word, 0) + 1
        
        # Sort by frequency
        trending = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [{'topic': word, 'mentions': count} for word, count in trending]
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get information about news sources"""
        return {
            'sources': list(self.sources.keys()),
            'total_sources': len(self.sources),
            'last_update': self.last_update
        }
