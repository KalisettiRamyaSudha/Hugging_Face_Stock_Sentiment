"""
Sentiment analysis using Hugging Face pre-trained models
"""
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
import logging
from config import config

logger = logging.getLogger(__name__)

class HuggingFaceSentimentAnalyzer:
    """
    Sentiment analysis using Hugging Face transformers
    """
    
    def __init__(self, model_name=None):
        if model_name is None:
            model_name = config.HF_SENTIMENT_MODEL
        
        self.model_name = model_name
        
        logger.info(f"🤖 Loading {model_name} from Hugging Face...")
        logger.info("⏱️  First time: ~1-2 minutes download, then cached")
        
        # Determine device
        device = 0 if torch.cuda.is_available() else -1
        device_name = 'GPU' if device == 0 else 'CPU'
        
        # Load pipeline
        try:
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=device,
                cache_dir=str(config.HF_CACHE_DIR)
            )
            
            logger.info(f"✅ Model loaded on {device_name}")
            
            if device == -1:
                logger.info("💡 Running on CPU - expect ~0.5-1s per text")
            else:
                logger.info("⚡ Running on GPU - expect ~0.05-0.1s per text")
                
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise
    
    def analyze(self, text):
        """
        Analyze sentiment of single text
        
        Returns:
            dict: {'label': str, 'score': float, 'compound': float}
        """
        if not text or pd.isna(text):
            return {'label': 'neutral', 'score': 0.0, 'compound': 0.0}
        
        try:
            # Truncate to model's max length
            text = str(text)[:512]
            
            result = self.pipeline(text)[0]
            
            label = result['label'].lower()
            score = result['score']
            
            # Convert to compound score (-1 to 1)
            if 'positive' in label:
                compound = score
                label = 'positive'
            elif 'negative' in label:
                compound = -score
                label = 'negative'
            else:
                compound = 0.0
                label = 'neutral'
            
            return {
                'label': label,
                'score': score,
                'compound': compound
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {'label': 'neutral', 'score': 0.0, 'compound': 0.0}
    
    def analyze_batch(self, texts, batch_size=None):
        """
        Analyze multiple texts efficiently
        
        Args:
            texts: List of texts
            batch_size: Batch size (default from config)
        """
        if batch_size is None:
            batch_size = config.BATCH_SIZE
        
        results = []
        total = len(texts)
        
        logger.info(f"Processing {total} texts in batches of {batch_size}...")
        
        for i in range(0, total, batch_size):
            batch = texts[i:i+batch_size]
            
            # Truncate texts
            batch = [str(text)[:512] if text and not pd.isna(text) else "" for text in batch]
            
            try:
                batch_results = self.pipeline(batch)
                
                for result in batch_results:
                    label = result['label'].lower()
                    score = result['score']
                    
                    if 'positive' in label:
                        compound = score
                        label = 'positive'
                    elif 'negative' in label:
                        compound = -score
                        label = 'negative'
                    else:
                        compound = 0.0
                        label = 'neutral'
                    
                    results.append({
                        'label': label,
                        'score': score,
                        'compound': compound
                    })
                
                # Progress
                processed = min(i + batch_size, total)
                if processed % 50 == 0 or processed == total:
                    logger.info(f"Progress: {processed}/{total} ({processed/total*100:.1f}%)")
                    
            except Exception as e:
                logger.error(f"Error processing batch {i}: {e}")
                # Add neutral results for failed batch
                results.extend([
                    {'label': 'neutral', 'score': 0.0, 'compound': 0.0}
                    for _ in batch
                ])
        
        return results
    
    def analyze_dataframe(self, df, text_column='news_text'):
        """
        Add sentiment analysis to entire dataframe
        """
        logger.info(f"Analyzing sentiment for {len(df)} records...")
        
        texts = df[text_column].fillna('').tolist()
        results = self.analyze_batch(texts)
        
        # Add to dataframe
        df['sentiment_label'] = [r['label'] for r in results]
        df['sentiment_score'] = [r['score'] for r in results]
        df['sentiment_compound'] = [r['compound'] for r in results]
        
        logger.info(f"✅ Sentiment analysis complete")
        logger.info(f"Distribution: {df['sentiment_label'].value_counts().to_dict()}")
        
        return df
