from vector_store_manager import VectorStoreManager
from llama_index.core import Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from prompts import context, fblDocQuery_discription
from document_processor import DocumentProcessor
from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_index.core import StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core import VectorStoreIndex
import os
from dotenv import load_dotenv

def setup_agent():
    """Set up and return the ReAct agent with all necessary components"""
    load_dotenv()

    # Check for required environment variables
    required_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "SUPABASE_DB_CONNECTION": os.getenv("SUPABASE_DB_CONNECTION"),
        "LLAMA_CLOUD_API_KEY": os.getenv("LLAMA_CLOUD_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }

    # Check if any required variables are missing
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Initialize VectorStoreManager with all required credentials
    vector_manager = VectorStoreManager(
        supabase_url=required_vars["SUPABASE_URL"],
        supabase_key=required_vars["SUPABASE_KEY"],
        postgres_connection=required_vars["SUPABASE_DB_CONNECTION"],
        llama_cloud_api_key=required_vars["LLAMA_CLOUD_API_KEY"]
    )
    
    # Initialize DocumentProcessor
    doc_processor = DocumentProcessor(vector_manager)
    
    # Process any new documents
    if not doc_processor.process_documents():
        print("Warning: Some documents failed to process")
    
    # Use the storage context from vector_manager
    storage_context = vector_manager.storage_context

    # Set up LLM and configure settings
    llm = OpenAI(model="gpt-4", temperature=0.3)
    Settings.llm = llm
    Settings.chunk_size = 2048  # Increased chunk size for better context
    Settings.chunk_overlap = 220  # Increased overlap to maintain context between chunks
    Settings.num_output = 2048  # Increase max output tokens
    
    # Create index using vector_manager's create_index method
    # First get all documents to create the index
    documents = doc_processor.get_all_documents()
    index = vector_manager.create_index(documents)
    
    # Configure query engine with better retrieval and response synthesis
    query_engine = index.as_query_engine(similarity_top_k=8)

    tools = [
        QueryEngineTool(
            query_engine=query_engine,
            metadata=ToolMetadata(
                name="fblDocQuery",
                description=fblDocQuery_discription,
            ),
        ),
    ]

    # Create and return the agent
    return ReActAgent.from_tools(
        tools, 
        llm=llm,
        verbose=True, 
        context=context, 
        max_iterations=10
    )