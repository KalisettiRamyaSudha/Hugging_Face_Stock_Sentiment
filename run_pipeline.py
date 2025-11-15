"""
Main pipeline with Hugging Face integration
"""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config import config
from src.data_collection.stock_collector import StockCollector
from src.sentiment.sentiment_factor import create_sentiment_analyzer
from src.models.feature_engineer import FeatureEngineer
from src.models.predictor import StockPredictor

# NEW imports for Hugging Face
from src.data_collection.hf_data_loader import HuggingFaceDataLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run complete pipeline with Hugging Face"""
    print("="*70)
    print("🚀 STOCK MARKET PREDICTOR - HUGGING FACE PIPELINE")
    print("="*70)
    print(f"\n📦 Configuration:")
    print(f"  - Using HF Dataset: {config.USE_HF_DATASET}")
    print(f"  - Dataset: {config.HF_DATASET_NAME}")
    print(f"  - Using HF Sentiment: {config.USE_HF_SENTIMENT}")
    print(f"  - Sentiment Model: {config.HF_SENTIMENT_MODEL}")
    print(f"  - Max Samples: {config.MAX_SAMPLES}")
    
    try:
        # Step 1: Load Data from Hugging Face
        print("\n" + "="*70)
        print("STEP 1: LOADING DATA FROM HUGGING FACE")
        print("="*70)
        
        hf_loader = HuggingFaceDataLoader()
        
        # Load financial text dataset from HF
        financial_df = hf_loader.load_financial_dataset()
        
        if financial_df.empty:
            logger.error("Failed to load financial dataset")
            return
        
        # Load stock data (still using yfinance for real market data)
        stock_collector = StockCollector()
        stock_df = stock_collector.collect_stock_data(period="60d")
        
        if stock_df.empty:
            logger.error("Failed to load stock data")
            return
        
        stock_collector.save(stock_df)
        
        # Combine datasets
        combined_df = hf_loader.create_stock_news_dataset(
            financial_df, 
            stock_df,
            max_samples=config.MAX_SAMPLES
        )
        
        if combined_df.empty:
            logger.error("Failed to create combined dataset")
            return
        
        # Save as CSV for inspection
        combined_path = config.PROCESSED_DATA_DIR / "combined_dataset.csv"
        combined_df.to_csv(combined_path, index=False)
        
        # Optional: Save as HF dataset
        dataset_dict = hf_loader.save_as_hf_dataset(combined_df)
        
        logger.info(f"✅ Data preparation complete: {len(combined_df)} records")
        
        # Step 2: Sentiment Analysis
        print("\n" + "="*70)
        print("STEP 2: SENTIMENT ANALYSIS")
        print("="*70)
        
        # Create appropriate sentiment analyzer
        sentiment_analyzer = create_sentiment_analyzer()
        
        # Analyze sentiment
        combined_df = sentiment_analyzer.analyze_dataframe(
            combined_df, 
            text_column='news_text'
        )
        
        # Save with sentiment
        sentiment_path = config.PROCESSED_DATA_DIR / "sentiment_data.csv"
        combined_df.to_csv(sentiment_path, index=False)
        logger.info(f"✅ Sentiment analysis complete")
        
        # Step 3: Feature Engineering
        print("\n" + "="*70)
        print("STEP 3: FEATURE ENGINEERING")
        print("="*70)
        
        feature_engineer = FeatureEngineer()
        combined_df = feature_engineer.create_features(combined_df)
        X, y = feature_engineer.prepare_for_training(combined_df)
        
        X_train, X_test, y_train, y_test = feature_engineer.train_test_split(X, y)
        feature_engineer.save_artifacts()
        
        logger.info(f"✅ Feature engineering complete")
        
        # Step 4: Model Training
        print("\n" + "="*70)
        print("STEP 4: MODEL TRAINING")
        print("="*70)
        
        predictor = StockPredictor()
        predictor.train(X_train, y_train, X_test, y_test)
        predictor.save_model()
        
        logger.info(f"✅ Model training complete")
        
        # Summary
        print("\n" + "="*70)
        print("✅ HUGGING FACE PIPELINE COMPLETE!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"  - HF Dataset: {config.HF_DATASET_NAME}")
        print(f"  - Sentiment Model: {config.HF_SENTIMENT_MODEL}")
        print(f"  - Total records: {len(combined_df)}")
        print(f"  - Training samples: {len(X_train)}")
        print(f"  - Test samples: {len(X_test)}")
        print(f"  - Features: {len(feature_engineer.feature_columns)}")
        print(f"\n💾 Saved:")
        print(f"  - Model: {config.MODELS_DIR / 'stock_predictor.pkl'}")
        print(f"  - Preprocessing: {config.MODELS_DIR / 'preprocessing.pkl'}")
        print(f"  - Data: {sentiment_path}")
        print(f"  - HF Dataset: {config.PROCESSED_DATA_DIR / 'custom_stock_dataset'}")
        print(f"\n🚀 Next steps:")
        print(f"  1. Start API: python run_api.py")
        print(f"  2. Start Dashboard: python run_dashboard.py")
        print(f"  3. Open browser: http://localhost:8080")
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()