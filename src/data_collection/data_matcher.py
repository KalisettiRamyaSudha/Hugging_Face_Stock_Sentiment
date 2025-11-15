"""
Match news articles with stock data
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)

class DataMatcher:
    def match(self, news_df, stock_df):
        """Match news to stock data by date and symbol"""
        logger.info("Matching news to stock data...")
        
        if news_df.empty or stock_df.empty:
            logger.warning("Empty dataframes provided")
            return pd.DataFrame()
        
        # Prepare dates
        news_df['published_at'] = pd.to_datetime(news_df['published_at'])
        stock_df['date'] = pd.to_datetime(stock_df['date'])
        
        news_df['news_date'] = news_df['published_at'].dt.date
        stock_df['stock_date'] = stock_df['date'].dt.date
        
        matched_data = []
        
        for symbol in news_df['symbol'].unique():
            symbol_news = news_df[news_df['symbol'] == symbol]
            symbol_stock = stock_df[stock_df['symbol'] == symbol]
            
            if symbol_stock.empty:
                continue
            
            for _, news_row in symbol_news.iterrows():
                # Find matching stock day
                same_day = symbol_stock[symbol_stock['stock_date'] == news_row['news_date']]
                
                if not same_day.empty:
                    stock_row = same_day.iloc[0]
                else:
                    # Find closest trading day
                    stock_dates = symbol_stock['stock_date'].tolist()
                    if not stock_dates:
                        continue
                    
                    closest_date = min(stock_dates, 
                                     key=lambda x: abs((x - news_row['news_date']).days))
                    stock_row = symbol_stock[symbol_stock['stock_date'] == closest_date].iloc[0]
                
                # Create matched record
                matched_data.append({
                    'symbol': symbol,
                    'news_title': news_row['title'],
                    'news_description': news_row.get('description', ''),
                    'news_source': news_row.get('source', ''),
                    'news_date': news_row['news_date'],
                    'stock_date': stock_row['stock_date'],
                    'open_price': stock_row['Open'],
                    'close_price': stock_row['Close'],
                    'high_price': stock_row['High'],
                    'low_price': stock_row['Low'],
                    'volume': stock_row['Volume'],
                    'price_change_pct': stock_row.get('price_change_pct', 0),
                    'high_low_pct': stock_row.get('high_low_pct', 0),
                    'rsi': stock_row.get('rsi', 50),
                    'price_direction': stock_row.get('price_direction', 0)
                })
        
        df = pd.DataFrame(matched_data)
        logger.info(f"Created {len(df)} matched records")
        return df
    
    def save(self, df, filename=None):
        """Save matched data"""
        if filename is None:
            filename = f"matched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = config.PROCESSED_DATA_DIR / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved matched data to {filepath}")
        return filepath