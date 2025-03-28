import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import app as api_app, get_agent
import os
from dotenv import load_dotenv

# Create and configure the FastAPI application
app = FastAPI(
    title="Document Query System",
    description="AI-powered document query system using LlamaIndex and GPT-4",
    version="1.0.0"
)


# Configure CORS
origins = ["https://fbl-chatbot.vercel.app", "https://chatbot-api.n8ndeutschauto.de"]  # Allow both Vercel and Cloudflare tunnel domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  
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
    
    # Initialize the agent at startup
    print("Initializing agent and processing documents...")
    get_agent()
    print("Agent initialization complete")
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))  # Changed default port to 8080 to avoid conflicts
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