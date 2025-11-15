"""
Stock movement prediction model
"""
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import pandas as pd
import logging
from config import config

logger = logging.getLogger(__name__)

class StockPredictor:
    def __init__(self):
        self.model = None
        self.feature_engineer = None
    
    def train(self, X_train, y_train, X_test=None, y_test=None):
        """Train the prediction model"""
        logger.info("Training Random Forest model...")
        
        self.model = RandomForestClassifier(
            n_estimators=config.RANDOM_FOREST_ESTIMATORS,
            max_depth=10,
            random_state=config.RANDOM_STATE,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        train_acc = self.model.score(X_train, y_train)
        logger.info(f"Train accuracy: {train_acc:.3f}")
        
        if X_test is not None and y_test is not None:
            test_acc = self.model.score(X_test, y_test)
            logger.info(f"Test accuracy: {test_acc:.3f}")
            
            y_pred = self.model.predict(X_test)
            print("\nClassification Report:")
            
            # Map class labels to names
            class_map = {-1: 'Down', 0: 'Neutral', 1: 'Up'}
            
            # Get unique classes that appear in y_test or y_pred
            unique_classes = sorted(list(set(y_test.unique()) | set(y_pred)))
            target_names = [class_map[c] for c in unique_classes]
            
            print(classification_report(y_test, y_pred, 
                                       labels=unique_classes,
                                       target_names=target_names))
        
        return self.model
    
    def predict(self, features):
        """Make prediction"""
        if isinstance(features, dict):
            features = pd.DataFrame([features])
        
        prediction = self.model.predict(features)[0]
        proba = self.model.predict_proba(features)[0]
        
        direction = 'UP' if prediction == 1 else 'DOWN' if prediction == -1 else 'NEUTRAL'
        confidence = max(proba)
        
        return {
            'prediction': int(prediction),
            'direction': direction,
            'confidence': float(confidence)
        }
    
    def save_model(self):
        """Save trained model"""
        filepath = config.MODELS_DIR / "stock_predictor.pkl"
        joblib.dump(self.model, filepath)
        logger.info(f"Saved model to {filepath}")
    
    def load_model(self):
        """Load trained model"""
        filepath = config.MODELS_DIR / "stock_predictor.pkl"
        self.model = joblib.load(filepath)
        logger.info("Loaded saved model")