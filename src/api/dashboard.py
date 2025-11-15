from flask import Flask, render_template_string
from flask_cors import CORS
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock Market Predictor Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
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
        }
        .input-section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group.full-width {
            grid-column: 1 / -1;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
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
            font-family: inherit;
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
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        .loading.show { display: block; }
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
        }
        .result-section.show { display: block; }
        .result-card {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .result-header {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .prediction-value {
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            text-transform: uppercase;
        }
        .prediction-value.up { color: #10b981; }
        .prediction-value.down { color: #ef4444; }
        .prediction-value.neutral { color: #f59e0b; }
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
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
        }
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            transition: width 0.5s ease;
        }
        .sentiment-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            margin: 5px;
            font-size: 1.1em;
        }
        .sentiment-positive { background: #d1fae5; color: #065f46; }
        .sentiment-negative { background: #fee2e2; color: #991b1b; }
        .sentiment-neutral { background: #fef3c7; color: #92400e; }
        .info-table {
            width: 100%;
            border-collapse: collapse;
        }
        .info-table td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        .info-table td:first-child {
            font-weight: 600;
            color: #666;
        }
        .info-table td:last-child {
            text-align: right;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert.error {
            background: #fee2e2;
            color: #991b1b;
            border-left: 4px solid #ef4444;
        }
        .alert.warning {
            background: #fef3c7;
            color: #92400e;
            border-left: 4px solid #f59e0b;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 Stock Market Predictor</h1>
        <p class="subtitle">
            AI-Powered Stock Movement Prediction
            <span class="badge live">● LIVE</span>
        </p>
        
        <div class="input-section">
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
                    <label for="news_text">News Article / Headline</label>
                    <textarea id="news_text" name="news_text" 
                              placeholder="Enter news article or headline about the company...
Example: Apple announces record-breaking iPhone sales with strong revenue growth in Q4." required></textarea>
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
                               step="0.01" placeholder="152.00" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="volume">Trading Volume</label>
                    <input type="number" id="volume" name="volume" 
                           placeholder="1000000" required>
                </div>
                
                <button type="submit" id="submitBtn">🔮 Predict Stock Movement</button>
            </form>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="color: #666; font-size: 1.1em;">Analyzing sentiment and predicting...</p>
        </div>
        
        <div class="result-section" id="results">
            <div class="result-card">
                <div class="result-header">📊 Prediction Result</div>
                <div class="prediction-value" id="predictionValue">-</div>
                
                <div class="confidence-container">
                    <div class="confidence-label">
                        <span>Confidence Level</span>
                        <span id="confidenceText">0%</span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" id="confidenceBar" style="width: 0%;"></div>
                    </div>
                </div>
            </div>
            
            <div class="result-card">
                <div class="result-header">💭 Sentiment Analysis</div>
                <div id="sentimentResult"></div>
            </div>
            
            <div class="result-card">
                <div class="result-header">📈 Market Data</div>
                <table class="info-table" id="marketData">
                    <tr>
                        <td>Symbol</td>
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
                </table>
            </div>
        </div>
    </div>
    
    <script>
        const API_URL = 'http://localhost:5000';
        
        document.getElementById('predictionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
            document.getElementById('submitBtn').disabled = true;
            
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
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    throw new Error('API request failed');
                }
                
                const result = await response.json();
                displayResults(result, formData);
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error making prediction. Make sure API is running on localhost:5000');
            } finally {
                document.getElementById('loading').classList.remove('show');
                document.getElementById('submitBtn').disabled = false;
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
            
            // Confidence
            document.getElementById('confidenceBar').style.width = confidence + '%';
            document.getElementById('confidenceText').textContent = confidence.toFixed(1) + '%';
            
            // Sentiment
            const sentiment = result.sentiment;
            const sentClass = sentiment.label;
            
            document.getElementById('sentimentResult').innerHTML = `
                <div style="text-align: center; margin: 20px 0;">
                    <span class="sentiment-badge sentiment-${sentClass}">
                        ${sentiment.label.toUpperCase()}
                    </span>
                    <p style="margin-top: 15px; color: #666; font-size: 1.1em;">
                        Score: ${(sentiment.score * 100).toFixed(1)}% | 
                        Compound: ${sentiment.compound.toFixed(3)}
                    </p>
                </div>
            `;
            
            // Market data
            const priceChange = formData.close_price - formData.open_price;
            const priceChangePct = (priceChange / formData.open_price * 100).toFixed(2);
            const priceColor = priceChange >= 0 ? '#10b981' : '#ef4444';
            
            document.getElementById('displaySymbol').textContent = formData.symbol;
            document.getElementById('displayPriceChange').innerHTML = 
                `<span style="color: ${priceColor}; font-weight: bold;">${priceChangePct}%</span>`;
            document.getElementById('displayVolume').textContent = 
                formData.volume.toLocaleString();
            document.getElementById('displayPriceRange').textContent = 
                `$${formData.open_price.toFixed(2)} → $${formData.close_price.toFixed(2)}`;
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

# Create Flask app for dashboard
dashboard_app = Flask(__name__)
CORS(dashboard_app)

@dashboard_app.route('/')
def dashboard():
    """Render dashboard"""
    return render_template_string(DASHBOARD_HTML)

def run_dashboard(host=None, port=None, debug=False):
    """Run the dashboard server"""
    if host is None:
        host = config.API_HOST
    if port is None:
        port = config.DASHBOARD_PORT
    
    logger.info(f"🎨 Starting Dashboard on {host}:{port}")
    logger.info(f"📱 Open browser: http://localhost:{port}")
    dashboard_app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_dashboard(debug=True)
