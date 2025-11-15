"""
Django REST Framework serializers for the storage app.
"""

from rest_framework import serializers
from .models import MediaFile, JSONDataStore, UploadBatch


class MediaFileSerializer(serializers.ModelSerializer):
    """Serializer for MediaFile model."""

    class Meta:
        model = MediaFile
        fields = '__all__'
        read_only_fields = [
            'detected_type', 'mime_type', 'file_extension',
            'magic_description', 'ai_category', 'ai_subcategory',
            'ai_tags', 'ai_description', 'storage_category',
            'storage_subcategory', 'relative_path', 'uploaded_at',
            'processed_at'
        ]


class JSONDataStoreSerializer(serializers.ModelSerializer):
    """Serializer for JSONDataStore model."""

    class Meta:
        model = JSONDataStore
        fields = '__all__'
        read_only_fields = [
            'database_type', 'confidence_score', 'inferred_schema',
            'structure_depth', 'has_nested_objects', 'has_arrays',
            'is_consistent', 'ai_reasoning', 'record_count',
            'created_at', 'updated_at'
        ]


class UploadBatchSerializer(serializers.ModelSerializer):
    """Serializer for UploadBatch model."""

    class Meta:
        model = UploadBatch
        fields = '__all__'
        read_only_fields = ['batch_id', 'started_at', 'completed_at']


class FileUploadSerializer(serializers.Serializer):
    """Serializer for file upload requests."""

    file = serializers.FileField(required=True)
    user_comment = serializers.CharField(required=False, allow_blank=True)


class BatchFileUploadSerializer(serializers.Serializer):
    """Serializer for batch file upload requests."""

    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )
    user_comment = serializers.CharField(required=False, allow_blank=True)


class JSONUploadSerializer(serializers.Serializer):
    """Serializer for JSON data upload requests."""

    data = serializers.JSONField(required=True)
    name = serializers.CharField(required=False)
    user_comment = serializers.CharField(required=False, allow_blank=True)
    force_db_type = serializers.ChoiceField(
        choices=['SQL', 'NoSQL'],
        required=False,
        help_text="Force a specific database type instead of AI recommendation"
    )
