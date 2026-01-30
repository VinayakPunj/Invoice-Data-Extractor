"""
OCR processing module for Invoice Data Extractor.
Handles PDF text extraction using Tesseract OCR.
"""
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from typing import List, Optional
from pathlib import Path
import tempfile

from config import Config
from src.logger import setup_logger

logger = setup_logger(__name__)

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD


class OCRProcessor:
    """Handles OCR processing for invoice PDFs."""
    
    def __init__(self, max_pages: int = None):
        """
        Initialize OCR processor.
        
        Args:
            max_pages: Maximum number of pages to process per PDF
        """
        self.max_pages = max_pages or Config.MAX_PAGES_PER_PDF
        logger.info(f"OCR Processor initialized with max_pages={self.max_pages}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using OCR.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from all pages
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If OCR processing fails
        """
        if not Path(pdf_path).exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            logger.info(f"Converting PDF to images: {pdf_path}")
            pages = convert_from_path(pdf_path)
            extracted_text = ""
            
            pages_to_process = min(len(pages), self.max_pages)
            logger.info(f"Processing {pages_to_process} pages")
            
            for page_num, page in enumerate(pages[:pages_to_process], 1):
                logger.debug(f"Processing page {page_num}/{pages_to_process}")
                text = pytesseract.image_to_string(page)
                extracted_text += text + "\n"
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters")
            return extracted_text
            
        except Exception as e:
            logger.error(f"OCR processing failed for {pdf_path}: {e}")
            raise Exception(f"OCR processing failed: {e}")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            logger.info(f"Extracted text from image: {image_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from image {image_path}: {e}")
            raise Exception(f"Image OCR failed: {e}")
    
    def process_uploaded_file(self, file_bytes: bytes, filename: str) -> str:
        """
        Process uploaded file bytes.
        
        Args:
            file_bytes: Raw file bytes
            filename: Original filename
            
        Returns:
            Extracted text
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        try:
            text = self.extract_text_from_pdf(tmp_path)
            return text
        finally:
            # Cleanup temporary file
            Path(tmp_path).unlink(missing_ok=True)
    
    @staticmethod
    def validate_tesseract_installation() -> bool:
        """
        Check if Tesseract is properly installed and accessible.
        
        Returns:
            True if Tesseract is available
        """
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is properly configured")
            return True
        except Exception as e:
            logger.error(f"Tesseract validation failed: {e}")
            return False
