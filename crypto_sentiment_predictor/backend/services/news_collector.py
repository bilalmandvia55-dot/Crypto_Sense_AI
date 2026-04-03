import os
import requests
import pandas as pd

def fetch_recent_news(symbol: str) -> list[dict]:
    """
    Fetch real cryptocurrency news data using NewsAPI.
    Stores results in a pandas DataFrame initially.
    """
    print(f"Fetching real news using NewsAPI for {symbol}...")
    
    api_key = os.getenv("NEWSAPI_KEY", "e99ac166ddf249cfbeecd194f30f4977")
    if api_key == "e99ac166ddf249cfbeecd194f30f4977":
        print("Using provided hardcoded NEWSAPI_KEY.")
    
    # Using NewsAPI everything endpoint
    url = "https://newsapi.org/v2/everything"
    
    # Query related to Bitcoin, Ethereum, cryptocurrency
    query = f"{symbol} AND (cryptocurrency OR Bitcoin OR Ethereum OR crypto)"
    
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20, # latest 10-20 articles
        "apiKey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            print(f"NewsAPI error: {data.get('message')}")
            return []
            
        articles = data.get("articles", [])
        if not articles:
            return []
            
        # Parse and store results in a DataFrame as requested
        parsed_articles = []
        for item in articles:
            parsed_articles.append({
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "source": item.get("source", {}).get("name", ""),
                "published_at": item.get("publishedAt", "")
            })
            
        df = pd.DataFrame(parsed_articles)
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from NewsAPI: {e}")
        # Return empty DataFrame gracefully on failure
        return pd.DataFrame()
