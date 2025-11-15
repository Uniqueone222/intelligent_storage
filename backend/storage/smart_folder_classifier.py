"""
Smart Folder Classification System

Automatically classifies uploaded files into specific folders based on:
- File type and extension
- MIME type detection
- Content analysis
- Magic bytes inspection

Categories include:
- Photos (jpg, png, etc.)
- GIFs
- Videos
- Audio
- HTML/Web files
- Code files
- Documents
- Archives
- And many more...
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, Tuple, Optional
import magic
import logging

logger = logging.getLogger(__name__)


class SmartFolderClassifier:
    """
    Intelligent file classification system that automatically categorizes
    uploaded files into specific folders based on type and content.
    """

    # Comprehensive file type classifications
    FILE_CATEGORIES = {
        # Images
        'photos': {
            'extensions': ['.jpg', '.jpeg', '.png', '.heic', '.heif', '.raw', '.cr2', '.nef', '.arw'],
            'mime_patterns': ['image/jpeg', 'image/png', 'image/heic', 'image/x-canon-cr2'],
            'description': 'Photographic images'
        },
        'gifs': {
            'extensions': ['.gif'],
            'mime_patterns': ['image/gif'],
            'description': 'Animated GIF images'
        },
        'vector_graphics': {
            'extensions': ['.svg', '.eps', '.ai', '.cdr'],
            'mime_patterns': ['image/svg+xml', 'application/postscript'],
            'description': 'Vector graphics and illustrations'
        },
        'webp': {
            'extensions': ['.webp'],
            'mime_patterns': ['image/webp'],
            'description': 'WebP images'
        },
        'icons': {
            'extensions': ['.ico', '.icns'],
            'mime_patterns': ['image/x-icon', 'image/vnd.microsoft.icon'],
            'description': 'Icon files'
        },

        # Videos
        'videos_mp4': {
            'extensions': ['.mp4', '.m4v'],
            'mime_patterns': ['video/mp4'],
            'description': 'MP4 video files'
        },
        'videos_mov': {
            'extensions': ['.mov', '.qt'],
            'mime_patterns': ['video/quicktime'],
            'description': 'QuickTime videos'
        },
        'videos_avi': {
            'extensions': ['.avi'],
            'mime_patterns': ['video/x-msvideo'],
            'description': 'AVI video files'
        },
        'videos_mkv': {
            'extensions': ['.mkv'],
            'mime_patterns': ['video/x-matroska'],
            'description': 'Matroska video files'
        },
        'videos_webm': {
            'extensions': ['.webm'],
            'mime_patterns': ['video/webm'],
            'description': 'WebM video files'
        },
        'videos_other': {
            'extensions': ['.wmv', '.flv', '.mpg', '.mpeg', '.3gp', '.ogv'],
            'mime_patterns': ['video/x-ms-wmv', 'video/x-flv', 'video/mpeg'],
            'description': 'Other video formats'
        },

        # Audio
        'audio_music': {
            'extensions': ['.mp3', '.m4a', '.aac', '.flac', '.alac'],
            'mime_patterns': ['audio/mpeg', 'audio/mp4', 'audio/aac', 'audio/flac'],
            'description': 'Music files'
        },
        'audio_wav': {
            'extensions': ['.wav', '.wave'],
            'mime_patterns': ['audio/wav', 'audio/x-wav'],
            'description': 'WAV audio files'
        },
        'audio_ogg': {
            'extensions': ['.ogg', '.oga'],
            'mime_patterns': ['audio/ogg'],
            'description': 'OGG audio files'
        },
        'audio_other': {
            'extensions': ['.wma', '.opus', '.mid', '.midi'],
            'mime_patterns': ['audio/x-ms-wma', 'audio/opus', 'audio/midi'],
            'description': 'Other audio formats'
        },

        # Web files
        'html': {
            'extensions': ['.html', '.htm'],
            'mime_patterns': ['text/html'],
            'description': 'HTML web pages'
        },
        'css': {
            'extensions': ['.css', '.scss', '.sass', '.less'],
            'mime_patterns': ['text/css'],
            'description': 'CSS stylesheets'
        },
        'javascript': {
            'extensions': ['.js', '.mjs', '.jsx'],
            'mime_patterns': ['application/javascript', 'text/javascript'],
            'description': 'JavaScript files'
        },
        'typescript': {
            'extensions': ['.ts', '.tsx'],
            'mime_patterns': ['application/typescript'],
            'description': 'TypeScript files'
        },

        # Programming languages
        'python': {
            'extensions': ['.py', '.pyw', '.pyx', '.ipynb'],
            'mime_patterns': ['text/x-python', 'application/x-python-code'],
            'description': 'Python source files'
        },
        'java': {
            'extensions': ['.java', '.class', '.jar'],
            'mime_patterns': ['text/x-java-source', 'application/java-archive'],
            'description': 'Java files'
        },
        'cpp': {
            'extensions': ['.cpp', '.cc', '.cxx', '.c', '.h', '.hpp'],
            'mime_patterns': ['text/x-c++', 'text/x-c'],
            'description': 'C/C++ source files'
        },
        'csharp': {
            'extensions': ['.cs'],
            'mime_patterns': ['text/x-csharp'],
            'description': 'C# source files'
        },
        'ruby': {
            'extensions': ['.rb', '.erb'],
            'mime_patterns': ['text/x-ruby'],
            'description': 'Ruby files'
        },
        'php': {
            'extensions': ['.php', '.phtml'],
            'mime_patterns': ['application/x-php', 'text/x-php'],
            'description': 'PHP files'
        },
        'go': {
            'extensions': ['.go'],
            'mime_patterns': ['text/x-go'],
            'description': 'Go source files'
        },
        'rust': {
            'extensions': ['.rs'],
            'mime_patterns': ['text/x-rust'],
            'description': 'Rust source files'
        },
        'swift': {
            'extensions': ['.swift'],
            'mime_patterns': ['text/x-swift'],
            'description': 'Swift source files'
        },
        'kotlin': {
            'extensions': ['.kt', '.kts'],
            'mime_patterns': ['text/x-kotlin'],
            'description': 'Kotlin source files'
        },

        # Documents
        'pdf': {
            'extensions': ['.pdf'],
            'mime_patterns': ['application/pdf'],
            'description': 'PDF documents'
        },
        'word': {
            'extensions': ['.doc', '.docx', '.odt'],
            'mime_patterns': ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            'description': 'Word documents'
        },
        'excel': {
            'extensions': ['.xls', '.xlsx', '.ods'],
            'mime_patterns': ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            'description': 'Excel spreadsheets'
        },
        'powerpoint': {
            'extensions': ['.ppt', '.pptx', '.odp'],
            'mime_patterns': ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'],
            'description': 'PowerPoint presentations'
        },
        'text': {
            'extensions': ['.txt', '.text', '.log'],
            'mime_patterns': ['text/plain'],
            'description': 'Plain text files'
        },
        'markdown': {
            'extensions': ['.md', '.markdown', '.mdown'],
            'mime_patterns': ['text/markdown', 'text/x-markdown'],
            'description': 'Markdown files'
        },
        'rtf': {
            'extensions': ['.rtf'],
            'mime_patterns': ['application/rtf', 'text/rtf'],
            'description': 'Rich Text Format'
        },

        # Data formats
        'json': {
            'extensions': ['.json', '.jsonl', '.geojson'],
            'mime_patterns': ['application/json'],
            'description': 'JSON data files'
        },
        'xml': {
            'extensions': ['.xml', '.xsd', '.xsl'],
            'mime_patterns': ['application/xml', 'text/xml'],
            'description': 'XML files'
        },
        'yaml': {
            'extensions': ['.yaml', '.yml'],
            'mime_patterns': ['application/x-yaml', 'text/yaml'],
            'description': 'YAML files'
        },
        'csv': {
            'extensions': ['.csv'],
            'mime_patterns': ['text/csv'],
            'description': 'CSV data files'
        },
        'sql': {
            'extensions': ['.sql'],
            'mime_patterns': ['application/sql'],
            'description': 'SQL files'
        },

        # Archives
        'zip': {
            'extensions': ['.zip'],
            'mime_patterns': ['application/zip'],
            'description': 'ZIP archives'
        },
        'rar': {
            'extensions': ['.rar'],
            'mime_patterns': ['application/x-rar-compressed', 'application/vnd.rar'],
            'description': 'RAR archives'
        },
        'tar': {
            'extensions': ['.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2'],
            'mime_patterns': ['application/x-tar', 'application/gzip'],
            'description': 'TAR archives'
        },
        '7zip': {
            'extensions': ['.7z'],
            'mime_patterns': ['application/x-7z-compressed'],
            'description': '7-Zip archives'
        },
        'archives_other': {
            'extensions': ['.gz', '.bz2', '.xz', '.iso', '.dmg'],
            'mime_patterns': ['application/gzip', 'application/x-bzip2'],
            'description': 'Other archive formats'
        },

        # Executables
        'windows_exe': {
            'extensions': ['.exe', '.msi', '.dll'],
            'mime_patterns': ['application/x-msdownload', 'application/x-msi'],
            'description': 'Windows executables'
        },
        'mac_apps': {
            'extensions': ['.app', '.dmg', '.pkg'],
            'mime_patterns': ['application/x-apple-diskimage'],
            'description': 'macOS applications'
        },
        'linux_bin': {
            'extensions': ['.deb', '.rpm', '.appimage'],
            'mime_patterns': ['application/x-debian-package', 'application/x-rpm'],
            'description': 'Linux packages'
        },

        # Fonts
        'fonts': {
            'extensions': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
            'mime_patterns': ['font/ttf', 'font/otf', 'font/woff', 'font/woff2'],
            'description': 'Font files'
        },

        # 3D and CAD
        '3d_models': {
            'extensions': ['.obj', '.fbx', '.stl', '.blend', '.3ds', '.dae', '.gltf', '.glb'],
            'mime_patterns': ['model/obj', 'model/gltf+json', 'model/gltf-binary'],
            'description': '3D model files'
        },
        'cad': {
            'extensions': ['.dwg', '.dxf', '.step', '.stp', '.iges'],
            'mime_patterns': ['application/acad', 'image/vnd.dxf'],
            'description': 'CAD files'
        },

        # Ebooks
        'ebooks': {
            'extensions': ['.epub', '.mobi', '.azw', '.azw3'],
            'mime_patterns': ['application/epub+zip'],
            'description': 'E-book files'
        },

        # Subtitles
        'subtitles': {
            'extensions': ['.srt', '.sub', '.vtt', '.ass', '.ssa'],
            'mime_patterns': ['text/vtt', 'application/x-subrip'],
            'description': 'Subtitle files'
        },

        # Configuration
        'config': {
            'extensions': ['.conf', '.cfg', '.ini', '.env', '.properties'],
            'mime_patterns': ['text/plain'],
            'description': 'Configuration files'
        },

        # Shell scripts
        'shell_scripts': {
            'extensions': ['.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd', '.ps1'],
            'mime_patterns': ['application/x-sh', 'application/x-shellscript'],
            'description': 'Shell scripts'
        },

        # Blockchain/Crypto
        'blockchain': {
            'extensions': ['.sol', '.vy'],
            'mime_patterns': [],
            'description': 'Smart contract files'
        },

        # Torrent
        'torrents': {
            'extensions': ['.torrent'],
            'mime_patterns': ['application/x-bittorrent'],
            'description': 'Torrent files'
        },

        # Unknown/Other
        'other': {
            'extensions': [],
            'mime_patterns': [],
            'description': 'Uncategorized files'
        }
    }

    def __init__(self):
        """Initialize the smart folder classifier"""
        logger.info("Smart Folder Classifier initialized")

    def classify_file(self, filename: str, content: Optional[bytes] = None) -> Tuple[str, Dict[str, str]]:
        """
        Classify a file into the most appropriate category

        Args:
            filename: Name of the file
            content: Optional file content for magic byte detection

        Returns:
            Tuple of (category_name, category_info)
        """
        file_ext = Path(filename).suffix.lower()

        # Try MIME type detection if content provided
        mime_type = None
        if content:
            try:
                mime = magic.Magic(mime=True)
                mime_type = mime.from_buffer(content)
            except Exception as e:
                logger.warning(f"Magic detection failed: {e}")

        # Fallback to extension-based MIME detection
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(filename)

        # Search through categories for best match
        for category_name, category_info in self.FILE_CATEGORIES.items():
            # Check extension match
            if file_ext in category_info['extensions']:
                return category_name, {
                    'category': category_name,
                    'description': category_info['description'],
                    'matched_by': 'extension',
                    'extension': file_ext,
                    'mime_type': mime_type or 'unknown'
                }

            # Check MIME type match
            if mime_type:
                for mime_pattern in category_info['mime_patterns']:
                    if mime_pattern in mime_type or mime_type.startswith(mime_pattern.split('/')[0]):
                        return category_name, {
                            'category': category_name,
                            'description': category_info['description'],
                            'matched_by': 'mime_type',
                            'extension': file_ext,
                            'mime_type': mime_type
                        }

        # Default to 'other' if no match found
        return 'other', {
            'category': 'other',
            'description': 'Uncategorized files',
            'matched_by': 'default',
            'extension': file_ext,
            'mime_type': mime_type or 'unknown'
        }

    def get_folder_path(self, category: str, base_path: Path,
                       use_date_subfolders: bool = True) -> Path:
        """
        Get the folder path for a specific category

        Args:
            category: File category
            base_path: Base storage path
            use_date_subfolders: Whether to use date-based subfolders

        Returns:
            Path object for the folder
        """
        from datetime import datetime

        # Create category folder
        category_path = base_path / category

        # Add date-based subfolder if requested (CDN-ready structure)
        if use_date_subfolders:
            date_path = datetime.now().strftime('%Y/%m/%d')
            category_path = category_path / date_path

        # Ensure path exists
        category_path.mkdir(parents=True, exist_ok=True)

        return category_path

    def get_all_categories(self) -> Dict[str, str]:
        """
        Get all available categories with descriptions

        Returns:
            Dictionary of {category_name: description}
        """
        return {
            name: info['description']
            for name, info in self.FILE_CATEGORIES.items()
        }

    def get_statistics(self, base_path: Path) -> Dict[str, int]:
        """
        Get file count statistics for each category

        Args:
            base_path: Base storage path

        Returns:
            Dictionary of {category_name: file_count}
        """
        stats = {}

        for category in self.FILE_CATEGORIES.keys():
            category_path = base_path / category

            if category_path.exists():
                # Count files recursively
                file_count = sum(1 for _ in category_path.rglob('*') if _.is_file())
                stats[category] = file_count
            else:
                stats[category] = 0

        return stats


# Global classifier instance
_classifier_instance = None


def get_smart_classifier() -> SmartFolderClassifier:
    """Get singleton smart classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = SmartFolderClassifier()
    return _classifier_instance
