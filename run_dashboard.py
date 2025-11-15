import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from flask import Flask, render_template_string
from flask_cors import CORS
import logging
from config import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# HTML DASHBOARD TEMPLATE
# ============================================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Market Predictor - AI Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .badge.live {
            background: #d1fae5;
            color: #065f46;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .input-section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 20px;
            font-weight: 600;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 0;
        }
        
        .form-group.full-width {
            grid-column: 1 / -1;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 0.95em;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            transition: all 0.3s;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        button:disabled {
            background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result-section {
            display: none;
            animation: fadeIn 0.5s;
        }
        
        .result-section.show {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .result-card {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
        }
        
        .result-header {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .prediction-value {
            font-size: 3.5em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .prediction-value.up {
            color: #10b981;
            text-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
        }
        
        .prediction-value.down {
            color: #ef4444;
            text-shadow: 0 2px 10px rgba(239, 68, 68, 0.3);
        }
        
        .prediction-value.neutral {
            color: #f59e0b;
            text-shadow: 0 2px 10px rgba(245, 158, 11, 0.3);
        }
        
        .confidence-container {
            margin-top: 20px;
        }
        
        .confidence-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-weight: 600;
            color: #666;
        }
        
        .confidence-bar {
            background: #e5e7eb;
            height: 35px;
            border-radius: 17.5px;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 1.1em;
            transition: width 0.5s ease;
        }
        
        .sentiment-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            margin: 5px;
            font-size: 1.2em;
        }
        
        .sentiment-positive {
            background: #d1fae5;
            color: #065f46;
        }
        
        .sentiment-negative {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .sentiment-neutral {
            background: #fef3c7;
            color: #92400e;
        }
        
        .info-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .info-table tr {
            border-bottom: 1px solid #e5e7eb;
        }
        
        .info-table tr:last-child {
            border-bottom: none;
        }
        
        .info-table td {
            padding: 15px 10px;
        }
        
        .info-table td:first-child {
            font-weight: 600;
            color: #666;
            width: 40%;
        }
        
        .info-table td:last-child {
            text-align: right;
            color: #333;
            font-weight: 500;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid;
        }
        
        .alert.error {
            background: #fee2e2;
            color: #991b1b;
            border-color: #ef4444;
        }
        
        .alert.warning {
            background: #fef3c7;
            color: #92400e;
            border-color: #f59e0b;
        }
        
        .alert.info {
            background: #dbeafe;
            color: #1e40af;
            border-color: #3b82f6;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            color: #666;
            font-size: 0.9em;
        }
        
        .example-link {
            color: #667eea;
            cursor: pointer;
            text-decoration: underline;
            font-size: 0.9em;
            display: inline-block;
            margin-top: 5px;
        }
        
        .example-link:hover {
            color: #764ba2;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .form-row {
                grid-template-columns: 1fr;
            }
            
            .prediction-value {
                font-size: 2.5em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📈 Stock Market Predictor</h1>
            <p class="subtitle">
                AI-Powered Stock Movement Prediction with Sentiment Analysis
                <span class="badge live">● LIVE</span>
            </p>
        </header>
        
        <div class="alert info">
            <strong>ℹ️ How it works:</strong> Enter a news headline and stock data to predict whether the stock will go UP, DOWN, or stay NEUTRAL based on AI sentiment analysis.
        </div>
        
        <div class="input-section">
            <div class="section-title">📝 Enter Stock Information</div>
            <form id="predictionForm">
                <div class="form-row">
                    <div class="form-group">
                        <label for="symbol">Stock Symbol</label>
                        <select id="symbol" name="symbol" required>
                            <option value="AAPL">AAPL - Apple Inc.</option>
                            <option value="GOOGL">GOOGL - Alphabet Inc.</option>
                            <option value="MSFT">MSFT - Microsoft Corp.</option>
                            <option value="AMZN">AMZN - Amazon.com Inc.</option>
                            <option value="TSLA">TSLA - Tesla Inc.</option>
                            <option value="META">META - Meta Platforms</option>
                            <option value="NVDA">NVDA - NVIDIA Corp.</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group full-width">
                    <label for="news_text">
                        News Article / Headline
                        <span class="example-link" onclick="fillExample()">Try an example →</span>
                    </label>
                    <textarea id="news_text" name="news_text" 
                              placeholder="Enter a recent news headline or article about the company...
                              
Example: Apple announces record-breaking iPhone sales with strong revenue growth in the fourth quarter." required></textarea>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="open_price">Opening Price ($)</label>
                        <input type="number" id="open_price" name="open_price" 
                               step="0.01" placeholder="150.00" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="close_price">Closing Price ($)</label>
                        <input type="number" id="close_price" name="close_price" 
                               step="0.01" placeholder="152.50" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="volume">Trading Volume</label>
                    <input type="number" id="volume" name="volume" 
                           placeholder="50000000" required>
                </div>
                
                <button type="submit" id="submitBtn">
                    🔮 Predict Stock Movement
                </button>
            </form>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="color: #666; font-size: 1.2em; font-weight: 500;">
                Analyzing sentiment and predicting market movement...
            </p>
        </div>
        
        <div class="result-section" id="results">
            <div class="result-card">
                <div class="result-header">📊 Prediction Result</div>
                <div class="prediction-value" id="predictionValue">-</div>
                
                <div class="confidence-container">
                    <div class="confidence-label">
                        <span>Prediction Confidence</span>
                        <span id="confidenceText">0%</span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" id="confidenceBar" style="width: 0%;">
                            <span id="confidenceBarText"></span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-header">💭 News Sentiment Analysis</div>
                <div id="sentimentResult"></div>
            </div>
            
            <div class="result-card">
                <div class="result-header">📈 Market Data Summary</div>
                <table class="info-table" id="marketData">
                    <tr>
                        <td>Stock Symbol</td>
                        <td id="displaySymbol">-</td>
                    </tr>
                    <tr>
                        <td>Price Change</td>
                        <td id="displayPriceChange">-</td>
                    </tr>
                    <tr>
                        <td>Trading Volume</td>
                        <td id="displayVolume">-</td>
                    </tr>
                    <tr>
                        <td>Price Range</td>
                        <td id="displayPriceRange">-</td>
                    </tr>
                    <tr>
                        <td>Sentiment Score</td>
                        <td id="displaySentimentScore">-</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <footer>
            <p>🤖 Powered by AI Sentiment Analysis & Machine Learning</p>
            <p style="margin-top: 5px; font-size: 0.85em;">
                Stock Market Predictor © 2024 | 
                <a href="http://localhost:5000" target="_blank" style="color: #667eea;">API Status</a>
            </p>
        </footer>
    </div>
    
    <script>
        const API_URL = 'http://localhost:5000';
        
        // Example data
        function fillExample() {
            document.getElementById('symbol').value = 'AAPL';
            document.getElementById('news_text').value = 'Apple announces record-breaking iPhone 15 sales, exceeding analyst expectations with strong holiday quarter performance and expanding market share in Asia.';
            document.getElementById('open_price').value = '150.25';
            document.getElementById('close_price').value = '153.80';
            document.getElementById('volume').value = '52000000';
        }
        
        // Form submission
        document.getElementById('predictionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
            document.getElementById('submitBtn').disabled = true;
            document.getElementById('submitBtn').textContent = '⏳ Processing...';
            
            // Get form data
            const formData = {
                symbol: document.getElementById('symbol').value,
                news_text: document.getElementById('news_text').value,
                open_price: parseFloat(document.getElementById('open_price').value),
                close_price: parseFloat(document.getElementById('close_price').value),
                volume: parseInt(document.getElementById('volume').value)
            };
            
            try {
                const response = await fetch(`${API_URL}/predict`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    throw new Error(`API request failed: ${response.status}`);
                }
                
                const result = await response.json();
                displayResults(result, formData);
                
            } catch (error) {
                console.error('Error:', error);
                alert(`❌ Error making prediction: ${error.message}\n\nMake sure the API is running:\npython run_api.py`);
            } finally {
                document.getElementById('loading').classList.remove('show');
                document.getElementById('submitBtn').disabled = false;
                document.getElementById('submitBtn').textContent = '🔮 Predict Stock Movement';
            }
        });
        
        function displayResults(result, formData) {
            // Show results section
            document.getElementById('results').classList.add('show');
            
            // Prediction
            const direction = result.prediction.direction;
            const confidence = result.prediction.confidence * 100;
            
            const predValue = document.getElementById('predictionValue');
            predValue.textContent = direction;
            predValue.className = 'prediction-value ' + direction.toLowerCase();
            
            // Confidence bar
            const confidenceBar = document.getElementById('confidenceBar');
            const confidenceText = document.getElementById('confidenceText');
            const confidenceBarText = document.getElementById('confidenceBarText');
            
            confidenceBar.style.width = confidence + '%';
            confidenceText.textContent = confidence.toFixed(1) + '%';
            confidenceBarText.textContent = confidence.toFixed(1) + '%';
            
            // Sentiment
            const sentiment = result.sentiment;
            const sentClass = sentiment.label;
            const sentScore = (sentiment.score * 100).toFixed(1);
            
            document.getElementById('sentimentResult').innerHTML = `
                <div style="text-align: center; margin: 20px 0;">
                    <span class="sentiment-badge sentiment-${sentClass}">
                        ${sentiment.label.toUpperCase()}
                    </span>
                    <p style="margin-top: 15px; color: #666; font-size: 1.1em;">
                        <strong>Sentiment Score:</strong> ${sentScore}%<br>
                        <strong>Compound Score:</strong> ${sentiment.compound.toFixed(3)}
                    </p>
                </div>
                <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <p style="color: #666; font-style: italic; line-height: 1.6;">
                        "${formData.news_text.substring(0, 150)}${formData.news_text.length > 150 ? '...' : ''}"
                    </p>
                </div>
            `;
            
            // Market data
            const priceChange = formData.close_price - formData.open_price;
            const priceChangePct = (priceChange / formData.open_price * 100).toFixed(2);
            const priceColor = priceChange >= 0 ? '#10b981' : '#ef4444';
            const priceSymbol = priceChange >= 0 ? '▲' : '▼';
            
            document.getElementById('displaySymbol').innerHTML = `<strong>${formData.symbol}</strong>`;
            document.getElementById('displayPriceChange').innerHTML = 
                `<span style="color: ${priceColor}; font-weight: bold;">${priceSymbol} ${priceChangePct}%</span>`;
            document.getElementById('displayVolume').textContent = 
                formData.volume.toLocaleString();
            document.getElementById('displayPriceRange').textContent = 
                `$${formData.open_price.toFixed(2)} → $${formData.close_price.toFixed(2)}`;
            document.getElementById('displaySentimentScore').innerHTML = 
                `<span class="sentiment-badge sentiment-${sentClass}" style="padding: 5px 10px; font-size: 0.9em;">${sentiment.label.toUpperCase()}</span>`;
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }
        
        // Check API status on load
        window.addEventListener('load', async function() {
            try {
                const response = await fetch(`${API_URL}/health`);
                if (!response.ok) {
                    throw new Error('API not responding');
                }
                console.log('✅ API is running');
            } catch (error) {
                console.warn('⚠️ API not available:', error);
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert warning';
                alertDiv.innerHTML = '<strong>⚠️ Warning:</strong> API server not detected. Please start the API: <code>python run_api.py</code>';
                document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.input-section'));
            }
        });
    </script>
</body>
</html>
"""

# ============================================================================
# FLASK APPLICATION
# ============================================================================

# Create Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def dashboard():
    """Render the dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'dashboard'}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to start dashboard"""
    print("=" * 70)
    print("🎨 STARTING STOCK PREDICTOR DASHBOARD")
    print("=" * 70)
    print(f"\n📱 Dashboard URL:")
    print(f"   http://localhost:{config.DASHBOARD_PORT}")
    print(f"\n⚠️  Important:")
    print(f"   Make sure API is running on port {config.API_PORT}")
    print(f"   Start API: python run_api.py")
    print(f"\n💡 Press Ctrl+C to stop the dashboard")
    print(f"\n{'='*70}\n")
    
    try:
        app.run(
            host=config.API_HOST,
            port=config.DASHBOARD_PORT,
            debug=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped")
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print(f"1. Check if port {config.DASHBOARD_PORT} is already in use")
        print(f"2. Try a different port in config.py")
        print(f"3. Make sure Flask is installed: pip install flask flask-cors")

if __name__ == '__main__':
    main()