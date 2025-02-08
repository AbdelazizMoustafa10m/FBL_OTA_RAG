from vector_store_manager import VectorStoreManager
from llama_index.embeddings.openai import OpenAIEmbedding

def test_direct_search():
    # Initialize the vector store manager
    vm = VectorStoreManager()
    embed_model = OpenAIEmbedding()
    
    # Create embedding for our search query
    query = "Scope of Delivery Flash Bootloader"
    query_embedding = embed_model.get_text_embedding(query)
    
    # Search using raw SQL through Supabase
    try:
        result = vm.client.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'similarity_threshold': 0.7,
                'match_count': 5
            }
        ).execute()
        
        print("\nSearch Results:")
        for item in result.data:
            print("\n---")
            print(f"Similarity: {item['similarity']:.3f}")
            print(f"Content: {item['content']}")
            if item.get('metadata'):
                print(f"Metadata: {item['metadata']}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_direct_search()
