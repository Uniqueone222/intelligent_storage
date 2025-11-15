from django.db import models
from pgvector.django import VectorField


class MediaFile(models.Model):
    """
    Represents an uploaded media file with comprehensive metadata.
    """
    # File information
    original_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=1024)
    file_size = models.BigIntegerField(help_text="File size in bytes")

    # Type detection
    detected_type = models.CharField(max_length=50, help_text="Primary file category")
    mime_type = models.CharField(max_length=100)
    file_extension = models.CharField(max_length=20)
    magic_description = models.TextField(blank=True, null=True)

    # AI Analysis
    ai_category = models.CharField(max_length=255, blank=True, null=True)
    ai_subcategory = models.CharField(max_length=255, blank=True, null=True)
    ai_tags = models.JSONField(default=list, blank=True)
    ai_description = models.TextField(blank=True, null=True)

    # User input
    user_comment = models.TextField(blank=True, null=True)

    # Storage organization
    storage_category = models.CharField(max_length=100)
    storage_subcategory = models.CharField(max_length=100)
    relative_path = models.CharField(max_length=1024)

    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['detected_type']),
            models.Index(fields=['storage_category']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return f"{self.original_name} ({self.detected_type})"

class JSONDataStore(models.Model):
    """
    Tracks JSON data storage in either SQL or NoSQL database.
    """
    # Identification
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    # Database choice
    DATABASE_TYPES = [
        ('SQL', 'PostgreSQL'),
        ('NoSQL', 'MongoDB'),
    ]
    database_type = models.CharField(max_length=10, choices=DATABASE_TYPES)
    confidence_score = models.IntegerField(help_text="AI confidence in DB choice (0-100)")

    # Storage details
    table_name = models.CharField(max_length=255, blank=True, null=True)
    collection_name = models.CharField(max_length=255, blank=True, null=True)

    # Schema information
    inferred_schema = models.JSONField(default=dict)
    sample_data = models.JSONField(default=dict, blank=True)

    # Analysis metadata
    structure_depth = models.IntegerField(default=0)
    has_nested_objects = models.BooleanField(default=False)
    has_arrays = models.BooleanField(default=False)
    is_consistent = models.BooleanField(default=True)
    ai_reasoning = models.TextField(blank=True, null=True)

    # User input
    user_comment = models.TextField(blank=True, null=True)

    # Stats
    record_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['database_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.database_type})"


class UploadBatch(models.Model):
    """
    Tracks batch upload operations.
    """
    batch_id = models.CharField(max_length=100, unique=True)
    total_files = models.IntegerField(default=0)
    processed_files = models.IntegerField(default=0)
    failed_files = models.IntegerField(default=0)

    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Batch {self.batch_id} ({self.status})"


class DocumentChunk(models.Model):
    """
    Stores chunked document content with vector embeddings for semantic search.
    Implements RAG (Retrieval Augmented Generation) capabilities.
    """
    # Source file reference
    media_file = models.ForeignKey(
        MediaFile,
        on_delete=models.CASCADE,
        related_name='chunks',
        null=True,
        blank=True,
        help_text="Reference to the source media file (if applicable)"
    )

    # Chunk information
    chunk_index = models.IntegerField(help_text="Position of this chunk in the document")
    chunk_text = models.TextField(help_text="The actual text content of this chunk")
    chunk_size = models.IntegerField(help_text="Number of characters in this chunk")

    # Vector embedding for semantic search
    embedding = VectorField(
        dimensions=768,
        help_text="Vector embedding generated by Ollama nomic-embed-text model"
    )

    # Metadata
    file_name = models.CharField(max_length=255, help_text="Original file name")
    file_type = models.CharField(max_length=50, help_text="File type/category")
    page_number = models.IntegerField(null=True, blank=True, help_text="Page number (for PDFs)")

    # Additional context
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata (author, date, tags, etc.)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['media_file', 'chunk_index']
        indexes = [
            models.Index(fields=['file_name']),
            models.Index(fields=['file_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.file_name} - Chunk {self.chunk_index}"


class SearchQuery(models.Model):
    """
    Tracks search queries for analytics and improvement.
    """
    query_text = models.TextField(help_text="The search query")
    query_embedding = VectorField(
        dimensions=768,
        help_text="Vector embedding of the query"
    )

    # Results metadata
    results_count = models.IntegerField(default=0)
    top_result_score = models.FloatField(null=True, blank=True)

    # Context
    user_session = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Query: {self.query_text[:50]}..."