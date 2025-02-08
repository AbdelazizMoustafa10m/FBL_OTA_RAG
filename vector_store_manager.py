from typing import List, Dict, Any, Optional
from supabase import Client, create_client
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document
import os
from dotenv import load_dotenv

class VectorStoreManager:
    def __init__(self, supabase_url: str = None, supabase_key: str = None,
                 table_name: str = 'document_store',
                 embedding_dim: int = 1536,
                 similarity_top_k: int = 8,  # Increased for better context coverage
                 similarity_cutoff: float = 0.7):  # Increased for more relevant matches
        """
        Initialize the VectorStoreManager.
        
        Args:
            supabase_url (str): Supabase project URL
            supabase_key (str): Supabase project key
            table_name (str): Name of the table to store vectors
            embedding_dim (int): Dimension of the embedding vectors
        """
        load_dotenv()
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self.table_name = table_name
        self.embedding_dim = embedding_dim
        self.client = create_client(self.supabase_url, self.supabase_key)
        self.embed_model = OpenAIEmbedding()
        self.similarity_top_k = similarity_top_k
        self.similarity_cutoff = similarity_cutoff  # Minimum similarity score to consider

    def insert_document(self, document: Document) -> Dict[str, Any]:
        """
        Insert a single document into the vector store.
        
        Args:
            document (Document): Document object containing text and metadata
            
        Returns:
            Dict containing the response from Supabase
        """
        try:
            embedding = self.embed_model.get_text_embedding(document.text)
            document_data = {
                'content': document.text,
                'metadata': document.metadata,
                'embedding': embedding
            }
            
            result = self.client.table(self.table_name).insert(document_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            raise Exception(f"Error inserting document: {str(e)}")

    def batch_insert_documents(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Insert multiple documents into the vector store.
        
        Args:
            documents (List[Document]): List of Document objects
            
        Returns:
            List of responses from Supabase
        """
        try:
            document_data_list = []
            for doc in documents:
                embedding = self.embed_model.get_text_embedding(doc.text)
                document_data = {
                    'content': doc.text,
                    'metadata': doc.metadata,
                    'embedding': embedding
                }
                document_data_list.append(document_data)
            
            result = self.client.table(self.table_name).insert(document_data_list).execute()
            return result.data if result.data else []
        except Exception as e:
            raise Exception(f"Error batch inserting documents: {str(e)}")

    def query_documents(self, filters: Dict[str, Any] = None, 
                       page: int = 0, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Query documents with optional filters and pagination.
        
        Args:
            filters (Dict): Dictionary of filters to apply
            page (int): Page number (0-based)
            page_size (int): Number of items per page
            
        Returns:
            List of documents matching the query
        """
        try:
            query = self.client.table(self.table_name).select('*')
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            start = page * page_size
            end = start + page_size - 1
            result = query.range(start, end).execute()
            
            return result.data if result.data else []
        except Exception as e:
            raise Exception(f"Error querying documents: {str(e)}")

    def update_document(self, document_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a document by ID.
        
        Args:
            document_id (int): ID of the document to update
            updates (Dict): Dictionary of fields to update
            
        Returns:
            Updated document data
        """
        try:
            if 'content' in updates:
                updates['embedding'] = self.embed_model.get_text_embedding(updates['content'])
            
            result = self.client.table(self.table_name)\
                .update(updates)\
                .eq('id', document_id)\
                .execute()
            
            return result.data[0] if result.data else {}
        except Exception as e:
            raise Exception(f"Error updating document: {str(e)}")

    def delete_document(self, document_id: int) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id (int): ID of the document to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            result = self.client.table(self.table_name)\
                .delete()\
                .eq('id', document_id)\
                .execute()
            
            return bool(result.data)
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")

    def get_document_count(self) -> int:
        """
        Get the total number of documents in the store.
        
        Returns:
            int: Total number of documents
        """
        try:
            result = self.client.table(self.table_name)\
                .select('id', count='exact')\
                .execute()
            
            return result.count if hasattr(result, 'count') else 0
        except Exception as e:
            raise Exception(f"Error getting document count: {str(e)}")
            
    def check_table_exists(self) -> bool:
        """
        Check if the document_store table exists in Supabase.
        
        Returns:
            bool: True if the table exists, False otherwise
        """
        try:
            # Try to select from the table - if it exists, this will succeed
            self.client.table(self.table_name).select('id').limit(1).execute()
            return True
        except Exception as e:
            if 'relation "document_store" does not exist' in str(e):
                return False
            # If it's some other error, re-raise it
            raise e
            
    def create_index(self, embed_model=None):
        """
        Create a VectorStoreIndex from the documents in Supabase.
        
        Args:
            embed_model: Optional embedding model to use. If not provided, uses the default OpenAI model.
            
        Returns:
            VectorStoreIndex: The created index
        """
        from llama_index.core import VectorStoreIndex
        from llama_index.vector_stores.supabase import SupabaseVectorStore
        
        # Use the provided embed model or the default one
        if embed_model:
            self.embed_model = embed_model
            
        # Create vector store using simple setup
        from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
        from llama_index.core.storage.storage_context import StorageContext
        
        # Create an in-memory vector store
        storage_context = StorageContext.from_defaults()
        
        # Create and return the index
        return VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=self.embed_model
        )
        
    def add_documents(self, documents):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add
        """
        # Process documents in batches to avoid overwhelming the system
        batch_size = 10
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            self.batch_insert_documents(batch)
