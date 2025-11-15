"""
Smart Upload API Views with Auto-Categorization

Provides RESTful API endpoints for:
- Intelligent JSON upload with auto SQL/NoSQL routing
- Media file upload with optimized storage
- Fast retrieval with caching
- Admin-only access control
- Monitoring and logging
"""

import json
import logging
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from .admin_auth import require_admin, get_auth_manager
from .smart_db_router import get_db_router
from .media_storage import get_media_storage
from .json_analyzer import analyze_json_for_database

logger = logging.getLogger(__name__)


# ============================================================================
# Authentication Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def admin_login(request):
    """
    Admin login endpoint

    POST /api/auth/login
    Body: {"username": "admin", "password": "password"}
    Returns: {"token": "...", "admin_id": "..."}
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({
                'error': 'Username and password required'
            }, status=400)

        auth_manager = get_auth_manager()
        result = auth_manager.authenticate(username, password)

        if result['success']:
            return JsonResponse(result)
        else:
            return JsonResponse(result, status=401)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def admin_create(request):
    """
    Create admin user endpoint (first-time setup or existing admin only)

    POST /api/auth/create
    Body: {"username": "admin", "password": "password", "email": "admin@example.com"}
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password:
            return JsonResponse({
                'error': 'Username and password required'
            }, status=400)

        auth_manager = get_auth_manager()
        result = auth_manager.create_admin(username, password, email)

        if result['success']:
            return JsonResponse(result, status=201)
        else:
            return JsonResponse(result, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Admin creation error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_admin
def admin_logout(request, admin_id):
    """
    Admin logout endpoint

    POST /api/auth/logout
    Header: Authorization: Bearer <token>
    """
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = auth_header[7:]  # Remove 'Bearer ' prefix

        auth_manager = get_auth_manager()
        result = auth_manager.logout(token)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Logout error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# ============================================================================
# JSON Upload Endpoints with Smart Routing
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
@require_admin
def upload_json(request, admin_id):
    """
    Upload JSON with automatic SQL/NoSQL categorization

    POST /api/upload/json
    Header: Authorization: Bearer <token>
    Body: JSON data (any structure)
    Returns: Analysis result and storage information
    """
    try:
        # Parse JSON from request
        json_data = json.loads(request.body)

        # Get optional tags from query params
        tags = request.GET.get('tags', '').split(',') if request.GET.get('tags') else None

        # Route to appropriate database
        db_router = get_db_router()
        result = db_router.analyze_and_route(json_data, admin_id, tags)

        # Log decision
        logger.info(
            f"JSON uploaded by {admin_id}: {result['doc_id']} -> "
            f"{result['database_type'].upper()} (confidence: {result['confidence']})"
        )

        # Cache result for fast retrieval
        cache_key = f"json_{result['doc_id']}"
        cache.set(cache_key, result, timeout=3600)  # 1 hour cache

        return JsonResponse(result, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"JSON upload error: {e}", exc_info=True)
        return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_admin
def analyze_json(request, admin_id):
    """
    Analyze JSON without storing (preview mode)

    POST /api/analyze/json
    Header: Authorization: Bearer <token>
    Body: JSON data
    Returns: Analysis result without storage
    """
    try:
        json_data = json.loads(request.body)

        # Analyze without storing
        analysis = analyze_json_for_database(json_data)

        return JsonResponse({
            'recommended_db': analysis.recommended_db,
            'confidence': analysis.confidence,
            'reasons': analysis.reasons,
            'metrics': analysis.metrics,
            'schema_info': analysis.schema_info
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"JSON analysis error: {e}")
        return JsonResponse({'error': 'Analysis failed'}, status=500)


# ============================================================================
# Media Upload Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
@require_admin
def upload_media(request, admin_id):
    """
    Upload media file (image, video, audio, document)

    POST /api/upload/media
    Header: Authorization: Bearer <token>
    Content-Type: multipart/form-data
    Body: file upload
    Returns: Storage information with thumbnails (for images)
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        uploaded_file = request.FILES['file']

        # Store media
        media_storage = get_media_storage()
        result = media_storage.store_media(
            uploaded_file.file,
            uploaded_file.name,
            admin_id
        )

        # Log upload
        logger.info(
            f"Media uploaded by {admin_id}: {result['file_id']} "
            f"({result['file_type']}, {result['file_size']} bytes)"
        )

        # Cache result
        cache_key = f"media_{result['file_id']}"
        cache.set(cache_key, result, timeout=3600)

        return JsonResponse(result, status=201)

    except Exception as e:
        logger.error(f"Media upload error: {e}", exc_info=True)
        return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)


# ============================================================================
# Retrieval Endpoints with Caching
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
@require_admin
def retrieve_json(request, doc_id, admin_id):
    """
    Retrieve JSON document by ID (with caching)

    GET /api/retrieve/json/<doc_id>
    Header: Authorization: Bearer <token>
    Returns: JSON document data
    """
    try:
        # Check cache first
        cache_key = f"json_{doc_id}"
        cached_result = cache.get(cache_key)

        if cached_result:
            logger.info(f"Cache hit for {doc_id}")
            return JsonResponse({
                'cached': True,
                **cached_result
            })

        # Retrieve from database
        db_router = get_db_router()
        result = db_router.retrieve(doc_id, admin_id)

        if not result:
            return JsonResponse({'error': 'Document not found or unauthorized'}, status=404)

        # Cache for next time
        cache.set(cache_key, result, timeout=3600)

        logger.info(f"Retrieved {doc_id} from database")

        return JsonResponse({
            'cached': False,
            **result
        })

    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        return JsonResponse({'error': 'Retrieval failed'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_admin
def retrieve_media(request, file_id, admin_id):
    """
    Retrieve media file by ID

    GET /api/retrieve/media/<file_id>?thumbnail=<size>
    Header: Authorization: Bearer <token>
    Query params: thumbnail (optional): small, medium, large
    Returns: File content with appropriate MIME type
    """
    try:
        thumbnail_size = request.GET.get('thumbnail')

        # Check cache for file info
        cache_key = f"media_{file_id}"
        if thumbnail_size:
            cache_key += f"_{thumbnail_size}"

        # Retrieve file
        media_storage = get_media_storage()
        file_info = media_storage.retrieve_media(file_id, admin_id, thumbnail_size)

        if not file_info:
            return JsonResponse({'error': 'File not found or unauthorized'}, status=404)

        # Return file
        response = FileResponse(
            open(file_info['file_path'], 'rb'),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'inline; filename="{file_info["filename"]}"'

        logger.info(f"Retrieved media {file_id} (thumbnail={thumbnail_size})")

        return response

    except Exception as e:
        logger.error(f"Media retrieval error: {e}")
        return JsonResponse({'error': 'Retrieval failed'}, status=500)


# ============================================================================
# List Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
@require_admin
def list_json_documents(request, admin_id):
    """
    List all JSON documents for admin

    GET /api/list/json?db_type=<sql|nosql>&limit=<number>
    Header: Authorization: Bearer <token>
    Returns: List of documents
    """
    try:
        db_type = request.GET.get('db_type')
        limit = int(request.GET.get('limit', 100))

        db_router = get_db_router()
        documents = db_router.list_documents(admin_id, db_type, limit)

        return JsonResponse({
            'count': len(documents),
            'documents': documents
        })

    except Exception as e:
        logger.error(f"List documents error: {e}")
        return JsonResponse({'error': 'List failed'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_admin
def list_media_files(request, admin_id):
    """
    List all media files for admin

    GET /api/list/media?file_type=<image|video|audio|document>&limit=<number>
    Header: Authorization: Bearer <token>
    Returns: List of media files
    """
    try:
        file_type = request.GET.get('file_type')
        limit = int(request.GET.get('limit', 100))

        media_storage = get_media_storage()
        files = media_storage.list_media(admin_id, file_type, limit)

        return JsonResponse({
            'count': len(files),
            'files': files
        })

    except Exception as e:
        logger.error(f"List media error: {e}")
        return JsonResponse({'error': 'List failed'}, status=500)


# ============================================================================
# Delete Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["DELETE"])
@require_admin
def delete_json(request, doc_id, admin_id):
    """
    Delete JSON document

    DELETE /api/delete/json/<doc_id>
    Header: Authorization: Bearer <token>
    """
    try:
        db_router = get_db_router()
        success = db_router.delete_document(doc_id, admin_id)

        if success:
            # Clear cache
            cache_key = f"json_{doc_id}"
            cache.delete(cache_key)

            return JsonResponse({'success': True, 'message': 'Document deleted'})
        else:
            return JsonResponse({'error': 'Delete failed or unauthorized'}, status=404)

    except Exception as e:
        logger.error(f"Delete error: {e}")
        return JsonResponse({'error': 'Delete failed'}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_admin
def delete_media(request, file_id, admin_id):
    """
    Delete media file

    DELETE /api/delete/media/<file_id>
    Header: Authorization: Bearer <token>
    """
    try:
        media_storage = get_media_storage()
        success = media_storage.delete_media(file_id, admin_id)

        if success:
            # Clear cache
            cache_key = f"media_{file_id}"
            cache.delete(cache_key)

            return JsonResponse({'success': True, 'message': 'File deleted'})
        else:
            return JsonResponse({'error': 'Delete failed or unauthorized'}, status=404)

    except Exception as e:
        logger.error(f"Delete media error: {e}")
        return JsonResponse({'error': 'Delete failed'}, status=500)


# ============================================================================
# Statistics and Monitoring
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
@require_admin
def get_statistics(request, admin_id):
    """
    Get storage statistics for admin

    GET /api/stats
    Header: Authorization: Bearer <token>
    Returns: Statistics about stored data
    """
    try:
        db_router = get_db_router()
        media_storage = get_media_storage()

        # Get document counts
        sql_docs = db_router.list_documents(admin_id, 'sql', limit=10000)
        nosql_docs = db_router.list_documents(admin_id, 'nosql', limit=10000)

        # Get media counts
        all_media = media_storage.list_media(admin_id, limit=10000)
        images = [f for f in all_media if f['file_type'] == 'images']
        videos = [f for f in all_media if f['file_type'] == 'videos']
        audio = [f for f in all_media if f['file_type'] == 'audio']
        documents = [f for f in all_media if f['file_type'] == 'documents']

        # Calculate total storage
        total_media_size = sum(f['size'] for f in all_media)

        stats = {
            'admin_id': admin_id,
            'json_documents': {
                'total': len(sql_docs) + len(nosql_docs),
                'sql': len(sql_docs),
                'nosql': len(nosql_docs)
            },
            'media_files': {
                'total': len(all_media),
                'images': len(images),
                'videos': len(videos),
                'audio': len(audio),
                'documents': len(documents),
                'total_size_bytes': total_media_size,
                'total_size_human': media_storage._human_readable_size(total_media_size)
            }
        }

        return JsonResponse(stats)

    except Exception as e:
        logger.error(f"Statistics error: {e}")
        return JsonResponse({'error': 'Failed to get statistics'}, status=500)
