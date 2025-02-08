from pathlib import Path
from typing import List, Set
import json
from llama_index.core import Document
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import MetadataMode
import os
from vector_store_manager import VectorStoreManager

class DocumentProcessor:
    def __init__(self, vector_store_manager: VectorStoreManager):
        """
        Initialize DocumentProcessor with a VectorStoreManager instance.
        
        Args:
            vector_store_manager (VectorStoreManager): Instance of VectorStoreManager
        """
        self.vector_store_manager = vector_store_manager
        self.processed_files_path = Path("processed_files.json")
        self.data_dir = Path("./data")
        self.parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
            result_type="markdown",
            verbose=True
        )

    def get_processed_files(self) -> Set[str]:
        """Get the set of files that have already been processed"""
        if self.processed_files_path.exists():
            with open(self.processed_files_path, "r") as f:
                return set(json.load(f))
        return set()

    def save_processed_files(self, processed_files: Set[str]) -> None:
        """Save the set of processed files"""
        with open(self.processed_files_path, "w") as f:
            json.dump(list(processed_files), f)

    def get_new_documents(self) -> List[str]:
        """Get paths of new documents that haven't been processed yet"""
        processed_files = self.get_processed_files()
        
        # Get all PDF files in the data directory
        current_files = {str(f.absolute()) for f in self.data_dir.glob("**/*.pdf")}
        
        # Find new files that haven't been processed
        new_files = current_files - processed_files
        
        if not new_files:
            print("No new documents to process")
            return []
        
        print(f"Found {len(new_files)} new documents to process")
        return list(new_files)

    def process_documents(self) -> bool:
        """
        Process new documents and add them to the vector store
        Returns:
            bool: True if processing was successful, False otherwise
        """
        new_file_paths = self.get_new_documents()
        if not new_file_paths:
            return True

        print("Processing new documents...")
        processed_files = self.get_processed_files()
        success = True

        # Load documents using SimpleDirectoryReader with LlamaParse
        file_extractor = {".pdf": self.parser}
        try:
            # Initialize text splitter for better chunking
            text_splitter = SentenceSplitter(
                chunk_size=512,
                chunk_overlap=50,
                include_metadata=True
            )
            
            # Load and process documents
            reader = SimpleDirectoryReader(
                input_files=new_file_paths,
                file_extractor=file_extractor,
                filename_as_id=True
            )
            documents = reader.load_data()
            
            # Split documents into smaller chunks while preserving metadata
            processed_documents = []
            for doc in documents:
                nodes = text_splitter.get_nodes_from_documents([doc])
                # Convert nodes back to documents while preserving metadata
                for node in nodes:
                    processed_documents.append(Document(text=node.text, metadata=node.metadata))
            
            # Batch insert processed documents into vector store
            self.vector_store_manager.batch_insert_documents(processed_documents)
            
            # Update processed files list
            processed_files.update(new_file_paths)
            self.save_processed_files(processed_files)
            
            print(f"Successfully processed {len(documents)} documents")
        except Exception as e:
            print(f"Error processing documents: {str(e)}")
            success = False

        return success
