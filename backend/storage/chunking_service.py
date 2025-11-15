"""
Document chunking service for RAG implementation.
Splits documents into optimal chunks for embedding and retrieval.
"""

import logging
import os
from typing import List, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ChunkingService:
    """
    Service for chunking documents into optimal sizes for embedding.
    """

    def __init__(
        self,
        max_chunk_size: int = 500,
        overlap_size: int = 50,
        separators: List[str] = None
    ):
        """
        Initialize chunking service.

        Args:
            max_chunk_size: Maximum number of characters per chunk
            overlap_size: Number of overlapping characters between chunks
            separators: List of separators to split on (in order of preference)
        """
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.separators = separators or ['\n\n', '\n', '. ', ' ', '']

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with overlap.

        Args:
            text: Input text to chunk
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []

        chunks = []
        metadata = metadata or {}

        # Simple recursive chunking
        current_chunks = self._recursive_split(text, self.separators)

        # Process chunks with overlap
        for i, chunk_text in enumerate(current_chunks):
            if not chunk_text.strip():
                continue

            chunk_dict = {
                'chunk_index': i,
                'chunk_text': chunk_text.strip(),
                'chunk_size': len(chunk_text),
                'metadata': metadata.copy()
            }
            chunks.append(chunk_dict)

        return chunks

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively split text using separators.

        Args:
            text: Text to split
            separators: List of separators to try

        Returns:
            List of text chunks
        """
        if not separators:
            # Base case: split by character limit
            return self._split_by_length(text)

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == '':
            # Last resort: split by character
            return self._split_by_length(text)

        splits = text.split(separator)
        chunks = []

        current_chunk = ""
        for split in splits:
            # Try to add split to current chunk
            test_chunk = current_chunk + separator + split if current_chunk else split

            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                # Current chunk is full
                if current_chunk:
                    chunks.append(current_chunk)

                # If the split itself is too large, recursively split it
                if len(split) > self.max_chunk_size:
                    sub_chunks = self._recursive_split(split, remaining_separators)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = split

        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _split_by_length(self, text: str) -> List[str]:
        """
        Split text by fixed length with overlap.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.max_chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            # Move start forward with overlap
            start = end - self.overlap_size

        return chunks

    def extract_text_from_file(self, file_path: str, file_type: str = None) -> str:
        """
        Extract text content from various file types.

        Args:
            file_path: Path to the file
            file_type: Optional file type hint

        Returns:
            Extracted text content
        """
        file_ext = Path(file_path).suffix.lower()

        try:
            # Plain text files
            if file_ext in ['.txt', '.md', '.csv', '.log', '.json', '.xml', '.yaml', '.yml']:
                return self._read_text_file(file_path)

            # Code files
            elif file_ext in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php',
                            '.rb', '.go', '.rs', '.swift', '.kt', '.ts', '.jsx', '.tsx']:
                return self._read_text_file(file_path)

            # PDF files
            elif file_ext == '.pdf':
                return self._extract_pdf_text(file_path)

            # Word documents
            elif file_ext in ['.docx', '.doc']:
                return self._extract_docx_text(file_path)

            # HTML files
            elif file_ext in ['.html', '.htm']:
                return self._extract_html_text(file_path)

            else:
                logger.warning(f"Unsupported file type for text extraction: {file_ext}")
                return ""

        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            return ""

    def _read_text_file(self, file_path: str) -> str:
        """Read plain text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n\n"
            return text
        except ImportError:
            logger.warning("PyPDF2 not installed. Cannot extract PDF text.")
            return ""
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            return ""

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except ImportError:
            logger.warning("python-docx not installed. Cannot extract DOCX text.")
            return ""
        except Exception as e:
            logger.error(f"DOCX extraction failed: {str(e)}")
            return ""

    def _extract_html_text(self, file_path: str) -> str:
        """Extract text from HTML file."""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                return soup.get_text(separator='\n', strip=True)
        except ImportError:
            logger.warning("BeautifulSoup not installed. Cannot extract HTML text.")
            return self._read_text_file(file_path)  # Fallback to plain text
        except Exception as e:
            logger.error(f"HTML extraction failed: {str(e)}")
            return ""


# Singleton instance
chunking_service = ChunkingService()
