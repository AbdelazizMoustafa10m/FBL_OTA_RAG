# Flash Bootloader & OTA RAG Assistant

An AI-powered information retrieval system for Flash Bootloader and Over-The-Air (OTA) update technologies using Retrieval Augmented Generation (RAG). This system helps developers and engineers access relevant information about bootloader configurations, OTA updates, and related security practices through natural language queries.

## Features
- Natural language query understanding for technical questions
- Intelligent retrieval of bootloader and OTA documentation
- Context-aware responses using RAG technology
- Bootloader configuration recommendations based on use cases
- Security best practices for OTA implementations
- Real-time information processing using LlamaIndex and OpenAI
- Vector-based document storage for efficient retrieval

## Prerequisites
- Python 3.9 or higher
- OpenAI API key
- Sufficient storage for vector database

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
VECTOR_DB_PATH=chroma_db/
```

2. Ensure your vector database directory exists:
```bash
mkdir -p chroma_db
```

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
- `chroma_db/`: Vector database storage
- `.env`: Environment configuration

## Dependencies
- llama-index-core: Core RAG functionality
- llama-parse: Document parsing
- langchain-community: LLM utilities
- openai: OpenAI API interface
- python-dotenv: Environment management

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
