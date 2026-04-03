import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from services import market_data

# Global model instance
model = None

def train_model():
    """
    Trains a Logistic Regression model using synthetic data.
    Features: [sentiment_score, price_trend_percent]
    Target: 1 (UP) or 0 (DOWN)
    """
    global model
    print("Training Logistic Regression model...")
    
    np.random.seed(42)
    # Synthetic feature 1: Average sentiment score (-1.0 to 1.0)
    X_sentiment = np.random.uniform(-1.0, 1.0, 1000)
    
    # Synthetic feature 2: Price trend percentage (-10% to 10%)
    X_trend = np.random.uniform(-10.0, 10.0, 1000)
    
    X = np.column_stack((X_sentiment, X_trend))
    
    # Rule for training data:
    # A positive sentiment and a positive trend highly correlate with "UP".
    # We weight sentiment and trend (equally influential for the domain mapping).
    score = (X_sentiment * 10) + X_trend
    y = (score > 0).astype(int)
    
    model = LogisticRegression()
    model.fit(X, y)
    print("Logistic Regression model training complete.")

# Train the model once when the module loads
train_model()


def predict_trend(sentiment_dict: dict, market_dict: dict) -> dict:
    """
    Predict trend based on sentiment and market data using trained model.
    """
    global model
    if model is None:
        train_model()
        
    print("Predicting trend using Logistic Regression...")
    
    symbol = market_dict.get("symbol", "BTC")
    
    # 1. Feature: Average sentiment score
    sentiment_score = sentiment_dict.get("score", 0.0)
    
    # 2. Feature: Price trend
    # Fetch recent closing prices (last 5-10 data points)
    df = market_data.fetch_historical_dataframe(symbol)
    
    if df is not None and not df.empty and len(df) >= 5:
        # Get up to 10 recent points
        recent_closes = df["close"].tail(10).values
        first_close = recent_closes[0]
        last_close = recent_closes[-1]
        
        # Calculate percent trend (difference between last and first) normalized
        price_trend = ((last_close - first_close) / first_close) * 100
    else:
        # Fallback to general 24h market change
        price_trend = market_dict.get("price_change_24h_percent", 0.0)
        
    # Format input for sklearn
    X_input = np.array([[sentiment_score, price_trend]])
    
    # Get probability and prediction
    prob_up = model.predict_proba(X_input)[0][1]
    prediction_class = model.predict(X_input)[0]
    
    prediction = "UP" if prediction_class == 1 else "DOWN"
    confidence = prob_up * 100 if prediction == "UP" else (1 - prob_up) * 100
    
    return {
        "prediction": prediction,
        "confidence_percent": round(float(confidence), 2),
        "timeframe": "Next 24 Hours",
        "features_used": {
            "sentiment_score": round(float(sentiment_score), 2),
            "price_trend_percent": round(float(price_trend), 2)
        }
    }
