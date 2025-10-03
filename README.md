# Legal Document Assistant

> AI-powered legal document review chatbot specialized in debt collection compliance analysis

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-latest-green.svg)](https://python.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-latest-red.svg)](https://streamlit.io/)

## Overview

Legal Document Assistant is an enterprise-grade AI chatbot designed for legal departments in debt collection agencies. It provides automated analysis of legal documents with specialized focus on FDCPA (Fair Debt Collection Practices Act) and TCPA (Telephone Consumer Protection Act) compliance.

### Key Features

- **Advanced OCR Processing**: Handles both native and scanned PDFs with automatic rotation detection
- **Multi-Agent Architecture**: Specialized agents for different query types using LangGraph
- **Compliance Checking**: Automated FDCPA and TCPA compliance analysis
- **Risk Assessment**: Identify legal risks and liabilities in documents
- **Clause Extraction**: Find and analyze specific contractual clauses
- **Document Summarization**: Generate comprehensive legal summaries
- **Interactive UI**: Clean Streamlit interface with document management

### Supported Document Formats

- PDF (native text and scanned/image-based)
- PNG, JPG, JPEG, TIFF, BMP

## Architecture

```
User Query → Classifier → Router → Specialized Agent → Response
                                    ├─ Clause Extractor
                                    ├─ Compliance Checker
                                    ├─ Document Summarizer
                                    ├─ Risk Assessor
                                    └─ General Assistant
```

The system uses a multi-agent workflow powered by LangGraph, with Google's Gemini 2.5 Flash model for language understanding.

## Installation

### Prerequisites

- Python 3.9 or higher
- Tesseract OCR installed on your system
- Google API key (Gemini)

### Install Tesseract

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

### Python Dependencies

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/legal-doc-assistant.git
cd legal-doc-assistant

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

### Streamlit Web Interface

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

### Command Line Interface

```bash
python main.py
```

**CLI Commands:**
- `load <filepath>` - Load a document
- `info` - Show current document information
- `clear` - Clear loaded document
- `exit` - Exit the application

### Example Queries

```
"Check this document for FDCPA compliance issues"
"Extract all payment terms and deadlines"
"Conduct a risk assessment for litigation exposure"
"Summarize the key obligations in this contract"
"Find cease and desist clauses"
```

## Project Structure

```
legal_chatbot/
├── agents/
│   └── classifier.py       # Multi-agent nodes and routing logic
├── chatbot/
│   └── chatbot.py         # Main chatbot interface
├── document_processing/
│   └── processor.py       # OCR and document extraction
├── models/
│   └── query_models.py    # Pydantic models and state definitions
├── workflow/
│   └── graph.py           # LangGraph workflow construction
├── app.py                 # Streamlit UI
├── config.py              # Configuration and constants
└── main.py               # CLI entry point
```

## Configuration

Edit `config.py` to adjust:

- **LLM Model**: Default is `gemini-2.5-flash`
- **Temperature**: Set to 0.1 for consistent legal analysis
- **DPI**: 300 DPI for scanned PDF processing
- **Document Size Limit**: 50MB maximum
- **OCR Configuration**: Tesseract parameters

## Features Deep Dive

### OCR Processing

- **Automatic Rotation Detection**: Uses Tesseract OSD with fallback to edge detection
- **Image Preprocessing**: Denoising and adaptive thresholding
- **Smart PDF Handling**: Attempts native extraction before falling back to OCR
- **Multi-page Support**: Processes multiple pages with page markers

### Query Classification

The system automatically classifies queries into:
- Clause Search
- Compliance Check
- Document Summary
- Risk Assessment
- General Inquiry

### Specialized Agents

Each agent is optimized for specific legal analysis tasks:

- **Clause Extractor**: Identifies and quotes specific contractual terms
- **Compliance Checker**: Analyzes FDCPA, TCPA, and state law compliance
- **Summarizer**: Creates structured legal summaries
- **Risk Assessor**: Evaluates litigation exposure and regulatory risks
- **General Assistant**: Handles other legal inquiries

## Security Considerations

- Never commit `.env` files or API keys
- Documents are processed in-memory and cleared on reset
- No persistent storage of sensitive documents
- Use appropriate access controls in production

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black legal_chatbot/

# Lint
pylint legal_chatbot/
```

## Limitations

- Maximum document size: 50MB
- OCR accuracy depends on document quality
- Requires active internet connection for LLM API
- Not a substitute for professional legal review

## Acknowledgments

- Built with LangChain and LangGraph
- Powered by Google Gemini API
- OCR by Tesseract
- UI framework: Streamlit

## Support

For questions or issues:
- Internal: Contact Legal Tech Team
- Technical issues: Create an issue in this repository

---

**Version:** 2.0.0  
**Author:** Legal Tech Team  
**Last Updated:** 2025