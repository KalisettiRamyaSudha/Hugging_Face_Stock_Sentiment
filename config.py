"""
Central configuration for Stock Market Predictor
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Base directories
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    CACHE_DIR = DATA_DIR / "cache"
    HF_CACHE_DIR = DATA_DIR / "hf_cache"
    MODELS_DIR = BASE_DIR / "models" / "saved_models"
    LOGS_DIR = BASE_DIR / "logs"
    
    # API Keys (optional)
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    HF_TOKEN = os.getenv('HF_TOKEN')
    
    # Stock Configuration
    STOCK_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA']
    
    # Hugging Face Configuration
    USE_HF_DATASET = True
    HF_DATASET_NAME = "zeroshot/twitter-financial-news-sentiment"  # Compatible alternative
    HF_DATASET_CONFIG = None  # This dataset doesn't use configs
    
    USE_HF_SENTIMENT = False  # Start with VADER for speed
    HF_SENTIMENT_MODEL = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    
    SENTIMENT_MODE = 'huggingface' if USE_HF_SENTIMENT else 'vader'
    
    # Model Settings
    USE_CACHE = True
    DEFAULT_DAYS_BACK = 30
    MAX_SAMPLES = 500
    BATCH_SIZE = 16
    
    # API Settings
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DASHBOARD_PORT = 8080
    
    # Model Parameters
    RANDOM_FOREST_ESTIMATORS = 50
    TRAIN_TEST_SPLIT = 0.8
    RANDOM_STATE = 42

config = Config()
