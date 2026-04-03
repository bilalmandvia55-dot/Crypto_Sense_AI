import yfinance as yf
import pandas as pd

def fetch_historical_dataframe(symbol: str) -> pd.DataFrame:
    """
    Fetch real-time and historical price data for the given cryptocurrency.
    Returns a pandas DataFrame with columns: (timestamp, open, high, low, close, volume).
    """
    # Map common crypto symbols to Yahoo Finance ticker equivalents
    ticker_map = {
        "BTC": "BTC-USD",
        "ETH": "ETH-USD",
        "SOL": "SOL-USD",
        "ADA": "ADA-USD",
        "DOGE": "DOGE-USD"
    }
    
    ticker_symbol = ticker_map.get(symbol.upper(), f"{symbol.upper()}-USD")
    print(f"Fetching real market data for {symbol} ({ticker_symbol})...")
    
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="1mo")
    
    if df.empty:
        print(f"Warning: No data found for {ticker_symbol}")
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
        
    df = df.reset_index()
    
    # Standardize column naming format based on requirements
    rename_mapping = {
        "Date": "timestamp",
        "Datetime": "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    }
    df.rename(columns=rename_mapping, inplace=True)
    
    # Select requested columns
    cols = ["timestamp", "open", "high", "low", "close", "volume"]
    df = df[[c for c in cols if c in df.columns]]
    
    return df

def calculate_recent_trend(df: pd.DataFrame, periods: int = 5) -> str:
    """
    Calculate the recent price trend based on the latest N data points.
    Returns 'UP', 'DOWN', or 'FLAT'.
    """
    if df is None or len(df) < periods:
        return "FLAT"
        
    recent_closes = df['close'].tail(periods).values
    start_price = recent_closes[0]
    end_price = recent_closes[-1]
    
    if end_price > start_price * 1.01:  # More than 1% increase
        return "UP"
    elif end_price < start_price * 0.99:  # More than 1% decrease
        return "DOWN"
    else:
        return "FLAT"

def fetch_price_data(symbol: str) -> dict:
    """
    Main compatibility entrypoint for existing backend structure.
    Fetches real dataframe, computes required metrics, and returns the expected dictionary.
    """
    df = fetch_historical_dataframe(symbol)
    
    if df.empty:
        return {
            "symbol": symbol,
            "current_price_usd": 0.0,
            "volume_24h": 0.0,
            "price_change_24h_percent": 0.0,
            "recent_trend": "FLAT"
        }
        
    current_price = float(df['close'].iloc[-1])
    volume_24h = float(df['volume'].iloc[-1])
    
    # Price change compared to previous interval
    if len(df) >= 2:
        prev_price = float(df['close'].iloc[-2])
        price_change_24h = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0.0
    else:
        price_change_24h = 0.0
        
    recent_trend = calculate_recent_trend(df, periods=5)
    
    # Safely convert timestamp to string to prevent JSON serialization errors
    df_chart = df[['timestamp', 'close']].copy()
    if pd.api.types.is_datetime64_any_dtype(df_chart['timestamp']):
        df_chart['timestamp'] = df_chart['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        df_chart['timestamp'] = df_chart['timestamp'].astype(str)
        
    historical_data = df_chart.to_dict('records')
    
    return {
        "symbol": symbol,
        "current_price_usd": round(current_price, 2),
        "volume_24h": round(volume_24h, 2),
        "price_change_24h_percent": round(price_change_24h, 2),
        "recent_trend": recent_trend,
        "historical_data": historical_data
    }
