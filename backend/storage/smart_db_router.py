"""
Smart Database Router for Intelligent Storage System

Automatically routes JSON data to the optimal database (SQL/NoSQL) based on
structure analysis and provides unified interface for data operations.
"""

import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from django.conf import settings
from django.db import connection
from pymongo import MongoClient, ASCENDING, DESCENDING
from .json_analyzer import analyze_json_for_database, AnalysisResult
import logging

logger = logging.getLogger(__name__)


class SmartDatabaseRouter:
    """
    Intelligent database router that:
    1. Analyzes JSON structure
    2. Routes to SQL (PostgreSQL) or NoSQL (MongoDB)
    3. Handles storage and retrieval with optimization
    4. Provides caching for fast access
    """

    def __init__(self):
        """Initialize database connections"""
        # MongoDB connection
        mongo_config = settings.DATABASES.get('mongodb', {})
        mongo_host = mongo_config.get('HOST', 'localhost')
        mongo_port = mongo_config.get('PORT', 27017)
        mongo_user = mongo_config.get('USER', '')
        mongo_password = mongo_config.get('PASSWORD', '')
        mongo_db_name = mongo_config.get('NAME', 'intelligent_storage_nosql')

        if mongo_user and mongo_password:
            mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"
        else:
            mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/"

        self.mongo_client = MongoClient(mongo_uri)
        self.mongo_db = self.mongo_client[mongo_db_name]

        # Collections for different data types
        self.json_documents = self.mongo_db['json_documents']
        self.metadata_collection = self.mongo_db['metadata']

        # Create indexes for fast retrieval
        self._setup_indexes()

    def _setup_indexes(self):
        """Create optimized indexes for fast retrieval"""
        try:
            # Indexes for JSON documents
            self.json_documents.create_index([('doc_id', ASCENDING)], unique=True)
            self.json_documents.create_index([('created_at', DESCENDING)])
            self.json_documents.create_index([('admin_id', ASCENDING)])
            self.json_documents.create_index([('db_type', ASCENDING)])
            self.json_documents.create_index([('tags', ASCENDING)])

            # Indexes for metadata
            self.metadata_collection.create_index([('doc_id', ASCENDING)], unique=True)
            self.metadata_collection.create_index([('content_hash', ASCENDING)])

            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    def analyze_and_route(self, json_data: Any, admin_id: str,
                         tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze JSON structure and route to optimal database

        Args:
            json_data: JSON data to store
            admin_id: Admin user ID (for access control)
            tags: Optional tags for categorization

        Returns:
            Dictionary with storage info and analysis results
        """
        # Step 1: Analyze JSON structure
        logger.info("Analyzing JSON structure...")
        analysis = analyze_json_for_database(json_data)

        # Step 2: Generate unique document ID
        doc_id = self._generate_doc_id(json_data)

        # Step 3: Route to appropriate database
        if analysis.recommended_db == 'sql':
            storage_result = self._store_in_sql(json_data, doc_id, admin_id, analysis, tags)
        else:
            storage_result = self._store_in_nosql(json_data, doc_id, admin_id, analysis, tags)

        # Step 4: Store metadata
        self._store_metadata(doc_id, analysis, storage_result, admin_id)

        return {
            'success': True,
            'doc_id': doc_id,
            'database_type': analysis.recommended_db,
            'confidence': analysis.confidence,
            'reasons': analysis.reasons,
            'metrics': analysis.metrics,
            'storage_info': storage_result,
            'timestamp': datetime.now().isoformat()
        }

    def _generate_doc_id(self, data: Any) -> str:
        """Generate unique document ID based on content hash"""
        content_str = json.dumps(data, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"doc_{timestamp}_{content_hash[:12]}"

    def _store_in_sql(self, data: Any, doc_id: str, admin_id: str,
                      analysis: AnalysisResult, tags: Optional[List[str]]) -> Dict[str, Any]:
        """
        Store data in PostgreSQL with optimal schema

        For SQL storage, we create a dynamic table based on the schema analysis
        """
        logger.info(f"Storing {doc_id} in PostgreSQL (SQL)")

        # Create table name from doc_id (sanitize for SQL)
        table_name = f"json_data_{doc_id.replace('-', '_')}"

        try:
            with connection.cursor() as cursor:
                # For structured data, we'll create a normalized table
                schema_info = analysis.schema_info

                # Build CREATE TABLE statement
                columns = [
                    "id SERIAL PRIMARY KEY",
                    "doc_id VARCHAR(100) NOT NULL",
                    "admin_id VARCHAR(100) NOT NULL",
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    "data JSONB NOT NULL"  # Store as JSONB for flexibility
                ]

                # Add indexed fields for common query patterns
                if 'fields' in schema_info:
                    # We'll use JSONB with GIN index for fast queries
                    pass

                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(columns)}
                );
                """
                cursor.execute(create_table_sql)

                # Create GIN index on JSONB column for fast queries
                index_sql = f"""
                CREATE INDEX IF NOT EXISTS {table_name}_data_gin_idx
                ON {table_name} USING GIN (data);
                """
                cursor.execute(index_sql)

                # Create index on doc_id for fast lookups
                doc_id_index_sql = f"""
                CREATE INDEX IF NOT EXISTS {table_name}_doc_id_idx
                ON {table_name} (doc_id);
                """
                cursor.execute(doc_id_index_sql)

                # Insert data
                if isinstance(data, list):
                    # Insert multiple rows
                    for item in data:
                        insert_sql = f"""
                        INSERT INTO {table_name} (doc_id, admin_id, data)
                        VALUES (%s, %s, %s)
                        """
                        cursor.execute(insert_sql, [doc_id, admin_id, json.dumps(item)])
                else:
                    # Insert single row
                    insert_sql = f"""
                    INSERT INTO {table_name} (doc_id, admin_id, data)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(insert_sql, [doc_id, admin_id, json.dumps(data)])

            return {
                'table_name': table_name,
                'database': 'postgresql',
                'indexed_fields': ['data (GIN)', 'doc_id'],
                'optimization': 'JSONB with GIN indexing for fast queries'
            }

        except Exception as e:
            logger.error(f"Error storing in SQL: {e}")
            # Fallback to NoSQL on SQL error
            return self._store_in_nosql(data, doc_id, admin_id, analysis, tags)

    def _store_in_nosql(self, data: Any, doc_id: str, admin_id: str,
                        analysis: AnalysisResult, tags: Optional[List[str]]) -> Dict[str, Any]:
        """
        Store data in MongoDB with optimized structure
        """
        logger.info(f"Storing {doc_id} in MongoDB (NoSQL)")

        try:
            document = {
                'doc_id': doc_id,
                'admin_id': admin_id,
                'data': data,
                'db_type': 'nosql',
                'created_at': datetime.now(),
                'tags': tags or [],
                'analysis': {
                    'confidence': analysis.confidence,
                    'metrics': analysis.metrics
                }
            }

            result = self.json_documents.insert_one(document)

            return {
                'collection': 'json_documents',
                'database': 'mongodb',
                'object_id': str(result.inserted_id),
                'indexed_fields': ['doc_id', 'admin_id', 'created_at', 'db_type', 'tags'],
                'optimization': 'Document storage with compound indexes'
            }

        except Exception as e:
            logger.error(f"Error storing in NoSQL: {e}")
            raise

    def _store_metadata(self, doc_id: str, analysis: AnalysisResult,
                       storage_result: Dict[str, Any], admin_id: str):
        """Store metadata about the document for tracking"""
        try:
            metadata = {
                'doc_id': doc_id,
                'admin_id': admin_id,
                'database_type': analysis.recommended_db,
                'confidence': analysis.confidence,
                'reasons': analysis.reasons,
                'metrics': analysis.metrics,
                'storage_info': storage_result,
                'created_at': datetime.now()
            }

            self.metadata_collection.update_one(
                {'doc_id': doc_id},
                {'$set': metadata},
                upsert=True
            )
            logger.info(f"Metadata stored for {doc_id}")

        except Exception as e:
            logger.error(f"Error storing metadata: {e}")

    def retrieve(self, doc_id: str, admin_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document by ID (admin-only access)

        Args:
            doc_id: Document ID
            admin_id: Admin user ID (for access control)

        Returns:
            Document data or None if not found/unauthorized
        """
        # Check metadata to determine database type
        metadata = self.metadata_collection.find_one({'doc_id': doc_id})

        if not metadata:
            logger.warning(f"Document {doc_id} not found")
            return None

        # Admin-only access control
        if metadata.get('admin_id') != admin_id:
            logger.warning(f"Unauthorized access attempt to {doc_id} by {admin_id}")
            return None

        db_type = metadata.get('database_type')

        try:
            if db_type == 'sql':
                return self._retrieve_from_sql(doc_id, metadata)
            else:
                return self._retrieve_from_nosql(doc_id)

        except Exception as e:
            logger.error(f"Error retrieving {doc_id}: {e}")
            return None

    def _retrieve_from_sql(self, doc_id: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve data from PostgreSQL"""
        table_name = metadata['storage_info'].get('table_name')

        if not table_name:
            return None

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT data FROM {table_name} WHERE doc_id = %s", [doc_id])
                rows = cursor.fetchall()

                if not rows:
                    return None

                # Return all rows if multiple, otherwise single object
                data = [json.loads(row[0]) for row in rows]
                return {
                    'doc_id': doc_id,
                    'data': data if len(data) > 1 else data[0],
                    'database_type': 'sql',
                    'metadata': metadata
                }

        except Exception as e:
            logger.error(f"Error retrieving from SQL: {e}")
            return None

    def _retrieve_from_nosql(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from MongoDB"""
        try:
            document = self.json_documents.find_one({'doc_id': doc_id})

            if not document:
                return None

            # Remove MongoDB internal ID
            document.pop('_id', None)

            return {
                'doc_id': doc_id,
                'data': document.get('data'),
                'database_type': 'nosql',
                'metadata': {
                    'created_at': document.get('created_at'),
                    'tags': document.get('tags'),
                    'analysis': document.get('analysis')
                }
            }

        except Exception as e:
            logger.error(f"Error retrieving from NoSQL: {e}")
            return None

    def list_documents(self, admin_id: str, db_type: Optional[str] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all documents for an admin (admin-only)

        Args:
            admin_id: Admin user ID
            db_type: Filter by 'sql' or 'nosql' (optional)
            limit: Maximum number of results

        Returns:
            List of document metadata
        """
        query = {'admin_id': admin_id}
        if db_type:
            query['database_type'] = db_type

        try:
            documents = self.metadata_collection.find(query).sort('created_at', DESCENDING).limit(limit)

            results = []
            for doc in documents:
                doc.pop('_id', None)
                results.append(doc)

            return results

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []

    def delete_document(self, doc_id: str, admin_id: str) -> bool:
        """
        Delete document (admin-only)

        Args:
            doc_id: Document ID
            admin_id: Admin user ID

        Returns:
            True if deleted, False otherwise
        """
        # Check access
        metadata = self.metadata_collection.find_one({'doc_id': doc_id})

        if not metadata or metadata.get('admin_id') != admin_id:
            logger.warning(f"Unauthorized delete attempt for {doc_id}")
            return False

        db_type = metadata.get('database_type')

        try:
            if db_type == 'sql':
                table_name = metadata['storage_info'].get('table_name')
                if table_name:
                    with connection.cursor() as cursor:
                        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            else:
                self.json_documents.delete_one({'doc_id': doc_id})

            # Delete metadata
            self.metadata_collection.delete_one({'doc_id': doc_id})

            logger.info(f"Document {doc_id} deleted successfully")
            return True

        except Exception as e:
            logger.error(f"Error deleting {doc_id}: {e}")
            return False


# Global router instance
_router_instance = None


def get_db_router() -> SmartDatabaseRouter:
    """Get singleton database router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = SmartDatabaseRouter()
    return _router_instance
