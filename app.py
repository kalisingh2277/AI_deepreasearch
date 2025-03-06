import os
import logging
import asyncio
import webbrowser
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from src.agents.research_agent import ResearchAgent
from dotenv import load_dotenv
from hypercorn.config import Config
from hypercorn.asyncio import serve
from asgiref.wsgi import WsgiToAsgi

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
asgi_app = WsgiToAsgi(app)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({
        "error": "Method not allowed",
        "message": "This endpoint only accepts POST requests",
        "allowed_methods": list(error.valid_methods)
    }), 405

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/research', methods=['POST', 'OPTIONS'])
async def research():
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Request must be JSON",
                "error_code": "INVALID_CONTENT_TYPE"
            }), 400

        data = request.get_json()
        
        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Invalid JSON format",
                "error_code": "INVALID_JSON"
            }), 400

        query = data.get('query')
        depth = data.get('depth', 3)

        # Validate query
        if not query or not isinstance(query, str):
            return jsonify({
                "status": "error",
                "message": "Query is required and must be a string",
                "error_code": "INVALID_QUERY"
            }), 400

        # Validate depth
        try:
            depth = int(depth)
            if depth < 1 or depth > 5:
                raise ValueError("Depth out of range")
        except (TypeError, ValueError):
            return jsonify({
                "status": "error",
                "message": "Depth must be an integer between 1 and 5",
                "error_code": "INVALID_DEPTH"
            }), 400

        # Log request details
        logger.info(f"Processing research request - Query: {query}, Depth: {depth}")

        # Initialize agent and process request
        agent = ResearchAgent()
        results = await agent.search_and_analyze(query, depth)
        
        # Validate response
        if not isinstance(results, dict):
            logger.error(f"Invalid response format: {type(results)}")
            return jsonify({
                "status": "error",
                "message": "Invalid response format from research agent",
                "error_code": "INVALID_RESPONSE"
            }), 500

        # Return successful response
        return jsonify(results)
            
    except Exception as e:
        logger.error(f"Error processing research request: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_code": "SERVER_ERROR"
        }), 500

def open_browser():
    """Open the browser after a short delay"""
    try:
        webbrowser.open('http://localhost:5000')
    except Exception as e:
        logger.error(f"Error opening browser: {str(e)}")

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        config = Config()
        config.bind = [f"0.0.0.0:{port}"]
        config.use_reloader = True
        config.worker_class = "asyncio"
        
        # Schedule browser opening
        asyncio.get_event_loop().call_later(1.5, open_browser)
        
        logger.info(f"Starting server on http://localhost:{port}")
        asyncio.run(serve(asgi_app, config))
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise 