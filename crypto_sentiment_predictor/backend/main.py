from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI(
    title="Crypto Sentiment Predictor API",
    description="API for cryptocurrency sentiment analysis and price prediction.",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Crypto Sentiment Predictor API"}
