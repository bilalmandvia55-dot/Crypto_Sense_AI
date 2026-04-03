from fastapi import APIRouter
from services import market_data, news_collector, predictor, sentiment_analyzer

router = APIRouter()

@router.get("/sentiment/{symbol}")
def get_sentiment(symbol: str):
    """Get current sentiment for a cryptocurrency."""
    news = news_collector.fetch_recent_news(symbol)
    sentiment = sentiment_analyzer.analyze_sentiment(news)
    return {"symbol": symbol, "sentiment": sentiment}

@router.get("/market/{symbol}")
def get_market_data(symbol: str):
    """Get current market data for a cryptocurrency."""
    data = market_data.fetch_price_data(symbol)
    return {"symbol": symbol, "market_data": data}

@router.get("/news/{symbol}")
def get_news_data(symbol: str):
    """Get recent news for a cryptocurrency along with sentiment scores."""
    news = news_collector.fetch_recent_news(symbol)
    
    # This call mutates the news dataframe, adding sentiment_score and sentiment_label
    sentiment_summary = sentiment_analyzer.analyze_sentiment(news)
    
    news = news.fillna("")
    news_records = news.to_dict(orient="records") if not news.empty else []
    
    return {
        "symbol": symbol, 
        "news": news_records, 
        "overall_sentiment": sentiment_summary
    }

@router.get("/predict/{symbol}")
def get_prediction(symbol: str):
    """Get prediction for a cryptocurrency."""
    news = news_collector.fetch_recent_news(symbol)
    sentiment = sentiment_analyzer.analyze_sentiment(news)
    market = market_data.fetch_price_data(symbol)
    prediction = predictor.predict_trend(sentiment, market)
    
    return {
        "symbol": symbol,
        "sentiment": sentiment,
        "market_data": market,
        "prediction": prediction
    }
