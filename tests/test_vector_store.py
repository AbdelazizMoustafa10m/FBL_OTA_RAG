from vector_store_manager import VectorStoreManager
import os
from dotenv import load_dotenv

load_dotenv()

def test_vector_query():
    vector_manager = VectorStoreManager()
    
    # Get total count
    count = vector_manager.get_document_count()
    print(f"Total documents in store: {count}")
    
    # Try to query some documents
    query_result = vector_manager.query_documents(page_size=5)
    print("\nSample documents:")
    for doc in query_result:
        print(f"\nDocument content (first 200 chars): {doc.get('content', '')[:200]}")
        print(f"Metadata: {doc.get('metadata', {})}")

if __name__ == "__main__":
    test_vector_query()
