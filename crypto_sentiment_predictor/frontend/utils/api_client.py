import sys
import os
import streamlit as st
import pandas as pd

# Safely inject the backend directory into sys.path to allow native service imports
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from services import market_data, news_collector, predictor, sentiment_analyzer

@st.cache_data(ttl=60, show_spinner=False)
def get_sentiment(symbol: str) -> dict:
    news = news_collector.fetch_recent_news(symbol)
    sentiment = sentiment_analyzer.analyze_sentiment(news)
    return {"symbol": symbol, "sentiment": sentiment}

@st.cache_data(ttl=60, show_spinner=False)
def get_market_data(symbol: str) -> dict:
    data = market_data.fetch_price_data(symbol)
    return {"symbol": symbol, "market_data": data}

@st.cache_data(ttl=60, show_spinner=False)
def get_prediction(symbol: str) -> dict:
    news = news_collector.fetch_recent_news(symbol)
    sentiment = sentiment_analyzer.analyze_sentiment(news)
    market = market_data.fetch_price_data(symbol)
    pred_data = predictor.predict_trend(sentiment, market)
    
    return {
        "symbol": symbol,
        "sentiment": sentiment,
        "market_data": market,
        "prediction": pred_data
    }

@st.cache_data(ttl=60, show_spinner=False)
def get_news(symbol: str) -> dict:
    news = news_collector.fetch_recent_news(symbol)
    
    # Mutates the dataframe adding sent_score and label
    sentiment_summary = sentiment_analyzer.analyze_sentiment(news)
    
    if news is not None and not news.empty:
        news = news.fillna("")
        news_records = news.to_dict(orient="records")
    else:
        news_records = []
        
    return {
        "symbol": symbol, 
        "news": news_records, 
        "overall_sentiment": sentiment_summary
    }
