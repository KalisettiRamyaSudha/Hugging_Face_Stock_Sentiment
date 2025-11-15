from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import config
from src.sentiment.vader_analyzer import VADERSentimentAnalyzer
from src.sentiment.sentiment_factor import create_sentiment_analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables for models
sentiment_analyzer = None
predictor_model = None
scaler = None
feature_columns = None

def load_models():
    """Load saved models on startup"""
    global sentiment_analyzer, predictor_model, scaler, feature_columns
    
    logger.info("Loading models...")
    
    # Load sentiment analyzer
    sentiment_analyzer = create_sentiment_analyzer()
    
    # Load predictor and preprocessing
    try:
        model_path = config.MODELS_DIR / "stock_predictor.pkl"
        predictor_model = joblib.load(model_path)
        logger.info("✅ Predictor model loaded")
        
        preprocessing_path = config.MODELS_DIR / "preprocessing.pkl"
        artifacts = joblib.load(preprocessing_path)
        scaler = artifacts['scaler']
        feature_columns = artifacts['feature_columns']
        logger.info("✅ Preprocessing artifacts loaded")
        
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
        logger.warning("⚠️  Run pipeline first to train models!")

# Load models on startup
load_models()

@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        'name': 'Stock Market Predictor API',
        'version': '1.0.0',
        'status': 'online',
        'models_loaded': predictor_model is not None,
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'POST /sentiment': 'Analyze text sentiment',
            'POST /predict': 'Predict stock movement',
            'GET /stats': 'Model statistics'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'sentiment_analyzer': sentiment_analyzer is not None,
        'predictor_model': predictor_model is not None
    })

@app.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    """
    Analyze sentiment of text
    
    Request body:
    {
        "text": "Apple announces record profits!"
    }
    """
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        result = sentiment_analyzer.analyze(text)
        
        return jsonify({
            'text': text,
            'sentiment': result
        })
    
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict_stock():
    """
    Predict stock movement
    
    Request body:
    {
        "symbol": "AAPL",
        "news_text": "Apple announces...",
        "open_price": 150.0,
        "close_price": 152.0,
        "volume": 1000000
    }
    """
    try:
        if predictor_model is None:
            return jsonify({
                'error': 'Model not loaded. Please train the model first.'
            }), 503
        
        data = request.json
        
        # Get sentiment
        news_text = data.get('news_text', '')
        sentiment = sentiment_analyzer.analyze(news_text)
        
        # Calculate price change
        open_price = data.get('open_price', 0)
        close_price = data.get('close_price', 0)
        
        if open_price != 0:
            price_change_pct = ((close_price - open_price) / open_price) * 100
        else:
            price_change_pct = 0
        
        # Prepare features
        features_dict = {
            'sentiment_compound': sentiment['compound'],
            'sentiment_score': sentiment['score'],
            'sentiment_lag_1': 0,  # Default for real-time
            'sentiment_lag_3': 0,
            'sentiment_rolling_mean_3': sentiment['compound'],
            'price_change_pct': price_change_pct,
            'price_change_lag_1': 0,
            'price_change_lag_3': 0,
            'high_low_pct': 0,
            'volume': data.get('volume', 0),
            'rsi': 50,  # Neutral default
            'sentiment_volume_interaction': sentiment['compound'] * data.get('volume', 0)
        }
        
        # Create feature vector
        features_df = pd.DataFrame([features_dict])
        features_df = features_df[[col for col in feature_columns if col in features_df.columns]]
        
        # Fill missing columns with 0
        for col in feature_columns:
            if col not in features_df.columns:
                features_df[col] = 0
        
        # Reorder columns
        features_df = features_df[feature_columns]
        
        # Scale
        features_scaled = scaler.transform(features_df)
        
        # Predict
        prediction = predictor_model.predict(features_scaled)[0]
        proba = predictor_model.predict_proba(features_scaled)[0]
        
        direction = 'UP' if prediction == 1 else 'DOWN' if prediction == -1 else 'NEUTRAL'
        confidence = float(max(proba))
        
        return jsonify({
            'symbol': data.get('symbol', 'UNKNOWN'),
            'news_text': news_text,
            'sentiment': sentiment,
            'prediction': {
                'direction': direction,
                'confidence': confidence,
                'prediction_value': int(prediction)
            },
            'input_features': {
                'open_price': open_price,
                'close_price': close_price,
                'price_change_pct': round(price_change_pct, 2),
                'volume': data.get('volume', 0)
            }
        })
    
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def get_stats():
    """Get model statistics"""
    return jsonify({
        'model_type': 'Random Forest',
        'features_count': len(feature_columns) if feature_columns else 0,
        'sentiment_analyzer': 'VADER',
        'training_samples': 'See logs for details'
    })

def run_api(host=None, port=None, debug=False):
    """Run the API server"""
    if host is None:
        host = config.API_HOST
    if port is None:
        port = config.API_PORT
    
    logger.info(f"🚀 Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_api(debug=True)