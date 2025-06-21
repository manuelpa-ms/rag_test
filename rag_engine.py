from langchain_ollama import OllamaLLM
from typing import List, Dict, Any

class RAGEngine:
    def __init__(self, model_name: str = "qwen3:8b"):
        """Initialize the RAG engine with Ollama."""
        self.llm = OllamaLLM(
            model=model_name,
            base_url="http://localhost:11434"
        )
        self.model_name = model_name
    
    def generate_answer(self, question: str, relevant_docs: List[Dict[str, Any]]) -> str:
        """Generate an answer based on the question and relevant documents."""
        
        # Prepare context from relevant documents
        context_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            filename = doc['metadata'].get('filename', 'Unknown')
            content = doc['content']
            context_parts.append(f"Document {i} ({filename}):\n{content}\n")
        
        context = "\n".join(context_parts)
        
        # Create the prompt
        prompt = self._create_prompt(question, context)
        
        try:
            # Generate response
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}. Please make sure Ollama is running and the model '{self.model_name}' is available."
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create a prompt for the LLM."""
        prompt = f"""You are a helpful assistant that answers questions based on the provided documents. 
Use only the information from the provided documents to answer the question. 
If the answer cannot be found in the documents, say so clearly.

Context from documents:
{context}

Question: {question}

Answer: """
        
        return prompt
    
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = self.llm.invoke("Hello")
            return True
        except Exception:
            return False
    
    def list_available_models(self) -> List[str]:
        """List available Ollama models (placeholder for now)."""
        # This would require making an API call to Ollama
        # For now, return common models
        return ["llama3.2", "llama3.1", "mistral", "codellama", "phi3"]
