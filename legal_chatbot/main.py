from chatbot.chatbot import LegalChatbot
from config import Config
import argparse

def main():
    """
    Application entry point with command-line arguments.
    """
    
    parser = argparse.ArgumentParser(
        description='Legal Document Review Chatbot with Advanced OCR'
    )
    parser.add_argument(
        '-t', '--tesseract-path',
        help='Path to Tesseract executable (if not in PATH)'
    )
    parser.add_argument(
        '-d', '--dpi',
        type=int,
        default=Config.DEFAULT_DPI,
        help=f'DPI for PDF to image conversion (default: {Config.DEFAULT_DPI})'
    )
    parser.add_argument(
        '--load',
        help='Load a document at startup'
    )
    
    args = parser.parse_args()
    
    # Initialize chatbot
    chatbot = LegalChatbot(
        tesseract_path=args.tesseract_path,
        dpi=args.dpi
    )
    
    # Load document if provided
    if args.load:
        print("\n⏳ Loading document at startup...")
        print(chatbot.load_document(args.load))
    
    # Run interactive session
    chatbot.run()


if __name__ == "__main__":
    main()