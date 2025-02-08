from vector_store_manager import VectorStoreManager
from llama_index.embeddings.openai import OpenAIEmbedding

def test_direct_search():
    # Initialize the vector store manager and embedding model
    vm = VectorStoreManager()
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
            
            result = vm.client.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'similarity_threshold': 0.5,
                    'match_count': 3
                }
            ).execute()
            
            for item in result.data:
                if "delivery includes:" in item['content'].lower():
                    print(f"\nFound relevant content (similarity: {item['similarity']:.3f}):")
                    print("---")
                    print(item['content'])
                    return  # Exit after finding the first good match
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_direct_search()
