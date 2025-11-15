"""
Fast sentiment analysis using VADER
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class VADERSentimentAnalyzer:
    def __init__(self):
        logger.info("Loading VADER sentiment analyzer")
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text):
        """Analyze single text"""
        if not text or pd.isna(text):
            return {'label': 'neutral', 'score': 0.0, 'compound': 0.0}
        
        scores = self.analyzer.polarity_scores(str(text))
        compound = scores['compound']
        
        if compound >= 0.05:
            label = 'positive'
        elif compound <= -0.05:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'label': label,
            'score': abs(compound),
            'compound': compound
        }
    
    def analyze_dataframe(self, df, text_column='news_title'):
        """Add sentiment to dataframe"""
        logger.info(f"Analyzing sentiment for {len(df)} records")
        
        sentiments = df[text_column].apply(self.analyze)
        
        df['sentiment_label'] = sentiments.apply(lambda x: x['label'])
        df['sentiment_score'] = sentiments.apply(lambda x: x['score'])
        df['sentiment_compound'] = sentiments.apply(lambda x: x['compound'])
        
        logger.info(f"Sentiment distribution: {df['sentiment_label'].value_counts().to_dict()}")
        return df