"""
Intelligent Database Selection Engine.
Analyzes JSON structure AND usage patterns to choose optimal database.

Key Considerations:
- SQL: Faster writes, ACID compliance, structured queries
- NoSQL: Faster reads, horizontal scaling, flexible schema
"""

import json
import re
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class SmartDatabaseSelector:
    """
    Advanced database selection using multiple analysis factors.

    Decision Factors:
    1. Data structure (nesting, arrays, consistency)
    2. Read/write ratio (predicted usage pattern)
    3. Query complexity
    4. Data size and growth
    5. Relationship complexity
    """

    def __init__(self):
        # Performance characteristics
        self.sql_write_speed = 1.0      # Baseline
        self.nosql_write_speed = 0.7    # Slower writes
        self.sql_read_speed = 0.8       # Slower reads
        self.nosql_read_speed = 1.0     # Baseline (faster)

        # Regex patterns for data analysis
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}')
        self.date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        self.id_pattern = re.compile(r'^[a-zA-Z_]+_?id$', re.IGNORECASE)

    def analyze_and_select(
        self,
        data: Dict or List,
        user_comment: str = None,
        expected_read_write_ratio: float = None
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis to select optimal database.

        Args:
            data: JSON data to analyze
            user_comment: User context about usage
            expected_read_write_ratio: Expected reads/writes ratio
                                      >1.0 = read-heavy, <1.0 = write-heavy

        Returns:
            Analysis result with database recommendation
        """
        # Step 1: Structural Analysis
        structure_analysis = self._analyze_structure(data)

        # Step 2: Pattern Analysis
        pattern_analysis = self._analyze_patterns(data, user_comment)

        # Step 3: Usage Pattern Prediction
        usage_prediction = self._predict_usage(
            data, user_comment, expected_read_write_ratio
        )

        # Step 4: Calculate Scores
        sql_score = self._calculate_sql_score(
            structure_analysis, pattern_analysis, usage_prediction
        )
        nosql_score = self._calculate_nosql_score(
            structure_analysis, pattern_analysis, usage_prediction
        )

        # Step 5: Make Decision
        if sql_score > nosql_score:
            database_type = 'SQL'
            confidence = int((sql_score / (sql_score + nosql_score)) * 100)
        else:
            database_type = 'NoSQL'
            confidence = int((nosql_score / (sql_score + nosql_score)) * 100)

        # Step 6: Generate Reasoning
        reasoning = self._generate_reasoning(
            database_type, structure_analysis, pattern_analysis, usage_prediction
        )

        # Step 7: Generate Suggested Schema
        suggested_schema = self._generate_schema_suggestion(data, database_type)

        return {
            'database_type': database_type,
            'confidence': confidence,
            'reasoning': reasoning,
            'suggested_schema': suggested_schema,
            'structure_analysis': structure_analysis,
            'usage_prediction': usage_prediction,
            'sql_score': sql_score,
            'nosql_score': nosql_score,
            'performance_estimate': self._estimate_performance(
                database_type, usage_prediction
            )
        }

    def _analyze_structure(self, data: Dict or List) -> Dict:
        """Analyze data structure characteristics."""
        sample = data[0] if isinstance(data, list) and data else data

        analysis = {
            'depth': self._calculate_depth(sample),
            'has_nested_objects': self._has_nested_objects(sample),
            'has_arrays': self._has_arrays(sample),
            'array_complexity': self._analyze_array_complexity(sample),
            'field_count': self._count_fields(sample),
            'is_consistent': self._check_consistency(data) if isinstance(data, list) else True,
            'has_relationships': self._detect_relationships(sample),
            'data_size': len(json.dumps(data)),
            'record_count': len(data) if isinstance(data, list) else 1
        }

        return analysis

    def _analyze_patterns(self, data: Dict or List, user_comment: str = None) -> Dict:
        """Analyze data patterns and types."""
        sample = data[0] if isinstance(data, list) and data else data

        patterns = {
            'has_ids': self._detect_id_fields(sample),
            'has_timestamps': self._detect_timestamps(sample),
            'has_emails': self._detect_emails(json.dumps(sample)),
            'data_types': self._analyze_data_types(sample),
            'field_cardinality': self._estimate_cardinality(data),
            'has_foreign_keys': self._detect_foreign_keys(sample)
        }

        # Analyze user comment for clues
        if user_comment:
            comment_lower = user_comment.lower()
            patterns['user_hints'] = {
                'mentions_analytics': any(w in comment_lower for w in ['analytic', 'report', 'dashboard']),
                'mentions_transactions': any(w in comment_lower for w in ['transaction', 'order', 'payment']),
                'mentions_logs': any(w in comment_lower for w in ['log', 'event', 'activity']),
                'mentions_profile': any(w in comment_lower for w in ['profile', 'user', 'account']),
                'mentions_real_time': any(w in comment_lower for w in ['real-time', 'live', 'streaming'])
            }
        else:
            patterns['user_hints'] = {}

        return patterns

    def _predict_usage(
        self,
        data: Dict or List,
        user_comment: str = None,
        explicit_ratio: float = None
    ) -> Dict:
        """
        Predict read/write usage patterns.

        Returns expected_read_write_ratio:
        - > 2.0 : Read-heavy (analytics, reports) → NoSQL better
        - 1.0-2.0: Balanced → Either OK
        - < 1.0: Write-heavy (transactions) → SQL better
        """
        if explicit_ratio is not None:
            read_write_ratio = explicit_ratio
        else:
            # Predict based on data characteristics
            read_write_ratio = 1.5  # Default: slightly read-heavy

            # Adjust based on data type
            sample = data[0] if isinstance(data, list) and data else data

            # Transaction-like data (write-heavy)
            if self._looks_like_transaction(sample):
                read_write_ratio = 0.8

            # Log/event data (write-heavy, append-only)
            elif self._looks_like_log(sample):
                read_write_ratio = 0.5

            # Analytics/reporting data (read-heavy)
            elif self._looks_like_analytics(sample):
                read_write_ratio = 3.0

            # User profiles (balanced but favor reads)
            elif self._looks_like_profile(sample):
                read_write_ratio = 1.8

            # User comment hints
            if user_comment:
                comment_lower = user_comment.lower()
                if 'report' in comment_lower or 'analytics' in comment_lower:
                    read_write_ratio += 1.0
                elif 'transaction' in comment_lower or 'payment' in comment_lower:
                    read_write_ratio -= 0.5

        return {
            'read_write_ratio': read_write_ratio,
            'usage_type': self._classify_usage_type(read_write_ratio),
            'expected_queries': self._predict_query_types(data),
            'growth_pattern': self._predict_growth(data)
        }

    def _calculate_sql_score(
        self,
        structure: Dict,
        patterns: Dict,
        usage: Dict
    ) -> float:
        """Calculate SQL suitability score."""
        score = 50.0  # Base score

        # Structure factors (favor SQL for flat, consistent data)
        if structure['depth'] <= 2:
            score += 15
        elif structure['depth'] <= 3:
            score += 5
        else:
            score -= 10

        if structure['is_consistent']:
            score += 20

        if not structure['has_nested_objects']:
            score += 15

        if not structure['has_arrays']:
            score += 10

        if structure['has_relationships']:
            score += 15  # SQL excellent for relationships

        # Pattern factors
        if patterns['has_ids']:
            score += 10

        if patterns['has_foreign_keys']:
            score += 15

        if patterns['has_timestamps']:
            score += 5

        # Usage factors (SQL better for write-heavy, ACID transactions)
        read_write_ratio = usage['read_write_ratio']
        if read_write_ratio < 1.0:
            # Write-heavy: SQL advantage
            score += 20 * (1.0 - read_write_ratio)
        elif read_write_ratio > 2.0:
            # Read-heavy: SQL disadvantage
            score -= 10

        if usage['usage_type'] == 'transactional':
            score += 25  # ACID compliance critical

        # Data size (SQL better for smaller, structured data)
        if structure['record_count'] < 10000:
            score += 10

        return max(0, min(100, score))

    def _calculate_nosql_score(
        self,
        structure: Dict,
        patterns: Dict,
        usage: Dict
    ) -> float:
        """Calculate NoSQL suitability score."""
        score = 50.0  # Base score

        # Structure factors (favor NoSQL for complex, nested data)
        if structure['depth'] > 3:
            score += 20
        elif structure['depth'] > 2:
            score += 10

        if structure['has_nested_objects']:
            score += 15

        if structure['has_arrays']:
            score += 15

        if structure['array_complexity'] > 0.5:
            score += 10

        if not structure['is_consistent']:
            score += 20  # NoSQL handles schema flexibility well

        # Pattern factors
        if patterns['data_types'].get('mixed_types', False):
            score += 10

        # Usage factors (NoSQL better for read-heavy, horizontal scaling)
        read_write_ratio = usage['read_write_ratio']
        if read_write_ratio > 2.0:
            # Read-heavy: NoSQL advantage
            score += 15 * (read_write_ratio - 1.0)
        elif read_write_ratio < 1.0:
            # Write-heavy: NoSQL disadvantage (slower writes)
            score -= 10

        if usage['usage_type'] in ['analytics', 'logging']:
            score += 20

        # Data size (NoSQL better for large, growing datasets)
        if structure['record_count'] > 10000:
            score += 15

        if usage['growth_pattern'] == 'high':
            score += 15

        return max(0, min(100, score))

    def _generate_reasoning(
        self,
        db_type: str,
        structure: Dict,
        patterns: Dict,
        usage: Dict
    ) -> str:
        """Generate human-readable reasoning."""
        reasons = []

        if db_type == 'SQL':
            # Structure reasons
            if structure['depth'] <= 2:
                reasons.append("flat data structure ideal for relational tables")
            if structure['is_consistent']:
                reasons.append("consistent schema across records")
            if structure['has_relationships']:
                reasons.append("detected relationships benefit from SQL joins")

            # Usage reasons
            if usage['read_write_ratio'] < 1.0:
                reasons.append("write-heavy workload optimized by SQL's fast writes")
            if usage['usage_type'] == 'transactional':
                reasons.append("transactional data requires ACID guarantees")

        else:  # NoSQL
            # Structure reasons
            if structure['depth'] > 3:
                reasons.append("deep nesting handled naturally by document storage")
            if structure['has_nested_objects']:
                reasons.append("nested objects avoid complex SQL joins")
            if not structure['is_consistent']:
                reasons.append("flexible schema accommodates varying structures")

            # Usage reasons
            if usage['read_write_ratio'] > 2.0:
                reasons.append("read-heavy workload benefits from NoSQL's fast reads")
            if usage['growth_pattern'] == 'high':
                reasons.append("high growth potential favors horizontal scaling")

        return "; ".join(reasons) if reasons else f"{db_type} selected based on overall analysis"

    def _estimate_performance(self, db_type: str, usage: Dict) -> Dict:
        """Estimate performance characteristics."""
        ratio = usage['read_write_ratio']

        if db_type == 'SQL':
            # SQL: Fast writes, slower reads
            write_perf = self.sql_write_speed
            read_perf = self.sql_read_speed
        else:
            # NoSQL: Slower writes, fast reads
            write_perf = self.nosql_write_speed
            read_perf = self.nosql_read_speed

        # Overall performance weighted by usage pattern
        total_ops = ratio + 1  # reads + writes
        overall = (read_perf * ratio + write_perf) / total_ops

        return {
            'write_performance': f"{write_perf * 100:.0f}%",
            'read_performance': f"{read_perf * 100:.0f}%",
            'overall_performance': f"{overall * 100:.0f}%",
            'optimal_for': 'reads' if read_perf > write_perf else 'writes'
        }

    # Helper methods for pattern detection

    def _calculate_depth(self, obj, current=0):
        """Calculate maximum nesting depth."""
        if isinstance(obj, dict):
            return max([self._calculate_depth(v, current + 1) for v in obj.values()] or [current])
        elif isinstance(obj, list) and obj:
            return max([self._calculate_depth(item, current) for item in obj] or [current])
        return current

    def _has_nested_objects(self, obj):
        """Check for nested objects."""
        if isinstance(obj, dict):
            return any(isinstance(v, dict) for v in obj.values())
        return False

    def _has_arrays(self, obj):
        """Check for arrays."""
        if isinstance(obj, dict):
            return any(isinstance(v, list) for v in obj.values())
        return False

    def _analyze_array_complexity(self, obj):
        """Analyze array complexity (0.0 to 1.0)."""
        if not isinstance(obj, dict):
            return 0.0

        array_fields = [v for v in obj.values() if isinstance(v, list)]
        if not array_fields:
            return 0.0

        # Check if arrays contain objects (complex) vs primitives (simple)
        complex_arrays = sum(
            1 for arr in array_fields
            if arr and isinstance(arr[0], (dict, list))
        )

        return complex_arrays / len(array_fields) if array_fields else 0.0

    def _count_fields(self, obj):
        """Count total fields."""
        if isinstance(obj, dict):
            return len(obj)
        return 0

    def _check_consistency(self, data_list):
        """Check if array items have consistent structure."""
        if not isinstance(data_list, list) or len(data_list) < 2:
            return True

        first_keys = set(data_list[0].keys()) if isinstance(data_list[0], dict) else set()
        return all(
            set(item.keys()) == first_keys
            for item in data_list[1:]
            if isinstance(item, dict)
        )

    def _detect_relationships(self, obj):
        """Detect potential relationships (foreign keys)."""
        if not isinstance(obj, dict):
            return False

        # Look for *_id fields
        return any(self.id_pattern.match(key) for key in obj.keys())

    def _detect_id_fields(self, obj):
        """Detect ID fields."""
        if isinstance(obj, dict):
            return any(self.id_pattern.match(k) for k in obj.keys())
        return False

    def _detect_timestamps(self, obj):
        """Detect timestamp fields."""
        if isinstance(obj, dict):
            timestamp_keywords = ['created', 'updated', 'timestamp', 'date', 'time']
            return any(
                any(kw in k.lower() for kw in timestamp_keywords)
                for k in obj.keys()
            )
        return False

    def _detect_emails(self, text):
        """Detect email addresses."""
        return bool(self.email_pattern.search(text))

    def _analyze_data_types(self, obj):
        """Analyze data type distribution."""
        if not isinstance(obj, dict):
            return {}

        types = defaultdict(int)
        for v in obj.values():
            types[type(v).__name__] += 1

        return {
            'type_distribution': dict(types),
            'mixed_types': len(types) > 3
        }

    def _estimate_cardinality(self, data):
        """Estimate field cardinality (uniqueness)."""
        if not isinstance(data, list) or not data:
            return 'unknown'

        # Sample first item
        if isinstance(data[0], dict):
            return 'high' if len(set(str(v) for v in data[0].values())) > 0.7 * len(data[0]) else 'low'

        return 'medium'

    def _detect_foreign_keys(self, obj):
        """Detect potential foreign key relationships."""
        if not isinstance(obj, dict):
            return False

        # Look for patterns like user_id, order_id, etc.
        fk_patterns = [r'.*_id$', r'.*Id$', r'.*ID$']
        return any(
            any(re.match(pattern, key) for pattern in fk_patterns)
            for key in obj.keys()
        )

    def _looks_like_transaction(self, obj):
        """Detect transaction-like data."""
        if not isinstance(obj, dict):
            return False

        transaction_keywords = ['amount', 'payment', 'order', 'transaction', 'status', 'user_id']
        return sum(any(kw in k.lower() for kw in transaction_keywords) for k in obj.keys()) >= 2

    def _looks_like_log(self, obj):
        """Detect log/event data."""
        if not isinstance(obj, dict):
            return False

        log_keywords = ['timestamp', 'event', 'log', 'level', 'message', 'source']
        return sum(any(kw in k.lower() for kw in log_keywords) for k in obj.keys()) >= 2

    def _looks_like_analytics(self, obj):
        """Detect analytics/metrics data."""
        if not isinstance(obj, dict):
            return False

        analytics_keywords = ['metric', 'count', 'total', 'average', 'sum', 'stats']
        return sum(any(kw in k.lower() for kw in analytics_keywords) for k in obj.keys()) >= 2

    def _looks_like_profile(self, obj):
        """Detect user profile data."""
        if not isinstance(obj, dict):
            return False

        profile_keywords = ['name', 'email', 'username', 'profile', 'user', 'account']
        return sum(any(kw in k.lower() for kw in profile_keywords) for k in obj.keys()) >= 2

    def _classify_usage_type(self, ratio):
        """Classify usage type based on read/write ratio."""
        if ratio < 0.5:
            return 'write_intensive'
        elif ratio < 1.0:
            return 'transactional'
        elif ratio < 2.0:
            return 'balanced'
        else:
            return 'analytics'

    def _predict_query_types(self, data):
        """Predict likely query patterns."""
        sample = data[0] if isinstance(data, list) and data else data

        if not isinstance(sample, dict):
            return ['simple']

        queries = []

        if self._detect_id_fields(sample):
            queries.append('key-value lookup')

        if self._detect_timestamps(sample):
            queries.append('time-range queries')

        if self._has_nested_objects(sample):
            queries.append('document traversal')

        if len(sample.keys()) > 10:
            queries.append('complex filtering')

        return queries if queries else ['simple queries']

    def _predict_growth(self, data):
        """Predict data growth pattern."""
        if not isinstance(data, list):
            return 'unknown'

        count = len(data)

        if count > 10000:
            return 'high'
        elif count > 1000:
            return 'medium'
        else:
            return 'low'

    def _generate_schema_suggestion(self, data, db_type):
        """Generate schema suggestion."""
        sample = data[0] if isinstance(data, list) and data else data

        if not isinstance(sample, dict):
            return {}

        schema = {}
        for key, value in sample.items():
            if isinstance(value, bool):
                schema[key] = 'boolean'
            elif isinstance(value, int):
                schema[key] = 'integer'
            elif isinstance(value, float):
                schema[key] = 'float'
            elif isinstance(value, str):
                schema[key] = 'string'
            elif isinstance(value, list):
                schema[key] = 'array'
            elif isinstance(value, dict):
                schema[key] = 'object'
            else:
                schema[key] = 'mixed'

        return schema


# Global instance
smart_db_selector = SmartDatabaseSelector()
