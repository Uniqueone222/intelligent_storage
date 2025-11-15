"""
File Browser Views
Allow users to browse their uploaded files by category.
"""

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.views.generic import ListView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from pathlib import Path
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os

from .models import MediaFile
from .file_organizer import file_organizer


class FileBrowserView(TemplateView):
    """Browse files by category."""
    template_name = 'storage/file_browser.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get folder statistics
        stats = file_organizer.get_folder_stats()
        context['folder_stats'] = stats

        # Get selected category from URL
        category = self.request.GET.get('category', 'all')
        context['selected_category'] = category

        # Normalize category (handle both singular and plural forms)
        category_map = {
            'image': 'images',
            'video': 'videos',
            'audio': 'audio',
            'document': 'documents',
            'code': 'code',
            'compressed': 'compressed',
            'program': 'programs',
            'other': 'others',
        }

        # Get files for selected category (exclude deleted files)
        if category == 'all':
            files = MediaFile.objects.filter(is_deleted=False).order_by('-uploaded_at')[:100]
        else:
            db_category = category_map.get(category, category)
            files = MediaFile.objects.filter(
                detected_type=db_category,
                is_deleted=False
            ).order_by('-uploaded_at')[:100]

        context['files'] = files

        # Categories for sidebar
        context['categories'] = [
            {'key': 'all', 'name': 'All Files', 'icon': '📁'},
            {'key': 'image', 'name': 'Images', 'icon': '🖼️'},
            {'key': 'video', 'name': 'Videos', 'icon': '🎬'},
            {'key': 'audio', 'name': 'Audio', 'icon': '🎵'},
            {'key': 'document', 'name': 'Documents', 'icon': '📄'},
            {'key': 'code', 'name': 'Code', 'icon': '💻'},
            {'key': 'compressed', 'name': 'Archives', 'icon': '📦'},
            {'key': 'other', 'name': 'Others', 'icon': '📎'},
        ]

        return context


def file_browser_api(request):
    """
    API endpoint to browse files by category.

    Query params:
    - category: Filter by file type (image, video, document, etc.)
    - limit: Number of files to return (default: 50)
    - offset: Pagination offset (default: 0)
    """
    category = request.GET.get('category', 'all')
    limit = min(int(request.GET.get('limit', 50)), 100)
    offset = int(request.GET.get('offset', 0))

    # Normalize category (handle both singular and plural forms)
    # Database stores plural forms like "images", "videos"
    category_map = {
        'image': 'images',
        'video': 'videos',
        'audio': 'audio',
        'document': 'documents',
        'code': 'code',
        'compressed': 'compressed',
        'program': 'programs',
        'other': 'others',
    }

    # Get files (exclude deleted files unless viewing trash)
    if category == 'trash':
        files = MediaFile.objects.filter(is_deleted=True)
    elif category == 'all':
        files = MediaFile.objects.filter(is_deleted=False)
    else:
        # Use mapped plural form for database query
        db_category = category_map.get(category, category)
        files = MediaFile.objects.filter(detected_type=db_category, is_deleted=False)

    # Pagination
    total_count = files.count()
    files = files.order_by('-uploaded_at')[offset:offset+limit]

    # Reverse map for serialization (plural to singular)
    type_display_map = {
        'images': 'image',
        'videos': 'video',
        'audio': 'audio',
        'documents': 'document',
        'code': 'code',
        'compressed': 'compressed',
        'programs': 'program',
        'others': 'other',
    }

    # Serialize files
    files_data = []
    for file in files:
        # Convert plural form back to singular for frontend
        display_type = type_display_map.get(file.detected_type, file.detected_type)

        files_data.append({
            'id': file.id,
            'name': file.original_name,
            'type': display_type,
            'size': file.file_size,
            'mime_type': file.mime_type,
            'uploaded_at': file.uploaded_at.isoformat(),
            'is_indexed': file.is_indexed,
            'relative_path': file.relative_path,
            'preview_url': f'/media/{file.relative_path}' if file.relative_path else None,
        })

    return JsonResponse({
        'files': files_data,
        'total_count': total_count,
        'limit': limit,
        'offset': offset,
        'has_more': offset + limit < total_count,
    })


def folder_stats_api(request):
    """Get statistics for all file type folders."""
    stats = file_organizer.get_folder_stats()

    # Add total stats
    total = {
        'count': sum(s['count'] for s in stats.values()),
        'size_bytes': sum(s['size_bytes'] for s in stats.values()),
        'size_mb': sum(s['size_mb'] for s in stats.values()),
    }

    # Add trash count
    trash_count = MediaFile.objects.filter(is_deleted=True).count()

    return JsonResponse({
        'by_type': stats,
        'total': total,
        'trash': trash_count,
    })


def download_file(request, file_id):
    """Download a file by ID."""
    try:
        media_file = MediaFile.objects.get(id=file_id)

        if not media_file.file_path or not os.path.exists(media_file.file_path):
            raise Http404('File not found on disk')

        # Serve file
        response = FileResponse(
            open(media_file.file_path, 'rb'),
            content_type=media_file.mime_type
        )
        response['Content-Disposition'] = f'attachment; filename="{media_file.original_name}"'

        return response

    except MediaFile.DoesNotExist:
        raise Http404('File not found in database')


def preview_file(request, file_id):
    """Preview a file (for images, PDFs, etc.)."""
    try:
        media_file = MediaFile.objects.get(id=file_id)

        if not media_file.file_path or not os.path.exists(media_file.file_path):
            raise Http404('File not found on disk')

        # Serve file for preview (inline)
        response = FileResponse(
            open(media_file.file_path, 'rb'),
            content_type=media_file.mime_type
        )
        response['Content-Disposition'] = f'inline; filename="{media_file.original_name}"'

        return response

    except MediaFile.DoesNotExist:
        raise Http404('File not found in database')


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_file(request, file_id):
    """Move file to trash (soft delete)."""
    try:
        media_file = MediaFile.objects.get(id=file_id)

        # Soft delete - move to trash
        media_file.is_deleted = True
        media_file.deleted_at = timezone.now()
        media_file.save()

        return JsonResponse({
            'success': True,
            'message': f'File "{media_file.original_name}" moved to trash'
        })

    except MediaFile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'File not found in database'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def permanent_delete_file(request, file_id):
    """Permanently delete a file from trash."""
    try:
        media_file = MediaFile.objects.get(id=file_id, is_deleted=True)

        # Delete physical file from disk
        if media_file.file_path and os.path.exists(media_file.file_path):
            try:
                os.remove(media_file.file_path)
            except OSError as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to delete physical file: {str(e)}'
                }, status=500)

        # Delete database record permanently
        file_name = media_file.original_name
        media_file.delete()

        return JsonResponse({
            'success': True,
            'message': f'File "{file_name}" permanently deleted'
        })

    except MediaFile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'File not found in trash'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def restore_file(request, file_id):
    """Restore a file from trash."""
    try:
        media_file = MediaFile.objects.get(id=file_id, is_deleted=True)

        # Restore file
        media_file.is_deleted = False
        media_file.deleted_at = None
        media_file.save()

        return JsonResponse({
            'success': True,
            'message': f'File "{media_file.original_name}" restored'
        })

    except MediaFile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'File not found in trash'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
