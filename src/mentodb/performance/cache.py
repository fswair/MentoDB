"""Query result caching for performance optimization."""
import hashlib
import json
import time
from typing import Any
from collections import OrderedDict
from threading import Lock


class QueryCache:
    """
    LRU cache for query results with TTL support.

    Example:
        cache = QueryCache(max_size=1000, ttl=300)

        # Cache query result
        result = cache.get(query, params)
        if result is None:
            result = execute_query(query, params)
            cache.set(query, params, result)
    """

    def __init__(self, max_size: int = 1000, ttl: int = 300):
        """
        Initialize query cache.

        Args:
            max_size: Maximum number of cached queries (LRU eviction)
            ttl: Time-to-live in seconds (0 = no expiration)
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def _make_key(self, query: str, params: tuple = ()) -> str:
        """
        Create cache key from query and parameters.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cache key (hash)
        """
        # Normalize query (remove extra whitespace)
        normalized_query = " ".join(query.split())

        # Create key from query + params
        key_data = f"{normalized_query}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def get(self, query: str, params: tuple = ()) -> Any | None:
        """
        Get cached query result.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cached result or None if not found/expired
        """
        key = self._make_key(query, params)

        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            # Check if expired
            cached_data = self._cache[key]
            if self.ttl > 0:
                age = time.time() - cached_data["timestamp"]
                if age > self.ttl:
                    # Remove expired entry
                    del self._cache[key]
                    self._misses += 1
                    return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return cached_data["result"]

    def set(self, query: str, params: tuple, result: Any) -> None:
        """
        Cache query result.

        Args:
            query: SQL query string
            params: Query parameters
            result: Query result to cache
        """
        key = self._make_key(query, params)

        with self._lock:
            # Remove oldest entry if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._cache.popitem(last=False)  # Remove oldest (FIFO)

            # Add or update entry
            self._cache[key] = {
                "result": result,
                "timestamp": time.time(),
            }
            self._cache.move_to_end(key)

    def invalidate(self, query: str | None = None, params: tuple = ()) -> int:
        """
        Invalidate cached entries.

        Args:
            query: SQL query to invalidate (None = invalidate all)
            params: Query parameters (only used if query is specified)

        Returns:
            Number of entries invalidated
        """
        with self._lock:
            if query is None:
                # Clear all
                count = len(self._cache)
                self._cache.clear()
                return count
            else:
                # Clear specific query
                key = self._make_key(query, params)
                if key in self._cache:
                    del self._cache[key]
                    return 1
                return 0

    def invalidate_table(self, table_name: str) -> int:
        """
        Invalidate all cached queries for a specific table.

        Args:
            table_name: Table name

        Returns:
            Number of entries invalidated

        Note:
            This is a simple implementation that checks if table name
            appears in the query. More sophisticated detection could be added.
        """
        with self._lock:
            keys_to_remove = []

            for key, data in self._cache.items():
                # This is a simple heuristic - may have false positives/negatives
                # A more sophisticated approach would parse the SQL
                if table_name.lower() in key.lower():
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self._cache[key]

            return len(keys_to_remove)

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.2f}%",
            }

    def __len__(self) -> int:
        """Get number of cached entries."""
        return len(self._cache)


class CachedConnection:
    """
    Database connection wrapper with query caching.

    Example:
        cache = QueryCache(max_size=1000, ttl=300)
        cached_conn = CachedConnection(connection, cache)

        # Cached queries
        result = cached_conn.execute("SELECT * FROM users WHERE id = ?", (1,))
    """

    def __init__(self, connection: "sqlite3.Connection", cache: QueryCache):
        """
        Initialize cached connection.

        Args:
            connection: SQLite connection
            cache: Query cache instance
        """
        self.connection = connection
        self.cache = cache

    def execute(
        self,
        query: str,
        params: tuple = (),
        use_cache: bool = True,
    ) -> Any:
        """
        Execute query with optional caching.

        Args:
            query: SQL query
            params: Query parameters
            use_cache: Whether to use cache

        Returns:
            Query results
        """
        # Only cache SELECT queries
        is_select = query.strip().upper().startswith("SELECT")

        if use_cache and is_select:
            # Try cache first
            cached_result = self.cache.get(query, params)
            if cached_result is not None:
                return cached_result

        # Execute query
        cursor = self.connection.cursor()
        cursor.execute(query, params)

        if is_select:
            result = cursor.fetchall()
            if use_cache:
                self.cache.set(query, params, result)
            return result
        else:
            # Non-SELECT queries, invalidate cache
            # Try to extract table name (simple heuristic)
            words = query.split()
            if len(words) >= 3:
                # INSERT INTO table, UPDATE table, DELETE FROM table
                table_name = words[2] if words[0].upper() in ("INSERT", "DELETE") else words[1]
                self.cache.invalidate_table(table_name)

            self.connection.commit()
            return cursor

    def invalidate_cache(self, table: str | None = None) -> int:
        """
        Invalidate cache entries.

        Args:
            table: Table name to invalidate (None = all)

        Returns:
            Number of entries invalidated
        """
        if table:
            return self.cache.invalidate_table(table)
        else:
            return self.cache.invalidate()
