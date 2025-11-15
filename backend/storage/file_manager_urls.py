"""
File Manager URL Configuration
"""

from django.urls import path
from . import file_manager_views

urlpatterns = [
    # Web Interface
    path('', file_manager_views.file_manager_ui, name='file_manager_ui'),

    # Browse folders
    path('folders/', file_manager_views.browse_folders, name='browse_folders'),

    # List files in category
    path('category/<str:category>/', file_manager_views.list_files_in_category, name='list_category_files'),

    # Search
    path('search/', file_manager_views.search_files, name='search_files'),

    # File operations
    path('file/<path:file_path>/', file_manager_views.get_file_info, name='get_file_info'),
    path('download/<path:file_path>/', file_manager_views.download_file, name='download_file'),
    path('thumbnail/<path:file_path>/', file_manager_views.get_thumbnail, name='get_thumbnail'),
    path('delete/<path:file_path>/', file_manager_views.delete_file, name='delete_file'),

    # Statistics
    path('stats/', file_manager_views.get_storage_stats, name='storage_stats'),
]
