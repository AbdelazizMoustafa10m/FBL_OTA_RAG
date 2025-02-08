from vector_store_manager import VectorStoreManager
from document_processor import DocumentProcessor
import os
from dotenv import load_dotenv

load_dotenv()

vector_manager = VectorStoreManager()
doc_processor = DocumentProcessor(vector_manager)
doc_processor.process_documents()

count = vector_manager.get_document_count()
print(f"Documents in vector store: {count}")