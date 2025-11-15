"""
Load and prepare data from Hugging Face datasets
"""
from datasets import load_dataset, Dataset
import pandas as pd
import logging
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)

class HuggingFaceDataLoader:
    """
    Load financial datasets from Hugging Face Hub
    """
    
    def __init__(self):
        self.cache_dir = str(config.HF_CACHE_DIR)
    
    def load_financial_dataset(self, dataset_name=None, config_name=None):
        """
        Load financial dataset from Hugging Face
        
        Args:
            dataset_name: HF dataset name (default from config)
            config_name: Dataset configuration (default from config)
        """
        if dataset_name is None:
            dataset_name = config.HF_DATASET_NAME
        if config_name is None:
            config_name = config.HF_DATASET_CONFIG
        
        logger.info(f"📚 Loading {dataset_name} from Hugging Face...")
        
        try:
            # Load dataset with or without config
            if config_name:
                dataset = load_dataset(
                    dataset_name, 
                    config_name,
                    cache_dir=self.cache_dir,
                    trust_remote_code=False
                )
            else:
                dataset = load_dataset(
                    dataset_name,
                    cache_dir=self.cache_dir,
                    trust_remote_code=False
                )
            
            # Get the first split available (could be 'train', 'validation', etc.)
            split_name = list(dataset.keys())[0] if isinstance(dataset, dict) else 'train'
            
            # Convert to pandas
            df = pd.DataFrame(dataset[split_name])
            
            # Limit to avoid memory issues
            if len(df) > config.MAX_SAMPLES * 2:
                df = df.sample(n=config.MAX_SAMPLES * 2, random_state=config.RANDOM_STATE)
            
            # Standardize format based on dataset
            df = self._standardize_format(df, dataset_name)
            
            logger.info(f"✅ Loaded {len(df)} samples")
            logger.info(f"Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error loading dataset: {e}")
            logger.info("💡 Using fallback: Creating synthetic financial dataset...")
            return self._create_fallback_dataset()
    
    def _standardize_format(self, df, dataset_name):
        """
        Standardize different HF datasets to common format
        """
        if 'twitter-financial' in dataset_name:
            # twitter-financial-news-sentiment format
            if 'text' in df.columns:
                df['text'] = df['text']
            elif 'sentence' in df.columns:
                df['text'] = df['sentence']
            else:
                # Use first text-like column
                text_cols = [c for c in df.columns if 'text' in c.lower() or 'sentence' in c.lower()]
                if text_cols:
                    df['text'] = df[text_cols[0]]
            
            # Map sentiment labels
            if 'label' in df.columns:
                # Handle both numeric and string labels
                if df['label'].dtype == 'object':
                    df['sentiment'] = df['label'].str.lower()
                else:
                    label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
                    df['sentiment'] = df['label'].map(label_map)
            elif 'sentiment' not in df.columns:
                df['sentiment'] = 'neutral'  # default
                
        elif 'financial_phrasebank' in dataset_name:
            # Map labels: 0=negative, 1=neutral, 2=positive
            label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
            df['sentiment'] = df['label'].map(label_map)
            df['text'] = df['sentence']
            
        elif 'stocknet' in dataset_name:
            # Adapt based on stocknet structure
            pass
        
        # Ensure required columns exist
        if 'text' not in df.columns:
            logger.warning("'text' column not found, using first string column")
            string_cols = df.select_dtypes(include=['object']).columns
            if len(string_cols) > 0:
                df['text'] = df[string_cols[0]]
        
        if 'sentiment' not in df.columns:
            logger.warning("'sentiment' column not found, defaulting to 'neutral'")
            df['sentiment'] = 'neutral'
        
        return df
    
    def create_stock_news_dataset(self, financial_df, stock_df, max_samples=None):
        """
        Create combined dataset by matching financial texts with stock data
        
        This simulates having news articles for each stock trading day
        """
        logger.info("🔗 Creating combined news-stock dataset...")
        
        if max_samples is None:
            max_samples = config.MAX_SAMPLES
        
        combined_data = []
        
        import numpy as np
        np.random.seed(config.RANDOM_STATE)
        
        # Ensure date column is in datetime format
        stock_df = stock_df.copy()
        if 'date' in stock_df.columns:
            stock_df['date'] = pd.to_datetime(stock_df['date'])
        
        # For each stock record, assign random financial sentences
        for _, stock_row in stock_df.iterrows():
            # Sample 1-3 sentences per trading day
            num_sentences = min(np.random.randint(1, 4), len(financial_df))
            sample_texts = financial_df.sample(n=num_sentences)
            
            for _, text_row in sample_texts.iterrows():
                # Extract date and convert to date object for matching
                stock_date = stock_row['date']
                if hasattr(stock_date, 'date'):  # if it's a datetime
                    stock_date = stock_date.date()
                
                combined_data.append({
                    'symbol': stock_row['symbol'],
                    'date': stock_row['date'],
                    'stock_date': stock_date,
                    'news_text': text_row.get('text', text_row.get('sentence', '')),
                    'news_sentiment': text_row.get('sentiment', 'neutral'),
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
                
                if len(combined_data) >= max_samples:
                    break
            
            if len(combined_data) >= max_samples:
                break
        
        df = pd.DataFrame(combined_data)
        logger.info(f"✅ Created {len(df)} combined records")
        
        return df
    
    def save_as_hf_dataset(self, df, dataset_name="custom_stock_dataset"):
        """
        Convert pandas DataFrame to Hugging Face Dataset and save
        """
        dataset = Dataset.from_pandas(df)
        
        # Split into train/test
        dataset_dict = dataset.train_test_split(test_size=0.2, seed=config.RANDOM_STATE)
        
        # Save to disk
        save_path = config.PROCESSED_DATA_DIR / dataset_name
        dataset_dict.save_to_disk(str(save_path))
        
        logger.info(f"💾 Saved HF dataset to {save_path}")
        
        return dataset_dict
    
    def load_local_hf_dataset(self, dataset_name="custom_stock_dataset"):
        """
        Load previously saved Hugging Face dataset
        """
        load_path = config.PROCESSED_DATA_DIR / dataset_name
        
        if not load_path.exists():
            logger.warning(f"Dataset not found at {load_path}")
            return None
        
        from datasets import load_from_disk
        dataset_dict = load_from_disk(str(load_path))
        
        logger.info(f"📂 Loaded HF dataset from {load_path}")
        return dataset_dict
    
    def _create_fallback_dataset(self):
        """
        Create a synthetic financial sentiment dataset as fallback
        """
        logger.info("🔧 Creating fallback dataset with financial sentiment samples...")
        
        financial_texts = [
            "Stock prices are rising due to strong earnings reports.",
            "The company reported a significant drop in revenue this quarter.",
            "Market volatility continues to affect investor confidence.",
            "Positive momentum in tech stocks continues.",
            "Concerns about inflation impact market outlook.",
            "Strong earnings beat expectations by 15%.",
            "Analysts downgrade stock due to competitive pressure.",
            "The company announced a successful product launch.",
            "Market uncertainty leads to cautious trading.",
            "Growth prospects remain stable for the year ahead.",
            "Bankruptcy fears impact trading activity.",
            "Merger announcement sparks investor interest.",
            "Technical analysis suggests bullish trend.",
            "Economic data disappoints market expectations.",
            "Company expands into new markets successfully.",
            "Regulatory concerns weigh on stock price.",
            "Record quarterly profit announced today.",
            "Dividend increase signals confidence.",
            "Supply chain disruptions impact operations.",
            "Innovation pipeline looks promising.",
        ]
        
        sentiments = ['positive', 'negative', 'neutral']
        
        # Extend to create more samples
        import itertools
        extended_texts = list(itertools.islice(itertools.cycle(financial_texts), config.MAX_SAMPLES * 2))
        extended_sentiments = [sentiments[i % len(sentiments)] for i in range(len(extended_texts))]
        
        df = pd.DataFrame({
            'text': extended_texts,
            'sentiment': extended_sentiments
        })
        
        logger.info(f"✅ Created fallback dataset with {len(df)} samples")
        return df