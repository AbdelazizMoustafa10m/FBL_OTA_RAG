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
        """Initialize DocumentProcessor with a VectorStoreManager instance.
        
        Args:
            vector_store_manager (VectorStoreManager): Instance of VectorStoreManager
        """
        self.vector_store_manager = vector_store_manager
        self.processed_files_path = Path("processed_files.json")
        self.data_dir = Path("./data")
        # We'll use the parser from vector_store_manager
        self.parser = vector_store_manager.parser

    def _extract_section_header(self, text: str) -> str:
        """Extract section header from text chunk."""
        lines = text.split('\n')
        for line in lines[:2]:  # Check first two lines
            # Look for common section header patterns
            if any(pattern in line.lower() for pattern in ['class', 'section', 'chapter']):
                return line.strip()
        return ''

    def _identify_content_type(self, text: str) -> str:
        """Identify the type of content in the chunk."""
        text_lower = text.lower()
        if 'security class' in text_lower:
            return 'security_class_definition'
        elif any(word in text_lower for word in ['example', 'usage']):
            return 'example'
        elif any(word in text_lower for word in ['warning', 'caution', 'note']):
            return 'notice'
        return 'general'

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
        
        # Initialize text splitter with enhanced chunking strategy
        text_splitter = SentenceSplitter(
            chunk_size=512,
            chunk_overlap=150,  # Increased overlap for better context
            include_metadata=True
        )

        # Process each document individually with error handling
        for file_path in new_file_paths:
            try:
                print(f"Processing document: {file_path}")
                file_extractor = {".pdf": self.parser}
                
                # Process single document
                reader = SimpleDirectoryReader(
                    input_files=[file_path],  # Process just one file
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
                        # Enhance metadata with section and content type information
                        enhanced_metadata = node.metadata.copy() if node.metadata else {}
                        enhanced_metadata.update({
                            'section': self._extract_section_header(node.text),
                            'content_type': self._identify_content_type(node.text)
                        })
                        processed_documents.append(Document(text=node.text, metadata=enhanced_metadata))
                
                # Insert documents into the vector store
                result = self.vector_store_manager.insert_documents(processed_documents)
                
                if result['failed_insertions'] > 0:
                    print(f"Warning: {result['failed_insertions']} documents failed to insert for {file_path}")
                    success = False
                else:
                    print(f"Successfully inserted {result['successful_insertions']} documents for {file_path}")
                    # Only mark as processed if successful
                    processed_files.add(file_path)
                    self.save_processed_files(processed_files)
                    
            except Exception as e:
                print(f"Error processing document {file_path}: {e}")
                success = False
                # Continue with next document
        
        return success

    def get_all_documents(self) -> List[Document]:
        """Get all processed documents from the vector store directly using the load_documents_from_store method."""
        try:
            return self.vector_store_manager.load_documents_from_store()
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []