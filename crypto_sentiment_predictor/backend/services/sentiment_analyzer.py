import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure VADER lexicon is firmly downloaded once natively
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

print("Initializing Lightning Fast VADER Sentiment Engine...")
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(news_df: pd.DataFrame) -> dict:
    """
    Real-time high-velocity sentiment analysis using NLTK VADER.
    Expects a pandas DataFrame containing news headlines in the 'title' column.
    """
    if news_df is None or news_df.empty:
        return {
            "score": 0.0,
            "label": "Neutral",
            "articles_analyzed": 0
        }
        
    print(f"Analyzing sentiment for {len(news_df)} articles using VADER...")
    
    if 'title' not in news_df.columns:
        news_df['title'] = ""
    
    news_titles = news_df['title'].astype(str).tolist()
    
    mapped_scores = []
    confidence_scores = []
    mapped_labels = []
    
    for title in news_titles:
        # Get VADER polarity scores (-1.0 to 1.0 compound)
        scores = sia.polarity_scores(title)
        compound = scores['compound']
        
        # Determine strict Sentiment Label
        if compound >= 0.05:
            label = "Positive"
        elif compound <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"
            
        mapped_labels.append(label)
        
        # Calculate raw probabilities purely for schema stability padding
        # Mapping absolute compound as a "confidence-like" float range output
        confidence_scores.append(round(abs(compound), 4))
        
        # Bipolar mapped score
        mapped_scores.append(compound)
            
    # Add columns seamlessly into dataframe structure
    news_df['sentiment_label'] = mapped_labels
    news_df['confidence_score'] = confidence_scores
    news_df['sentiment_score'] = mapped_scores
    
    # Calculate aggregate dictionary for FastAPI response compatibility
    avg_score = round(news_df['sentiment_score'].mean(), 2)
    
    if avg_score >= 0.05:
        overall_label = "Positive"
    elif avg_score <= -0.05:
        overall_label = "Negative"
    else:
        overall_label = "Neutral"
    
    return {
        "score": avg_score,
        "label": overall_label,
        "articles_analyzed": len(news_df)
    }
