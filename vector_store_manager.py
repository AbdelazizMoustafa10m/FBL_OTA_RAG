from typing import List, Dict, Any, Optional
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import uuid
import os

class VectorStoreManager:
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        collection_name: str = "FBL_RAG",  # Changed default collection name as requested
        local_path: Optional[str] = None,
        llama_cloud_api_key: Optional[str] = None
    ):
        """Initialize the VectorStoreManager with necessary credentials.

        Args:
            qdrant_url: Qdrant server URL (for cloud deployment)
            qdrant_api_key: Qdrant API key (for cloud deployment)
            collection_name: Name of the collection in Qdrant
            local_path: Path to store Qdrant data locally (if not using cloud)
            llama_cloud_api_key: Optional API key for LlamaParse
        """
        # Set up Qdrant client based on whether we're using cloud or local
        if qdrant_url and qdrant_api_key:
            # Cloud Qdrant
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            )
            self.using_cloud = True
        else:
            # Local Qdrant
            local_path = local_path or "./qdrant_data"
            self.client = QdrantClient(path=local_path)
            self.using_cloud = False
        
        self.collection_name = collection_name
        
        # Ensure the collection exists before proceeding
        self._ensure_collection_exists()
        
        # Initialize vector store with the client
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name
        )
        
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.embed_model = OpenAIEmbedding()
        
        # Initialize LlamaParse if API key is provided
        if llama_cloud_api_key:
            self.parser = LlamaParse(
                api_key=llama_cloud_api_key,
                result_type="markdown",
                verbose=True
            )

    def _ensure_collection_exists(self):
        """Ensure the Qdrant collection exists, create it if it doesn't."""
        try:
            # Check if the collection exists by getting all collections
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if not collection_exists:
                print(f"Collection '{self.collection_name}' not found. Creating now...")
                # Create the collection with appropriate settings for OpenAI embeddings
                vector_size = 1536  # OpenAI embedding dimension
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Successfully created collection '{self.collection_name}'")
            else:
                print(f"Using existing collection '{self.collection_name}'")
        except Exception as e:
            print(f"Error checking/creating collection: {e}")
            raise

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
        """Insert documents into Qdrant vector store.

        Args:
            documents: List of Document objects to insert

        Returns:
            Dict containing success status and counts
        """
        success_count = 0
        error_count = 0

        try:
            # Prepare documents with embeddings
            for doc in documents:
                try:
                    # Generate embedding for the document
                    embedding = self.embed_model.get_text_embedding(doc.text)
                    
                    # Prepare payload with text and metadata
                    payload = {
                        'text': doc.text, 
                        'metadata': doc.metadata if doc.metadata else {}
                    }
                    
                    # Insert into Qdrant
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=[{
                            'id': str(uuid.uuid4()),
                            'vector': embedding,
                            'payload': payload
                        }]
                    )
                    success_count += 1
                except Exception as e:
                    print(f"Error inserting document: {e}")
                    error_count += 1
        except Exception as e:
            print(f"Batch insertion error: {e}")
            error_count += len(documents) - success_count

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
        # Get collection info from Qdrant to determine document count
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.vectors_count
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0

    def load_documents_from_store(self) -> List[Document]:
        """Load all documents from the vector store and return them as Document objects."""
        # Qdrant doesn't have a direct method to retrieve all documents
        # So we'll use a full scroll search with a high limit
        try:
            records = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Adjust this based on your expected collection size
                with_payload=True,
                with_vectors=False  # We don't need the vectors for document retrieval
            )[0]  # The scroll method returns a tuple (records, next_page_offset)
            
            documents = []
            for record in records:
                payload = record.payload
                if payload and 'text' in payload:
                    # Convert Qdrant payload back to a Document object
                    documents.append(Document(
                        text=payload.get('text', ''), 
                        metadata=payload.get('metadata', {})
                    ))
            
            return documents
        except Exception as e:
            print(f"Error loading documents from store: {e}")
            return []

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
        
        # Set up metadata filter if content_type is specified
        filter_conditions = None
        if content_type:
            filter_conditions = {
                "must": [
                    {
                        "key": "metadata.content_type",
                        "match": {
                            "value": content_type
                        }
                    }
                ]
            }
        
        try:
            # Perform vector search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                filter=filter_conditions,
                with_payload=True
            )
            
            # Convert search results to Document objects
            documents = []
            for result in search_results:
                if result.payload and 'text' in result.payload:
                    documents.append(Document(
                        text=result.payload.get('text', ''),
                        metadata=result.payload.get('metadata', {})
                    ))
            
            return documents
        except Exception as e:
            print(f"Error performing hybrid search: {e}")
            return []