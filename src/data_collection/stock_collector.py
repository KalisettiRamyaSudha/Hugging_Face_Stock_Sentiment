"""
Stock data collection using yfinance
"""
import yfinance as yf
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)

class StockCollector:
    def __init__(self):
        self.cache = {}
    
    def collect_stock_data(self, symbols=None, period="30d"):
        """Collect stock data for symbols"""
        if symbols is None:
            symbols = config.STOCK_SYMBOLS
        
        logger.info(f"Collecting stock data for {len(symbols)} symbols")
        
        all_data = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                if not hist.empty:
                    hist['symbol'] = symbol
                    hist['date'] = hist.index
                    
                    # Calculate indicators
                    hist['price_change_pct'] = hist['Close'].pct_change() * 100
                    hist['high_low_pct'] = ((hist['High'] - hist['Low']) / hist['Low']) * 100
                    hist['volume_ma_5'] = hist['Volume'].rolling(window=5).mean()
                    
                    # RSI
                    hist['rsi'] = self._calculate_rsi(hist['Close'])
                    
                    # Price direction
                    hist['price_direction'] = hist['price_change_pct'].apply(
                        lambda x: 1 if x > 0 else -1 if x < 0 else 0
                    )
                    
                    all_data.append(hist.reset_index(drop=True))
                    logger.info(f"✅ {symbol}: {len(hist)} records")
            
            except Exception as e:
                logger.error(f"❌ {symbol}: {e}")
        
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            logger.info(f"Total stock records: {len(df)}")
            return df
        
        return pd.DataFrame()
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def save(self, df, filename=None):
        """Save stock data"""
        if filename is None:
            filename = f"stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = config.RAW_DATA_DIR / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved stock data to {filepath}")
        return filepath