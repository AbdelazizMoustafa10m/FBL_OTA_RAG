from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from prompts import context, fblDocQuery_discription
import os
from dotenv import load_dotenv

def setup_agent():
    """Set up and return the ReAct agent with all necessary components"""
    load_dotenv()

    # Initialize Vector Store & Embeddings
    vector_store = SupabaseVectorStore(
        postgres_connection_string=os.getenv("SUPABASE_DB_CONNECTION"),
        collection_name="documents_collection"
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    embed_model = OpenAIEmbedding()

    # Check for existing index or create new one
    try:
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embed_model
        )
    except ValueError:
        # Parse documents only when creating new index
        parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
            result_type="markdown",
            verbose=True
        )
        
        file_extractor = {".pdf": parser}
        documents = SimpleDirectoryReader(
            "./data", 
            file_extractor=file_extractor
        ).load_data()
        
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=embed_model
        )

    # Set up query engine and tools
    Settings.llm = OpenAI(model="gpt-4")
    query_engine = index.as_query_engine(similarity_top_k=3)

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
        llm=OpenAI(model="gpt-4"), 
        verbose=True, 
        context=context, 
        max_iterations=10
    )