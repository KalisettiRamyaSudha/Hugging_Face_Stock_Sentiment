"""
Start the Flask API server
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.api.app import run_api

if __name__ == "__main__":
    print("="*70)
    print("🚀 Starting Stock Predictor API")
    print("="*70)
    print("\n📡 API Endpoints:")
    print("  - http://localhost:5000/")
    print("  - http://localhost:5000/health")
    print("  - http://localhost:5000/predict (POST)")
    print("  - http://localhost:5000/sentiment (POST)")
    print("\n💡 Press Ctrl+C to stop\n")
    
    run_api(debug=True)