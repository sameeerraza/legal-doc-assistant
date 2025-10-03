from dotenv import load_dotenv
import logging
import os

# ==================== Configuration ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """Centralized configuration for the legal chatbot."""
    
    # Load environment variables
    load_dotenv()
    
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    # LLM Configuration
    LLM_MODEL = "gemini-2.5-flash"
    LLM_TEMPERATURE = 0.1  # Low temperature for consistent legal analysis
    
    # Document Processing
    SUPPORTED_FORMATS = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    MAX_DOCUMENT_SIZE_MB = 50
    DEFAULT_DPI = 300  # DPI for PDF to image conversion
    OCR_CONFIG = r'--oem 3 --psm 6'  # Tesseract configuration
    
    # Legal Domain Settings
    LEGAL_CONTEXT = """US Collection Agency - Legal Department
    Focus areas: FDCPA compliance, TCPA regulations, state collection laws,
    consumer rights, debt validation, cease and desist clauses."""