"""
Factory to create appropriate sentiment analyzer based on config
"""
import logging
from config import config

logger = logging.getLogger(__name__)

def create_sentiment_analyzer():
    """
    Create sentiment analyzer based on configuration
    
    Returns appropriate analyzer (HuggingFace or VADER)
    """
    if config.USE_HF_SENTIMENT:
        logger.info("Creating Hugging Face sentiment analyzer...")
        from src.sentiment.hf_sentiment_analyzer import HuggingFaceSentimentAnalyzer
        return HuggingFaceSentimentAnalyzer()
    else:
        logger.info("Creating VADER sentiment analyzer...")
        from src.sentiment.vader_analyzer import VADERSentimentAnalyzer
        return VADERSentimentAnalyzer()