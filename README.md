# Flash Bootloader & OTA RAG Assistant

An AI-powered information retrieval system for Flash Bootloader and Over-The-Air (OTA) update technologies using Retrieval Augmented Generation (RAG). This system helps developers and engineers access relevant information about bootloader configurations, OTA updates, and related security practices through natural language queries.

## Features
- Special handling for security class queries with strict adherence to source documentation
- Support for both cloud and local vector database deployments
- Natural language query understanding for technical questions
- Intelligent retrieval of bootloader and OTA documentation
- Context-aware responses using RAG technology
- Bootloader configuration recommendations based on use cases
- Security best practices for OTA implementations
- Enhanced document processing with:
  - Automatic PDF parsing and markdown conversion
  - Smart section header extraction
  - Content type classification (security, examples, notices)
  - Improved chunking with increased overlap for better context
- Advanced vector store management:
  - Hybrid search combining semantic and keyword matching
  - Efficient document chunking and embedding generation
  - Intelligent document deduplication and processing tracking
  - High-performance vector similarity search with metadata filtering
  - Scalable vector storage using Qdrant vector database (both cloud and local options)
- Real-time response generation with OpenAI
- RESTful API endpoints using FastAPI
- Docker containerization for easy deployment
- Comprehensive API testing suite
- CORS support for web integration

## Prerequisites
- Python 3.9 or higher
- OpenAI API key
- Qdrant instance (cloud or local)
- LlamaParse API key (for document processing)

## Installation
```bash
# Clone the repository
git clone https://github.com/your-username/simple_rag.git
cd simple_rag

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration
1. Create a `.env` file in the project root with your configuration:
```ini
OPENAI_API_KEY=your-key-here
LLAMA_CLOUD_API_KEY=your-llama-parse-key

# For cloud Qdrant (optional)
QDRANT_URL=your-qdrant-url
QDRANT_API_KEY=your-qdrant-api-key
```

2. Qdrant Configuration:
- For cloud deployment: Set up a Qdrant cloud instance and add credentials to `.env`
- For local deployment: No additional setup needed, local storage will be created automatically

## Usage

### Running Locally
1. Start the API server:
```bash
python run_server.py
```

2. The API will be available at `http://localhost:8080`

### Using Docker
1. Build the Docker image:
```bash
docker build -t fbl-ota-rag .
```

2. Run the container:
```bash
docker run -p 8080:8080 --env-file .env fbl-ota-rag
```

### API Endpoints
- `POST /query`: Submit a natural language query about Flash Bootloader and OTA updates
  ```json
  {
    "query": "What are the security best practices for OTA updates?"
  }
  ```

- Additional endpoints documentation available at `/docs` when server is running

## Project Structure
- `main.py`: FastAPI server setup and configuration
- `api.py`: API endpoints and route handlers
- `agent_setup.py`: RAG agent configuration and setup
- `vector_store_manager.py`: Vector store management using Qdrant and document processing
- `document_processor.py`: Document processing and tracking
- `prompts.py`: System prompts and query templates
- `processed_files.json`: Tracking file for processed documents
- `test_api.py`: API testing suite
- `requirements.txt`: Project dependencies
- `.env`: Environment configuration
- `Dockerfile`: Container configuration
- `.dockerignore`: Docker build exclusions

## Configuration Parameters
### Agent Configuration
- Chunk size: 4096 tokens (optimized for context preservation)
- Chunk overlap: 300 tokens (ensures smooth context transitions)
- Maximum output tokens: 4096
- Top-k similarity matches: 10 (for comprehensive retrieval)

### Vector Store Configuration
- Uses Qdrant for efficient vector storage (supports both cloud and local deployments)
- Automatic document tracking and deduplication
- Metadata-enhanced document processing
- Improved error handling and fallback mechanisms

## Dependencies
### Core Dependencies
- llama-index-core: Core RAG functionality and vector operations
- llama-parse: Advanced document parsing and structuring
- llama-index-llms-openai: OpenAI integration for LlamaIndex
- llama-index-embeddings-openai: OpenAI embeddings for vector search
- qdrant-client: Vector database integration
- llama-index-vector-stores-qdrant: Qdrant integration for LlamaIndex
- python-dotenv: Environment management

### API Dependencies
- fastapi: Modern web framework for building APIs
- uvicorn: ASGI server implementation
- pydantic: Data validation using Python type annotations

### Development Dependencies
- python-multipart: Handling form data
- requests: HTTP library for API testing

## Deployment

### Process Management with PM2
The application uses PM2 for process management to ensure high availability and automatic restarts. The configuration is in `ecosystem.config.js` and includes:

1. FastAPI Server Process:
```javascript
{
  name: 'fbl-ota-rag',
  script: 'uvicorn',
  args: 'main:app --host 0.0.0.0 --port 8080',
  // ... other configurations
}
```

2. Cloudflare Tunnel Process:
```javascript
{
  name: 'fbl-ota-tunnel',
  script: 'cloudflared',
  args: 'tunnel --config /path/to/cloudflared.yml run',
  // ... other configurations
}
```

To start the processes:
```bash
pm2 start ecosystem.config.js
pm2 save  # Save process list for automatic startup
```

### Cloudflare Tunnel Configuration
The application uses Cloudflare Tunnels for secure access. Configuration is in `cloudflared.yml`:

```yaml
tunnel: your-tunnel-id
credentials-file: /path/to/credentials.json

ingress:
  - hostname: your-domain.example.com
    service: http://localhost:8080
  - service: http_status:404
```

Setup steps:
1. Install cloudflared
2. Create a tunnel: `cloudflared tunnel create <name>`
3. Configure DNS: `cloudflared tunnel route dns <tunnel-id> <hostname>`
4. Update CORS settings in `main.py` to allow your domain
5. Start the tunnel using PM2

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
