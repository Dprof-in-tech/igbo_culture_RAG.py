from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
import traceback
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class Query(BaseModel):
    prompt: str

# Import with error handling
try:
    from api.routes.chat import (
        build_full_prompt,
        send_to_openai
    )
    logger.info("Successfully imported chat functions")
except ImportError as e:
    logger.error(f"Failed to import chat functions: {e}")
    build_full_prompt = None
    send_to_openai = None

@app.route("/api/chat", methods=['POST'])
def fill_and_send_prompt():
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Starting chat request")
    
    try:
        # Step 1: Check if functions are available
        if build_full_prompt is None or send_to_openai is None:
            logger.error(f"[{request_id}] Chat functions not imported properly")
            return jsonify({
                "error": "Server configuration error",
                "details": "Chat functions not available",
                "request_id": request_id
            }), 500
        
        # Step 2: Check if request has JSON data
        if not request.is_json:
            logger.error(f"[{request_id}] Request is not JSON")
            return jsonify({
                "error": "Invalid request format",
                "details": "Request must be JSON",
                "request_id": request_id
            }), 400
        
        # Step 3: Get and validate request data
        try:
            data = request.get_json()
            logger.info(f"[{request_id}] Received data: {data}")
        except Exception as e:
            logger.error(f"[{request_id}] Failed to parse JSON: {e}")
            return jsonify({
                "error": "JSON parsing error",
                "details": str(e),
                "request_id": request_id
            }), 400
        
        # Step 4: Extract prompt
        if not data:
            logger.error(f"[{request_id}] No data received")
            return jsonify({
                "error": "No data provided",
                "details": "Request body is empty",
                "request_id": request_id
            }), 400
        
        prompt = data.get("prompt")
        if not prompt:
            logger.error(f"[{request_id}] No prompt in request data")
            return jsonify({
                "error": "Missing prompt",
                "details": "Request must include 'prompt' field",
                "request_id": request_id
            }), 400
        
        if not isinstance(prompt, str):
            logger.error(f"[{request_id}] Prompt is not a string: {type(prompt)}")
            return jsonify({
                "error": "Invalid prompt type",
                "details": f"Prompt must be a string, got {type(prompt).__name__}",
                "request_id": request_id
            }), 400
        
        # Step 5: Validate with Pydantic
        try:
            query = Query(prompt=prompt)
            logger.info(f"[{request_id}] Prompt validated: '{prompt[:100]}...'")
        except ValidationError as e:
            logger.error(f"[{request_id}] Pydantic validation error: {e}")
            return jsonify({
                "error": "Validation error",
                "details": str(e),
                "request_id": request_id
            }), 400
        
        # Step 6: Build full prompt
        try:
            logger.info(f"[{request_id}] Building full prompt...")
            docs = build_full_prompt(prompt)
            logger.info(f"[{request_id}] Full prompt built successfully. Length: {len(str(docs)) if docs else 0}")
        except Exception as e:
            logger.error(f"[{request_id}] Error in build_full_prompt: {e}")
            logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
            return jsonify({
                "error": "Prompt building error",
                "details": str(e),
                "function": "build_full_prompt",
                "request_id": request_id
            }), 500
        
        # Step 7: Send to OpenAI
        try:
            logger.info(f"[{request_id}] Sending to OpenAI...")
            response = send_to_openai(docs)
            logger.info(f"[{request_id}] OpenAI response received. Length: {len(str(response)) if response else 0}")
        except Exception as e:
            logger.error(f"[{request_id}] Error in send_to_openai: {e}")
            logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
            return jsonify({
                "error": "OpenAI API error", 
                "details": str(e),
                "function": "send_to_openai",
                "request_id": request_id
            }), 500
        
        # Step 8: Return successful response
        logger.info(f"[{request_id}] Request completed successfully")
        return jsonify({
            "text": response,
            "request_id": request_id,
            "status": "success"
        })
    
    except Exception as e:
        # Catch-all error handler
        logger.error(f"[{request_id}] Unexpected error: {e}")
        logger.error(f"[{request_id}] Full traceback: {traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e),
            "traceback": traceback.format_exc(),
            "request_id": request_id
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not found",
        "details": "The requested endpoint does not exist",
        "path": request.path
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method not allowed",
        "details": f"Method {request.method} not allowed for {request.path}",
        "allowed_methods": ["POST"]
    }), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({
        "error": "Internal server error",
        "details": "An unexpected error occurred"
    }), 500


