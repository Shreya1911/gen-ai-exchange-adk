#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI server for exposing the Trip Planner agent built using ADK."""

import os
import logging
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware  # Added CORS import
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set GOOGLE_CLOUD_PROJECT environment variable for cloud tracing
# Update with your actual project ID
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "kisan-project-gcp")

# Get the absolute path of the current directory
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create FastAPI app with enabled cloud tracing
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    trace_to_cloud=False,
)

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://genai-exchange-ui.vercel.app/","http://localhost:3000", "http://localhost:5173","http://localhost:8083","http://localhost:8080"],  # Frontend URLs (Vite dev server)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Add gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware to log requests and responses
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log the request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process the request and get the response
        response = await call_next(request)
        
        # Log the response status code
        logger.info(f"Response: {response.status_code}")
        
        return response

# Add the logging middleware
app.add_middleware(LoggingMiddleware)

app.title = "trip-planner-agent"
app.description = "API for interacting with the Trip Planner Agent that helps users plan and manage their travel"

# Custom error handler for better error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )

# Interceptor for the /run endpoint to enhance response handling
@app.middleware("http")
async def process_run_response(request: Request, call_next):
    # Check if client requested no compression
    no_compress = False
      # Check URL query parameters for noCompress flag
    try:
        query_params = dict(request.query_params)
        logger.info(f"Request query parameters: {query_params}")
        no_compress = query_params.get("noCompress", "").lower() in ["true", "1", "yes"]
        if no_compress:
            logger.info("Client requested no compression for this response")
            logger.info("Will remove Content-Encoding header if present")
    except Exception as e:
        logger.error(f"Error parsing query params: {e}")
    
    # Process the request and get the response
    response = await call_next(request)
    
    # Only process responses from the /run endpoint
    if request.url.path == "/run" and response.status_code == 200:
        # Get the response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
            
        # Try to decode and log the response for debugging
        try:
            import json
            import gzip

            decoded_body = body
            # Check if the response is gzipped and decompress if necessary
            if response.headers.get("content-encoding") == "gzip":
                logger.info("Decompressing gzipped response body for logging.")
                decoded_body = gzip.decompress(body)

            response_data = json.loads(decoded_body.decode())
            logger.info(f"Processed /run response: {json.dumps(response_data)[:1000]}...")
        except Exception as e:
            logger.error(f"Error processing response body: {e}")
        
        # Create response headers, but don't include Content-Encoding: gzip if no_compress is True
        headers = dict(response.headers)
        if no_compress and "Content-Encoding" in headers:
            logger.info(f"Removing Content-Encoding header ({headers['Content-Encoding']}) as requested by client")
            del headers["Content-Encoding"]
        
        # Return a new response with the original body
        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )
    
    return response

# Main execution
if __name__ == "__main__":
    import uvicorn
    
    # Default to port 8080, but allow override via environment variable
    port = int(os.environ.get("PORT", 8080))
    
    logger.info(f"Starting Trip Planner Agent API on port {port}")
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")