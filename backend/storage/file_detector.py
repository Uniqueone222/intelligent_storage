"""
Robust file type detection module.
Uses multiple methods to accurately detect file types:
1. Magic bytes (most reliable)
2. MIME type detection
3. File extension fallback
"""

import magic
import mimetypes
import os
from pathlib import Path
from typing import Dict, Tuple


class FileTypeDetector:
    """
    Advanced file type detection with multiple validation methods.
    """

    # Comprehensive file type mappings
    FILE_TYPE_CATEGORIES = {
        'images': {
            'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
                          '.ico', '.tiff', '.tif', '.heic', '.heif', '.raw', '.cr2',
                          '.nef', '.orf', '.sr2'],
            'mime_prefixes': ['image/'],
            'magic_patterns': ['image data', 'bitmap', 'graphics image', 'JPEG',
                             'PNG', 'GIF', 'SVG', 'WebP']
        },
        'videos': {
            'extensions': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm',
                          '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv', '.ts', '.vob'],
            'mime_prefixes': ['video/'],
            'magic_patterns': ['video', 'MPEG', 'ISO Media', 'Matroska', 'AVI',
                             'QuickTime', 'WebM']
        },
        'audio': {
            'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
                          '.opus', '.ape', '.alac', '.aiff'],
            'mime_prefixes': ['audio/'],
            'magic_patterns': ['audio', 'MPEG ADTS', 'WAVE', 'FLAC', 'Ogg data']
        },
        'compressed': {
            'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
                          '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2'],
            'mime_prefixes': ['application/zip', 'application/x-rar',
                            'application/x-7z-compressed', 'application/gzip',
                            'application/x-tar', 'application/x-bzip2'],
            'magic_patterns': ['Zip archive', 'RAR archive', '7-zip archive',
                             'gzip compressed', 'bzip2 compressed', 'XZ compressed',
                             'POSIX tar archive']
        },
        'programs': {
            'extensions': ['.exe', '.dll', '.so', '.dylib', '.app', '.bin', '.sh',
                          '.bat', '.cmd', '.msi', '.deb', '.rpm', '.apk', '.jar'],
            'mime_prefixes': ['application/x-executable', 'application/x-sharedlib',
                            'application/x-msdos-program'],
            'magic_patterns': ['executable', 'shared library', 'PE32', 'ELF',
                             'Mach-O', 'MS-DOS executable', 'shell script',
                             'Debian binary package', 'RPM']
        },
        'documents': {
            'extensions': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                          '.odt', '.ods', '.odp', '.txt', '.rtf', '.csv', '.md',
                          '.html', '.xml', '.json'],
            'mime_prefixes': ['application/pdf', 'application/msword',
                            'application/vnd.openxmlformats-officedocument',
                            'application/vnd.oasis.opendocument', 'text/'],
            'magic_patterns': ['PDF document', 'Microsoft Word', 'Microsoft Excel',
                             'Microsoft PowerPoint', 'OpenDocument', 'ASCII text',
                             'UTF-8 Unicode text', 'HTML document', 'XML']
        }
    }

    def __init__(self):
        """Initialize the file detector."""
        self.mime = magic.Magic(mime=True)
        self.description = magic.Magic()

    def detect_file_type(self, file_path: str) -> Tuple[str, Dict[str, str]]:
        """
        Detect file type using multiple methods for robustness.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Tuple of (category, metadata_dict)
            category: One of 'images', 'videos', 'audio', 'compressed',
                     'programs', 'documents', 'others'
            metadata_dict: Additional information about the file
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Gather detection data
        extension = file_path.suffix.lower()
        mime_type = self._get_mime_type(file_path)
        magic_desc = self._get_magic_description(file_path)

        # Score each category
        scores = {}
        for category, patterns in self.FILE_TYPE_CATEGORIES.items():
            score = 0

            # Check extension (weight: 1)
            if extension in patterns['extensions']:
                score += 1

            # Check MIME type (weight: 2 - more reliable)
            if any(mime_type.startswith(prefix) for prefix in patterns['mime_prefixes']):
                score += 2

            # Check magic description (weight: 3 - most reliable)
            if any(pattern.lower() in magic_desc.lower()
                   for pattern in patterns['magic_patterns']):
                score += 3

            scores[category] = score

        # Get the category with highest score
        if max(scores.values()) == 0:
            category = 'others'
        else:
            category = max(scores, key=scores.get)

        # Build metadata
        metadata = {
            'extension': extension,
            'mime_type': mime_type,
            'magic_description': magic_desc,
            'file_size': file_path.stat().st_size,
            'file_name': file_path.name,
            'detection_confidence': scores.get(category, 0),
        }

        return category, metadata

    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type using python-magic."""
        try:
            return self.mime.from_file(str(file_path))
        except Exception as e:
            # Fallback to mimetypes module
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return mime_type or 'application/octet-stream'

    def _get_magic_description(self, file_path: Path) -> str:
        """Get file description using libmagic."""
        try:
            return self.description.from_file(str(file_path))
        except Exception:
            return ''

    def get_subcategory_suggestion(self, file_path: str,
                                   ai_analysis: dict = None) -> str:
        """
        Suggest a subcategory for organizing the file.
        Can be enhanced with AI analysis results.

        Args:
            file_path: Path to the file
            ai_analysis: Optional dict with AI analysis results

        Returns:
            Suggested subcategory name
        """
        category, metadata = self.detect_file_type(file_path)

        # If AI analysis is available, use it
        if ai_analysis and 'category' in ai_analysis:
            return self._sanitize_category_name(ai_analysis['category'])

        # Otherwise, create basic subcategory from metadata
        if category == 'images':
            # Check if it's a specific image format
            ext = metadata['extension'].replace('.', '')
            return ext.upper()

        elif category == 'videos':
            ext = metadata['extension'].replace('.', '')
            return ext.upper()

        elif category == 'compressed':
            return 'archives'

        elif category == 'programs':
            if metadata['extension'] in ['.exe', '.dll', '.msi']:
                return 'windows'
            elif metadata['extension'] in ['.so', '.dylib']:
                return 'libraries'
            elif metadata['extension'] in ['.sh', '.bat', '.cmd']:
                return 'scripts'
            else:
                return 'executables'

        elif category == 'documents':
            if 'pdf' in metadata['mime_type'].lower():
                return 'pdf'
            elif 'word' in metadata['magic_description'].lower():
                return 'word'
            elif 'excel' in metadata['magic_description'].lower():
                return 'spreadsheets'
            else:
                return 'general'

        else:
            return 'uncategorized'

    def _sanitize_category_name(self, name: str) -> str:
        """Sanitize category name for use as directory name."""
        # Remove special characters, replace spaces with underscores
        import re
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[-\s]+', '_', name)
        return name.lower()


# Singleton instance
file_detector = FileTypeDetector()
