# Local RAG with Ollama

A local Retrieval Augmented Generation (RAG) application powered by Ollama that processes Word and OneNote documents and allows you to ask questions about their content.

## Features

- 📁 Upload and process Word (.docx) and OneNote (.one) files
- 🧠 Uses local LLM via Ollama (no data sent to external services)
- 💾 Caches processed documents to avoid reprocessing
- 🔍 Vector similarity search using ChromaDB
- 💬 Interactive chat interface with Streamlit
- 📊 Document statistics and source references

## Prerequisites

1. **Python 3.8+**
2. **Ollama installed and running**
   - Download from: https://ollama.ai/
   - After installation, pull a model: `ollama pull llama3.2`

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd c:\Users\Manuel\Documents\Projects\rag_test
   ```

2. **Activate your virtual environment**
   ```bash
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. **Start Ollama** (if not already running)
   ```bash
   ollama serve
   ```

2. **Pull a model** (if you haven't already)
   ```bash
   ollama pull llama3.2
   ```

## Running the Application

1. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to http://localhost:8501

## Usage

1. **Upload Documents**: Use the sidebar to upload Word (.docx) files
2. **Process Files**: Click "Process Files" to extract text and create embeddings
3. **Ask Questions**: Type questions about your documents in the main area
4. **View Sources**: Expand "Source Documents" to see which parts of your documents were used

## File Structure

```
rag_test/
├── app.py                 # Main Streamlit application
├── document_processor.py  # Document processing logic
├── vector_store.py       # ChromaDB vector store wrapper
├── rag_engine.py         # Ollama LLM integration
├── requirements.txt      # Python dependencies
├── cache/               # Cached processed documents
└── chroma_db/          # ChromaDB vector database
```

## Supported File Types

- ✅ **Word Documents (.docx)**: Full text extraction from paragraphs and tables
- 📄 **PDF Files (.pdf)**: Text extraction from all pages with page number references
- 🔄 **OneNote (.one)**: Placeholder (requires additional setup)

## PDF Support

The RAG application now supports PDF files in addition to Word documents (.docx). Here's what you need to know:

### Supported File Types
- **Word Documents (.docx)** - Full text extraction from paragraphs and tables
- **PDF Files (.pdf)** - Text extraction from all pages with page number references
- **OneNote Files (.one)** - Limited support (export to supported format recommended)

### PDF Processing Features
- Extracts text from all pages in the PDF
- Handles multi-page documents efficiently
- Includes page number references in extracted text (e.g., [Page 1], [Page 2])
- Robust error handling for problematic pages
- Supports both text-based and OCR-readable PDFs
- Automatic text chunking with configurable overlap

### PDF Processing Notes
- Scanned PDFs without OCR text layers may not extract text properly
- Complex layouts, tables, and images are converted to plain text
- Password-protected PDFs are not currently supported
- Very large PDFs are processed in chunks to optimize memory usage

### Dependencies
The PDF support requires the `pypdf` library which has been added to requirements.txt.

## Configuration

You can modify the following in the respective files:

- **Model**: Change the model in `rag_engine.py` (default: llama3.2)
- **Chunk Size**: Adjust chunking parameters in `document_processor.py`
- **Vector Store**: Modify ChromaDB settings in `vector_store.py`

## Troubleshooting

### Ollama Not Running
- Make sure Ollama is installed and running: `ollama serve`
- Check if the model is available: `ollama list`

### Import Errors
- Make sure you're in the virtual environment: `.venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`

### OneNote Files
- OneNote processing is currently a placeholder
- For full OneNote support, additional libraries would be needed

## Future Enhancements

- [ ] Better text chunking strategies
- [ ] OneNote file processing
- [ ] PDF support
- [ ] Advanced metadata extraction
- [ ] Query history
- [ ] Multi-model support
- [ ] Batch processing
