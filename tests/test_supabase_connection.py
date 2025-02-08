from supabase import create_client
import os
from dotenv import load_dotenv
import numpy as np

def test_supabase_connection():
    """Test Supabase connection and vector store functionality"""
    load_dotenv()
    
    # Print environment variables (without sensitive info)
    print("Checking environment variables...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    db_connection = os.getenv("SUPABASE_DB_CONNECTION")
    
    print(f"SUPABASE_URL exists: {bool(supabase_url)}")
    print(f"SUPABASE_KEY exists: {bool(supabase_key)}")
    print(f"SUPABASE_DB_CONNECTION exists: {bool(db_connection)}")
    
    try:
        print("\nTesting Supabase connection...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Test basic table operations
        print("\nTesting table operations...")
        result = supabase.table('document_store').select('id').limit(1).execute()
        print("✓ Successfully queried document_store table")
        
        # Test vector operations
        print("\nTesting vector operations...")
        # Create a test document with embedding
        test_embedding = np.random.rand(1536).tolist()  # Create random embedding
        test_doc = {
            'content': 'test document',
            'metadata': {'test': True},
            'embedding': test_embedding
        }
        
        # Insert test document
        insert_result = supabase.table('document_store').insert(test_doc).execute()
        print("✓ Successfully inserted test document with embedding")
        
        # Clean up test document
        if insert_result.data:
            test_id = insert_result.data[0]['id']
            supabase.table('document_store').delete().eq('id', test_id).execute()
            print("✓ Successfully cleaned up test document")
        
        print("\n✅ All tests passed! Your Supabase vector store is properly configured.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
