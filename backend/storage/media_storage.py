"""
Optimized Media Storage Handler with Smart Folder Classification

Handles media files with:
- Smart automatic folder classification (photos, gifs, html, videos, etc.)
- Local filesystem storage with CDN-ready structure
- Intelligent organization by type and date
- Thumbnail generation for images
- Metadata extraction
- Fast retrieval with proper MIME types
- Admin-only access control
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, BinaryIO
from PIL import Image
import magic
import logging
from .smart_folder_classifier import get_smart_classifier

logger = logging.getLogger(__name__)


class MediaStorageHandler:
    """
    Handles media file storage with optimization for:
    - Fast retrieval
    - Efficient organization
    - Secure admin-only access
    - CDN-ready structure
    """

    # Supported media types
    SUPPORTED_TYPES = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'],
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'],
        'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.md', '.csv', '.xlsx']
    }

    THUMBNAIL_SIZES = {
        'small': (150, 150),
        'medium': (300, 300),
        'large': (600, 600)
    }

    def __init__(self, base_storage_path: str = None):
        """
        Initialize media storage handler with smart classification

        Args:
            base_storage_path: Base directory for media storage
        """
        if base_storage_path is None:
            # Default to media directory in project root
            base_storage_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'media_storage'
            )

        self.base_path = Path(base_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Initialize smart classifier
        self.classifier = get_smart_classifier()

        # Legacy paths for backward compatibility
        self.images_path = self.base_path / 'images'
        self.videos_path = self.base_path / 'videos'
        self.audio_path = self.base_path / 'audio'
        self.documents_path = self.base_path / 'documents'
        self.thumbnails_path = self.base_path / 'thumbnails'
        self.temp_path = self.base_path / 'temp'

        # Create essential directories
        for path in [self.thumbnails_path, self.temp_path]:
            path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Media storage initialized with smart classification at: {self.base_path}")

    def store_media(self, file_data: BinaryIO, filename: str, admin_id: str,
                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store media file with smart automatic folder classification

        Args:
            file_data: File binary data
            filename: Original filename
            admin_id: Admin user ID (for access control)
            metadata: Optional metadata dictionary

        Returns:
            Dictionary with storage information
        """
        # Read file content
        content = file_data.read()

        # Use smart classifier to determine category
        category, classification_info = self.classifier.classify_file(filename, content)

        # Generate unique filename
        file_hash = hashlib.sha256(content).hexdigest()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_ext = Path(filename).suffix.lower()
        unique_filename = f"{admin_id}_{timestamp}_{file_hash[:12]}{file_ext}"

        # Get smart folder path (with date-based subdirectories)
        storage_path = self.classifier.get_folder_path(
            category=category,
            base_path=self.base_path,
            use_date_subfolders=True
        )

        # Full file path
        file_path = storage_path / unique_filename

        # Write file
        with open(file_path, 'wb') as f:
            f.write(content)

        logger.info(f"Stored file in smart folder '{category}': {file_path}")

        # Build result
        result = {
            'success': True,
            'file_id': f"{category}_{timestamp}_{file_hash[:12]}",
            'filename': unique_filename,
            'original_filename': filename,
            'category': category,
            'classification': classification_info,
            'file_type': classification_info['mime_type'],
            'file_size': len(content),
            'storage_path': str(file_path.relative_to(self.base_path)),
            'full_path': str(file_path),
            'admin_id': admin_id,
            'created_at': datetime.now().isoformat(),
            'url_path': f"/media/{file_path.relative_to(self.base_path)}"
        }

        # Generate thumbnails for photo categories
        is_photo_category = category in ['photos', 'gifs', 'webp', 'icons']
        if is_photo_category and file_ext.lower() not in ['.svg']:
            try:
                thumbnails = self._generate_thumbnails(file_path, unique_filename)
                result['thumbnails'] = thumbnails
            except Exception as e:
                logger.error(f"Error generating thumbnails: {e}")
                result['thumbnails'] = {}

        # Extract metadata
        if metadata:
            result['metadata'] = metadata
        else:
            result['metadata'] = self._extract_metadata(file_path, category, content)

        return result

    def _detect_file_type(self, content: bytes, filename: str) -> Tuple[str, str]:
        """
        Detect file type using magic bytes and extension

        Args:
            content: File content
            filename: Original filename

        Returns:
            Tuple of (file_type, mime_type)
        """
        # Use python-magic for accurate detection
        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(content)
        except Exception as e:
            logger.warning(f"Magic detection failed: {e}, falling back to extension")
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                mime_type = 'application/octet-stream'

        # Determine category
        file_ext = Path(filename).suffix.lower()

        for category, extensions in self.SUPPORTED_TYPES.items():
            if file_ext in extensions or mime_type.startswith(category):
                return category, mime_type

        # Default to document
        return 'document', mime_type

    def _get_storage_path(self, file_type: str) -> Path:
        """Get storage path for file type"""
        paths = {
            'image': self.images_path,
            'video': self.videos_path,
            'audio': self.audio_path,
            'document': self.documents_path
        }
        return paths.get(file_type, self.documents_path)

    def _generate_thumbnails(self, image_path: Path, filename: str) -> Dict[str, str]:
        """
        Generate thumbnails for images

        Args:
            image_path: Path to original image
            filename: Filename for thumbnails

        Returns:
            Dictionary with thumbnail paths
        """
        thumbnails = {}

        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background

                for size_name, dimensions in self.THUMBNAIL_SIZES.items():
                    # Create thumbnail
                    thumb = img.copy()
                    thumb.thumbnail(dimensions, Image.Resampling.LANCZOS)

                    # Create thumbnail path
                    thumb_filename = f"{Path(filename).stem}_{size_name}.jpg"
                    thumb_path = self.thumbnails_path / thumb_filename

                    # Save thumbnail
                    thumb.save(thumb_path, 'JPEG', quality=85, optimize=True)

                    thumbnails[size_name] = {
                        'path': str(thumb_path.relative_to(self.base_path)),
                        'url': f"/media/thumbnails/{thumb_filename}",
                        'width': thumb.width,
                        'height': thumb.height
                    }

        except Exception as e:
            logger.error(f"Error generating thumbnails for {image_path}: {e}")

        return thumbnails

    def _extract_metadata(self, file_path: Path, file_type: str, content: bytes) -> Dict[str, Any]:
        """
        Extract metadata from file

        Args:
            file_path: Path to file
            file_type: Type of file
            content: File content

        Returns:
            Dictionary with metadata
        """
        metadata = {
            'file_size_bytes': len(content),
            'file_size_human': self._human_readable_size(len(content))
        }

        # Image-specific metadata
        if file_type == 'image':
            try:
                with Image.open(file_path) as img:
                    metadata.update({
                        'width': img.width,
                        'height': img.height,
                        'format': img.format,
                        'mode': img.mode,
                        'has_transparency': img.mode in ('RGBA', 'LA', 'P')
                    })

                    # Get EXIF data if available
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = img._getexif()
                        metadata['exif'] = {k: str(v) for k, v in exif.items() if k < 1000}

            except Exception as e:
                logger.error(f"Error extracting image metadata: {e}")

        return metadata

    def retrieve_media(self, file_id: str, admin_id: str,
                      thumbnail_size: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve media file (admin-only) - works with smart classification

        Args:
            file_id: File ID
            admin_id: Admin user ID
            thumbnail_size: Optional thumbnail size ('small', 'medium', 'large')

        Returns:
            Dictionary with file info or None
        """
        # Parse file_id to get category
        # file_id format: {category}_{timestamp}_{hash}
        parts = file_id.split('_')
        if len(parts) < 3:
            return None

        category = parts[0]

        # Search for file in the category folder
        category_path = self.base_path / category

        # Also check legacy paths for backward compatibility
        legacy_paths = [self.images_path, self.videos_path, self.audio_path, self.documents_path]
        search_paths = [category_path] + legacy_paths

        for storage_path in search_paths:
            if not storage_path.exists():
                continue

            # Search in date-based subdirectories
            for root, dirs, files in os.walk(storage_path):
                for filename in files:
                    if file_id[len(category) + 1:] in filename and admin_id in filename:
                        file_path = Path(root) / filename

                        # Check if requesting thumbnail
                        is_photo_category = category in ['photos', 'gifs', 'webp', 'icons', 'image']
                        if thumbnail_size and is_photo_category:
                            thumb_filename = f"{Path(filename).stem}_{thumbnail_size}.jpg"
                            thumb_path = self.thumbnails_path / thumb_filename

                            if thumb_path.exists():
                                file_path = thumb_path

                        return {
                            'file_path': str(file_path),
                            'filename': filename,
                            'category': category,
                            'exists': True,
                            'size': file_path.stat().st_size
                        }

        return None

    def delete_media(self, file_id: str, admin_id: str) -> bool:
        """
        Delete media file (admin-only) - works with smart classification

        Args:
            file_id: File ID
            admin_id: Admin user ID

        Returns:
            True if deleted, False otherwise
        """
        file_info = self.retrieve_media(file_id, admin_id)

        if not file_info:
            return False

        try:
            # Delete main file
            file_path = Path(file_info['file_path'])
            if file_path.exists():
                file_path.unlink()

            # Delete thumbnails if photo category
            category = file_info.get('category', '')
            is_photo_category = category in ['photos', 'gifs', 'webp', 'icons', 'image']
            if is_photo_category:
                for size_name in self.THUMBNAIL_SIZES.keys():
                    thumb_filename = f"{Path(file_info['filename']).stem}_{size_name}.jpg"
                    thumb_path = self.thumbnails_path / thumb_filename
                    if thumb_path.exists():
                        thumb_path.unlink()

            logger.info(f"Deleted media file: {file_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting {file_id}: {e}")
            return False

    def list_media(self, admin_id: str, category: Optional[str] = None,
                  limit: int = 100) -> list[Dict[str, Any]]:
        """
        List all media files for admin - supports smart classification

        Args:
            admin_id: Admin user ID
            category: Optional filter by smart category (e.g., 'photos', 'gifs', 'html')
            limit: Maximum number of results

        Returns:
            List of file information
        """
        results = []

        # Determine paths to search
        if category:
            # Search specific category folder
            search_paths = [self.base_path / category]
        else:
            # Search all category folders (excluding thumbnails and temp)
            search_paths = [p for p in self.base_path.iterdir()
                          if p.is_dir() and p.name not in ['thumbnails', 'temp']]

        for storage_path in search_paths:
            if not storage_path.exists():
                continue

            for root, dirs, files in os.walk(storage_path):
                for filename in files:
                    if admin_id in filename:
                        file_path = Path(root) / filename

                        # Determine category from path
                        try:
                            relative_path = file_path.relative_to(self.base_path)
                            file_category = relative_path.parts[0]
                        except:
                            file_category = storage_path.name

                        results.append({
                            'filename': filename,
                            'category': file_category,
                            'file_path': str(file_path.relative_to(self.base_path)),
                            'size': file_path.stat().st_size,
                            'size_human': self._human_readable_size(file_path.stat().st_size),
                            'created_at': datetime.fromtimestamp(
                                file_path.stat().st_ctime
                            ).isoformat()
                        })

                        if len(results) >= limit:
                            return results

        return results

    @staticmethod
    def _human_readable_size(size_bytes: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"


# Global storage handler instance
_storage_instance = None


def get_media_storage() -> MediaStorageHandler:
    """Get singleton media storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = MediaStorageHandler()
    return _storage_instance
