import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000/api/v1"

@st.cache_data(ttl=60, show_spinner=False)
def get_sentiment(symbol: str) -> dict:
    response = requests.get(f"{API_BASE_URL}/sentiment/{symbol}")
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data(ttl=60, show_spinner=False)
def get_market_data(symbol: str) -> dict:
    response = requests.get(f"{API_BASE_URL}/market/{symbol}")
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data(ttl=60, show_spinner=False)
def get_prediction(symbol: str) -> dict:
    response = requests.get(f"{API_BASE_URL}/predict/{symbol}")
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data(ttl=60, show_spinner=False)
def get_news(symbol: str) -> dict:
    response = requests.get(f"{API_BASE_URL}/news/{symbol}")
    if response.status_code == 200:
        return response.json()
    return None
