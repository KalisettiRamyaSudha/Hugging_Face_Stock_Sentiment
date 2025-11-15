"""
News data collection from multiple sources
"""
import pandas as pd
import logging
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import finnhub
import time
from config import config

logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self):
        if config.NEWS_API_KEY:
            self.newsapi = NewsApiClient(api_key=config.NEWS_API_KEY)
        else:
            self.newsapi = None
            logger.warning("NewsAPI key not found")
        
        if config.FINNHUB_API_KEY:
            self.finnhub = finnhub.Client(api_key=config.FINNHUB_API_KEY)
        else:
            self.finnhub = None
            logger.warning("Finnhub key not found")
    
    def collect_news(self, symbols=None, days_back=30):
        """Collect news for specified symbols"""
        if symbols is None:
            symbols = config.STOCK_SYMBOLS
        
        logger.info(f"Collecting news for {len(symbols)} symbols, {days_back} days back")
        
        all_articles = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        for symbol in symbols:
            if symbol in config.COMPANY_MAPPINGS:
                # Use company keywords
                keywords = config.COMPANY_MAPPINGS[symbol]
                
                for keyword in keywords[:2]:  # Limit keywords to avoid rate limits
                    articles = self._fetch_newsapi(keyword, start_date, end_date)
                    
                    for article in articles:
                        article['symbol'] = symbol
                        article['keyword'] = keyword
                    
                    all_articles.extend(articles)
                    time.sleep(1)  # Rate limiting
        
        df = pd.DataFrame(all_articles)
        
        if not df.empty:
            df['published_at'] = pd.to_datetime(df['published_at'])
            df = df.drop_duplicates(subset=['title', 'symbol'])
            df = df.sort_values('published_at', ascending=False)
        
        logger.info(f"Collected {len(df)} articles")
        return df
    
    def _fetch_newsapi(self, query, from_date, to_date):
        """Fetch from NewsAPI"""
        if not self.newsapi:
            return []
        
        try:
            result = self.newsapi.get_everything(
                q=query,
                from_param=from_date.strftime('%Y-%m-%d'),
                to=to_date.strftime('%Y-%m-%d'),
                language='en',
                sort_by='relevancy',
                page_size=20
            )
            
            if result['status'] == 'ok':
                articles = []
                for article in result['articles']:
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'published_at': article.get('publishedAt', '')
                    })
                return articles
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
        
        return []
    
    def save(self, df, filename=None):
        """Save news data"""
        if filename is None:
            filename = f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = config.RAW_DATA_DIR / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved news data to {filepath}")
        return filepath