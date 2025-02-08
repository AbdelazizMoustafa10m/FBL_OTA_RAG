from vector_store_manager import VectorStoreManager

def test_specific_section():
    # Initialize the vector store manager
    vm = VectorStoreManager()
    
    try:
        # Search for the specific section using exact text match
        result = vm.client.table('document_store')\
            .select('content')\
            .textSearch('content', '1.5 Scope of Delivery', config='english')\
            .execute()
        
        print("\nSearch Results:")
        for item in result.data:
            print("---")
            print(item['content'])
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_specific_section()
