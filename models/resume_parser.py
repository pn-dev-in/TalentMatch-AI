"""
Resume Parser for Windows
Supports: .pdf, .docx, .txt
"""

import os
from typing import Optional

from utils.logger import setup_logger
logger = setup_logger(__name__)

# PDF extraction
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# DOCX extraction
try:
    from docx import Document
except ImportError:
    Document = None

class ResumeParser:
    @staticmethod
    def parse(file_path: str) -> Optional[str]:
        """
        Extract text from resume file.
        Returns: string or None if extraction fails.
        """
        if not os.path.exists(file_path):
            return None, f"File not found: {file_path}"
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return ResumeParser._parse_pdf(file_path)
        elif ext == '.docx':
            return ResumeParser._parse_docx(file_path)
        elif ext == '.txt':
            return ResumeParser._parse_txt(file_path)
        else:
            return None, f"Unsupported file type: {ext}"
    
    @staticmethod
    def _parse_pdf(file_path: str):
        # Try pdfplumber first (better for complex layouts)
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                if text.strip():
                    return text.strip(), None
                else:
                    return None, "PDF contains no extractable text (may be scanned/image)"
            except Exception as e:
                # Fallback to PyPDF2
                pass
        
        # Fallback to PyPDF2
        if PyPDF2:
            try:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                if text.strip():
                    return text.strip(), None
                else:
                    return None, "PDF has no extractable text (maybe scanned)"
            except Exception as e:
                return None, f"PyPDF2 error: {str(e)}"
        
        return None, "No PDF library available. Install pdfplumber or PyPDF2"
    
    @staticmethod
    def _parse_docx(file_path: str):
        if Document is None:
            return None, "python-docx not installed"
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            if text.strip():
                return text.strip(), None
            else:
                return None, "DOCX file appears empty"
        except Exception as e:
            return None, f"DOCX parsing error: {str(e)}"
    
    @staticmethod
    def _parse_txt(file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            if text.strip():
                return text.strip(), None
            else:
                return None, "TXT file is empty"
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                return text.strip(), None
            except Exception as e:
                return None, f"TXT decode error: {str(e)}"
        except Exception as e:
            return None, f"TXT read error: {str(e)}"


# Quick test (run from project root)
if __name__ == "__main__":
    # Example usage:
    # parser = ResumeParser()
    # text, error = parser.parse("C:/path/to/resume.pdf")
    # print(text if text else error)
    print("ResumeParser class loaded. Call .parse(file_path) to use.")