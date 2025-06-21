import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid

class VectorStore:
    def __init__(self, collection_name: str = "rag_documents"):
        """Initialize ChromaDB vector store."""
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = collection_name
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_documents(self, chunks: List[str], metadata: Dict[str, Any]):
        """Add document chunks to the vector store."""
        if not chunks:
            return
        
        # Generate unique IDs for each chunk
        ids = [str(uuid.uuid4()) for _ in chunks]
        
        # Create metadata for each chunk
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = i
            chunk_metadata['chunk_id'] = ids[i]
            metadatas.append(chunk_metadata)
        
        # Add to collection
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        # Format results
        documents = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                doc = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if results['distances'] else None
                }
                documents.append(doc)
        
        return documents
    
    def has_documents(self) -> bool:
        """Check if the vector store has any documents."""
        try:
            count = self.collection.count()
            return count > 0
        except:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        try:
            total_chunks = self.collection.count()
            
            # Get all metadata to calculate unique files
            all_results = self.collection.get()
            unique_files = set()
            
            if all_results['metadatas']:
                for metadata in all_results['metadatas']:
                    if 'filename' in metadata:
                        unique_files.add(metadata['filename'])
            
            return {
                'total_chunks': total_chunks,
                'unique_files': len(unique_files),
                'total_docs': len(unique_files)  # Same as unique_files for now
            }
        except:
            return {
                'total_chunks': 0,
                'unique_files': 0,
                'total_docs': 0
            }
    
    def clear(self):
        """Clear all documents from the vector store."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except:
            pass
    
    def remove_documents_by_filename(self, filename: str):
        """Remove all documents with the specified filename from the vector store."""
        try:
            # Get all documents
            all_results = self.collection.get()
            
            # Find IDs of documents with matching filename
            ids_to_remove = []
            if all_results['metadatas']:
                for i, metadata in enumerate(all_results['metadatas']):
                    if metadata.get('filename') == filename:
                        ids_to_remove.append(all_results['ids'][i])
            
            # Remove the documents
            if ids_to_remove:
                self.collection.delete(ids=ids_to_remove)
                return len(ids_to_remove)
            return 0
        except Exception as e:
            print(f"Error removing documents for {filename}: {e}")
            return 0
