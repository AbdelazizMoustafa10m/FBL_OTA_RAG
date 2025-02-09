import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import app as api_app
import os
from dotenv import load_dotenv

# Create and configure the FastAPI application
app = FastAPI(
    title="Document Query System",
    description="AI-powered document query system using LlamaIndex and GPT-4",
    version="1.0.0"
)


# Configure CORS
origins = ["*"]  # Allow all origins temporarily for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400  # Cache preflight requests for 24 hours
)


# Include the API router
app.include_router(api_app)

def main():
    """Main entry point of the application"""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "False").lower() == "true"
    
    # Run the server
    print(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )

if __name__ == "__main__":
    main()