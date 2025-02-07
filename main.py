from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from llama_index.vector_stores.supabase import SupabaseVectorStore  # type: ignore
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from prompts import context, fblDocQuery_discription
import os
from dotenv import load_dotenv
import re

load_dotenv()

def format_response(response):
    """
    Format the agent's response by:
    1. Removing markdown-style asterisks
    2. Properly formatting numbered lists
    3. Adding proper spacing and indentation
    """
    if not response:
        return response
    
    # Remove markdown asterisks while preserving the text
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', str(response))
    
    # Format numbered points if they exist
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Check if line starts with a number followed by a period
        if re.match(r'^\d+\.', line):
            # Add proper indentation for numbered points
            parts = line.split(': ', 1)
            if len(parts) > 1:
                number, content = parts
                formatted_lines.append(f"{number} {content}")
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


# Document Parsing with LlamaParse
parser = LlamaParse(
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    result_type="markdown",  # Changed from parsing_instruction
    verbose=True
)

# Initialize Vector Store & Embeddings
vector_store = SupabaseVectorStore(
    postgres_connection_string=os.getenv("SUPABASE_DB_CONNECTION"),
    collection_name="documents_collection"
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)


# Create/Load Embeddings
embed_model = OpenAIEmbedding()

# Check for existing index
try:
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model
    )
    print("Successfully loaded existing index!")
except ValueError:
    # Parse documents only when creating new index
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


#Create Query Engine
Settings.llm = OpenAI(model="gpt-4o-mini")  # Set your LLM
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

agent = ReActAgent.from_tools(tools, llm=OpenAI(model="gpt-4o-mini"), verbose=True, context=context, max_iterations=4)

while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    try:
        response = agent.query(prompt)
        if not response:
            print("No relevant information found. Please refine your query.")
        else:
            formatted_response = format_response(response)
            print("\nResponse:")
            print("------------------------")
            print(formatted_response)
            print("------------------------\n")
    except ValueError as e:
        print(f"Query processing error: {e}. Try rephrasing your question.")