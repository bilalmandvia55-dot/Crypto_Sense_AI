import streamlit as st
import pandas as pd
from utils import api_client

st.set_page_config(page_title="Crypto Analytics Dashboard", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for compact spacing ---
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1, h2, h3 { margin-top: 0.5rem; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# --- 1. HEADER ---
st.title("🚀 Crypto News Sentiment & Trend Predictor")
st.markdown("*Analyze live sentiment & predict short-term price trends for top cryptocurrencies.*")

# Sidebar
st.sidebar.header("⚙️ Configuration")
symbol = st.sidebar.selectbox("Select Cryptocurrency", ["BTC", "ETH", "SOL", "ADA", "DOGE"])
st.sidebar.markdown("---")
st.sidebar.info("System is actively pulling Live News and Market data.")

with st.spinner(f"Fetching latest data..."):
    # API calls strictly leveraged via fast caching
    prediction_data = api_client.get_prediction(symbol)
    news_data = api_client.get_news(symbol)
    
    if prediction_data and news_data:
        sentiment = prediction_data["sentiment"]
        market = prediction_data["market_data"]
        prediction = prediction_data["prediction"]
        
        # Formattings
        is_up = prediction['prediction'] == "UP"
        pred_icon = "📈" if is_up else "📉"
        pred_color = ":green" if is_up else ":red"
        pred_text = f"{pred_color}[{pred_icon} {prediction['prediction']}]"
        
        is_pos = sentiment["label"] == "Positive"
        is_neg = sentiment["label"] == "Negative"
        if is_pos:
            sent_text = ":green[🟢 Positive 📈]"
        elif is_neg:
            sent_text = ":red[🔴 Negative 📉]"
        else:
            sent_text = "Neutral ➖"
        
        st.divider()
        
        # --- 2. KEY METRICS ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="🏷️ Current Price", 
                value=f"${market['current_price_usd']:,.2f}", 
                delta=f"{market['price_change_24h_percent']}%"
            )
        with col2:
            st.markdown(f"**🧠 Sentiment**<br><h3 style='margin:0;'>{sent_text}</h3><span style='color:gray;'>Score: {sentiment['score']}</span>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"**🔮 24Hr Prediction**<br><h3 style='margin:0;'>{pred_text}</h3><span style='color:gray;'>Confidence: {prediction['confidence_percent']}%</span>", unsafe_allow_html=True)
            
        st.divider()
        
        # --- 3. CHARTS AND CONFIDENCE ---
        chart_col, conf_col = st.columns([2, 1], gap="large")
        
        with chart_col:
            st.subheader(f"📊 {symbol} Price Trend")
            if "historical_data" in market and market["historical_data"]:
                df_hist = pd.DataFrame(market["historical_data"])
                if not df_hist.empty and "timestamp" in df_hist.columns and "close" in df_hist.columns:
                    df_hist['timestamp'] = pd.to_datetime(df_hist['timestamp'])
                    df_hist.set_index('timestamp', inplace=True)
                    st.line_chart(df_hist[['close']], height=250)
            else:
                st.info("Historical data not available.")
        
        with conf_col:
            st.subheader("🎯 Prediction Confidence")
            st.write(f"Model predicts price will go **{pred_text}** within {prediction['timeframe']}.")
            st.progress(float(prediction["confidence_percent"]) / 100.0)
            st.caption(f"**{prediction['confidence_percent']}%** Certainty")
            
            st.markdown("#### Market Context")
            st.write(f"**24h Volume:** ${market['volume_24h']:,.0f}")
            
            trend = market.get('recent_trend', 'FLAT')
            t_icon = "📈" if trend == "UP" else ("📉" if trend == "DOWN" else "➖")
            t_color = ":green" if trend == "UP" else (":red" if trend == "DOWN" else "")
            st.write(f"**Recent Base Trend:** {t_color}[{t_icon} {trend}]")

        st.divider()
        
        # --- 4. SENTIMENT & NEWS ---
        sent_col, news_col = st.columns([1, 2], gap="large")
        df_news = pd.DataFrame(news_data.get("news", []))
        
        with sent_col:
            st.subheader("🌐 Sentiment")
            st.write(f"**Articles Analyzed:** {sentiment['articles_analyzed']}")
            
            if not df_news.empty and "sentiment_label" in df_news.columns:
                counts = df_news["sentiment_label"].value_counts()
                st.bar_chart(counts, height=200)
            else:
                st.caption("Distribution data unavailable.")
                
        with news_col:
            st.subheader("📰 Latest Headlines")
            if not df_news.empty:
                if 'title' in df_news.columns and 'sentiment_score' in df_news.columns:
                    display_cols = ["title", "source", "sentiment_score", "sentiment_label"]
                    display_cols = [c for c in display_cols if c in df_news.columns]
                    st.dataframe(df_news[display_cols], height=250, use_container_width=True)
                else:
                    st.dataframe(df_news, height=250, use_container_width=True)
            else:
                st.info("No recent news headlines found.")
            
        # Optional Debug display
        with st.expander("Debug: Raw API Response"):
            st.json(news_data)
            
    else:
        st.error("Failed to connect to the backend API or data is missing.")
