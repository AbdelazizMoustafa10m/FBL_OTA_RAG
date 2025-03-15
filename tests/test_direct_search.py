from vector_store_manager import VectorStoreManager
from llama_index.embeddings.openai import OpenAIEmbedding
import os
from dotenv import load_dotenv

def test_direct_search():
    # Load environment variables
    load_dotenv()
    
    # Initialize the vector store manager and embedding model
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    if qdrant_url and qdrant_api_key:
        vm = VectorStoreManager(qdrant_url=qdrant_url, qdrant_api_key=qdrant_api_key)
    else:
        vm = VectorStoreManager(local_path="./qdrant_data")
        
    embed_model = OpenAIEmbedding()
    
    # Create multiple search queries to try to find the exact content
    search_queries = [
        "The Flash Bootloader delivery includes:",
        "1.5 Scope of Delivery Flash Bootloader delivery includes",
        "Bootloader as configurable C source code Flash driver",
        "HexView for preparing flash data and containers"
    ]
    
    try:
        print("\nSearching with multiple queries...")
        for query in search_queries:
            print(f"\nQuery: {query}")
            query_embedding = embed_model.get_text_embedding(query)
            
            # Search using Qdrant client
            search_results = vm.client.search(
                collection_name="document_store",
                query_vector=query_embedding,
                limit=3,
                with_payload=True
            )
            
            for result in search_results:
                payload = result.payload
                if payload and "text" in payload:
                    content = payload["text"]
                    if "delivery includes:" in content.lower():
                        print(f"\nFound relevant content (similarity: {result.score:.3f}):")
                        print("---")
                        print(content)
                        return  # Exit after finding the first good match
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_direct_search()