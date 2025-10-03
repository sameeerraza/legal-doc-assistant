from typing import Optional
from config import Config, logger
from pathlib import Path
from typing import Optional, Dict, Tuple
try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    import numpy as np
    import cv2
    import PyPDF2
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Install with: pip install PyPDF2 Pillow pytesseract pdf2image numpy opencv-python")
    raise

class AdvancedDocumentProcessor:
    """
    Advanced document processor with OCR, rotation detection, and preprocessing.
    Integrates sophisticated scanned PDF handling capabilities.
    """
    
    def __init__(self, tesseract_path: Optional[str] = None, dpi: int = Config.DEFAULT_DPI):
        """
        Initialize the document processor.
        
        Args:
            tesseract_path: Path to tesseract executable (if not in PATH)
            dpi: DPI for PDF to image conversion
        """
        self.dpi = dpi
        
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Verify Tesseract installation
        try:
            pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {pytesseract.get_tesseract_version()}")
        except Exception as e:
            logger.warning(f"Tesseract not found: {e}. OCR functionality will be limited.")
    
    # ==================== Rotation Detection ====================
    
    def detect_rotation(self, image: Image.Image) -> int:
        """
        Detect the rotation angle of text in an image using Tesseract OSD.
        
        Args:
            image: PIL Image object
            
        Returns:
            Rotation angle (0, 90, 180, or 270 degrees)
        """
        try:
            # Use Tesseract's Orientation and Script Detection (OSD)
            osd = pytesseract.image_to_osd(image)
            
            # Parse rotation angle from OSD output
            rotation_line = [line for line in osd.split('\n') if 'Rotate' in line][0]
            rotation = int(rotation_line.split(':')[1].strip())
            
            logger.debug(f"Detected rotation: {rotation} degrees")
            return rotation
            
        except Exception as e:
            logger.debug(f"OSD rotation detection failed, using fallback: {e}")
            return self._detect_rotation_fallback(image)
    
    def _detect_rotation_fallback(self, image: Image.Image) -> int:
        """
        Fallback rotation detection using edge detection and Hough transform.
        
        Args:
            image: PIL Image object
            
        Returns:
            Best guess rotation angle (0, 90, 180, or 270)
        """
        try:
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(img_cv, 50, 150, apertureSize=3)
            
            # Detect lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
            
            if lines is not None:
                # Analyze line angles to determine predominant orientation
                angles = []
                for line in lines[:50]:  # Analyze top 50 lines
                    rho, theta = line[0]
                    angle = np.degrees(theta)
                    angles.append(angle)
                
                # Find most common orientation
                avg_angle = np.median(angles)
                
                # Map to nearest 90-degree rotation
                if 45 <= avg_angle < 135:
                    return 90
                elif 135 <= avg_angle < 180 or 0 <= avg_angle < 45:
                    return 0
                else:
                    return 270
            
        except Exception as e:
            logger.debug(f"Fallback rotation detection failed: {e}")
        
        return 0  # Default to no rotation
    
    def correct_rotation(self, image: Image.Image, rotation: int) -> Image.Image:
        """
        Rotate image to correct orientation.
        
        Args:
            image: PIL Image object
            rotation: Detected rotation angle
            
        Returns:
            Rotated PIL Image
        """
        if rotation == 0:
            return image
        
        # Rotate counter-clockwise to correct
        corrected = image.rotate(-rotation, expand=True)
        logger.debug(f"Corrected rotation by {-rotation} degrees")
        return corrected
    
    # ==================== Image Preprocessing ====================
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results.
        Applies denoising and adaptive thresholding.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        image = image.convert('L')
        
        # Convert to OpenCV format
        img_cv = np.array(image)
        
        # Apply denoising
        img_cv = cv2.fastNlMeansDenoising(img_cv, None, 10, 7, 21)
        
        # Apply adaptive thresholding for better contrast
        img_cv = cv2.adaptiveThreshold(
            img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Convert back to PIL
        return Image.fromarray(img_cv)
    
    # ==================== OCR Text Extraction ====================
    
    def extract_text_from_image(self, image: Image.Image, page_num: Optional[int] = None) -> str:
        """
        Extract text from a single image using Tesseract OCR with preprocessing.
        
        Args:
            image: PIL Image object
            page_num: Page number for logging purposes
            
        Returns:
            Extracted text
        """
        page_info = f"page {page_num}" if page_num else "image"
        
        # Detect and correct rotation
        rotation = self.detect_rotation(image)
        if rotation != 0:
            logger.info(f"Correcting rotation for {page_info}: {rotation} degrees")
            image = self.correct_rotation(image, rotation)
        
        # Preprocess image
        processed_image = self.preprocess_image(image)
        
        # Extract text with optimized config
        text = pytesseract.image_to_string(processed_image, config=Config.OCR_CONFIG)
        
        return text
    
    # ==================== PDF Processing ====================
    
    def extract_text_from_native_pdf(self, file_path: Path) -> Tuple[str, bool]:
        """
        Attempt to extract text from PDF using native text extraction.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, success_flag)
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(f"\n{'='*60}\nPAGE {page_num}\n{'='*60}\n\n{page_text}")
                
                full_text = "\n\n".join(text_parts)
                
                # Check if we got meaningful text (not just whitespace)
                if full_text.strip() and len(full_text.strip()) > 100:
                    logger.info("Successfully extracted text using native PDF extraction")
                    return full_text, True
                
        except Exception as e:
            logger.debug(f"Native PDF extraction failed: {e}")
        
        return "", False
    
    def extract_text_from_scanned_pdf(self, file_path: Path) -> str:
        """
        Extract text from scanned PDF using OCR with rotation correction.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text from all pages
        """
        logger.info(f"Processing scanned PDF with OCR: {file_path.name}")
        logger.info(f"Converting PDF to images at {self.dpi} DPI...")
        
        try:
            # Convert PDF pages to images
            images = convert_from_path(str(file_path), dpi=self.dpi)
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {e}")
            raise ValueError(f"PDF conversion failed: {str(e)}")
        
        logger.info(f"Processing {len(images)} pages with OCR...")
        
        # Extract text from each page
        all_text = []
        for i, image in enumerate(images, 1):
            logger.info(f"OCR processing page {i}/{len(images)}...")
            
            try:
                text = self.extract_text_from_image(image, page_num=i)
                all_text.append(f"{'='*60}\n")
                all_text.append(f"PAGE {i}\n")
                all_text.append(f"{'='*60}\n\n")
                all_text.append(text)
                all_text.append(f"\n\n")
            except Exception as e:
                logger.error(f"Error processing page {i}: {e}")
                all_text.append(f"\n[ERROR: Could not process page {i}]\n\n")
        
        full_text = ''.join(all_text)
        logger.info("OCR extraction complete!")
        return full_text
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """
        Intelligent PDF text extraction - tries native first, falls back to OCR.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        # Try native text extraction first
        text, success = self.extract_text_from_native_pdf(file_path)
        
        if success:
            return text
        
        # Fall back to OCR for scanned PDFs
        logger.info("Native extraction insufficient, using OCR...")
        return self.extract_text_from_scanned_pdf(file_path)
    
    def extract_text_from_image_file(self, file_path: Path) -> str:
        """
        Extract text from image file (PNG, JPG, TIFF, etc.).
        
        Args:
            file_path: Path to image file
            
        Returns:
            Extracted text
        """
        try:
            image = Image.open(file_path)
            text = self.extract_text_from_image(image)
            return text
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    # ==================== Main Processing Interface ====================
    
    def process_document(self, file_path: str) -> Tuple[str, Dict]:
        """
        Process a document and return extracted text and metadata.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > Config.MAX_DOCUMENT_SIZE_MB:
            raise ValueError(f"Document exceeds {Config.MAX_DOCUMENT_SIZE_MB}MB limit")
        
        # Extract text based on file type
        suffix = path.suffix.lower()
        logger.info(f"Processing {suffix} file: {path.name}")
        
        if suffix == '.pdf':
            text = self.extract_text_from_pdf(path)
        elif suffix in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            text = self.extract_text_from_image_file(path)
        else:
            raise ValueError(f"Unsupported format: {suffix}. Supported: {Config.SUPPORTED_FORMATS}")
        
        metadata = {
            "filename": path.name,
            "file_type": suffix,
            "size_mb": round(size_mb, 2),
            "char_count": len(text),
            "word_count": len(text.split()),
            "dpi_used": self.dpi if suffix == '.pdf' else 'N/A'
        }
        
        logger.info(f"Extraction complete: {metadata['word_count']} words extracted")
        
        return text, metadata