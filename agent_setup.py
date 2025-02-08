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

    # Initialize VectorStoreManager and DocumentProcessor
    vector_manager = VectorStoreManager()
    doc_processor = DocumentProcessor(vector_manager)
    
    # Process any new documents
    if not doc_processor.process_documents():
        print("Warning: Some documents failed to process")
    
    # Set up the vector store and storage context
    vector_store = SupabaseVectorStore(
        postgres_connection_string=os.getenv("SUPABASE_DB_CONNECTION"),
        client=vector_manager.client,
        collection_name=vector_manager.table_name
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Set up LLM and configure settings
    llm = OpenAI(model="gpt-4o-mini", temperature=0.3)
    Settings.llm = llm
    Settings.chunk_size = 512
    Settings.chunk_overlap = 100  # Increased for better context overlap
    
    # Create index with improved retrieval settings
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
    )
    
    # Configure query engine with better retrieval and response synthesis
    query_engine = index.as_query_engine(similarity_top_k=5)

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