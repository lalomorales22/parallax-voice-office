"""
MCP Web Search Server
Provides web search capabilities using Serper or Tavily APIs
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SearchCache:
    """Simple in-memory cache for search results"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached result for query"""
        if query in self.cache:
            entry = self.cache[query]
            # Check if expired
            cached_time = datetime.fromisoformat(entry['cached_at'])
            if datetime.now() - cached_time < timedelta(seconds=self.ttl_seconds):
                logger.info(f"Cache hit for query: {query}")
                return entry['result']
            else:
                # Expired, remove from cache
                del self.cache[query]
        return None

    def set(self, query: str, result: Dict[str, Any]):
        """Cache a search result"""
        self.cache[query] = {
            'result': result,
            'cached_at': datetime.now().isoformat()
        }

    def clear(self):
        """Clear all cached results"""
        self.cache.clear()


class MCPWebSearchServer:
    """
    MCP server for web search operations
    Supports Serper and Tavily search APIs
    """

    def __init__(self, provider: str = "auto", max_results: int = 10,
                 cache_enabled: bool = True, cache_ttl: int = 3600):
        """
        Initialize web search server

        Args:
            provider: 'serper', 'tavily', or 'auto' (tries available keys)
            max_results: Maximum number of results to return
            cache_enabled: Whether to cache search results
            cache_ttl: Cache time-to-live in seconds
        """
        self.provider = provider
        self.max_results = max_results
        self.cache_enabled = cache_enabled
        self.cache = SearchCache(ttl_seconds=cache_ttl) if cache_enabled else None

        # Get API keys from environment
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')

        # Determine which provider to use
        self.active_provider = self._determine_provider()

        if self.active_provider:
            logger.info(f"✅ Initialized web search server (provider: {self.active_provider})")
        else:
            logger.warning("⚠️  No web search API keys found. Web search will not be available.")

    def _determine_provider(self) -> Optional[str]:
        """Determine which search provider to use"""
        if self.provider == "serper" and self.serper_api_key:
            return "serper"
        elif self.provider == "tavily" and self.tavily_api_key:
            return "tavily"
        elif self.provider == "auto":
            # Auto-select based on available keys
            if self.serper_api_key:
                return "serper"
            elif self.tavily_api_key:
                return "tavily"
        return None

    def search(self, query: str, num_results: Optional[int] = None,
               search_type: str = "general") -> Dict[str, Any]:
        """
        Perform web search

        Args:
            query: Search query string
            num_results: Number of results (default: uses max_results from config)
            search_type: Type of search - 'general', 'news', 'images'

        Returns:
            Search results dictionary
        """
        if not self.active_provider:
            return {
                "status": "error",
                "message": "No web search API key configured. Please set SERPER_API_KEY or TAVILY_API_KEY in .env file"
            }

        # Check cache first
        if self.cache_enabled:
            cache_key = f"{query}:{num_results or self.max_results}:{search_type}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                cached_result['from_cache'] = True
                return cached_result

        # Perform search
        num_results = num_results or self.max_results

        if self.active_provider == "serper":
            result = self._search_serper(query, num_results, search_type)
        elif self.active_provider == "tavily":
            result = self._search_tavily(query, num_results, search_type)
        else:
            result = {
                "status": "error",
                "message": f"Unknown provider: {self.active_provider}"
            }

        # Cache successful results
        if self.cache_enabled and result.get('status') == 'success':
            cache_key = f"{query}:{num_results}:{search_type}"
            self.cache.set(cache_key, result)

        return result

    def _search_serper(self, query: str, num_results: int, search_type: str) -> Dict[str, Any]:
        """Search using Serper API"""
        try:
            url = "https://google.serper.dev/search"

            payload = {
                "q": query,
                "num": num_results
            }

            # Add search type specific parameters
            if search_type == "news":
                url = "https://google.serper.dev/news"
            elif search_type == "images":
                url = "https://google.serper.dev/images"

            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse results
            results = []
            if 'organic' in data:
                for item in data['organic'][:num_results]:
                    results.append({
                        "title": item.get('title', ''),
                        "link": item.get('link', ''),
                        "snippet": item.get('snippet', ''),
                        "position": item.get('position', 0)
                    })
            elif 'news' in data:
                for item in data['news'][:num_results]:
                    results.append({
                        "title": item.get('title', ''),
                        "link": item.get('link', ''),
                        "snippet": item.get('snippet', ''),
                        "date": item.get('date', '')
                    })

            return {
                "status": "success",
                "operation": "search",
                "provider": "serper",
                "query": query,
                "result_count": len(results),
                "results": results,
                "answer_box": data.get('answerBox'),
                "knowledge_graph": data.get('knowledgeGraph'),
                "searched_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Serper API error: {e}")
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }

    def _search_tavily(self, query: str, num_results: int, search_type: str) -> Dict[str, Any]:
        """Search using Tavily API"""
        try:
            url = "https://api.tavily.com/search"

            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "max_results": num_results,
                "search_depth": "advanced" if search_type == "general" else "basic",
                "include_answer": True,
                "include_raw_content": False
            }

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse results
            results = []
            if 'results' in data:
                for item in data['results']:
                    results.append({
                        "title": item.get('title', ''),
                        "link": item.get('url', ''),
                        "snippet": item.get('content', ''),
                        "score": item.get('score', 0.0)
                    })

            return {
                "status": "success",
                "operation": "search",
                "provider": "tavily",
                "query": query,
                "result_count": len(results),
                "results": results,
                "answer": data.get('answer'),
                "searched_at": datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Tavily API error: {e}")
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }

    def search_news(self, query: str, num_results: Optional[int] = None) -> Dict[str, Any]:
        """
        Search for news articles

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            News search results
        """
        return self.search(query, num_results, search_type="news")

    def get_answer(self, question: str) -> Dict[str, Any]:
        """
        Get direct answer to a question using web search

        Args:
            question: Question to answer

        Returns:
            Answer with sources
        """
        result = self.search(question, num_results=5)

        if result.get('status') != 'success':
            return result

        # Extract answer from answer box or knowledge graph
        answer = None
        if result.get('answer_box'):
            answer = result['answer_box'].get('answer') or result['answer_box'].get('snippet')
        elif result.get('knowledge_graph'):
            answer = result['knowledge_graph'].get('description')
        elif result.get('answer'):
            answer = result['answer']

        # If no direct answer, create summary from top results
        if not answer and result.get('results'):
            snippets = [r['snippet'] for r in result['results'][:3]]
            answer = ' '.join(snippets[:2])  # Combine first 2 snippets

        return {
            "status": "success",
            "operation": "get_answer",
            "question": question,
            "answer": answer,
            "sources": result.get('results', [])[:3],
            "provider": result.get('provider')
        }

    def clear_cache(self) -> Dict[str, Any]:
        """Clear the search cache"""
        if self.cache:
            self.cache.clear()
            return {
                "status": "success",
                "operation": "clear_cache",
                "message": "Search cache cleared"
            }
        return {
            "status": "success",
            "message": "Cache not enabled"
        }

    def get_status(self) -> Dict[str, Any]:
        """Get web search server status"""
        return {
            "status": "success",
            "active_provider": self.active_provider,
            "providers_available": {
                "serper": bool(self.serper_api_key),
                "tavily": bool(self.tavily_api_key)
            },
            "cache_enabled": self.cache_enabled,
            "max_results": self.max_results
        }
