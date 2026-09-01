from langchain_tavily import TavilySearch
import os 

search = TavilySearch(
    max_results=5,
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
)