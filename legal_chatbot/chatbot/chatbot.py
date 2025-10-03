from typing import Optional
from legal_chatbot.config import Config, logger
from langchain_core.messages import HumanMessage
from legal_chatbot.workflow.graph import build_legal_graph
from legal_chatbot.document_processing.processor import AdvancedDocumentProcessor
from legal_chatbot.models.query_models import LegalChatState

class LegalChatbot:
    """Main chatbot interface with advanced document management."""
    
    def __init__(self, tesseract_path: Optional[str] = None, dpi: int = Config.DEFAULT_DPI):
        """
        Initialize the legal chatbot.
        
        Args:
            tesseract_path: Path to Tesseract executable (optional)
            dpi: DPI for scanned PDF processing
        """
        self.graph = build_legal_graph()
        self.state: LegalChatState = {
            "messages": [],
            "query_type": None,
            "document_content": None,
            "document_metadata": None,
            "analysis_results": None,
            "routing_decision": None
        }
        self.doc_processor = AdvancedDocumentProcessor(
            tesseract_path=tesseract_path,
            dpi=dpi
        )
    
    def load_document(self, file_path: str) -> str:
        """
        Load and process a legal document with advanced OCR.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Confirmation message
        """
        try:
            text, metadata = self.doc_processor.process_document(file_path)
            self.state["document_content"] = text
            self.state["document_metadata"] = metadata
            
            return f"""
✓ Document loaded successfully!

File: {metadata['filename']}
Type: {metadata['file_type']}
Size: {metadata['size_mb']} MB
Words: {metadata['word_count']:,}
Characters: {metadata['char_count']:,}
DPI: {metadata.get('dpi_used', 'N/A')}

You can now ask questions about this document.
            """.strip()
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            return f"✗ Error loading document: {str(e)}"
    
    def clear_document(self) -> str:
        """Clear the currently loaded document."""
        self.state["document_content"] = None
        self.state["document_metadata"] = None
        return "✓ Document cleared from memory."
    
    def show_document_info(self) -> str:
        """Display information about the currently loaded document."""
        if not self.state["document_content"]:
            return "No document currently loaded."
        
        metadata = self.state["document_metadata"]
        return f"""
Current Document:
  File: {metadata['filename']}
  Type: {metadata['file_type']}
  Size: {metadata['size_mb']} MB
  Words: {metadata['word_count']:,}
  Characters: {metadata['char_count']:,}
        """.strip()
    
    def process_query(self, user_input: str) -> str:
        """
        Process a user query through the legal chatbot graph.
        
        Args:
            user_input: The user's question or request
            
        Returns:
            The assistant's response
        """
        # Add user message to state
        self.state["messages"].append(HumanMessage(content=user_input))
        
        # Run through graph
        self.state = self.graph.invoke(self.state)
        
        # Return last assistant message
        if self.state["messages"]:
            last_message = self.state["messages"][-1]
            return last_message.content
        
        return "Error: No response generated."
    
    def run(self):
        """Run the interactive chatbot CLI."""
        print("=" * 70)
        print("LEGAL DOCUMENT REVIEW CHATBOT")
        print("SueBot ⚖️ - Always 'ready to sue.'")
        print("=" * 70)
        print("\nCommands:")
        print("  load <filepath>  - Load a legal document (PDF/Image)")
        print("  info            - Show current document info")
        print("  clear           - Clear current document")
        print("  exit            - Exit the chatbot")
        print("\nSupported: PDF (native & scanned), PNG, JPG, TIFF, BMP")
        print("=" * 70)
        print()
        
        while True:
            try:
                user_input = input("\n📋 Query: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == "exit":
                    print("\n✓ Exiting chatbot. Goodbye!")
                    break
                
                elif user_input.lower() == "clear":
                    print(self.clear_document())
                    continue
                
                elif user_input.lower() == "info":
                    print(self.show_document_info())
                    continue
                
                elif user_input.lower().startswith("load "):
                    file_path = user_input[5:].strip()
                    print("\n⏳ Processing document...")
                    print(self.load_document(file_path))
                    continue
                
                # Process query
                print("\n⚖️  Analyzing...\n")
                response = self.process_query(user_input)
                print(f"Assistant:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n✓ Exiting chatbot. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                print(f"\n✗ Error: {str(e)}")
