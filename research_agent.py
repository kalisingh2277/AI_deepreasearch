from typing import List, Dict, Any, Optional
from tavily import TavilyClient
import os
from dotenv import load_dotenv
import logging
import asyncio
from datetime import datetime
import networkx as nx
from collections import defaultdict
from src.config.config import settings
from src.utils.error_handler import (
    error_handler,
    validate_tavily_request,
    handle_tavily_error,
    log_api_call,
    log_api_response,
    error_tracker,
    TavilyAPIError
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self):
        # Use settings from config
        self.api_key = settings.TAVILY_API_KEY
        if not self.api_key:
            logger.error("Tavily API key not found in environment variables")
            raise ValueError("Tavily API key is not configured")
        
        # Validate API key format
        if not self.api_key.startswith('tvly-'):
            logger.error("Invalid Tavily API key format")
            raise ValueError("Invalid Tavily API key format. Key should start with 'tvly-'")
            
        self.client = TavilyClient(api_key=self.api_key)
        self.max_depth = settings.MAX_RESEARCH_DEPTH
        self.max_urls = settings.MAX_URLS_PER_SEARCH
        self.rate_limit = asyncio.Semaphore(5)
        self.cache = {}
        
        logger.info("ResearchAgent initialized successfully")
        # Log only first few characters of API key for security
        logger.info(f"Using API key: {self.api_key[:8]}...")

    @error_handler
    async def search_and_analyze(self, query: str, search_depth: int = 1) -> Dict[str, Any]:
        """
        Perform a search and analyze the results using Tavily with improved error handling
        and caching
        """
        try:
            # Validate input parameters
            validate_tavily_request(query, search_depth)

            # Check cache
            cache_key = f"{query}:{search_depth}"
            if cache_key in self.cache:
                logger.info(f"Cache hit for query: {query}")
                return self.cache[cache_key]

            logger.info(f"Starting search for query: {query} with depth: {search_depth}")
            
            async with self.rate_limit:
                # Prepare search parameters according to Tavily API documentation
                search_params = {
                    "query": query,
                    "search_depth": "advanced" if search_depth > 1 else "basic",
                    "include_answer": True,
                    "include_domains": [],
                    "exclude_domains": [],
                    "max_tokens": 8000,
                    "search_type": "research"
                }
                
                # Log API call
                log_api_call("Tavily", search_params)
                
                try:
                    # Make API request
                    search_result = await asyncio.to_thread(
                        self.client.search,
                        query=search_params["query"],
                        search_depth=search_params["search_depth"],
                        include_answer=search_params["include_answer"],
                        search_type=search_params["search_type"]
                    )
                    
                    # Log API response
                    logger.debug(f"Raw API response type: {type(search_result)}")
                    logger.debug(f"Raw API response: {search_result}")
                    
                    # Ensure search_result is a dictionary
                    if not isinstance(search_result, dict):
                        try:
                            if isinstance(search_result, str):
                                # Try to parse string response as JSON
                                import json
                                search_result = json.loads(search_result)
                            else:
                                # Convert response to dictionary
                                search_result = {
                                    "status": "error",
                                    "error": f"Unexpected response type: {type(search_result)}",
                                    "raw_response": str(search_result)
                                }
                        except Exception as parse_error:
                            logger.error(f"Failed to parse API response: {parse_error}")
                            raise TavilyAPIError(
                                message="Invalid response format from API",
                                status_code=500,
                                response_body={"raw_response": str(search_result)}
                            )
                    
                    # Log processed response
                    log_api_response("Tavily", search_result)
                    
                    # Check for API errors
                    if "error" in search_result:
                        error_msg = search_result.get("error", "Unknown API error")
                        logger.error(f"API returned error: {error_msg}")
                        handle_tavily_error(422, search_result)
                    
                except Exception as e:
                    error_tracker.track_error(e, {
                        "query": query,
                        "depth": search_depth,
                        "params": search_params,
                        "raw_response": str(search_result) if 'search_result' in locals() else None
                    })
                    raise
                
                # Process results
                results = search_result.get("results", [])
                if not results:
                    logger.warning("No results found in API response")
                    raise TavilyAPIError(
                        message="No results found",
                        status_code=404,
                        response_body=search_result
                    )
                
                # Process sources
                sources = []
                for i, result in enumerate(results):
                    try:
                        source = {
                            "title": str(result.get("title", "Untitled")),
                            "url": str(result.get("url", "")),
                            "content": str(result.get("content", "No content available")),
                            "type": self._determine_content_type(result),
                            "domain": self._extract_domain(str(result.get("url", "")))
                        }
                        sources.append(source)
                    except Exception as e:
                        logger.error(f"Error processing result {i + 1}: {str(e)}", exc_info=True)
                        continue
                
                # Create knowledge graph
                try:
                    graph_data = self._create_knowledge_graph(sources)
                except Exception as e:
                    logger.error(f"Error creating knowledge graph: {str(e)}", exc_info=True)
                    graph_data = {"nodes": [], "links": []}
                
                # Create final response
                try:
                    response = {
                        "status": "success",
                        "query": query,
                        "depth": search_depth,
                        "timestamp": datetime.now().isoformat(),
                        "sources": sources[:self.max_urls],
                        "knowledge_graph": graph_data,
                        "metadata": {
                            "total_sources": len(sources),
                            "processed_sources": len(sources[:self.max_urls]),
                            "graph_nodes": len(graph_data["nodes"]),
                            "graph_edges": len(graph_data["links"])
                        }
                    }
                    
                    # Cache the results
                    self.cache[cache_key] = response
                    
                    return response
                    
                except (TypeError, ValueError) as e:
                    logger.error(f"Error creating JSON response: {str(e)}", exc_info=True)
                    raise TavilyAPIError(
                        message="Failed to create valid JSON response",
                        status_code=500,
                        response_body={"error": str(e)}
                    )
                
        except Exception as e:
            error_tracker.track_error(e, {
                "query": query,
                "depth": search_depth,
                "function": "search_and_analyze"
            })
            raise

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract key terms from content"""
        if not content:
            return []
        words = content.lower().split()
        # Remove common words and short terms
        keywords = [w for w in words if len(w) > 4 and w not in settings.COMMON_WORDS]
        return list(set(keywords))[:10]  # Return top 10 unique keywords

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except Exception as e:
            logger.error(f"Error extracting domain from URL {url}: {str(e)}")
            return url

    def _determine_content_type(self, result: Dict[str, Any]) -> str:
        """Determine the type of content based on the result"""
        url = str(result.get("url", "")).lower()
        if not url:
            return "unknown"
        if "pdf" in url:
            return "pdf"
        elif any(ext in url for ext in [".doc", ".docx"]):
            return "document"
        elif any(ext in url for ext in [".jpg", ".png", ".gif"]):
            return "image"
        else:
            return "webpage"

    def _create_knowledge_graph(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a knowledge graph from the sources"""
        G = nx.Graph()
        
        # Add nodes and edges
        for source in sources:
            title_node = source["title"][:50]  # Truncate long titles
            G.add_node(title_node, type="source")
            
            # Extract and add keyword nodes
            keywords = self._extract_keywords(source["content"])
            for keyword in keywords:
                G.add_node(keyword, type="keyword")
                G.add_edge(title_node, keyword)
        
        # Convert to D3.js format
        return {
            "nodes": [{"id": node, "label": node, "type": G.nodes[node]["type"]} 
                     for node in G.nodes()],
            "links": [{"source": u, "target": v} for (u, v) in G.edges()]
        }