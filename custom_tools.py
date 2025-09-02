from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import json
import requests
from bs4 import BeautifulSoup

class SerperSearchInput(BaseModel):
    """Input for Serper search tool"""
    query: str = Field(description="Search query to look for")

class SerperDevTool(BaseTool):
    name: str = "Search the internet"
    description: str = "Useful for searching the internet for current information on any topic"
    args_schema: Type[BaseModel] = SerperSearchInput
    
    def _run(self, query: str) -> str:
       
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "num": 10
        })
        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=30)
            result = response.json()
            
            # Format the results for better readability
            if 'organic' in result:
                formatted_results = []
                for item in result['organic'][:5]:  # Top 5 results
                    formatted_results.append(f"Title: {item.get('title', 'N/A')}\nURL: {item.get('link', 'N/A')}\nSnippet: {item.get('snippet', 'N/A')}\n")
                return "\n".join(formatted_results)
            else:
                return str(result)
                
        except Exception as e:
            return f"Error searching: {str(e)}"

class ScrapeWebsiteInput(BaseModel):
    """Input for website scraping tool"""
    url: str = Field(description="Website URL to scrape")

class ScrapeWebsiteTool(BaseTool):
    name: str = "Scrape website content"
    description: str = "Useful for extracting content from a specific website URL"
    args_schema: Type[BaseModel] = ScrapeWebsiteInput
    
    def _run(self, url: str) -> str:
        if not url or not url.startswith(('http://', 'https://')):
            return "Error: Invalid URL provided"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit length
            max_length = 5000
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
            
        except Exception as e:
            return f"Error scraping website: {str(e)}"