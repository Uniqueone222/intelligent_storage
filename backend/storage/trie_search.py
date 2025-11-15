"""
Trie (Prefix Tree) implementation for ultra-fast autocomplete and search.
Provides O(m) lookup time where m is the length of the search query.
"""

import re
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class TrieNode:
    """Node in the Trie data structure."""

    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word = False
        self.file_ids: Set[int] = set()  # Files containing this word
        self.frequency = 0  # How often this word appears


class Trie:
    """
    Trie (Prefix Tree) for efficient prefix-based search.

    Time Complexity:
    - Insert: O(m) where m is word length
    - Search: O(m)
    - Prefix search: O(m + n) where n is number of results

    Space Complexity: O(ALPHABET_SIZE * N * M)
    """

    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0

    def insert(self, word: str, file_id: int = None):
        """
        Insert a word into the Trie.

        Args:
            word: Word to insert
            file_id: Optional file ID associated with this word
        """
        word = word.lower().strip()
        if not word:
            return

        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_end_of_word = True
        node.frequency += 1

        if file_id is not None:
            node.file_ids.add(file_id)

        self.word_count += 1

    def search(self, word: str) -> bool:
        """
        Check if exact word exists in Trie.

        Args:
            word: Word to search

        Returns:
            True if word exists, False otherwise
        """
        node = self._find_node(word.lower())
        return node is not None and node.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        """
        Check if any word starts with the given prefix.

        Args:
            prefix: Prefix to search

        Returns:
            True if prefix exists, False otherwise
        """
        return self._find_node(prefix.lower()) is not None

    def autocomplete(self, prefix: str, max_results: int = 10) -> List[Tuple[str, int]]:
        """
        Get autocomplete suggestions for a prefix.

        Args:
            prefix: Prefix to autocomplete
            max_results: Maximum number of suggestions

        Returns:
            List of (word, frequency) tuples, sorted by frequency
        """
        prefix = prefix.lower()
        node = self._find_node(prefix)

        if node is None:
            return []

        suggestions = []
        self._collect_words(node, prefix, suggestions)

        # Sort by frequency (most common first)
        suggestions.sort(key=lambda x: x[1], reverse=True)

        return suggestions[:max_results]

    def search_files(self, word: str) -> Set[int]:
        """
        Get all file IDs containing this word.

        Args:
            word: Word to search

        Returns:
            Set of file IDs
        """
        node = self._find_node(word.lower())
        if node and node.is_end_of_word:
            return node.file_ids
        return set()

    def fuzzy_search(self, word: str, max_distance: int = 2) -> List[str]:
        """
        Fuzzy search allowing for typos (Levenshtein distance).

        Args:
            word: Word to search (possibly misspelled)
            max_distance: Maximum edit distance allowed

        Returns:
            List of matching words
        """
        word = word.lower()
        results = []

        def dfs(node, current_word, remaining_distance):
            if node.is_end_of_word and remaining_distance >= 0:
                results.append(current_word)

            if remaining_distance < 0:
                return

            for char, child_node in node.children.items():
                # Exact match
                if len(word) > len(current_word) and word[len(current_word)] == char:
                    dfs(child_node, current_word + char, remaining_distance)
                # Substitution, insertion, deletion
                else:
                    dfs(child_node, current_word + char, remaining_distance - 1)

        dfs(self.root, '', max_distance)
        return results[:10]  # Limit results

    def _find_node(self, word: str) -> TrieNode:
        """Find the node representing the given word/prefix."""
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _collect_words(self, node: TrieNode, prefix: str, results: List[Tuple[str, int]]):
        """Recursively collect all words with given prefix."""
        if node.is_end_of_word:
            results.append((prefix, node.frequency))

        for char, child_node in node.children.items():
            self._collect_words(child_node, prefix + char, results)

    def get_stats(self) -> Dict:
        """Get statistics about the Trie."""
        return {
            'total_words': self.word_count,
            'unique_words': self._count_unique_words(),
            'memory_nodes': self._count_nodes()
        }

    def _count_unique_words(self) -> int:
        """Count unique complete words."""
        count = 0

        def dfs(node):
            nonlocal count
            if node.is_end_of_word:
                count += 1
            for child in node.children.values():
                dfs(child)

        dfs(self.root)
        return count

    def _count_nodes(self) -> int:
        """Count total nodes in Trie."""
        count = 0

        def dfs(node):
            nonlocal count
            count += 1
            for child in node.children.values():
                dfs(child)

        dfs(self.root)
        return count


class TrieSearchIndex:
    """
    Search index using Trie for ultra-fast file search.
    """

    def __init__(self):
        self.trie = Trie()
        self.file_metadata: Dict[int, Dict] = {}  # file_id -> metadata

        # Regex patterns for efficient parsing
        self.word_pattern = re.compile(r'\b\w+\b')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.url_pattern = re.compile(r'https?://[^\s]+')
        self.number_pattern = re.compile(r'\b\d+\.?\d*\b')

    def index_file(self, file_id: int, content: str, metadata: Dict = None):
        """
        Index a file's content for fast search.

        Args:
            file_id: Unique file identifier
            content: File content to index
            metadata: Additional metadata (filename, type, etc.)
        """
        if metadata:
            self.file_metadata[file_id] = metadata

        # Extract and index words
        words = self._extract_words(content)
        for word in words:
            self.trie.insert(word, file_id)

    def _extract_words(self, content: str) -> Set[str]:
        """
        Extract words using regex for efficient parsing.

        Args:
            content: Text content

        Returns:
            Set of unique words
        """
        # Extract regular words
        words = set(self.word_pattern.findall(content.lower()))

        # Remove common stop words for efficiency
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being'
        }
        words = words - stop_words

        # Filter out very short words and very long words
        words = {w for w in words if 2 <= len(w) <= 50}

        return words

    def search(self, query: str, fuzzy: bool = False) -> List[Dict]:
        """
        Search for files containing the query.

        Args:
            query: Search query
            fuzzy: Enable fuzzy search for typos

        Returns:
            List of matching file metadata, sorted by relevance
        """
        query_words = self._extract_words(query)

        if not query_words:
            return []

        # Find files for each query word
        file_scores = defaultdict(int)

        for word in query_words:
            if fuzzy:
                # Find similar words (typo-tolerant)
                similar_words = self.trie.fuzzy_search(word, max_distance=2)
                for similar_word in similar_words:
                    file_ids = self.trie.search_files(similar_word)
                    for file_id in file_ids:
                        file_scores[file_id] += 0.5  # Lower score for fuzzy match
            else:
                # Exact match
                file_ids = self.trie.search_files(word)
                for file_id in file_ids:
                    file_scores[file_id] += 1

        # Sort by relevance (number of matching words)
        sorted_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)

        # Return file metadata
        results = []
        for file_id, score in sorted_files:
            if file_id in self.file_metadata:
                result = self.file_metadata[file_id].copy()
                result['relevance_score'] = score
                result['file_id'] = file_id
                results.append(result)

        return results

    def autocomplete(self, prefix: str, max_results: int = 10) -> List[str]:
        """
        Get autocomplete suggestions.

        Args:
            prefix: Partial word to complete
            max_results: Maximum suggestions

        Returns:
            List of suggested completions
        """
        suggestions = self.trie.autocomplete(prefix, max_results)
        return [word for word, _ in suggestions]

    def extract_entities(self, content: str) -> Dict[str, List[str]]:
        """
        Extract entities using regex patterns.

        Args:
            content: Text content

        Returns:
            Dictionary of entity types and their values
        """
        return {
            'emails': self.email_pattern.findall(content),
            'urls': self.url_pattern.findall(content),
            'numbers': self.number_pattern.findall(content)
        }

    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            'trie_stats': self.trie.get_stats(),
            'indexed_files': len(self.file_metadata)
        }


# Global search index instance
search_index = TrieSearchIndex()
