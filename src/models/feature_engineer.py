"""
Feature engineering for model training
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from config import config

logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_columns = None
    
    def create_features(self, df):
        """Engineer features from matched data"""
        logger.info("Engineering features...")
        
        df = df.copy()
        df = df.sort_values(['symbol', 'stock_date'])
        
        # Lag features
        for lag in [1, 3]:
            df[f'sentiment_lag_{lag}'] = df.groupby('symbol')['sentiment_compound'].shift(lag)
            df[f'price_change_lag_{lag}'] = df.groupby('symbol')['price_change_pct'].shift(lag)
        
        # Rolling features
        df['sentiment_rolling_mean_3'] = df.groupby('symbol')['sentiment_compound'].transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
        
        # Interaction features
        df['sentiment_volume_interaction'] = df['sentiment_compound'] * np.log1p(df['volume'])
        
        # Fill NaN
        df = df.fillna(method='bfill').fillna(0)
        
        logger.info(f"Created features: {df.shape[1]} columns")
        return df
    
    def prepare_for_training(self, df):
        """Prepare features and target"""
        logger.info("Preparing for training...")
        
        self.feature_columns = [
            'sentiment_compound', 'sentiment_score',
            'sentiment_lag_1', 'sentiment_lag_3',
            'sentiment_rolling_mean_3',
            'price_change_pct', 'price_change_lag_1', 'price_change_lag_3',
            'high_low_pct', 'volume', 'rsi',
            'sentiment_volume_interaction'
        ]
        
        # Filter available columns
        available = [col for col in self.feature_columns if col in df.columns]
        
        X = df[available].fillna(0)
        y = df['price_direction'].fillna(0)
        
        # Remove NaN in target
        mask = ~y.isna()
        X = X[mask]
        y = y[mask]
        
        logger.info(f"Features: {X.shape}, Target distribution: {y.value_counts().to_dict()}")
        
        # Scale
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=available, index=X.index)
        
        self.feature_columns = available
        
        return X_scaled, y
    
    def train_test_split(self, X, y):
        """Time-aware split"""
        split_idx = int(len(X) * config.TRAIN_TEST_SPLIT)
        
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
        
        return X_train, X_test, y_train, y_test
    
    def save_artifacts(self):
        """Save preprocessing artifacts"""
        filepath = config.MODELS_DIR / "preprocessing.pkl"
        joblib.dump({
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, filepath)
        logger.info(f"Saved preprocessing artifacts to {filepath}")
    
    def load_artifacts(self):
        """Load preprocessing artifacts"""
        filepath = config.MODELS_DIR / "preprocessing.pkl"
        artifacts = joblib.load(filepath)
        self.scaler = artifacts['scaler']
        self.feature_columns = artifacts['feature_columns']
        logger.info("Loaded preprocessing artifacts")