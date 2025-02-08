from typing import List, Dict, Any, Optional
from supabase import Client, create_client
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_parse import LlamaParse

class VectorStoreManager:
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        postgres_connection: str,
        llama_cloud_api_key: Optional[str] = None,
        collection_name: str = "document_store"
    ):
        """Initialize the VectorStoreManager with necessary credentials.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            postgres_connection: Postgres connection string
            llama_cloud_api_key: Optional API key for LlamaParse
            collection_name: Name of the collection in Supabase
        """
        self.supabase_client = create_client(supabase_url, supabase_key)
        self.vector_store = SupabaseVectorStore(
            postgres_connection_string=postgres_connection,
            client=self.supabase_client,
            collection_name=collection_name
        )
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.embed_model = OpenAIEmbedding()
        
        if llama_cloud_api_key:
            self.parser = LlamaParse(
                api_key=llama_cloud_api_key,
                result_type="markdown",
                verbose=True
            )

    def parse_documents(self, directory_path: str) -> List[Document]:
        """Parse documents from a directory using LlamaParse.

        Args:
            directory_path: Path to directory containing documents

        Returns:
            List of parsed Document objects
        """
        if not hasattr(self, 'parser'):
            raise ValueError("LlamaParse API key not provided during initialization")

        file_extractor = {".pdf": self.parser}
        return SimpleDirectoryReader(
            directory_path,
            file_extractor=file_extractor
        ).load_data()

    def insert_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """Insert documents into Supabase vector store.

        Args:
            documents: List of Document objects to insert

        Returns:
            Dict containing success status and counts
        """
        success_count = 0
        error_count = 0

        for doc in documents:
            embedding = self.embed_model.get_text_embedding(doc.text)
            document_data = {
                'content': doc.text,
                'metadata': doc.metadata,
                'embedding': embedding
            }

            result = self.supabase_client.table('document_store').insert(document_data).execute()
            if hasattr(result, 'error') and result.error is not None:
                error_count += 1
            else:
                success_count += 1

        return {
            'total_documents': len(documents),
            'successful_insertions': success_count,
            'failed_insertions': error_count
        }

    def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """Create a vector store index from documents.

        Args:
            documents: List of Document objects

        Returns:
            VectorStoreIndex object
        """
        # Use the existing storage context to maintain persistence
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=self.storage_context,
            embed_model=self.embed_model
        )
        
        # Persist the storage context
        self.storage_context.persist()
        
        return index

    def get_document_count(self) -> int:
        """Get the total number of documents in the vector store.

        Returns:
            Total number of documents
        """
        result = self.supabase_client.table('document_store').select('*').execute()
        if hasattr(result, 'error') and result.error is not None:
            raise Exception(f"Error checking documents: {result.error}")
        return len(result.data) if result.data else 0

    def load_documents_from_store(self) -> List[Document]:
        """Load all documents from the vector store in Supabase and return them as Document objects."""
        result = self.supabase_client.table('document_store').select('*').execute()
        if hasattr(result, 'error') and result.error is not None:
            raise Exception(f"Error loading documents: {result.error}")

        documents = []
        if result.data:
            for record in result.data:
                # Assuming record has 'content' and 'metadata' keys
                documents.append(Document(text=record.get('content', ''), metadata=record.get('metadata', {})))
        return documents

    def hybrid_search(self, query: str, content_type: Optional[str] = None, top_k: int = 5) -> List[Document]:
        """Perform hybrid search combining semantic and keyword search with metadata filtering.
        
        Args:
            query: Search query
            content_type: Optional filter for specific content types
            top_k: Number of results to return
            
        Returns:
            List of relevant Document objects
        """
        # Generate query embedding
        query_embedding = self.embed_model.get_text_embedding(query)
        
        # Build base query
        base_query = self.supabase_client.table('document_store')
        
        # Add content type filter if specified
        if content_type:
            base_query = base_query.eq('metadata->>content_type', content_type)
        
        # Combine semantic search with keyword matching
        # Note: This assumes Supabase is configured with pg_vector extension
        result = base_query.select('*').order(
            'embedding <-> $1::vector',
            'content ILIKE $2',
            ascending=[True, True],
            foreign_table={'embedding': query_embedding, 'pattern': f'%{query}%'}
        ).limit(top_k).execute()
        
        if hasattr(result, 'error') and result.error is not None:
            raise Exception(f"Error performing hybrid search: {result.error}")
            
        documents = []
        if result.data:
            for record in result.data:
                documents.append(Document(
                    text=record.get('content', ''),
                    metadata=record.get('metadata', {})
                ))
        
        return documents
