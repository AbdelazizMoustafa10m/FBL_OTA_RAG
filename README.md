# Flash Bootloader & OTA RAG Assistant

An AI-powered information retrieval system for Flash Bootloader and Over-The-Air (OTA) update technologies using Retrieval Augmented Generation (RAG). This system helps developers and engineers access relevant information about bootloader configurations, OTA updates, and related security practices through natural language queries.

## Features
- Natural language query understanding for technical questions
- Intelligent retrieval of bootloader and OTA documentation
- Context-aware responses using RAG technology
- Bootloader configuration recommendations based on use cases
- Security best practices for OTA implementations
- High-performance document processing using LlamaIndex and LlamaParse
- Scalable vector storage using Supabase PostgreSQL vector database
- Real-time response generation with OpenAI

## Prerequisites
- Python 3.9 or higher
- OpenAI API key
- Supabase account and project
- PostgreSQL with pgvector extension (handled by Supabase)

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
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-api-key
```

2. Set up Supabase:
- Create a new project in Supabase
- Enable the pgvector extension in your Supabase project
- Create necessary tables and indexes (see documentation)

## Usage
1. Start the assistant:
```bash
python main.py
```

2. Ask questions about Flash Bootloader and OTA updates in natural language.

## Project Structure
- `main.py`: Core application logic and RAG implementation
- `prompts.py`: System prompts and query templates
- `requirements.txt`: Project dependencies
- `.env`: Environment configuration

## Dependencies
- llama-index-core: Core RAG functionality and vector operations
- llama-parse: Advanced document parsing and structuring
- llama-index-llms-openai: OpenAI integration for LlamaIndex
- llama-index-embeddings-openai: OpenAI embeddings for vector search
- supabase: Vector database and PostgreSQL integration
- python-dotenv: Environment management

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
