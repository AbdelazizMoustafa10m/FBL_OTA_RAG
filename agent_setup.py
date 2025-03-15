from vector_store_manager import VectorStoreManager
from llama_index.core import Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage, MessageRole
from prompts import context, fblDocQuery_discription, system_prompt
from document_processor import DocumentProcessor
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
        "QDRANT_URL": os.getenv("QDRANT_URL"),
        "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY"),
        "LLAMA_CLOUD_API_KEY": os.getenv("LLAMA_CLOUD_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }

    # Check if any required variables are missing
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    # Initialize VectorStoreManager - handle both cloud and local options
    if "QDRANT_URL" in missing_vars or "QDRANT_API_KEY" in missing_vars:
        print("Using local Qdrant instance as cloud credentials are missing")
        vector_manager = VectorStoreManager(
            local_path="./qdrant_data",
            llama_cloud_api_key=required_vars["LLAMA_CLOUD_API_KEY"]
        )
    else:
        print("Using cloud Qdrant instance")
        vector_manager = VectorStoreManager(
            qdrant_url=required_vars["QDRANT_URL"],
            qdrant_api_key=required_vars["QDRANT_API_KEY"],
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
    llm = OpenAI(model="gpt-4o-mini", temperature=0.3)
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

    # Create and return the agent with proper system prompt and error handling
    try:
        # Format system prompt properly
        system_message = ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
        user_message = ChatMessage(role=MessageRole.USER, content=context)
        
        agent = ReActAgent.from_tools(
            tools, 
            llm=llm,
            verbose=True,
            system_message=system_message,
            context=context,
            max_iterations=10
        )
        
        # Add a custom query method with error handling
        original_query = agent.query
        
        def safe_query(query_str, **kwargs):
            try:
                # Check if this is a security class query
                if "security class" in query_str.lower():
                    print(f"Security class query detected: {query_str}")
                    # Try to get a response using the query engine directly for security queries
                    try:
                        # Get the first tool which should be the query engine
                        query_engine_tool = tools[0]
                        query_engine = query_engine_tool.query_engine
                        response = query_engine.query(query_str)
                        if response and str(response).strip():
                            return str(response)
                        else:
                            # Return the standard security class response when no info is found
                            return "I apologize, but I cannot find specific information about security classes in the available documentation. Could you please clarify what specific security-related information you're looking for?"
                    except Exception as sec_error:
                        print(f"Error in direct security query: {sec_error}")
                        # Return the standard security class response
                        return "I apologize, but I cannot find specific information about security classes in the available documentation. Could you please clarify what specific security-related information you're looking for?"
                
                # For non-security queries, use the original agent query method
                return original_query(query_str, **kwargs)
            except Exception as e:
                print(f"Error in agent query: {e}")
                # Return a fallback response when the agent encounters an error
                return "I apologize, but I encountered an error processing your query. Please try rephrasing your question or ask something else about the Flash Bootloader documentation."
        
        # Replace the query method with our safe version
        agent.query = safe_query
        
        return agent
    except Exception as e:
        print(f"Error setting up agent: {e}")
        raise