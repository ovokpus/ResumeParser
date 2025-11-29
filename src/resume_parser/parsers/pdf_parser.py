"""PDF file parser implementation."""

from pathlib import Path
from typing import Union
import PyPDF2

from resume_parser.parsers.base import FileParser
from resume_parser.exceptions import FileParsingError
from resume_parser.utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFParser(FileParser):
    """
    Parse PDF resume files to extract text content.
    
    Uses PyPDF2 for text extraction with robust error handling
    for various PDF formats and encodings.
    """
    
    def parse(self, file_path: Union[str, Path]) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text content
        
        Raises:
            FileParsingError: If PDF cannot be parsed
            FileNotFoundError: If file doesn't exist
        """
        # Validate file exists
        path = self._validate_file_exists(file_path)
        self._validate_file_size(path)
        
        logger.info(f"Parsing PDF file: {path}")
        
        try:
            text_content = []
            
            with open(path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    logger.warning(f"PDF is encrypted: {path}")
                    try:
                        pdf_reader.decrypt('')  # Try empty password
                    except Exception as e:
                        raise FileParsingError(
                            f"Cannot decrypt PDF: {path}. Error: {str(e)}"
                        )
                
                num_pages = len(pdf_reader.pages)
                logger.debug(f"PDF has {num_pages} pages")
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                        else:
                            logger.warning(f"No text extracted from page {page_num + 1}")
                    except Exception as e:
                        logger.warning(
                            f"Error extracting text from page {page_num + 1}: {str(e)}"
                        )
                        continue
            
            # Combine all pages
            full_text = "\n\n".join(text_content)
            
            if not full_text.strip():
                raise FileParsingError(
                    f"No text content extracted from PDF: {path}. "
                    "The PDF may be image-based or corrupted."
                )
            
            logger.info(f"Successfully extracted {len(full_text)} characters from PDF")
            return full_text
            
        except FileParsingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing PDF {path}: {str(e)}")
            raise FileParsingError(f"Failed to parse PDF: {str(e)}")

