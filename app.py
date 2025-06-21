import streamlit as st
import os
import hashlib
import pickle
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import shutil

from document_processor import DocumentProcessor
from vector_store import VectorStore
from rag_engine import RAGEngine

class RAGApp:
    def __init__(self):
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.rag_engine = RAGEngine()
        
    def parse_thinking_mode(self, text: str) -> Dict[str, str]:
        """Parse text that may contain <think></think> tags."""
        import re
        
        # Pattern to match <think>...</think> content
        think_pattern = r'<think>(.*?)</think>'
        
        # Find thinking content
        think_matches = re.findall(think_pattern, text, re.DOTALL)
        thinking_content = think_matches[0].strip() if think_matches else ""
        
        # Remove thinking tags from the main content
        clean_text = re.sub(think_pattern, '', text, flags=re.DOTALL).strip()
        
        return {
            'thinking': thinking_content,
            'answer': clean_text
        }
        
    def get_file_hash(self, file_path: str) -> str:
        """Generate hash for file to check if it's been processed before."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def is_file_processed(self, file_hash: str) -> bool:
        """Check if file has been processed before."""
        cache_file = self.cache_dir / f"{file_hash}.pkl"
        return cache_file.exists()
    
    def save_processed_file(self, file_hash: str, chunks: List[str], metadata: Dict[str, Any]):
        """Save processed file chunks to cache."""
        cache_file = self.cache_dir / f"{file_hash}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump({'chunks': chunks, 'metadata': metadata}, f)
    
    def load_processed_file(self, file_hash: str) -> Dict[str, Any]:
        """Load processed file chunks from cache."""
        cache_file = self.cache_dir / f"{file_hash}.pkl"
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

def main():
    st.set_page_config(
        page_title="Local RAG with Ollama",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Local RAG with Ollama")
    st.markdown("Upload documents and ask questions using local LLM powered by Ollama")
    
    # Initialize the app
    if 'rag_app' not in st.session_state:
        st.session_state.rag_app = RAGApp()
    
    rag_app = st.session_state.rag_app
    
    # Sidebar for file upload and previously processed documents
    with st.sidebar:
        st.header("📁 Document Upload")
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['docx', 'one'],  # Word and OneNote files
            accept_multiple_files=True,
            help="Upload Word (.docx) and OneNote (.one) files"
        )
        if uploaded_files:
            st.success(f"Uploaded {len(uploaded_files)} file(s)")
            # Process files button
            if st.button("🔄 Process Files", type="primary"):
                with st.spinner("Processing files..."):
                    processed_count = 0
                    cached_count = 0
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    for i, uploaded_file in enumerate(uploaded_files):
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name
                        try:
                            # Check if file has been processed before
                            file_hash = rag_app.get_file_hash(tmp_path)
                            status_text.text(f"Processing {uploaded_file.name}...")
                            if rag_app.is_file_processed(file_hash):
                                # Load from cache
                                cached_data = rag_app.load_processed_file(file_hash)
                                chunks = cached_data['chunks']
                                metadata = cached_data['metadata']
                                cached_count += 1
                                st.info(f"✅ {uploaded_file.name} loaded from cache")
                            else:
                                # Process the file
                                chunks, metadata = rag_app.doc_processor.process_file(tmp_path, uploaded_file.name)
                                # Save to cache
                                rag_app.save_processed_file(file_hash, chunks, metadata)
                                processed_count += 1
                                st.success(f"✅ {uploaded_file.name} processed successfully")
                            # Add to vector store
                            rag_app.vector_store.add_documents(chunks, metadata)
                        except Exception as e:
                            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                        finally:
                            # Clean up temp file
                            os.unlink(tmp_path)
                        # Update progress
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    status_text.text("Processing complete!")
                    if processed_count > 0:
                        st.success(f"Processed {processed_count} new file(s)")
                    if cached_count > 0:
                        st.info(f"Loaded {cached_count} file(s) from cache")        # Show previously processed documents
        st.markdown("---")
        st.subheader("📁 Previously Processed Documents")
        cache_dir = Path("cache")
        processed_files = list(cache_dir.glob("*.pkl"))
        if processed_files:
            for cache_file in processed_files:
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    meta = data.get('metadata', {})
                    filename = meta.get('filename', cache_file.stem)
                    file_type = meta.get('file_type', 'unknown')
                    note = meta.get('note', '')
                      # Create columns for filename and remove button
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{filename}** ({file_type})")
                        if note:
                            st.caption(note)
                    with col2:
                        if st.button("❌", key=f"remove_{cache_file.stem}", help=f"Remove {filename} from cache"):
                            try:
                                # Remove from vector store first
                                removed_chunks = rag_app.vector_store.remove_documents_by_filename(filename)
                                
                                # Remove from cache
                                cache_file.unlink()
                                
                                st.success(f"Removed {filename} from cache and vector store ({removed_chunks} chunks)")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error removing file: {e}")
                except Exception as e:
                    st.caption(f"[Error loading {cache_file.name}: {e}]")
        else:
            st.caption("No previously processed documents found.")
      # Main content area
    st.header("💬 Ask Questions")
    
    # Check if vector store has documents
    if not rag_app.vector_store.has_documents():
        st.info("👆 Please upload and process some documents first to start asking questions.")
        return
    
    # Question input using chat_input for better UX
    question = st.chat_input("Ask a question about your documents...")
    
    if question:
        # Display the question
        with st.chat_message("user"):
            st.write(question)
        
        # Generate and display answer immediately
        with st.chat_message("assistant"):
            with st.spinner("Generating answer..."):
                try:
                    # Get relevant documents
                    relevant_docs = rag_app.vector_store.similarity_search(question, k=5)                    # Generate answer
                    answer = rag_app.rag_engine.generate_answer(question, relevant_docs)
                    
                    # Parse thinking mode content
                    parsed_content = rag_app.parse_thinking_mode(answer)
                    
                    # 1. Display thinking content in collapsible section if present
                    if parsed_content['thinking']:
                        with st.expander("🤔 LLM Thinking Process", expanded=False):
                            st.markdown(parsed_content['thinking'])
                    
                    # 2. Display sources
                    with st.expander("📚 Source Documents", expanded=False):
                        for i, doc in enumerate(relevant_docs, 1):
                            st.markdown(f"**Source {i}:** {doc['metadata'].get('filename', 'Unknown')}")
                            st.markdown(f"```\n{doc['content'][:300]}...\n```")
                    
                    # 3. Display the main answer
                    st.markdown("### Answer")
                    if parsed_content['answer']:
                        st.markdown(parsed_content['answer'])
                    else:
                        # Fallback if no thinking tags found
                        st.markdown(answer)
                
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
    
    # Display current documents in vector store
    with st.expander("📊 Document Statistics"):
        stats = rag_app.vector_store.get_stats()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Documents", stats.get('total_docs', 0))
        with col2:
            st.metric("Total Chunks", stats.get('total_chunks', 0))
        with col3:
            st.metric("Unique Files", stats.get('unique_files', 0))

if __name__ == "__main__":
    main()
