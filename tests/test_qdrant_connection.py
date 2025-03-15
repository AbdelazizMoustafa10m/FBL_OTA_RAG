from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
import numpy as np
from qdrant_client.models import VectorParams, Distance, PointStruct

def test_qdrant_connection():
    """Test Qdrant connection and vector store functionality"""
    load_dotenv()
    
    # Print environment variables (without sensitive info)
    print("Checking environment variables...")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    
    print(f"QDRANT_URL exists: {bool(qdrant_url)}")
    print(f"QDRANT_API_KEY exists: {bool(qdrant_api_key)}")
    
    # Collection details
    collection_name = "document_store"
    vector_size = 1536  # OpenAI embedding dimension
    
    try:
        print("\nTesting Qdrant connection...")
        
        # Initialize client based on whether we're using cloud or local
        if qdrant_url and qdrant_api_key:
            client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            print("✓ Connected to cloud Qdrant instance")
        else:
            local_path = "./qdrant_data"
            client = QdrantClient(path=local_path)
            print(f"✓ Connected to local Qdrant instance at {local_path}")
        
        # Check if collection exists, create if it doesn't
        collections = client.get_collections().collections
        collection_exists = any(c.name == collection_name for c in collections)
        
        if not collection_exists:
            print(f"\nCreating collection '{collection_name}'...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            print(f"✓ Created collection '{collection_name}'")
        else:
            print(f"\n✓ Collection '{collection_name}' already exists")
        
        # Test insertion
        print("\nTesting vector operations...")
        # Create a test document with embedding
        test_embedding = np.random.rand(vector_size).tolist()  # Create random embedding
        test_point = PointStruct(
            id=np.random.randint(10000),
            vector=test_embedding,
            payload={
                "text": "test document",
                "metadata": {"test": True}
            }
        )
        
        # Insert test document
        client.upsert(
            collection_name=collection_name,
            points=[test_point]
        )
        print("✓ Successfully inserted test document with embedding")
        
        # Test search
        search_result = client.search(
            collection_name=collection_name,
            query_vector=test_embedding,
            limit=1
        )
        
        if search_result and len(search_result) > 0:
            print("✓ Successfully performed vector search")
            
            # Clean up test document
            client.delete(
                collection_name=collection_name,
                points_selector=[test_point.id]
            )
            print("✓ Successfully cleaned up test document")
        
        print("\n✅ All tests passed! Your Qdrant vector store is properly configured.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    test_qdrant_connection()